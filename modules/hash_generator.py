import hashlib
from rich.console import Console
from rich.table import Table

console = Console()


def run():
    text = console.input("[bold white]  Metin girin: [/bold white]").strip()
    if not text:
        console.print("[red]  Metin bos olamaz.[/red]")
        return

    encoded = text.encode("utf-8")

    table = Table(title="🌕 Hash Sonuclari", border_style="purple", show_header=True, header_style="bold magenta")
    table.add_column("Algoritma", style="bold white", min_width=12)
    table.add_column("Hash", style="#a78bfa")

    hashes = [
        ("MD5", hashlib.md5(encoded).hexdigest()),
        ("SHA1", hashlib.sha1(encoded).hexdigest()),
        ("SHA224", hashlib.sha224(encoded).hexdigest()),
        ("SHA256", hashlib.sha256(encoded).hexdigest()),
        ("SHA384", hashlib.sha384(encoded).hexdigest()),
        ("SHA512", hashlib.sha512(encoded).hexdigest()),
    ]

    for name, value in hashes:
        table.add_row(name, value)

    console.print()
    console.print(table)
