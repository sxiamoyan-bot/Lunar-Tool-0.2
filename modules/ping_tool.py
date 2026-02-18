import subprocess
import platform
from rich.console import Console
from rich.panel import Panel

console = Console()


def run():
    target = console.input("[bold white]  Hedef IP/Domain: [/bold white]").strip()
    if not target:
        console.print("[red]  Hedef bos olamaz.[/red]")
        return

    count = console.input("[bold white]  Paket sayisi (varsayilan 4): [/bold white]").strip()
    count = int(count) if count.isdigit() else 4

    try:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        with console.status(f"[magenta]  {target} adresine ping atiliyor...[/magenta]", spinner="moon"):
            result = subprocess.run(
                ["ping", param, str(count), target],
                capture_output=True, text=True, timeout=60
            )

        output = result.stdout if result.stdout else result.stderr
        console.print(Panel(output, title=f"🌕 Ping - {target}", border_style="purple", padding=(1, 2)))

    except subprocess.TimeoutExpired:
        console.print("[red]  Zaman asimi.[/red]")
    except FileNotFoundError:
        console.print("[red]  Ping komutu bulunamadi.[/red]")
    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")
