import codecs
import binascii
import urllib.parse
from rich.console import Console
from rich.table import Table

console = Console()


def run():
    text = console.input("[bold white]  Metin girin: [/bold white]").strip()
    if not text:
        console.print("[red]  Metin bos olamaz.[/red]")
        return

    table = Table(title="🌕 String Donusumleri", border_style="purple", show_header=True, header_style="bold magenta")
    table.add_column("Islem", style="bold white", min_width=20)
    table.add_column("Sonuc", style="#a78bfa")

    table.add_row("Orijinal", text)
    table.add_row("Ters Cevrilmis", text[::-1])
    table.add_row("BUYUK HARF", text.upper())
    table.add_row("kucuk harf", text.lower())
    table.add_row("Baslik Formatli", text.title())
    table.add_row("Ters Buyuk/Kucuk", text.swapcase())
    table.add_row("Karakter Sayisi", str(len(text)))
    table.add_row("Kelime Sayisi", str(len(text.split())))

    hex_val = binascii.hexlify(text.encode("utf-8")).decode("utf-8")
    table.add_row("Hexadecimal", hex_val)

    binary = " ".join(format(ord(c), "08b") for c in text)
    table.add_row("Binary", binary)

    rot13 = codecs.encode(text, "rot_13")
    table.add_row("ROT13", rot13)

    url_encoded = urllib.parse.quote(text)
    table.add_row("URL Encoded", url_encoded)

    morse_map = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
        '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
        '8': '---..', '9': '----.', ' ': '/'
    }
    morse = " ".join(morse_map.get(c.upper(), c) for c in text)
    table.add_row("Morse Kodu", morse)

    console.print()
    console.print(table)
