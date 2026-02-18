import requests
from rich.console import Console
from rich.table import Table

console = Console()


def run():
    url = console.input("[bold white]  URL (https://...): [/bold white]").strip()
    if not url:
        console.print("[red]  URL bos olamaz.[/red]")
        return

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        with console.status("[magenta]  Basliklar aliniyor...[/magenta]", spinner="moon"):
            r = requests.head(url, timeout=10, allow_redirects=True)

        table = Table(title=f"🌕 {url}", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("Baslik", style="bold white", min_width=25)
        table.add_column("Deger", style="#a78bfa")

        table.add_row("Durum Kodu", f"{r.status_code} {r.reason}")
        table.add_row("Final URL", str(r.url))

        security_headers = [
            "Content-Security-Policy", "Strict-Transport-Security",
            "X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection",
            "Referrer-Policy", "Permissions-Policy"
        ]

        for key, value in r.headers.items():
            table.add_row(key, value)

        console.print()
        console.print(table)

        console.print("\n[bold white]  Guvenlik Analizi:[/bold white]")
        for header in security_headers:
            if header.lower() in [h.lower() for h in r.headers]:
                console.print(f"    [#a78bfa]{header} — MEVCUT[/#a78bfa]")
            else:
                console.print(f"    [red]{header} — EKSIK[/red]")

    except requests.exceptions.ConnectionError:
        console.print("[red]  Baglanti kurulamadi.[/red]")
    except requests.exceptions.Timeout:
        console.print("[red]  Zaman asimi.[/red]")
    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")
