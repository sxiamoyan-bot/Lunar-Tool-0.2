import subprocess
import platform
import threading
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()


def ping_host(ip, results, index):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        result = subprocess.run(
            ["ping", param, "1", "-w", "1000", ip],
            capture_output=True, text=True, timeout=5
        )
        results[index] = (ip, result.returncode == 0)
    except Exception:
        results[index] = (ip, False)


def run():
    console.print("[dim]  Her satira bir IP girin. Bitirmek icin bos satir girin.[/dim]")

    ips = []
    while True:
        line = console.input("[bold white]  > [/bold white]").strip()
        if not line:
            break
        ips.append(line)

    if not ips:
        console.print("[red]  En az bir IP girin.[/red]")
        return

    results = [None] * len(ips)

    with Progress(
        SpinnerColumn(spinner_name="moon"),
        TextColumn("[magenta]{task.description}[/magenta]"),
        BarColumn(bar_width=30, style="purple", complete_style="#a78bfa"),
        TextColumn("[bold white]{task.completed}/{task.total}[/bold white]"),
        console=console,
    ) as progress:
        task = progress.add_task("Ping atiliyor...", total=len(ips))

        batch_size = 10
        for i in range(0, len(ips), batch_size):
            batch = ips[i:i+batch_size]
            batch_threads = []
            for j, ip in enumerate(batch):
                t = threading.Thread(target=ping_host, args=(ip, results, i+j))
                t.start()
                batch_threads.append(t)

            for t in batch_threads:
                t.join()
                progress.advance(task)

    table = Table(title="🌕 Mass Ping Sonuclari", border_style="purple", show_header=True, header_style="bold magenta")
    table.add_column("#", style="bold white", justify="center", width=4)
    table.add_column("IP Adresi", style="white", min_width=20)
    table.add_column("Durum", style="bold", justify="center")

    alive_count = 0
    for idx, (ip, alive) in enumerate(results, 1):
        if alive:
            alive_count += 1
            table.add_row(str(idx), ip, "[#a78bfa]ACIK[/#a78bfa]")
        else:
            table.add_row(str(idx), ip, "[red]KAPALI[/red]")

    console.print()
    console.print(table)
    console.print(f"\n[#a78bfa]  {alive_count}/{len(results)} host acik.[/#a78bfa]")
