🚀 Roteiro de Testes: Blockchain LSD


  🛠️ Preparação do Ambiente
   1. Certifique-se de ter o Python 3.10+ instalado.
   2. Abra três terminais (Nó A, Nó B e Nó C).
   3. Importante: Mantenha as janelas dos terminais grandes (mínimo 60x16) para o correto
      funcionamento da interface TUI.

  ---

  📅 Semana 1 & 2: Sockets, Estrutura de Nó e Blockchain
  Objetivo: Demonstrar a comunicação P2P independente e a integridade da cadeia local.


   1. Execução Independente:
      - Terminal 1 (Nó A): python3 main.py --porta 5000
      - Terminal 2 (Nó B): python3 main.py --porta 5001 --bootstrap localhost:5000
   2. Validação:
      - Verifique o cabeçalho de ambos: o contador de PEERS deve subir para 1.
      - Pressione [B] (Ver Blockchain): Mostre que ambos iniciam com o Bloco #0 (Gênesis).
      - Requisito: Nó sem servidor central, porta configurável e bloco gênesis fixo.

  ---

  📅 Semana 3: Transações e Pool (Mempool)
  Objetivo: Demonstrar a criação, campos obrigatórios e propagação de transações.


   1. Criação e Campos:
      - No Nó A, pressione [T] (Transferir).
      - Preencha: Origem: genesis, Destino: localhost:5000, Valor: 100.
   2. Propagação e Pool:
      - No Nó B, pressione [P] (Ver Pool de Transações).
      - Validação: A transação deve aparecer no Nó B antes de ser minerada.
   3. Regras de Negócio (Valores Positivos):
      - Tente criar uma transação com valor -10. O log deve exibir [!] Erro: Valor não
        positivo.
      - Requisito: Campos (ID, Origem, Destino, Valor, Timestamp) e proibição de valores
        negativos.

  ---


  📅 Semana 4: Proof of Work e Propagação de Blocos
  Objetivo: Demonstrar o consenso distribuído e a regra do Hash "000".


   1. Mineração (PoW):
      - No Nó A, pressione [M] (Minerar Bloco).
      - O log mostrará [*] Minerando.... Aguarde a confirmação [MINER] Bloco #1 OK.
   2. Validação de Hash e Propagação:
      - No Nó B, verifique o log: [BLOCK] Novo #1 recebido.
      - Pressione [B] no Nó B: O Hash do novo bloco deve começar obrigatoriamente com
        `000`.
      - Requisito: Dificuldade fixa "000", uso de SHA-256 e propagação automática após
        mineração.

  ---


  📅 Semana 5: Entrada Tardia e Sincronização
  Objetivo: Demonstrar que novos nós baixam a cadeia e resolvem conflitos.


   1. Entrada Tardia:
      - No Nó A, mine mais um bloco (Pressione [M]). Agora a rede tem 3 blocos (0, 1 e 2).
      - Terminal 3 (Nó C): python3 main.py --porta 5002 --bootstrap localhost:5000
   2. Resolução de Conflitos (Cadeia mais longa):
      - O Nó C iniciará e enviará um REQUEST_CHAIN.
      - Validação: Verifique o cabeçalho do Nó C. Ele deve exibir BLOCOS: 3 imediatamente.
      - Regra de Saldo Negativo:
        - No Nó C, consulte o saldo de localhost:5000 (Pressione [S]). Deve ser 100.0.
        - Tente enviar 150 de localhost:5000 para alguem. O log deve exibir [!] Erro:
          Saldo insuficiente.
      - Requisito: Sincronização automática via RESPONSE_CHAIN e proibição de saldo
        negativo.

  ---


  📅 Semana 6: Protocolo e Relatório Técnica
  Objetivo: Documentar e revisar os tipos de mensagens.


   1. Mensagens Implementadas:
      - NEW_TRANSACTION: Propagação imediata ao criar via menu.
      - NEW_BLOCK: Propagação imediata ao encontrar o Nonce.
      - REQUEST_CHAIN: Enviado automaticamente por novos nós ou ao detectar cadeia maior.
      - RESPONSE_CHAIN: Enviado em resposta ao pedido de sincronização.
   2. Checklist Final:
      - [ ] Comunicação via sockets TCP? Sim.
      - [ ] Mensagens serializadas em JSON? Sim.
      - [ ] Hash SHA-256 com sort_keys=True? Sim.
      - [ ] Interface visual amigável (TUI)? Sim.


  ---