import requests
import urllib.parse
from rich.console import Console
from rich.table import Table

console = Console()

DORK_CATEGORIES = {
    "Hassas Dosyalar": [
        'site:{target} filetype:sql',
        'site:{target} filetype:env',
        'site:{target} filetype:log',
        'site:{target} filetype:conf',
        'site:{target} filetype:bak',
        'site:{target} filetype:old',
        'site:{target} filetype:xml',
        'site:{target} filetype:json',
        'site:{target} filetype:csv',
    ],
    "Login Panelleri": [
        'site:{target} inurl:admin',
        'site:{target} inurl:login',
        'site:{target} inurl:panel',
        'site:{target} inurl:dashboard',
        'site:{target} inurl:wp-admin',
        'site:{target} inurl:administrator',
        'site:{target} intitle:"login"',
    ],
    "Dizin Listeleme": [
        'site:{target} intitle:"index of"',
        'site:{target} intitle:"directory listing"',
        'site:{target} intitle:"parent directory"',
    ],
    "Veritabani": [
        'site:{target} inurl:phpmyadmin',
        'site:{target} filetype:sql "INSERT INTO"',
        'site:{target} filetype:sql "CREATE TABLE"',
        'site:{target} inurl:db',
    ],
    "Konfigürasyon": [
        'site:{target} filetype:ini',
        'site:{target} filetype:cfg',
        'site:{target} filetype:yml',
        'site:{target} filetype:toml',
        'site:{target} inurl:config',
        'site:{target} inurl:setup',
    ],
    "Sifre / Kimlik": [
        'site:{target} filetype:txt "password"',
        'site:{target} filetype:log "password"',
        'site:{target} "username" "password" filetype:txt',
        'site:{target} inurl:credentials',
    ],
    "Subdomain": [
        'site:*.{target}',
        'site:*.*.{target}',
    ],
    "Hata Mesajlari": [
        'site:{target} "SQL syntax" "mysql"',
        'site:{target} "Warning:" "mysql"',
        'site:{target} "Fatal error"',
        'site:{target} "Stack trace"',
        'site:{target} inurl:debug',
    ],
}


def run():
    console.print()
    console.print(f"  [bold purple]🌙 GOOGLE DORKING[/bold purple]")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
    console.print(f"   [#a78bfa][1][/#a78bfa] Hedef site icin tum dorklar")
    console.print(f"   [#a78bfa][2][/#a78bfa] Kategori sec")
    console.print(f"   [#a78bfa][3][/#a78bfa] Ozel dork")
    console.print(f"   [#a78bfa][0][/#a78bfa] Geri don")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

    choice = console.input("\n[bold white]  Secim: [/bold white]").strip()

    if choice == "0":
        return

    if choice == "1":
        target = console.input("[bold white]  Hedef domain: [/bold white]").strip()
        if not target:
            console.print("[red]  Domain gerekli.[/red]")
            return

        table = Table(title=f"🌕 Google Dorklar - {target}", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("Kategori", style="bold white", min_width=18)
        table.add_column("Dork", style="#a78bfa")
        table.add_column("Link", style="dim")

        for cat, dorks in DORK_CATEGORIES.items():
            for i, dork in enumerate(dorks):
                d = dork.format(target=target)
                link = f"https://www.google.com/search?q={urllib.parse.quote(d)}"
                if i == 0:
                    table.add_row(cat, d, link)
                else:
                    table.add_row("", d, link)

        console.print()
        console.print(table)
        console.print(f"\n[dim]  Linkleri tarayicida acarak sonuclari gorebilirsiniz.[/dim]")

    elif choice == "2":
        console.print()
        cats = list(DORK_CATEGORIES.keys())
        for idx, cat in enumerate(cats, 1):
            console.print(f"   [#a78bfa][{idx}][/#a78bfa] {cat}")

        cat_choice = console.input("\n[bold white]  Kategori: [/bold white]").strip()
        if not cat_choice.isdigit() or int(cat_choice) < 1 or int(cat_choice) > len(cats):
            console.print("[red]  Gecersiz secim.[/red]")
            return

        target = console.input("[bold white]  Hedef domain: [/bold white]").strip()
        if not target:
            console.print("[red]  Domain gerekli.[/red]")
            return

        cat = cats[int(cat_choice) - 1]
        dorks = DORK_CATEGORIES[cat]

        table = Table(title=f"🌕 {cat} - {target}", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("#", style="bold white", justify="center", width=4)
        table.add_column("Dork", style="#a78bfa")
        table.add_column("Link", style="dim")

        for idx, dork in enumerate(dorks, 1):
            d = dork.format(target=target)
            link = f"https://www.google.com/search?q={urllib.parse.quote(d)}"
            table.add_row(str(idx), d, link)

        console.print()
        console.print(table)

    elif choice == "3":
        dork = console.input("[bold white]  Dork sorgusu: [/bold white]").strip()
        if dork:
            link = f"https://www.google.com/search?q={urllib.parse.quote(dork)}"
            console.print(f"\n[#a78bfa]  {link}[/#a78bfa]")

    else:
        console.print("[red]  Gecersiz secim.[/red]")
