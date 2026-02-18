import whois
from rich.console import Console
from rich.table import Table

console = Console()


def run():
    domain = console.input("[bold white]  Domain girin: [/bold white]").strip()
    if not domain:
        console.print("[red]  Domain bos olamaz.[/red]")
        return

    try:
        with console.status("[magenta]  Sorgulanıyor...[/magenta]", spinner="moon"):
            w = whois.whois(domain)

        table = Table(title=f"🌕 WHOIS - {domain}", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("Alan", style="bold white", min_width=20)
        table.add_column("Deger", style="#a78bfa")

        def fmt(val):
            if isinstance(val, list):
                return ", ".join(str(v) for v in val)
            return str(val) if val else "N/A"

        fields = [
            ("Domain", fmt(w.domain_name)),
            ("Registrar", fmt(w.registrar)),
            ("WHOIS Sunucu", fmt(w.whois_server)),
            ("Olusturulma", fmt(w.creation_date)),
            ("Guncelleme", fmt(w.updated_date)),
            ("Bitis", fmt(w.expiration_date)),
            ("Name Servers", fmt(w.name_servers)),
            ("Durum", fmt(w.status)),
            ("E-postalar", fmt(w.emails)),
            ("Ulke", fmt(w.country)),
            ("Sehir", fmt(w.city)),
            ("Organizasyon", fmt(w.org)),
        ]

        for name, value in fields:
            table.add_row(name, value)

        console.print()
        console.print(table)

    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")
