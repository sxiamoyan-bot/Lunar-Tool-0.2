import requests
from rich.console import Console
from rich.table import Table

console = Console()


def run():
    ip = console.input("[bold white]  IP adresi: [/bold white]").strip()
    if not ip:
        console.print("[red]  IP bos olamaz.[/red]")
        return

    try:
        with console.status("[magenta]  Konum sorgulanıyor...[/magenta]", spinner="moon"):
            r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,lat,lon,isp,org,query", timeout=10)
            data = r.json()

        if data.get("status") == "fail":
            console.print(f"[red]  Hata: {data.get('message', 'Bilinmeyen')}[/red]")
            return

        lat = data.get("lat", 0)
        lon = data.get("lon", 0)

        table = Table(title=f"🌕 {data.get('query', ip)} Konumu", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("Alan", style="bold white", min_width=15)
        table.add_column("Deger", style="#a78bfa")

        table.add_row("IP", data.get("query", "N/A"))
        table.add_row("Ulke", f"{data.get('country', 'N/A')} ({data.get('countryCode', '')})")
        table.add_row("Bolge", data.get("regionName", "N/A"))
        table.add_row("Sehir", data.get("city", "N/A"))
        table.add_row("Enlem", str(lat))
        table.add_row("Boylam", str(lon))
        table.add_row("ISP", data.get("isp", "N/A"))
        table.add_row("Organizasyon", data.get("org", "N/A"))

        google_maps = f"https://www.google.com/maps/@{lat},{lon},15z"
        table.add_row("Google Maps", google_maps)

        console.print()
        console.print(table)
        console.print(f"\n[magenta]  Harita: {google_maps}[/magenta]")

    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")
