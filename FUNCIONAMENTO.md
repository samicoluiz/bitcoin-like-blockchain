# Funcionamento Técnico: Blockchain LSD

Este documento detalha a implementação interna do sistema, descrevendo a relação entre os componentes de código e os fundamentos de sistemas distribuídos e criptomoedas.

---

## 1. Fundamentos da Blockchain Implementados

O sistema demonstra os três pilares de uma blockchain simplificada:

1.  **Imutabilidade (Hashing):** Cada bloco é selado por um hash SHA-256. Se um único caractere de uma transação for alterado, o hash do bloco muda, quebrando o encadeamento com o bloco seguinte.
2.  **Consenso (Proof of Work):** Para evitar que qualquer nó controle a rede, exige-se um esforço computacional (encontrar um *Nonce*) que resulte em um hash iniciado por "000".
3.  **Descentralização (P2P):** Não existe um servidor central. Todos os nós são iguais e utilizam um mecanismo de descoberta automática para propagar dados.

---

## 2. Arquitetura de Classes e Métodos

### 📂 `models/` (Estruturas de Dados)

#### Classe `Transacao` (`transaction.py`)
Representa a unidade básica de valor.
-   **`para_dict()`**: Converte o objeto em um dicionário JSON.
-   **`de_dict()`**: Método de classe que reconstrói o objeto a partir de um JSON recebido pela rede.

#### Classe `Bloco` (`block.py`)
Representa o contêiner de dados da cadeia.
-   **`calcular_hash()`**: O método mais crítico. Utiliza `json.dumps(dados, sort_keys=True)` para garantir que a ordem dos campos seja sempre a mesma, gerando hashes idênticos em qualquer máquina (essencial para interoperabilidade).

### 📂 `core/` (Lógica de Negócio)

#### Classe `Blockchain` (`blockchain.py`)
Gerencia o estado global e as regras de consenso.
-   **`obter_saldo(endereco)`**: Percorre toda a cadeia somando e subtraindo valores. O saldo é calculado "on-the-fly", refletindo a natureza transparente da blockchain.
-   **`adicionar_transacao(tx)`**: Valida se a transação é positiva, se o ID não é duplicado (prevenção de tempestade de broadcast) e se o remetente tem saldo.
-   **`adicionar_bloco(bloco)`**: Valida o índice, o hash anterior e o Proof of Work antes de oficializar o bloco na cadeia local.

### 📂 `network/` (Comunicação Distribuída)

#### Classe `No` (`node.py`)
Implementa o protocolo de rede e a inteligência P2P.
-   **`_lidar(conexao)`**: Implementa o protocolo de transmissão: lê 4 bytes (tamanho) e então processa o JSON correspondente.
-   **`_processar(mensagem)`**: O "cérebro" das mensagens. Trata os tipos `NEW_TRANSACTION`, `NEW_BLOCK` e `REQUEST_CHAIN`.
-   **`sincronizar(bootstrap)`**: Realiza o *Handshake* inicial. Pede a lista de peers (`DISCOVER_PEERS`) e a cadeia completa para garantir a entrada tardia no sistema.
-   **`transmitir(mensagem)`**: Realiza o *Broadcast* para todos os vizinhos conectados, garantindo a propagação viral da informação.

---

## 3. Fluxo de Vida de uma Operação

### Criando uma Transação
1.  O usuário usa o comando **[T]** no `main.py`.
2.  O `main.py` cria o objeto `Transacao` e chama `no.blockchain.adicionar_transacao()`.
3.  O `No` propaga a transação via rede.
4.  A transação entra na **Mempool** (Pool de Pendentes) de todos os nós conectados.

### Minerando um Bloco
1.  O usuário usa o comando **[M]** no `main.py`.
2.  Uma tarefa em segundo plano (`Thread`) cria uma transação **Coinbase** (recompensa de 50.0).
3.  O minerador junta a recompensa com as transações da Mempool.
4.  O loop de mineração incrementa o `nonce` até satisfazer a dificuldade "000".
5.  O bloco é enviado para a rede e, se válido, limpa a Mempool dos nós.

---

## 4. Regras de Interoperabilidade

Para que este nó converse com sistemas de outros desenvolvedores, ele segue:
-   **Porta Configurável**: Definida via argumento `--porta`.
-   **Endianness**: Tamanho da mensagem sempre em `big-endian`.
-   **Gênesis Identico**: Hash `0567c3...` garantido pelo timestamp `0`.
-   **Dificuldade**: Prefixo fixo `"000"`.

---

## 5. Scripts Auxiliares

-   **`test_blockchain.py`**: Testes unitários para validar a lógica de saldo e imutabilidade.
-   **`test_blockchain_full.py`**: Testes de integração que abrem sockets reais para validar a comunicação entre dois processos.
