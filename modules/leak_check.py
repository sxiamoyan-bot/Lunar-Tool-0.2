import requests
import hashlib
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def check_haveibeenpwned(email):
    try:
        sha1 = hashlib.sha1(email.lower().encode()).hexdigest().upper()
        prefix = sha1[:5]
        suffix = sha1[5:]

        r = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=10)
        if r.status_code == 200:
            for line in r.text.splitlines():
                h, count = line.split(":")
                if h == suffix:
                    return int(count)
        return 0
    except Exception:
        return -1


def check_leakcheck(email):
    try:
        r = requests.get(
            f"https://leakcheck.io/api/public?check={email}",
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if r.status_code == 200:
            data = r.json()
            return data
        return None
    except Exception:
        return None


def run():
    console.print()
    console.print(f"  [bold purple]🌙 LEAK DATABASE CHECK[/bold purple]")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
    console.print(f"   [#a78bfa][1][/#a78bfa] E-posta leak kontrol")
    console.print(f"   [#a78bfa][2][/#a78bfa] Sifre leak kontrol (hash)")
    console.print(f"   [#a78bfa][0][/#a78bfa] Geri don")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

    choice = console.input("\n[bold white]  Secim: [/bold white]").strip()

    if choice == "0":
        return

    if choice == "1":
        email = console.input("[bold white]  E-posta: [/bold white]").strip()
        if not email:
            console.print("[red]  E-posta gerekli.[/red]")
            return

        with console.status("[magenta]  Leak veritabanlari kontrol ediliyor...[/magenta]", spinner="moon"):
            pwned_count = check_haveibeenpwned(email)
            leak_data = check_leakcheck(email)

        table = Table(title=f"🌕 Leak Sonuclari - {email}", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("Kaynak", style="bold white", min_width=20)
        table.add_column("Sonuc", style="#a78bfa")

        if pwned_count > 0:
            table.add_row("PwnedPasswords", f"[red]{pwned_count} kez leak olmus![/red]")
        elif pwned_count == 0:
            table.add_row("PwnedPasswords", "[#a78bfa]Temiz[/#a78bfa]")
        else:
            table.add_row("PwnedPasswords", "[dim]Kontrol edilemedi[/dim]")

        if leak_data and leak_data.get("found"):
            table.add_row("LeakCheck", f"[red]Leak bulundu![/red]")
            for source in leak_data.get("sources", [])[:5]:
                table.add_row("", f"  {source.get('name', '?')} ({source.get('date', '?')})")
        elif leak_data:
            table.add_row("LeakCheck", "[#a78bfa]Temiz[/#a78bfa]")
        else:
            table.add_row("LeakCheck", "[dim]Kontrol edilemedi[/dim]")

        console.print()
        console.print(table)

    elif choice == "2":
        password = console.input("[bold white]  Sifre: [/bold white]").strip()
        if not password:
            console.print("[red]  Sifre gerekli.[/red]")
            return

        with console.status("[magenta]  Kontrol ediliyor...[/magenta]", spinner="moon"):
            sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
            prefix = sha1[:5]
            suffix = sha1[5:]

            try:
                r = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=10)
                found = False
                if r.status_code == 200:
                    for line in r.text.splitlines():
                        h, count = line.split(":")
                        if h == suffix:
                            console.print(f"\n[bold red]  Bu sifre {count} kez leak olmus![/bold red]")
                            console.print("[red]  Bu sifreyi KULLANMAYIN.[/red]")
                            found = True
                            break

                if not found:
                    console.print(f"\n[#a78bfa]  Bu sifre bilinen leak'lerde bulunamadi.[/#a78bfa]")
            except Exception as e:
                console.print(f"[red]  Hata: {e}[/red]")

    else:
        console.print("[red]  Gecersiz secim.[/red]")
