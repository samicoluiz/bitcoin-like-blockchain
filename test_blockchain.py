import unittest
import sys
import os
import time

# Garante que o diretório src está no path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from blockchain.transaction import Transacao
from blockchain.block import Bloco
from blockchain.blockchain import Blockchain

class TestBlockchainLSD(unittest.TestCase):

    def setUp(self):
        """Inicializa uma nova blockchain antes de cada teste."""
        self.bc = Blockchain()

    # --- TESTES DE REQUISITOS DO ENUNCIADO ---

    def test_bloco_genesis_fixo(self):
        """REQUISITO: Existir um bloco gênesis fixo com hash específico."""
        genesis = self.bc.cadeia[0]
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.previous_hash, "0" * 64)
        # Verifica o hash padronizado (0567c3...)
        self.assertTrue(genesis.hash.startswith("0567c32b"))

    def test_campos_obrigatorios_transacao(self):
        """REQUISITO: Transações devem possuir ID, origem, destino, valor e timestamp."""
        tx = Transacao("origem_teste", "destino_teste", 10.5)
        self.assertIsNotNone(tx.id)
        self.assertEqual(tx.origem, "origem_teste")
        self.assertEqual(tx.destino, "destino_teste")
        self.assertEqual(tx.valor, 10.5)
        self.assertIsInstance(tx.timestamp, float)

    def test_proibir_valor_negativo(self):
        """REQUISITO: Não permitir valores negativos em transações."""
        tx = Transacao("genesis", "aluno", -50.0)
        sucesso, msg = self.bc.adicionar_transacao(tx)
        self.assertFalse(sucesso)
        self.assertEqual(msg, "Valor não positivo")

    def test_proibir_saldo_negativo(self):
        """REQUISITO: Não permitir saldo negativo em nenhuma hipótese."""
        tx = Transacao("conta_vazia", "destino", 10.0)
        sucesso, msg = self.bc.adicionar_transacao(tx)
        self.assertFalse(sucesso)
        self.assertEqual(msg, "Saldo insuficiente")

    def test_proof_of_work_dificuldade(self):
        """REQUISITO: O hash do bloco deve começar com '000'."""
        tx = Transacao("coinbase", "minerador", 50.0)
        self.bc.adicionar_transacao(tx)
        
        ant = self.bc.ultimo_bloco
        novo_bloco = Bloco(ant.index + 1, ant.hash, self.bc.transacoes_pendentes.copy(), 0)
        
        while not novo_bloco.hash.startswith("000"):
            novo_bloco.nonce += 1
            novo_bloco.hash = novo_bloco.calcular_hash()
            
        self.assertTrue(novo_bloco.hash.startswith("000"))
        self.assertTrue(self.bc.adicionar_bloco(novo_bloco))

    # --- TESTES DE SEGURANÇA E INTEGRIDADE ---

    def test_integridade_cadeia_hashes(self):
        """REQUISITO: Cada bloco deve referenciar corretamente o hash do anterior."""
        for i in range(2):
            ant = self.bc.ultimo_bloco
            recompensa = Transacao("coinbase", "minerador", 50.0)
            bloco = Bloco(ant.index + 1, ant.hash, [recompensa], 0)
            while not bloco.hash.startswith("000"):
                bloco.nonce += 1
                bloco.hash = bloco.calcular_hash()
            self.bc.adicionar_bloco(bloco)
            
        for i in range(1, len(self.bc.cadeia)):
            self.assertEqual(self.bc.cadeia[i].previous_hash, self.bc.cadeia[i-1].hash)

    def test_detectar_fraude_em_transacao(self):
        """CENÁRIO: Se alguém alterar um valor dentro de um bloco, o hash deve invalidar."""
        ant = self.bc.ultimo_bloco
        tx = Transacao("genesis", "aluno", 100.0)
        bloco = Bloco(ant.index + 1, ant.hash, [tx], 0)
        while not bloco.hash.startswith("000"):
            bloco.nonce += 1
            bloco.hash = bloco.calcular_hash()
        self.bc.adicionar_bloco(bloco)
        
        self.bc.cadeia[1].transactions[0].valor = 9999.9
        self.assertNotEqual(self.bc.cadeia[1].hash, self.bc.cadeia[1].calcular_hash())

if __name__ == '__main__':
    unittest.main()
