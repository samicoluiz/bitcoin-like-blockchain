# Bitcoin Blockchain V2.0 - Criptomoeda Distribuída Simplificada

Implementação de um sistema distribuído de criptomoeda inspirado no Bitcoin com foco em interoperabilidade e segurança.

## Equipe

- **Luiz Sérgio Samico Maciel Filho - 202204940042**
- **Wesley Pontes Barbosa - 202204940006**

## Instalação

```bash
# Instalar dependências (Inclui cryptography para V2.0)
uv sync

# Executar nó
uv run python main.py --port 5000 --bootstrap localhost:5001
```

## Novidades Versão 2.0 (Interoperabilidade Total)

O sistema foi atualizado para incluir recursos avançados sem quebrar a compatibilidade com a Versão 1.0 (outros grupos):

1. **Segurança (Assinaturas Digitais):** Suporte a chaves Ed25519. Transações V2.0 são assinadas e validadas, enquanto transações V1.0 (sem assinatura) são aceitas como "legadas".
2. **Consenso (Dificuldade Dinâmica):** O nó ajusta a dificuldade de mineração (preferindo `0000` se a rede estiver rápida), mas mantém compatibilidade aceitando blocos com prefixo `000`.
3. **Economia (Recompensa Coinbase):** Mineradores recebem automaticamente 50 moedas por bloco.
4. **Monitoramento (Status Check):** Sistema de monitoramento camuflado em mensagens `PING`/`PONG` para evitar erros de parser em nós antigos.

## Protocolo de Mensagens

| Tipo | Descrição |
|------|-----------|
| `NEW_TRANSACTION` | Nova transação (Suporta campo opcional `assinatura`) |
| `NEW_BLOCK` | Bloco minerado |
| `REQUEST_CHAIN` | Solicita blockchain |
| `RESPONSE_CHAIN` | Resposta com blockchain |
| `PING` / `PONG` | Verificação de conexão e Status Check (V2.0) |

## Requisitos

- Proof of Work: Prefixo dinâmico (mínimo `000`)
- Comunicação: Sockets TCP + JSON
- Hash: SHA-256
- Criptografia: Ed25519 (EdDSA) para assinaturas digitais