import subprocess
import platform
from rich.console import Console
from rich.table import Table

console = Console()


def run():
    if platform.system().lower() != "windows":
        console.print("[red]  Bu ozellik sadece Windows'ta calisir.[/red]")
        return

    try:
        with console.status("[magenta]  WiFi profilleri taraniyor...[/magenta]", spinner="moon"):
            result = subprocess.run(
                ["netsh", "wlan", "show", "profiles"],
                capture_output=True, text=True, timeout=15
            )
            profiles = []
            for line in result.stdout.split("\n"):
                if "All User Profile" in line or "Tüm Kullanıcı Profili" in line:
                    profile = line.split(":")[-1].strip()
                    if profile:
                        profiles.append(profile)

        if not profiles:
            console.print("[dim]  Kayitli WiFi profili bulunamadi.[/dim]")
            return

        table = Table(title="🌕 Kayitli WiFi Sifreleri", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("#", style="bold white", justify="center", width=4)
        table.add_column("Ag Adi (SSID)", style="bold white", min_width=25)
        table.add_column("Sifre", style="#a78bfa", min_width=20)

        for idx, profile in enumerate(profiles, 1):
            try:
                key_result = subprocess.run(
                    ["netsh", "wlan", "show", "profile", profile, "key=clear"],
                    capture_output=True, text=True, timeout=10
                )
                password = ""
                for line in key_result.stdout.split("\n"):
                    if "Key Content" in line or "Anahtar İçeriği" in line:
                        password = line.split(":")[-1].strip()
                        break
                table.add_row(str(idx), profile, password if password else "[dim]Sifre yok[/dim]")
            except Exception:
                table.add_row(str(idx), profile, "[dim]Okunamadi[/dim]")

        console.print()
        console.print(table)
        console.print(f"\n[#a78bfa]  {len(profiles)} WiFi profili bulundu.[/#a78bfa]")

    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")
