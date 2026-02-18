import re
import dns.resolver
from rich.console import Console
from rich.table import Table

console = Console()


def run():
    email = console.input("[bold white]  E-posta adresi: [/bold white]").strip()
    if not email:
        console.print("[red]  E-posta bos olamaz.[/red]")
        return

    table = Table(title=f"🌕 {email}", border_style="purple", show_header=True, header_style="bold magenta")
    table.add_column("Kontrol", style="bold white", min_width=20)
    table.add_column("Sonuc", style="#a78bfa")

    regex_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    regex_valid = bool(re.match(regex_pattern, email))
    table.add_row("Format", "Gecerli" if regex_valid else "Gecersiz")

    if regex_valid:
        domain = email.split("@")[1]
        table.add_row("Domain", domain)

        try:
            with console.status("[magenta]  MX kayitlari kontrol ediliyor...[/magenta]", spinner="moon"):
                mx_records = dns.resolver.resolve(domain, 'MX')
                mx_list = [str(mx.exchange) for mx in mx_records]
                table.add_row("MX Kayitlari", "Mevcut")
                for i, mx in enumerate(mx_list[:3], 1):
                    table.add_row(f"  MX {i}", mx)
        except dns.resolver.NoAnswer:
            table.add_row("MX Kayitlari", "Bulunamadi")
        except dns.resolver.NXDOMAIN:
            table.add_row("MX Kayitlari", "Domain mevcut degil")
        except Exception:
            table.add_row("MX Kayitlari", "Kontrol edilemedi")

        providers = {
            "gmail.com": "Google Gmail", "outlook.com": "Microsoft Outlook",
            "hotmail.com": "Microsoft Hotmail", "yahoo.com": "Yahoo Mail",
            "icloud.com": "Apple iCloud", "protonmail.com": "ProtonMail",
        }
        provider = providers.get(domain.lower(), "Bilinmeyen / Ozel")
        table.add_row("Saglayici", provider)

    console.print()
    console.print(table)
