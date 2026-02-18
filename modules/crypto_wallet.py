import hashlib
import os
import secrets
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def generate_bitcoin():
    private_key = secrets.token_hex(32)
    pub_hash = hashlib.sha256(bytes.fromhex(private_key)).hexdigest()
    ripemd = hashlib.new("ripemd160", bytes.fromhex(pub_hash)).hexdigest()
    address = "1" + ripemd[:33]
    return private_key, address


def generate_ethereum():
    private_key = secrets.token_hex(32)
    address = "0x" + hashlib.sha256(bytes.fromhex(private_key)).hexdigest()[:40]
    return private_key, address


def run():
    console.print()
    console.print(f"  [bold purple]🌙 CRYPTO WALLET GENERATOR[/bold purple]")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
    console.print(f"   [#a78bfa][1][/#a78bfa] Bitcoin Wallet")
    console.print(f"   [#a78bfa][2][/#a78bfa] Ethereum Wallet")
    console.print(f"   [#a78bfa][3][/#a78bfa] Her ikisi")
    console.print(f"   [#a78bfa][0][/#a78bfa] Geri don")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

    choice = console.input("\n[bold white]  Secim: [/bold white]").strip()

    if choice == "0":
        return

    count = console.input("[bold white]  Kac adet (varsayilan 1): [/bold white]").strip()
    count = int(count) if count.isdigit() and int(count) > 0 else 1
    count = min(count, 20)

    wallets = []

    for _ in range(count):
        if choice in ("1", "3"):
            pk, addr = generate_bitcoin()
            wallets.append(("BTC", pk, addr))
        if choice in ("2", "3"):
            pk, addr = generate_ethereum()
            wallets.append(("ETH", pk, addr))

    table = Table(title="🌕 Olusturulan Cuzdanlar", border_style="purple", show_header=True, header_style="bold magenta")
    table.add_column("#", style="bold white", justify="center", width=4)
    table.add_column("Tip", style="magenta", justify="center", width=5)
    table.add_column("Adres", style="#a78bfa")
    table.add_column("Private Key", style="dim")

    for idx, (typ, pk, addr) in enumerate(wallets, 1):
        table.add_row(str(idx), typ, addr, pk[:20] + "...")

    console.print()
    console.print(table)

    save = console.input("\n[bold white]  Dosyaya kaydet? (e/h): [/bold white]").strip().lower()
    if save == "e":
        fname = f"wallets_{secrets.token_hex(4)}.txt"
        with open(fname, "w") as f:
            for typ, pk, addr in wallets:
                f.write(f"{typ} | {addr} | {pk}\n")
        console.print(f"[#a78bfa]  Kaydedildi: {os.path.abspath(fname)}[/#a78bfa]")

    console.print(f"\n[bold yellow]  Private key'leri guvenli saklayin![/bold yellow]")
