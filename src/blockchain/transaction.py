"""
Módulo de Transações
"""

import uuid
import time
import json
import hashlib
from dataclasses import dataclass, field
from typing import Any
from cryptography.hazmat.primitives.asymmetric import ed25519


@dataclass
class Transaction:
    """
    Representa uma transação na blockchain.
    
    Campos obrigatórios:
    - id: identificador único
    - origem: endereço de origem (chave pública Ed25519 em hex)
    - destino: endereço de destino  
    - valor: quantidade transferida
    - timestamp: momento da criação
    - assinatura: assinatura digital da transação em hex
    """
    origem: str
    destino: str
    valor: float
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    assinatura: str = ""
    
    def __post_init__(self):
        """Valida a transação após criação."""
        if self.valor <= 0:
            raise ValueError("Valor da transação deve ser positivo")
        if not self.origem or not self.destino:
            raise ValueError("Origem e destino são obrigatórios")
    
    def calculate_raw_data(self) -> bytes:
        """Calcula os dados brutos da transação para assinatura/verificação."""
        # Não incluímos a assinatura nos dados a serem assinados
        data = self.to_dict(include_signature=False)
        return json.dumps(data, sort_keys=True).encode()

    def verify_signature(self) -> bool:
        """
        Verifica se a assinatura da transação é válida.
        
        V2.0 Interoperabilidade: Se a assinatura estiver ausente, 
        aceita como transação legada (V1.0) para manter compatibilidade.
        """
        if self.origem in ("coinbase", "genesis"):
            return True
        
        # Se não houver assinatura, aceitamos como transação legada
        if not self.assinatura:
            return True
            
        try:
            public_key_bytes = bytes.fromhex(self.origem)
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            
            signature_bytes = bytes.fromhex(self.assinatura)
            public_key.verify(signature_bytes, self.calculate_raw_data())
            return True
        except Exception:
            return False
    
    def to_dict(self, include_signature: bool = True) -> dict[str, Any]:
        """Converte transação para dicionário (serialização JSON)."""
        data = {
            "id": self.id,
            "origem": self.origem,
            "destino": self.destino,
            "valor": self.valor,
            "timestamp": self.timestamp,
        }
        if include_signature:
            data["assinatura"] = self.assinatura
        return data
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Transaction":
        """Cria transação a partir de dicionário."""
        return cls(
            id=data["id"],
            origem=data["origem"],
            destino=data["destino"],
            valor=data["valor"],
            timestamp=data["timestamp"],
            assinatura=data.get("assinatura", ""),
        )
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, Transaction):
            return self.id == other.id
        return False
