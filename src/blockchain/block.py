import hashlib
import json
import time
from .transaction import Transacao

class Bloco:
    def __init__(self, index, previous_hash, transactions, nonce=0, timestamp=None, hash=""):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions # Lista de objetos Transacao
        self.nonce = nonce
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.hash = hash or self.calcular_hash()

    def calcular_hash(self):
        dados_bloco = {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "transactions": [tx.para_dict() for tx in self.transactions],
            "nonce": self.nonce,
            "timestamp": self.timestamp
        }
        # sort_keys=True é fundamental para consistência no Windows/Linux
        string_bloco = json.dumps(dados_bloco, sort_keys=True).encode()
        return hashlib.sha256(string_bloco).hexdigest()

    def para_dict(self):
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "transactions": [tx.para_dict() for tx in self.transactions],
            "nonce": self.nonce,
            "timestamp": self.timestamp,
            "hash": self.hash
        }

    @classmethod
    def de_dict(cls, dados):
        txs = [Transacao.de_dict(tx) for tx in dados["transactions"]]
        return cls(
            index=dados["index"],
            previous_hash=dados["previous_hash"],
            transactions=txs,
            nonce=dados["nonce"],
            timestamp=dados["timestamp"],
            hash=dados["hash"]
        )
