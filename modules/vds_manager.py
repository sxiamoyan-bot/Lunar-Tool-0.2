import socket
import threading
import time
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


connections = {}


def tcp_connect(host, port, user="root"):
    """Direct TCP connection to remote machine"""
    try:
        with console.status(f"[magenta]  {host}:{port} adresine baglaniliyor...[/magenta]", spinner="moon"):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, int(port)))

        cid = len(connections) + 1
        connections[cid] = {
            "sock": sock,
            "host": host,
            "port": port,
            "user": user,
            "connected_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "alive": True,
            "cmds": 0,
            "type": "TCP"
        }

        try:
            sock.settimeout(3)
            sock.send(b"whoami\n")
            info = sock.recv(4096).decode("utf-8", errors="replace").strip()
            connections[cid]["remote_user"] = info.split("\n")[0]
        except Exception:
            connections[cid]["remote_user"] = "-"

        console.print(f"\n[#a78bfa]  🌕 Baglanti #{cid} basarili[/#a78bfa]")
        console.print(f"[dim]  {host}:{port} | Kullanici: {connections[cid]['remote_user']}[/dim]")
        return cid

    except socket.timeout:
        console.print(f"[red]  Zaman asimi: {host}:{port}[/red]")
    except ConnectionRefusedError:
        console.print(f"[red]  Reddedildi: {host}:{port}[/red]")
    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")
    return None


def list_connections():
    if not connections:
        console.print("[dim]  Aktif baglanti yok.[/dim]")
        return

    table = Table(title="🌕 VDS / Makine Baglantilari", border_style="purple", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="bold #a78bfa", justify="center", width=4)
    table.add_column("Host", style="white", min_width=16)
    table.add_column("Port", style="dim", justify="center", width=6)
    table.add_column("Tip", style="magenta", justify="center", width=5)
    table.add_column("Kullanici", style="#a78bfa", width=12)
    table.add_column("Baglanti", style="dim", width=19)
    table.add_column("Komut", style="dim", justify="center", width=5)
    table.add_column("Durum", style="bold", justify="center", width=7)

    for cid, info in connections.items():
        alive = "[#a78bfa]AKTIF[/#a78bfa]" if info["alive"] else "[red]KAPALI[/red]"
        table.add_row(
            str(cid), info["host"], str(info["port"]), info["type"],
            info.get("remote_user", info["user"]),
            info["connected_at"], str(info["cmds"]), alive
        )

    console.print()
    console.print(table)

    active = sum(1 for c in connections.values() if c["alive"])
    console.print(f"\n[dim]  Toplam: {len(connections)}  |  Aktif: {active}[/dim]")


def interact(cid):
    if cid not in connections:
        console.print("[red]  Baglanti bulunamadi.[/red]")
        return

    info = connections[cid]
    if not info["alive"]:
        console.print("[red]  Baglanti aktif degil.[/red]")
        return

    sock = info["sock"]

    console.print(Panel(
        f"[bold white]ID:[/bold white] #{cid}\n"
        f"[bold white]Host:[/bold white] {info['host']}:{info['port']}\n"
        f"[bold white]Tip:[/bold white] {info['type']}\n"
        f"[bold white]Kullanici:[/bold white] {info.get('remote_user', info['user'])}",
        title="🌕 Terminal Etkileşim",
        border_style="purple",
        padding=(0, 2)
    ))
    console.print("[dim]  'back' ile cikin.[/dim]")

    while True:
        try:
            prompt_user = info.get("remote_user", info["user"])
            cmd = console.input(f"[bold magenta]  {prompt_user}@{info['host']} [/bold magenta][bold white]$ [/bold white]").strip()

            if cmd.lower() == "back":
                break
            if not cmd:
                continue

            sock.send((cmd + "\n").encode("utf-8"))
            sock.settimeout(5)
            info["cmds"] += 1

            response = b""
            while True:
                try:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                    if len(chunk) < 4096:
                        break
                except socket.timeout:
                    break

            if response:
                output = response.decode("utf-8", errors="replace")
                if len(output) > 2000:
                    output = output[:2000] + "\n... (kesildi)"
                console.print(Panel(output, border_style="#4a2c8a", padding=(0, 1)))
            else:
                console.print("[dim]  Yanit yok.[/dim]")

        except (ConnectionResetError, BrokenPipeError, OSError):
            console.print("[red]  Baglanti koptu.[/red]")
            info["alive"] = False
            break
        except KeyboardInterrupt:
            break


def kill_conn(cid):
    if cid not in connections:
        console.print("[red]  Baglanti bulunamadi.[/red]")
        return
    try:
        connections[cid]["sock"].close()
    except Exception:
        pass
    connections[cid]["alive"] = False
    console.print(f"[#a78bfa]  Baglanti #{cid} kapatildi.[/#a78bfa]")


def port_scan(host, ports):
    """Quick multi-port check"""
    table = Table(title=f"🌕 Port Tarama - {host}", border_style="purple", show_header=True, header_style="bold magenta")
    table.add_column("Port", style="white", justify="center", width=8)
    table.add_column("Durum", style="bold", justify="center", width=10)
    table.add_column("Servis", style="#a78bfa", width=15)

    common_services = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
        993: "IMAPS", 995: "POP3S", 1433: "MSSQL", 3306: "MySQL",
        3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 6379: "Redis",
        8080: "HTTP-Alt", 8443: "HTTPS-Alt", 27017: "MongoDB"
    }

    with console.status("[magenta]  Taranıyor...[/magenta]", spinner="moon"):
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.5)
                result = sock.connect_ex((host, port))
                sock.close()
                if result == 0:
                    service = common_services.get(port, "-")
                    table.add_row(str(port), "[#a78bfa]ACIK[/#a78bfa]", service)
                else:
                    table.add_row(str(port), "[red]KAPALI[/red]", "-")
            except Exception:
                table.add_row(str(port), "[red]HATA[/red]", "-")

    console.print()
    console.print(table)


def run():
    while True:
        console.print()
        console.print(f"  [bold purple]🌙 VDS MANAGER[/bold purple]")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

        active = sum(1 for c in connections.values() if c["alive"])
        console.print(f"   Aktif Baglanti: {active}")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

        console.print(f"   [#a78bfa]connect[/#a78bfa] [IP] [PORT]    Baglan")
        console.print(f"   [#a78bfa]list[/#a78bfa]                   Baglanti listesi")
        console.print(f"   [#a78bfa]interact[/#a78bfa] [ID]          Terminal etkileşim")
        console.print(f"   [#a78bfa]kill[/#a78bfa] [ID]              Baglanti kapat")
        console.print(f"   [#a78bfa]scan[/#a78bfa] [IP]              Yaygin port tara")
        console.print(f"   [#a78bfa]check[/#a78bfa] [IP] [PORT]      Tek port kontrol")
        console.print(f"   [#a78bfa]back[/#a78bfa]                   Geri don")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

        try:
            cmd = console.input("\n[bold magenta]  vds [/bold magenta][bold white]> [/bold white]").strip()
            parts = cmd.split()
            if not parts:
                continue

            action = parts[0].lower()

            if action == "back":
                break

            elif action == "connect":
                if len(parts) < 3:
                    console.print("[red]  Kullanim: connect [IP] [PORT] (opsiyonel: [USER])[/red]")
                    continue
                host, port = parts[1], parts[2]
                user = parts[3] if len(parts) > 3 else "root"
                tcp_connect(host, int(port), user)

            elif action == "list":
                list_connections()

            elif action == "interact":
                if len(parts) < 2:
                    console.print("[red]  Kullanim: interact [ID][/red]")
                    continue
                interact(int(parts[1]))

            elif action == "kill":
                if len(parts) < 2:
                    console.print("[red]  Kullanim: kill [ID][/red]")
                    continue
                kill_conn(int(parts[1]))

            elif action == "scan":
                if len(parts) < 2:
                    console.print("[red]  Kullanim: scan [IP][/red]")
                    continue
                common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 1433, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 27017]
                try:
                    resolved = socket.gethostbyname(parts[1])
                    port_scan(resolved, common_ports)
                except socket.gaierror:
                    console.print("[red]  Host cozumlenemedi.[/red]")

            elif action == "check":
                if len(parts) < 3:
                    console.print("[red]  Kullanim: check [IP] [PORT][/red]")
                    continue
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    result = sock.connect_ex((parts[1], int(parts[2])))
                    sock.close()
                    if result == 0:
                        console.print(f"[#a78bfa]  {parts[1]}:{parts[2]} ACIK[/#a78bfa]")
                    else:
                        console.print(f"[red]  {parts[1]}:{parts[2]} KAPALI[/red]")
                except Exception as e:
                    console.print(f"[red]  Hata: {e}[/red]")

            else:
                console.print("[red]  Bilinmeyen komut.[/red]")

        except KeyboardInterrupt:
            break
        except ValueError:
            console.print("[red]  Gecersiz deger.[/red]")
        except Exception as e:
            console.print(f"[red]  Hata: {e}[/red]")
