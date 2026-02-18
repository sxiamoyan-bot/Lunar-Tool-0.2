import socket
import threading
import time
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False

ssh_connections = {}


def ssh_connect(host, port, username, password=None, key_file=None):
    if not HAS_PARAMIKO:
        console.print("[red]  paramiko yuklu degil. pip install paramiko[/red]")
        return None

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        with console.status(f"[magenta]  {username}@{host}:{port} baglaniliyor...[/magenta]", spinner="moon"):
            if key_file and os.path.exists(key_file):
                client.connect(host, port=int(port), username=username, key_filename=key_file, timeout=10)
            else:
                client.connect(host, port=int(port), username=username, password=password, timeout=10)

        cid = len(ssh_connections) + 1
        ssh_connections[cid] = {
            "client": client,
            "host": host,
            "port": port,
            "user": username,
            "connected_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "alive": True,
            "cmds": 0
        }

        stdin, stdout, stderr = client.exec_command("whoami")
        remote_user = stdout.read().decode().strip()
        ssh_connections[cid]["remote_user"] = remote_user

        console.print(f"\n[#a78bfa]  🌕 SSH #{cid} basarili | {username}@{host}:{port} | {remote_user}[/#a78bfa]")
        return cid

    except Exception as e:
        console.print(f"[red]  SSH hatasi: {e}[/red]")
        return None


def list_ssh():
    if not ssh_connections:
        console.print("[dim]  Aktif SSH baglanti yok.[/dim]")
        return

    table = Table(title="🌕 SSH Baglantilari", border_style="purple", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="bold #a78bfa", justify="center", width=4)
    table.add_column("Host", style="white", min_width=16)
    table.add_column("Port", style="dim", justify="center", width=6)
    table.add_column("Kullanici", style="#a78bfa", width=12)
    table.add_column("Baglanti", style="dim", width=19)
    table.add_column("Komut", style="dim", justify="center", width=5)
    table.add_column("Durum", style="bold", justify="center", width=7)

    for cid, info in ssh_connections.items():
        alive = "[#a78bfa]AKTIF[/#a78bfa]" if info["alive"] else "[red]KAPALI[/red]"
        table.add_row(
            str(cid), info["host"], str(info["port"]),
            info["user"], info["connected_at"],
            str(info["cmds"]), alive
        )

    console.print()
    console.print(table)


def ssh_interact(cid):
    if cid not in ssh_connections:
        console.print("[red]  Baglanti bulunamadi.[/red]")
        return

    info = ssh_connections[cid]
    if not info["alive"]:
        console.print("[red]  Baglanti aktif degil.[/red]")
        return

    client = info["client"]

    console.print(Panel(
        f"[bold white]ID:[/bold white] #{cid}\n"
        f"[bold white]Host:[/bold white] {info['host']}:{info['port']}\n"
        f"[bold white]Kullanici:[/bold white] {info.get('remote_user', info['user'])}",
        title="🌕 SSH Terminal",
        border_style="purple",
        padding=(0, 2)
    ))
    console.print("[dim]  'back' ile cikin. 'get [dosya]' ile indir. 'put [dosya]' ile yukle.[/dim]")

    while True:
        try:
            cmd = console.input(f"[bold magenta]  {info['user']}@{info['host']} [/bold magenta][bold white]$ [/bold white]").strip()

            if not cmd:
                continue
            if cmd.lower() == "back":
                break

            if cmd.lower().startswith("get "):
                remote_path = cmd[4:].strip()
                local_path = os.path.basename(remote_path)
                try:
                    sftp = client.open_sftp()
                    sftp.get(remote_path, local_path)
                    sftp.close()
                    console.print(f"[#a78bfa]  Indirildi: {local_path}[/#a78bfa]")
                except Exception as e:
                    console.print(f"[red]  Indirme hatasi: {e}[/red]")
                info["cmds"] += 1
                continue

            if cmd.lower().startswith("put "):
                local_path = cmd[4:].strip()
                remote_path = f"/tmp/{os.path.basename(local_path)}"
                try:
                    sftp = client.open_sftp()
                    sftp.put(local_path, remote_path)
                    sftp.close()
                    console.print(f"[#a78bfa]  Yuklendi: {remote_path}[/#a78bfa]")
                except Exception as e:
                    console.print(f"[red]  Yukleme hatasi: {e}[/red]")
                info["cmds"] += 1
                continue

            stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
            output = stdout.read().decode("utf-8", errors="replace")
            errors = stderr.read().decode("utf-8", errors="replace")
            info["cmds"] += 1

            if output:
                if len(output) > 2000:
                    output = output[:2000] + "\n... (kesildi)"
                console.print(Panel(output, border_style="#4a2c8a", padding=(0, 1)))
            if errors:
                console.print(Panel(errors, border_style="red", padding=(0, 1)))
            if not output and not errors:
                console.print("[dim]  Cikti yok.[/dim]")

        except Exception as e:
            console.print(f"[red]  Hata: {e}[/red]")
            info["alive"] = False
            break


def ssh_kill(cid):
    if cid not in ssh_connections:
        console.print("[red]  Baglanti bulunamadi.[/red]")
        return
    try:
        ssh_connections[cid]["client"].close()
    except Exception:
        pass
    ssh_connections[cid]["alive"] = False
    console.print(f"[#a78bfa]  SSH #{cid} kapatildi.[/#a78bfa]")


def ssh_broadcast(cmd):
    results = []
    for cid, info in ssh_connections.items():
        if not info["alive"]:
            continue
        try:
            stdin, stdout, stderr = info["client"].exec_command(cmd, timeout=5)
            out = stdout.read().decode("utf-8", errors="replace")[:200]
            results.append((cid, info["host"], out.strip()))
            info["cmds"] += 1
        except Exception:
            info["alive"] = False
            results.append((cid, info["host"], "[HATA]"))

    if results:
        table = Table(title="🌕 SSH Broadcast", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("ID", justify="center", width=4, style="bold #a78bfa")
        table.add_column("Host", style="white", width=16)
        table.add_column("Cikti", style="#a78bfa")
        for cid, host, out in results:
            table.add_row(str(cid), host, out[:60])
        console.print()
        console.print(table)
    else:
        console.print("[dim]  Aktif SSH baglanti yok.[/dim]")


def run():
    while True:
        console.print()
        console.print(f"  [bold purple]🌙 SSH MANAGER[/bold purple]")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

        active = sum(1 for c in ssh_connections.values() if c["alive"])
        console.print(f"   Aktif: {active}  |  Paramiko: {'[#a78bfa]YUKLU[/#a78bfa]' if HAS_PARAMIKO else '[red]YUKLU DEGIL[/red]'}")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
        console.print(f"   [#a78bfa]connect[/#a78bfa] [IP] [PORT] [USER] [PASS]")
        console.print(f"   [#a78bfa]connectkey[/#a78bfa] [IP] [PORT] [USER] [KEY]")
        console.print(f"   [#a78bfa]list[/#a78bfa]                   Baglanti listesi")
        console.print(f"   [#a78bfa]interact[/#a78bfa] [ID]          Terminal")
        console.print(f"   [#a78bfa]kill[/#a78bfa] [ID]              Kapat")
        console.print(f"   [#a78bfa]broadcast[/#a78bfa] [CMD]        Toplu komut")
        console.print(f"   [#a78bfa]back[/#a78bfa]                   Geri don")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

        try:
            cmd = console.input("\n[bold magenta]  ssh [/bold magenta][bold white]> [/bold white]").strip()
            parts = cmd.split()
            if not parts:
                continue

            action = parts[0].lower()

            if action == "back":
                break

            elif action == "connect":
                if len(parts) < 4:
                    console.print("[red]  Kullanim: connect [IP] [PORT] [USER] [PASS][/red]")
                    continue
                ssh_connect(parts[1], int(parts[2]), parts[3], password=parts[4] if len(parts) > 4 else "")

            elif action == "connectkey":
                if len(parts) < 4:
                    console.print("[red]  Kullanim: connectkey [IP] [PORT] [USER] [KEY_FILE][/red]")
                    continue
                ssh_connect(parts[1], int(parts[2]), parts[3], key_file=parts[4] if len(parts) > 4 else None)

            elif action == "list":
                list_ssh()

            elif action == "interact":
                if len(parts) < 2:
                    console.print("[red]  ID gerekli.[/red]")
                    continue
                ssh_interact(int(parts[1]))

            elif action == "kill":
                if len(parts) < 2:
                    console.print("[red]  ID gerekli.[/red]")
                    continue
                ssh_kill(int(parts[1]))

            elif action == "broadcast":
                if len(parts) < 2:
                    console.print("[red]  Komut gerekli.[/red]")
                    continue
                ssh_broadcast(" ".join(parts[1:]))

            else:
                console.print("[red]  Bilinmeyen komut.[/red]")

        except KeyboardInterrupt:
            break
        except ValueError:
            console.print("[red]  Gecersiz deger.[/red]")
        except Exception as e:
            console.print(f"[red]  Hata: {e}[/red]")
