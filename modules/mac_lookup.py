import requests
from rich.console import Console
from rich.table import Table

console = Console()


def run():
    mac = console.input("[bold white]  MAC adresi (AA:BB:CC:DD:EE:FF): [/bold white]").strip()
    if not mac:
        console.print("[red]  MAC adresi bos olamaz.[/red]")
        return

    mac_clean = mac.replace(":", "").replace("-", "").replace(".", "").upper()
    if len(mac_clean) < 6:
        console.print("[red]  Gecersiz MAC adresi.[/red]")
        return

    prefix = mac_clean[:6]

    try:
        with console.status("[magenta]  Uretici sorgulanıyor...[/magenta]", spinner="moon"):
            r = requests.get(f"https://api.macvendors.com/{mac}", timeout=10)

        table = Table(title=f"🌕 MAC - {mac.upper()}", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("Alan", style="bold white", min_width=15)
        table.add_column("Deger", style="#a78bfa")

        formatted_mac = ":".join(mac_clean[i:i+2] for i in range(0, len(mac_clean), 2))
        table.add_row("MAC Adresi", formatted_mac)
        table.add_row("OUI Prefix", prefix)
        table.add_row("Uretici", r.text.strip() if r.status_code == 200 else "Bilinmiyor")

        console.print()
        console.print(table)

    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")
