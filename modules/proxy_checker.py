import requests
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()


def run():
    console.print("[dim]  Her satira bir proxy yazin (IP:PORT). Bitirmek icin bos satir girin.[/dim]")

    proxies = []
    while True:
        line = console.input("[bold white]  > [/bold white]").strip()
        if not line:
            break
        proxies.append(line)

    if not proxies:
        console.print("[red]  En az bir proxy girin.[/red]")
        return

    results = []

    with Progress(
        SpinnerColumn(spinner_name="moon"),
        TextColumn("[magenta]{task.description}[/magenta]"),
        BarColumn(bar_width=30, style="purple", complete_style="#a78bfa"),
        TextColumn("[bold white]{task.completed}/{task.total}[/bold white]"),
        console=console,
    ) as progress:
        task = progress.add_task("Kontrol ediliyor...", total=len(proxies))

        for proxy in proxies:
            try:
                proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
                r = requests.get("http://httpbin.org/ip", proxies=proxy_dict, timeout=5)
                if r.status_code == 200:
                    ext_ip = r.json().get("origin", "?")
                    results.append((proxy, "Calisiyor", ext_ip, f"{r.elapsed.total_seconds():.2f}s"))
                else:
                    results.append((proxy, "Basarisiz", "-", "-"))
            except Exception:
                results.append((proxy, "Basarisiz", "-", "-"))
            progress.advance(task)

    table = Table(title="🌕 Proxy Sonuclari", border_style="purple", show_header=True, header_style="bold magenta")
    table.add_column("Proxy", style="white", min_width=20)
    table.add_column("Durum", style="bold", justify="center")
    table.add_column("Dis IP", style="#a78bfa")
    table.add_column("Sure", style="dim white", justify="center")

    for proxy, status, ip, t in results:
        style = "#a78bfa" if "Calisiyor" in status else "red"
        table.add_row(proxy, f"[{style}]{status}[/{style}]", ip, t)

    console.print()
    console.print(table)

    working = sum(1 for _, s, _, _ in results if "Calisiyor" in s)
    console.print(f"\n[#a78bfa]  {working}/{len(results)} proxy calisiyor.[/#a78bfa]")
