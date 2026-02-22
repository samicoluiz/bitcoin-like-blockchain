import unittest
import socket
import json
import threading
import time
import sys
import os

# Adiciona src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from blockchain.transaction import Transacao
from blockchain.block import Bloco
from blockchain.blockchain import Blockchain
from blockchain.node import No

class TestBlockchainIntegracao(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Prepara o ambiente de rede para os testes."""
        cls.host = "localhost"
        cls.porta_a = 6000
        cls.porta_b = 6001
        
    def setUp(self):
        self.bc = Blockchain()

    # --- 1. REQUISITOS DE DADOS E REGRAS DE NEGÓCIO ---

    def test_01_genesis_e_sha256(self):
        """Valida Bloco Gênesis fixo e uso de SHA-256."""
        genesis = self.bc.cadeia[0]
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.previous_hash, "0" * 64)
        self.assertEqual(genesis.hash, genesis.calcular_hash())
        self.assertTrue(len(genesis.hash) == 64)

    def test_02_transacao_campos_e_regras(self):
        """Valida campos da transação e proibição de valores/saldos negativos."""
        tx = Transacao("origem", "destino", 10.0)
        self.assertTrue(hasattr(tx, 'id'))
        self.assertTrue(hasattr(tx, 'timestamp'))
        
        sucesso, msg = self.bc.adicionar_transacao(Transacao("origem", "destino", -1.0))
        self.assertFalse(sucesso)
        
        sucesso, msg = self.bc.adicionar_transacao(Transacao("pobre", "destino", 10.0))
        self.assertFalse(sucesso)

    def test_03_proof_of_work(self):
        """Valida se o Proof of Work exige o prefixo '000'."""
        ant = self.bc.ultimo_bloco
        novo = Bloco(ant.index + 1, ant.hash, [], 0)
        while not novo.hash.startswith("000"):
            novo.nonce += 1
            novo.hash = novo.calcular_hash()
        
        self.assertTrue(novo.hash.startswith("000"))
        self.assertTrue(self.bc.adicionar_bloco(novo))

    # --- 2. REQUISITOS DE PROTOCOLO E SERIALIZAÇÃO ---

    def test_04_json_e_header_bytes(self):
        """Valida se a mensagem segue o formato [4 bytes tamanho] + [JSON]."""
        msg = {"type": "PING", "payload": {}, "sender": "teste:123"}
        dados_json = json.dumps(msg).encode('utf-8')
        header = len(dados_json).to_bytes(4, 'big')
        
        self.assertEqual(header, (len(dados_json)).to_bytes(4, 'big'))
        msg_decodificada = json.loads(dados_json.decode('utf-8'))
        self.assertEqual(msg_decodificada["type"], "PING")

    # --- 3. REQUISITOS DE REDE (SOCKETS E P2P) ---

    def test_05_comunicacao_sockets_e_peers(self):
        """Testa se dois nós se conectam e trocam mensagens via Sockets."""
        no_a = No(self.host, self.porta_a)
        no_b = No(self.host, self.porta_b)
        
        no_a.iniciar()
        no_b.iniciar()
        
        try:
            # Nó B tenta sincronizar com Nó A
            no_b.sincronizar(f"{self.host}:{self.porta_a}")
            time.sleep(1) # Tempo para processamento de rede
            
            # Ambos devem ter registrado um ao outro
            self.assertIn(f"{self.host}:{self.porta_b}", no_a.peers)
            self.assertIn(f"{self.host}:{self.porta_a}", no_b.peers)
            
        finally:
            no_a.rodando = False
            no_b.rodando = False
            if hasattr(no_a, 'socket_servidor'): no_a.socket_servidor.close()
            if hasattr(no_b, 'socket_servidor'): no_b.socket_servidor.close()

    def test_06_sincronizacao_cadeia_mais_longa(self):
        """Testa se um nó atrasado baixa a cadeia maior ao se conectar."""
        no_lider = No(self.host, 6005)
        
        # Cria um bloco extra no líder
        ant = no_lider.blockchain.ultimo_bloco
        recompensa = Transacao("coinbase", no_lider.endereco, 50.0)
        bloco = Bloco(ant.index+1, ant.hash, [recompensa], 0)
        while not bloco.hash.startswith("000"):
            bloco.nonce += 1
            bloco.hash = bloco.calcular_hash()
        no_lider.blockchain.adicionar_bloco(bloco)
            
        self.assertEqual(len(no_lider.blockchain.cadeia), 2)
        
        no_lider.iniciar()
        no_atrasado = No(self.host, 6006)
        
        try:
            # Sincroniza
            no_atrasado.sincronizar(f"{self.host}:6005")
            time.sleep(1)
            
            # Deve ter baixado o bloco
            self.assertEqual(len(no_atrasado.blockchain.cadeia), 2)
            self.assertEqual(no_atrasado.blockchain.ultimo_bloco.hash, no_lider.blockchain.ultimo_bloco.hash)
            
        finally:
            no_lider.rodando = False
            no_atrasado.rodando = False
            if hasattr(no_lider, 'socket_servidor'): no_lider.socket_servidor.close()
            if hasattr(no_atrasado, 'socket_servidor'): no_atrasado.socket_servidor.close()

if __name__ == '__main__':
    unittest.main()
