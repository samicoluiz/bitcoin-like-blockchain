import socket
import json
import threading
from .block import Bloco
from .transaction import Transacao
from .blockchain import Blockchain

class No:
    def __init__(self, host, porta):
        self.host = host
        self.porta = porta
        # Se usar 0.0.0.0, descobre o IP real para se identificar na rede
        identificacao = host
        if host == "0.0.0.0":
            try:
                s_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s_temp.connect(("8.8.8.8", 80))
                identificacao = s_temp.getsockname()[0]
                s_temp.close()
            except:
                identificacao = "127.0.0.1"
        
        self.endereco = f"{identificacao}:{porta}"
        self.blockchain = Blockchain()
        self.peers = set()
        self.rodando = True
        self.logs = []

    def log(self, msg):
        self.logs.append(msg)
        if len(self.logs) > 20: self.logs.pop(0)

    def iniciar(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.porta))
        s.listen(10)
        self.socket_servidor = s
        threading.Thread(target=self._aceitar, name="Server", daemon=True).start()

    def _aceitar(self):
        while self.rodando:
            try:
                conexao, _ = self.socket_servidor.accept()
                threading.Thread(target=self._lidar, args=(conexao,), daemon=True).start()
            except: break

    def _lidar(self, conexao):
        try:
            raw_len = conexao.recv(4)
            if not raw_len: return
            msg_len = int.from_bytes(raw_len, 'big')
            
            data = b""
            while len(data) < msg_len:
                chunk = conexao.recv(min(msg_len - len(data), 8192))
                if not chunk: break
                data += chunk
            
            if data:
                mensagem = json.loads(data.decode('utf-8'))
                self._processar(mensagem, conexao)
        except: pass
        finally: conexao.close()

    def _processar(self, mensagem, conexao=None):
        tipo = mensagem.get("type")
        payload = mensagem.get("payload")
        remetente = mensagem.get("sender")

        if remetente and remetente != self.endereco:
            if remetente not in self.peers:
                self.peers.add(remetente)
                self.log(f"[REDE] Peer: {remetente}")

        if tipo == "NEW_TRANSACTION":
            tx = Transacao.de_dict(payload["transaction"])
            # adicionar_transacao agora retorna False para duplicadas, parando o loop
            sucesso, msg = self.blockchain.adicionar_transacao(tx)
            if sucesso:
                self.log(f"[TX] {tx.id[:8]} recebida")
                self.transmitir(mensagem, excluir=remetente)
            
        elif tipo == "NEW_BLOCK":
            bloco = Bloco.de_dict(payload["block"])
            if self.blockchain.adicionar_bloco(bloco):
                self.log(f"[BLOCK] #{bloco.index} aceito")
                self.transmitir(mensagem, excluir=remetente)
            elif bloco.index > self.blockchain.ultimo_bloco.index:
                threading.Thread(target=self.sincronizar, args=(remetente,), daemon=True).start()
            
        elif tipo == "REQUEST_CHAIN":
            res = {
                "type": "RESPONSE_CHAIN", 
                "payload": {"blockchain": {"chain": [b.para_dict() for b in self.blockchain.cadeia]}}, 
                "sender": self.endereco
            }
            if conexao: self._enviar_direto(conexao, res)

        elif tipo == "RESPONSE_CHAIN":
            bc_data = payload.get("blockchain", {}).get("chain", [])
            if not bc_data: bc_data = payload.get("chain", [])
            nova_cadeia = [Bloco.de_dict(b) for b in bc_data]
            if len(nova_cadeia) > len(self.blockchain.cadeia):
                self.blockchain.cadeia = nova_cadeia
                self.log(f"[SYNC] Sincronizado ({len(nova_cadeia)} blocos)")

        elif tipo == "DISCOVER_PEERS":
            res = {"type": "PEERS_LIST", "payload": {"peers": list(self.peers)}, "sender": self.endereco}
            if conexao: self._enviar_direto(conexao, res)

        elif tipo == "PEERS_LIST":
            for p in payload.get("peers", []):
                if p != self.endereco and p not in self.peers:
                    threading.Thread(target=self.conectar_e_apresentar, args=(p,), daemon=True).start()

        elif tipo == "PING":
            res = {"type": "PONG", "payload": {}, "sender": self.endereco}
            if conexao: self._enviar_direto(conexao, res)

    def _enviar_direto(self, conexao, mensagem):
        try:
            dados = json.dumps(mensagem).encode('utf-8')
            conexao.sendall(len(dados).to_bytes(4, 'big') + dados)
        except: pass

    def conectar_e_apresentar(self, peer_addr):
        if not peer_addr or peer_addr == self.endereco: return
        try:
            h, p = peer_addr.split(":")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect((h, int(p)))
                msg = {"type": "DISCOVER_PEERS", "payload": {}, "sender": self.endereco}
                self._enviar_direto(s, msg)
                
                raw_len = s.recv(4)
                if raw_len:
                    msg_len = int.from_bytes(raw_len, 'big')
                    data = b""
                    while len(data) < msg_len:
                        data += s.recv(msg_len - len(data))
                    self._processar(json.loads(data.decode('utf-8')))
        except: pass

    def sincronizar(self, bootstrap):
        if not bootstrap or bootstrap == self.endereco: return
        self.log(f"[*] Sincronizando com {bootstrap}...")
        self.conectar_e_apresentar(bootstrap)
        try:
            h, p = bootstrap.split(":")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((h, int(p)))
                req = {"type": "REQUEST_CHAIN", "payload": {}, "sender": self.endereco}
                self._enviar_direto(s, req)
                
                raw_len = s.recv(4)
                if raw_len:
                    msg_len = int.from_bytes(raw_len, 'big')
                    data = b""
                    while len(data) < msg_len:
                        data += s.recv(msg_len - len(data))
                    self._processar(json.loads(data.decode('utf-8')))
        except: pass

    def transmitir(self, mensagem, excluir=None):
        # Cria uma cópia da mensagem para não alterar o 'sender' original para os outros
        msg_copy = mensagem.copy()
        msg_copy["sender"] = self.endereco
        for peer in list(self.peers):
            if peer != excluir:
                threading.Thread(target=self._enviar_para_peer, args=(peer, msg_copy), daemon=True).start()

    def _enviar_para_peer(self, peer_addr, msg):
        try:
            h, p = peer_addr.split(":")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((h, int(p)))
                self._enviar_direto(s, msg)
        except: pass
