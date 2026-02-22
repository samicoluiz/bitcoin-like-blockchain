# Bitcoin Blockchain V2.0 - Criptomoeda Distribuída Simplificada

Implementação de um sistema distribuído de criptomoeda inspirado no Bitcoin com foco em interoperabilidade e segurança.

## Equipe

- **Luiz Sérgio Samico Maciel Filho - 202204940042**
- **Wesley Pontes Barbosa - 202204940006**

## Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Execução Local (Mesmo PC)
python main.py --port 5000
python main.py --port 5001 --bootstrap localhost:5000

# Execução em Rede (Computadores Diferentes)
# No Computador A:
python main.py --host \<IP_DA_MAQUINA\> --port 5555

# No Computador B:
python main.py --host \<IP_DA_MAQUINA\> --port 5555 --bootstrap <IP_DO_COMP_A>:5555
```

## Execução em Rede (Multi-Node)

Para testar o sistema entre computadores na mesma rede Wi-Fi ou Ethernet, siga estes passos:

### 1. Preparação da Rede
- **Perfil de Rede:** Certifique-se de que a rede está configurada como **"Privada"** no Windows (Configurações > Rede e Internet > Wi-Fi/Ethernet > Propriedades). Redes "Públicas" bloqueiam conexões P2P.
- **Firewall:** O Windows bloqueia conexões de entrada por padrão. Libere a porta desejada (ex: 5555) rodando no PowerShell como Administrador:
  ```powershell
  netsh advfirewall firewall add rule name="Blockchain LabDist" dir=in action=allow protocol=TCP localport=5555
  ```

### 2. Identificação de IP
O sistema agora possui **Auto-Discovery**. Ao iniciar com `--host 0.0.0.0`, o nó detectará automaticamente seu IP real na rede local para se anunciar corretamente aos outros peers.

### 3. Troubleshooting (Problemas Comuns)
- **Porta 5000 Ocupada:** O serviço *IP Helper* do Windows costuma ocupar as portas 5000/5001. Recomenda-se usar portas alternativas como **5555**, **8080** ou **9000**.
- **Peers: 0:** Se os nós não se detectarem, verifique se o **Ping** entre as máquinas funciona. Se o ping funcionar e o programa não, o Firewall ainda está bloqueando o tráfego TCP.
- **Erro 10049/10013:** Use `--host 0.0.0.0` para evitar erros de permissão ao tentar "amarrar" o socket a um IP específico que pode ter mudado.

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