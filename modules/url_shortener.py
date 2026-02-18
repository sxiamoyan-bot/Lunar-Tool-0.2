import requests
from rich.console import Console
from rich.panel import Panel

console = Console()


def run():
    url = console.input("[bold white]  Kisaltilacak URL: [/bold white]").strip()
    if not url:
        console.print("[red]  URL bos olamaz.[/red]")
        return

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        with console.status("[magenta]  URL kisaltiliyor...[/magenta]", spinner="moon"):
            r = requests.get(f"https://tinyurl.com/api-create.php?url={url}", timeout=10)

        if r.status_code == 200 and r.text.startswith("http"):
            console.print(Panel(
                f"[bold white]Orijinal:[/bold white] {url}\n[#a78bfa]Kisa URL:[/#a78bfa] {r.text}",
                title="🌕 URL Kisaltildi",
                border_style="purple",
                padding=(1, 2)
            ))
        else:
            console.print("[red]  URL kisaltilamadi.[/red]")

    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")
