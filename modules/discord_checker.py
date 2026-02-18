import requests
from rich.console import Console
from rich.table import Table

console = Console()


def run():
    token = console.input("[bold white]  Discord Token: [/bold white]").strip()
    if not token:
        console.print("[red]  Token bos olamaz.[/red]")
        return

    try:
        with console.status("[magenta]  Token dogrulaniyor...[/magenta]", spinner="moon"):
            headers = {"Authorization": token, "Content-Type": "application/json"}
            r = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=10)

        if r.status_code == 200:
            data = r.json()
            table = Table(title="🌕 Gecerli Token", border_style="purple", show_header=True, header_style="bold magenta")
            table.add_column("Alan", style="bold white", min_width=20)
            table.add_column("Deger", style="#a78bfa")

            table.add_row("Kullanici Adi", f"{data.get('username', 'N/A')}#{data.get('discriminator', '0')}")
            table.add_row("Display Name", data.get("global_name", "N/A") or "N/A")
            table.add_row("Kullanici ID", data.get("id", "N/A"))
            table.add_row("E-posta", data.get("email", "N/A") or "N/A")
            table.add_row("Telefon", data.get("phone", "N/A") or "N/A")
            table.add_row("MFA", "Acik" if data.get("mfa_enabled") else "Kapali")
            table.add_row("Dogrulanmis", "Evet" if data.get("verified") else "Hayir")
            table.add_row("Nitro", "Var" if data.get("premium_type", 0) > 0 else "Yok")

            flags = data.get("public_flags", 0)
            flag_list = []
            flag_map = {
                1: "Staff", 2: "Partner", 4: "HypeSquad Events",
                64: "Bravery", 128: "Brilliance", 256: "Balance",
                131072: "Verified Developer", 4194304: "Active Developer"
            }
            for bit, name in flag_map.items():
                if flags & bit:
                    flag_list.append(name)
            table.add_row("Rozetler", ", ".join(flag_list) if flag_list else "Yok")

            avatar = data.get("avatar")
            if avatar:
                ext = "gif" if avatar.startswith("a_") else "png"
                avatar_url = f"https://cdn.discordapp.com/avatars/{data['id']}/{avatar}.{ext}"
                table.add_row("Avatar", avatar_url)

            console.print()
            console.print(table)

        elif r.status_code == 401:
            console.print("\n[red]  Gecersiz Token.[/red]")
        elif r.status_code == 403:
            console.print("\n[yellow]  Token gecerli ama erisim engellendi (kilitli hesap).[/yellow]")
        elif r.status_code == 429:
            console.print("\n[yellow]  Rate limited. Biraz bekleyin.[/yellow]")
        else:
            console.print(f"\n[red]  Beklenmeyen yanit: {r.status_code}[/red]")

    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")
