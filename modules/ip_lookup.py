import requests
from rich.console import Console
from rich.table import Table

console = Console()


def run():
    ip = console.input("[bold white]  IP veya Domain girin: [/bold white]").strip()
    if not ip:
        console.print("[red]  IP/Domain bos olamaz.[/red]")
        return

    try:
        with console.status("[magenta]  Sorgulanıyor...[/magenta]", spinner="moon"):
            r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query", timeout=10)
            data = r.json()

        if data.get("status") == "fail":
            console.print(f"[red]  Hata: {data.get('message', 'Bilinmeyen hata')}[/red]")
            return

        table = Table(title=f"🌕 {data.get('query', ip)}", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("Alan", style="bold white", min_width=15)
        table.add_column("Deger", style="#a78bfa")

        fields = [
            ("IP", data.get("query", "N/A")),
            ("Ulke", f"{data.get('country', 'N/A')} ({data.get('countryCode', '')})"),
            ("Bolge", data.get("regionName", "N/A")),
            ("Sehir", data.get("city", "N/A")),
            ("Posta Kodu", data.get("zip", "N/A")),
            ("Enlem", str(data.get("lat", "N/A"))),
            ("Boylam", str(data.get("lon", "N/A"))),
            ("Saat Dilimi", data.get("timezone", "N/A")),
            ("ISP", data.get("isp", "N/A")),
            ("Organizasyon", data.get("org", "N/A")),
            ("AS", data.get("as", "N/A")),
        ]

        for name, value in fields:
            table.add_row(name, str(value))

        console.print()
        console.print(table)

    except requests.exceptions.Timeout:
        console.print("[red]  Baglanti zaman asimina ugradi.[/red]")
    except requests.exceptions.ConnectionError:
        console.print("[red]  Baglanti hatasi.[/red]")
    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")
