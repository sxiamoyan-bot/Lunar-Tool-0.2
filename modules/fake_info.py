from faker import Faker
from rich.console import Console
from rich.table import Table

console = Console()


def run():
    locale = console.input("[bold white]  Dil (tr_TR / en_US / de_DE, varsayilan tr_TR): [/bold white]").strip()
    if not locale:
        locale = "tr_TR"

    count = console.input("[bold white]  Kac kimlik (varsayilan 1): [/bold white]").strip()
    count = int(count) if count.isdigit() and int(count) > 0 else 1
    count = min(count, 10)

    try:
        fake = Faker(locale)
    except Exception:
        fake = Faker("tr_TR")

    for i in range(count):
        table = Table(title=f"🌕 Sahte Kimlik #{i+1}", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("Alan", style="bold white", min_width=18)
        table.add_column("Deger", style="#a78bfa")

        table.add_row("Ad Soyad", fake.name())
        table.add_row("E-posta", fake.email())
        table.add_row("Kullanici Adi", fake.user_name())
        table.add_row("Telefon", fake.phone_number())
        table.add_row("Adres", fake.address().replace("\n", ", "))
        table.add_row("Sehir", fake.city())
        table.add_row("Ulke", fake.country())
        table.add_row("Posta Kodu", fake.postcode())
        table.add_row("Sirket", fake.company())
        table.add_row("Meslek", fake.job())
        table.add_row("Dogum Tarihi", str(fake.date_of_birth(minimum_age=18, maximum_age=65)))
        table.add_row("Kredi Karti", fake.credit_card_number())
        table.add_row("IBAN", fake.iban())
        table.add_row("IP Adresi", fake.ipv4())
        table.add_row("User Agent", fake.user_agent())

        console.print()
        console.print(table)
