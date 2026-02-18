import requests
import random
import time
import threading
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()


FREE_PROXY_APIS = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all",
    "https://www.proxy-list.download/api/v1/get?type=http",
]

proxy_list = []
current_proxy_idx = 0
lock = threading.Lock()


def fetch_proxies():
    global proxy_list
    proxies = set()

    for api_url in FREE_PROXY_APIS:
        try:
            r = requests.get(api_url, timeout=10)
            if r.status_code == 200:
                for line in r.text.strip().splitlines():
                    line = line.strip()
                    if ":" in line:
                        proxies.add(line)
        except Exception:
            pass

    proxy_list = list(proxies)
    return len(proxy_list)


def test_proxy(proxy, timeout=5):
    try:
        r = requests.get(
            "http://httpbin.org/ip",
            proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
            timeout=timeout
        )
        if r.status_code == 200:
            return True, r.json().get("origin", "?"), f"{r.elapsed.total_seconds():.1f}s"
    except Exception:
        pass
    return False, "-", "-"


def get_next_proxy():
    global current_proxy_idx
    with lock:
        if not proxy_list:
            return None
        proxy = proxy_list[current_proxy_idx % len(proxy_list)]
        current_proxy_idx += 1
        return proxy


def run():
    global proxy_list, current_proxy_idx

    while True:
        console.print()
        console.print(f"  [bold purple]🌙 IP ROTATOR[/bold purple]")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
        console.print(f"   Yuklu proxy: {len(proxy_list)}  |  Sira: {current_proxy_idx}")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
        console.print(f"   [#a78bfa]fetch[/#a78bfa]                  Proxy listesi indir")
        console.print(f"   [#a78bfa]load[/#a78bfa] [DOSYA]           Dosyadan yukle")
        console.print(f"   [#a78bfa]test[/#a78bfa]                   Tum proxy'leri test et")
        console.print(f"   [#a78bfa]list[/#a78bfa]                   Proxy listesi")
        console.print(f"   [#a78bfa]rotate[/#a78bfa]                 Sonraki proxy'yi goster")
        console.print(f"   [#a78bfa]request[/#a78bfa] [URL]          Rotasyonlu istek gonder")
        console.print(f"   [#a78bfa]back[/#a78bfa]                   Geri don")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

        try:
            cmd = console.input("\n[bold magenta]  proxy [/bold magenta][bold white]> [/bold white]").strip()
            parts = cmd.split(maxsplit=1)
            if not parts:
                continue

            action = parts[0].lower()

            if action == "back":
                break

            elif action == "fetch":
                with console.status("[magenta]  Proxy listeleri indiriliyor...[/magenta]", spinner="moon"):
                    count = fetch_proxies()
                console.print(f"[#a78bfa]  {count} proxy yuklendi.[/#a78bfa]")

            elif action == "load":
                if len(parts) < 2:
                    console.print("[red]  Dosya yolu gerekli.[/red]")
                    continue
                try:
                    with open(parts[1].strip(), "r") as f:
                        loaded = [line.strip() for line in f if ":" in line.strip()]
                    proxy_list.extend(loaded)
                    console.print(f"[#a78bfa]  {len(loaded)} proxy yuklendi. Toplam: {len(proxy_list)}[/#a78bfa]")
                except Exception as e:
                    console.print(f"[red]  Hata: {e}[/red]")

            elif action == "test":
                if not proxy_list:
                    console.print("[red]  Once proxy yukleyin.[/red]")
                    continue

                working = []
                with Progress(
                    SpinnerColumn(spinner_name="moon"),
                    TextColumn("[magenta]{task.description}[/magenta]"),
                    BarColumn(bar_width=30, style="purple", complete_style="#a78bfa"),
                    TextColumn("[bold white]{task.completed}/{task.total}[/bold white]"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Test ediliyor...", total=min(len(proxy_list), 50))

                    for proxy in proxy_list[:50]:
                        ok, ip, speed = test_proxy(proxy)
                        if ok:
                            working.append((proxy, ip, speed))
                        progress.advance(task)

                proxy_list = [p for p, _, _ in working]

                table = Table(title="🌕 Calisan Proxy'ler", border_style="purple", show_header=True, header_style="bold magenta")
                table.add_column("#", style="bold white", justify="center", width=4)
                table.add_column("Proxy", style="white", min_width=20)
                table.add_column("Dis IP", style="#a78bfa")
                table.add_column("Hiz", style="dim", justify="center", width=8)

                for idx, (p, ip, speed) in enumerate(working, 1):
                    table.add_row(str(idx), p, ip, speed)

                console.print()
                console.print(table)
                console.print(f"\n[#a78bfa]  {len(working)} calisan proxy.[/#a78bfa]")

            elif action == "list":
                if not proxy_list:
                    console.print("[dim]  Proxy listesi bos.[/dim]")
                    continue
                for idx, p in enumerate(proxy_list[:20], 1):
                    marker = " <--" if idx - 1 == current_proxy_idx % len(proxy_list) else ""
                    console.print(f"   [#a78bfa]{idx:>3}.[/#a78bfa] {p}{marker}")
                if len(proxy_list) > 20:
                    console.print(f"   [dim]... ve {len(proxy_list) - 20} daha[/dim]")

            elif action == "rotate":
                proxy = get_next_proxy()
                if proxy:
                    console.print(f"[#a78bfa]  Sonraki proxy: {proxy}[/#a78bfa]")
                else:
                    console.print("[red]  Proxy listesi bos.[/red]")

            elif action == "request":
                if len(parts) < 2:
                    console.print("[red]  URL gerekli.[/red]")
                    continue
                url = parts[1].strip()
                if not url.startswith("http"):
                    url = "http://" + url

                proxy = get_next_proxy()
                if not proxy:
                    console.print("[red]  Proxy listesi bos.[/red]")
                    continue

                try:
                    r = requests.get(
                        url,
                        proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
                        timeout=10,
                        headers={"User-Agent": "Mozilla/5.0"}
                    )
                    console.print(f"[#a78bfa]  Proxy: {proxy}[/#a78bfa]")
                    console.print(f"[#a78bfa]  Status: {r.status_code}[/#a78bfa]")
                    console.print(f"[dim]  Boyut: {len(r.content)} bytes[/dim]")
                except Exception as e:
                    console.print(f"[red]  Hata: {e}[/red]")

            else:
                console.print("[red]  Bilinmeyen komut.[/red]")

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]  Hata: {e}[/red]")
