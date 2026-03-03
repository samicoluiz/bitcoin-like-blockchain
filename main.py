import curses
import argparse
import sys
import threading
import time
import os

# Adiciona src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from blockchain.node import No
from blockchain.transaction import Transacao
from blockchain.block import Bloco

def iniciar_tui(stdscr, no):
    curses.curs_set(0)
    stdscr.nodelay(1)
    
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

    while True:
        stdscr.erase()
        altura, largura = stdscr.getmaxyx()

        if altura < 16 or largura < 60:
            try:
                stdscr.addstr(0, 0, "Aumente o tamanho da janela!", curses.color_pair(4) | curses.A_BOLD)
                stdscr.addstr(1, 0, f"Atual: {largura}x{altura} | Requerido: 60x16")
            except: pass
            stdscr.refresh()
            time.sleep(0.5)
            continue

        try:
            status_line = f" ₿ LAB-DIST | NÓ: {no.endereco} | BLOCOS: {len(no.blockchain.cadeia)} | PEERS: {len(no.peers)} "
            stdscr.attron(curses.A_BOLD | curses.color_pair(2))
            stdscr.addstr(0, 0, status_line[:largura-1].ljust(largura-1), curses.A_REVERSE)
            stdscr.attroff(curses.A_BOLD | curses.color_pair(2))

            stdscr.addstr(2, 2, "--- OPERAÇÕES ---", curses.color_pair(1))
            stdscr.addstr(3, 2, " [T] Transferir Moedas")
            stdscr.addstr(4, 2, " [M] Minerar Novo Bloco")
            stdscr.addstr(5, 2, " [P] Ver Pool de Transações")
            stdscr.addstr(6, 2, " [S] Consultar Saldo")

            stdscr.addstr(8, 2, "--- REDE E P2P ---", curses.color_pair(1))
            stdscr.addstr(9, 2, " [B] Ver Blockchain")
            stdscr.addstr(10, 2, " [L] Lista de Peers")
            stdscr.addstr(11, 2, " [C] Conectar a Peer")
            stdscr.addstr(13, 2, " [Q] Sair do Sistema")

            log_start_x = largura // 2
            stdscr.addstr(2, log_start_x, "--- ATIVIDADE DA REDE ---", curses.color_pair(3))
            for i, log in enumerate(no.logs[-12:]):
                texto_log = f" {log}"[:largura - log_start_x - 1]
                stdscr.addstr(3 + i, log_start_x, texto_log)

            stdscr.addstr(altura-1, 0, " Pressione a tecla correspondente para agir. ".ljust(largura-1), curses.A_REVERSE)
        except curses.error:
            pass

        c = stdscr.getch()
        if c != -1:
            try:
                key = chr(c).lower()
                if key == 'q': break
                
                elif key in ['t', 's', 'c']:
                    stdscr.nodelay(0)
                    curses.echo()
                    curses.curs_set(1)
                    
                    if key == 't':
                        stdscr.addstr(altura-3, 2, "Origem:  ".ljust(largura-5))
                        stdscr.move(altura-3, 11)
                        orig = stdscr.getstr().decode('utf-8').strip()
                        
                        stdscr.addstr(altura-2, 2, "Destino: ".ljust(largura-5))
                        stdscr.move(altura-2, 11)
                        dest = stdscr.getstr().decode('utf-8').strip()
                        
                        stdscr.addstr(altura-1, 2, "Valor:   ".ljust(largura-5))
                        stdscr.move(altura-1, 11)
                        val_str = stdscr.getstr().decode('utf-8').strip()
                        
                        try:
                            val = float(val_str)
                            tx = Transacao(orig, dest, val)
                            res, msg = no.blockchain.adicionar_transacao(tx)
                            if res:
                                no.transmitir({"type": "NEW_TRANSACTION", "payload": {"transaction": tx.para_dict()}})
                                no.log(f"[TX] {val} de {orig} para {dest}")
                            else: no.log(f"[!] Erro: {msg}")
                        except: no.log("[!] Valor inválido")

                    elif key == 's':
                        stdscr.addstr(altura-2, 2, "Endereço: ".ljust(largura-5))
                        stdscr.move(altura-2, 12)
                        end = stdscr.getstr().decode('utf-8').strip()
                        if end:
                            saldo = no.blockchain.obter_saldo(end)
                            no.log(f"[SALDO] {end}: {saldo}")
                        else: no.log("[!] Endereço vazio")

                    elif key == 'c':
                        stdscr.addstr(altura-2, 2, "IP:Porta: ".ljust(largura-5))
                        stdscr.move(altura-2, 12)
                        peer_addr = stdscr.getstr().decode('utf-8').strip()
                        if peer_addr: no.sincronizar(peer_addr)

                    curses.noecho()
                    curses.curs_set(0)
                    stdscr.nodelay(1)

                elif key == 'm':
                    def minerar_task():
                        no.log("[*] Minerando...")
                        ant = no.blockchain.ultimo_bloco
                        
                        recompensa = Transacao("coinbase", no.endereco, 50.0)
                        txs = [recompensa] + no.blockchain.transacoes_pendentes.copy()
                        
                        bloco = Bloco(ant.index + 1, ant.hash, txs, 0)
                        while not bloco.hash.startswith(no.blockchain.dificuldade) and no.rodando:
                            bloco.nonce += 1
                            bloco.hash = bloco.calcular_hash()
                        
                        if no.blockchain.adicionar_bloco(bloco):
                            no.transmitir({"type": "NEW_BLOCK", "payload": {"block": bloco.para_dict()}})
                            no.log(f"[MINER] Bloco #{bloco.index} OK (+50 moedas)")
                        else: no.log("[!] Bloco rejeitado")
                    threading.Thread(target=minerar_task, daemon=True).start()

                elif key == 'p':
                    no.log(f"[POOL] {len(no.blockchain.transacoes_pendentes)} transações")
                    for tx in no.blockchain.transacoes_pendentes[:3]:
                        no.log(f" - {tx.origem[:5]}->{tx.destino[:5]}: {tx.valor}")

                elif key == 'b':
                    for b in no.blockchain.cadeia[-3:]:
                        no.log(f"[BLOCK] #{b.index} | Hash: {b.hash[:16]}...")

                elif key == 'l':
                    no.log(f"[REDE] Peers: {list(no.peers)}")

            except: pass

        stdscr.refresh()
        time.sleep(0.05)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost", help="IP para escutar (use seu IP local para rede externa)")
    parser.add_argument("--port", "--porta", type=int, default=5000)
    parser.add_argument("--bootstrap", type=str, nargs='?', help="IP:Porta de um nó existente")
    args = parser.parse_args()
    try:
        no = No(args.host, args.port); no.iniciar()
        if args.bootstrap: no.sincronizar(args.bootstrap)
        curses.wrapper(iniciar_tui, no)
    except Exception as e:
        print(f"\n[!] Erro: {e}")
    finally:
        if 'no' in locals(): no.rodando = False
