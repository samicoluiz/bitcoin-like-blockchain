from .block import Bloco
from .transaction import Transacao

class Blockchain:
    def __init__(self):
        self.dificuldade = "000"
        self.cadeia = [self.criar_genesis()]
        self.transacoes_pendentes = []

    def criar_genesis(self):
        return Bloco(0, "0" * 64, [], 0, 0)

    @property
    def ultimo_bloco(self):
        return self.cadeia[-1]

    def obter_saldo(self, endereco):
        saldo = 0.0
        for bloco in self.cadeia:
            for tx in bloco.transactions:
                if tx.destino == endereco: saldo += tx.valor
                if tx.origem == endereco: saldo -= tx.valor
        for tx in self.transacoes_pendentes:
            if tx.origem == endereco: saldo -= tx.valor
        return saldo

    def adicionar_transacao(self, tx):
        if tx.valor <= 0: return False, "Valor não positivo"
        
        # Evita propagação infinita e duplicidade
        if any(t.id == tx.id for t in self.transacoes_pendentes):
            return False, "Duplicada"
        for bloco in self.cadeia:
            if any(t.id == tx.id for t in bloco.transactions):
                return False, "Já minerada"

        if tx.origem not in ["genesis", "coinbase"] and self.obter_saldo(tx.origem) < tx.valor:
            return False, "Saldo insuficiente"
        
        self.transacoes_pendentes.append(tx)
        return True, "Sucesso"

    def adicionar_bloco(self, bloco):
        anterior = self.ultimo_bloco
        # Evita adicionar bloco que já temos ou bloco antigo
        if bloco.index <= anterior.index: return False
        
        if bloco.index == anterior.index + 1 and \
           bloco.previous_hash == anterior.hash and \
           bloco.hash.startswith(self.dificuldade) and \
           bloco.hash == bloco.calcular_hash():
            
            self.cadeia.append(bloco)
            ids_conf = [t.id for t in bloco.transactions]
            self.transacoes_pendentes = [t for t in self.transacoes_pendentes if t.id not in ids_conf]
            return True
        return False
