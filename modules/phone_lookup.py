import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from rich.console import Console
from rich.table import Table

console = Console()


def run():
    number = console.input("[bold white]  Telefon numarasi (+90...): [/bold white]").strip()
    if not number:
        console.print("[red]  Numara bos olamaz.[/red]")
        return

    try:
        parsed = phonenumbers.parse(number)
        if not phonenumbers.is_valid_number(parsed):
            console.print("[red]  Gecersiz telefon numarasi.[/red]")
            return

        location = geocoder.description_for_number(parsed, "tr") or geocoder.description_for_number(parsed, "en") or "N/A"
        carrier_name = carrier.name_for_number(parsed, "tr") or carrier.name_for_number(parsed, "en") or "N/A"
        tz = timezone.time_zones_for_number(parsed)
        formatted_intl = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        formatted_national = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)

        table = Table(title=f"🌕 {formatted_intl}", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("Alan", style="bold white", min_width=20)
        table.add_column("Deger", style="#a78bfa")

        table.add_row("Uluslararasi", formatted_intl)
        table.add_row("Ulusal", formatted_national)
        table.add_row("Ulke Kodu", f"+{parsed.country_code}")
        table.add_row("Konum", location)
        table.add_row("Operator", carrier_name)
        table.add_row("Saat Dilimi", ", ".join(tz) if tz else "N/A")
        table.add_row("Gecerli", "Evet" if phonenumbers.is_valid_number(parsed) else "Hayir")
        table.add_row("Olasi", "Evet" if phonenumbers.is_possible_number(parsed) else "Hayir")

        console.print()
        console.print(table)

    except phonenumbers.NumberParseException as e:
        console.print(f"[red]  Parse hatasi: {e}[/red]")
    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")
