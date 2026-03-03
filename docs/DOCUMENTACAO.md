# Documentação Técnica - Bitcoin Blockchain LSD

## Visão Geral

Sistema distribuído de criptomoeda simplificado (Bitcoin-like) implementado em Python puro, com interface TUI (Terminal User Interface). A arquitetura foi simplificada para minimizar dependências e facilitar a interoperabilidade.

**Equipe:** Luiz Samico, Wesley Barbosa

---

## Arquitetura do Sistema

```text
┌──────────────────────────────────────────────────────────────┐
│                         main.py                              │
│      - Interface TUI (Curses)                                │
│      - Tarefa de Mineração (Thread Dedicada)                 │
└──────────────────────────────────────────────────────────────┘
               │                        │
               ▼                        ▼
┌───────────────────────────┐    ┌─────────────────────────────┐
│      No (node.py)         │    │  Blockchain (blockchain.py) │
│ - Servidor TCP (Sockets)  │◄───┤ - Validação de Cadeia       │
│ - Protocolo JSON Integrado│    │ - Cálculo de Saldo          │
│ - Descoberta P2P Dinâmica │    │ - Gerenciamento de Pool     │
└───────────────────────────┘    └─────────────────────────────┘
               │                        │
               └───────────┬────────────┘
                           ▼
            ┌──────────────────────────────┐
            │      Estruturas de Dados     │
            │  - Bloco (block.py)          │
            │  - Transacao (transaction.py)│
            │  - Serialização JSON Estrita │
            └──────────────────────────────┘
```

---

## Módulos e Responsabilidades

### 1. `main.py` (Ponto de Entrada e Interface)
Este é o coração da interação com o usuário.
- **TUI:** Gerencia o desenho da tela usando `curses`, tratando entradas do teclado e exibindo logs em tempo real.
- **Mineração:** Contém a lógica do *Proof of Work*. Quando disparada, executa em uma *thread* separada para não travar a interface, gerando a transação de recompensa (*coinbase*) e buscando o *nonce* válido.

### 2. `node.py` (Rede e Protocolo)
Consolida toda a infraestrutura de comunicação distribuída.
- **Protocolo:** Implementa o formato `[4 bytes tamanho] + [JSON]` exigido pelo laboratório.
- **Servidor:** Mantém um socket TCP aberto para receber conexões simultâneas de outros nós.
- **P2P:** Gerencia a lista de *Peers* e implementa a descoberta automática (um nó novo pede a lista de amigos aos conhecidos e se conecta a todos).
- **Mensagens:** Processa e propaga `NEW_TRANSACTION`, `NEW_BLOCK`, `REQUEST_CHAIN` e `RESPONSE_CHAIN`.

### 3. `blockchain.py` (Lógica de Negócio)
Gerencia a integridade do livro-razão local.
- **Validação:** Aplica as regras de consenso (dificuldade "000", hashes SHA-256 encadeados).
- **Saldo:** Calcula o saldo somando créditos e subtraindo débitos, garantindo que ninguém gaste o que não tem.
- **Mempool:** Mantém o conjunto de transações pendentes que ainda não foram mineradas.

### 4. `transaction.py` & `block.py` (Modelos)
Definem os objetos fundamentais do sistema.
- **Imutabilidade:** Garantida pelo cálculo do hash SHA-256 sobre os dados serializados.
- **Interoperabilidade:** Utilizam `sort_keys=True` na geração do JSON para que o hash seja idêntico em diferentes sistemas operacionais.

---

## Requisitos do Sistema Atendidos

- [x] **Sockets:** Comunicação TCP entre processos independentes.
- [x] **JSON:** Mensagens e dados estruturados em JSON.
- [x] **Proof of Work:** Dificuldade fixa com prefixo "000".
- [x] **P2P:** Entrada tardia de nós e sincronização automática.
- [x] **Economia:** Recompensa de mineração e proibição de saldo negativo.

---

## Como Executar

1. **Linux/WSL:** `python3 main.py --porta 5000`
2. **Windows nativo:** Instalar `pip install windows-curses` e rodar `python main.py --porta 5000`.
