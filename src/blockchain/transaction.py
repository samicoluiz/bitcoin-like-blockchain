import uuid
import time

class Transacao:
    def __init__(self, origem, destino, valor, id=None, timestamp=None):
        self.id = id or str(uuid.uuid4())
        self.origem = origem
        self.destino = destino
        self.valor = valor
        self.timestamp = timestamp or time.time()

    def para_dict(self):
        return {
            "id": self.id,
            "origem": self.origem,
            "destino": self.destino,
            "valor": self.valor,
            "timestamp": self.timestamp
        }

    @classmethod
    def de_dict(cls, dados):
        return cls(**dados)
