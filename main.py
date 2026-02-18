import os
import sys
import time
import random
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

console = Console()

MODULES = {
    "01": ("IP Lookup", "modules.ip_lookup"),
    "02": ("Ping Tool", "modules.ping_tool"),
    "03": ("Port Scanner", "modules.port_scanner"),
    "04": ("Mass IP Pinger", "modules.mass_ping"),
    "05": ("DNS Lookup", "modules.dns_lookup"),
    "06": ("Subdomain Finder", "modules.subdomain_finder"),
    "07": ("HTTP Header Check", "modules.http_headers"),
    "08": ("Proxy Checker", "modules.proxy_checker"),
    "09": ("Reverse DNS", "modules.reverse_dns"),
    "10": ("IP Geolocation", "modules.geolocation"),
    "11": ("WHOIS Lookup", "modules.whois_lookup"),
    "12": ("Phone Lookup", "modules.phone_lookup"),
    "13": ("Email Validator", "modules.email_validator"),
    "14": ("MAC Lookup", "modules.mac_lookup"),
    "15": ("Social Media Scraper", "modules.social_scraper"),
    "16": ("Leak Database Check", "modules.leak_check"),
    "17": ("Website Tech Detect", "modules.tech_detector"),
    "18": ("Google Dorking", "modules.google_dorking"),
    "19": ("Exploit Scanner", "modules.exploit_scanner"),
    "20": ("Token Checker", "modules.discord_checker"),
    "21": ("Webhook Spammer", "modules.webhook_spammer"),
    "22": ("Hash Generator", "modules.hash_generator"),
    "23": ("Password Generator", "modules.password_generator"),
    "24": ("Base64 Tool", "modules.base64_tool"),
    "25": ("String Tools", "modules.string_tools"),
    "26": ("QR Code Generator", "modules.qr_generator"),
    "27": ("URL Shortener", "modules.url_shortener"),
    "28": ("WiFi Passwords", "modules.wifi_passwords"),
    "29": ("Fake Info Generator", "modules.fake_info"),
    "30": ("System Info", "modules.system_info"),
    "31": ("Crypto Wallet Gen", "modules.crypto_wallet"),
    "32": ("Steganography", "modules.steganography"),
    "33": ("IP Rotator", "modules.ip_rotator"),
    "34": ("ARP Spoofing", "modules.arp_spoof"),
    "35": ("Packet Sniffer", "modules.packet_sniffer"),
    "36": ("Brute Force", "modules.brute_force"),
}

CATEGORIES = {
    "NETWORK":  ["01", "02", "03", "04", "05", "06", "07", "08", "09"],
    "OSINT":    ["10", "11", "12", "13", "14", "15", "16", "17", "18", "19"],
    "DISCORD":  ["20", "21"],
    "UTILITY":  ["22", "23", "24", "25", "26", "27", "28", "29", "30"],
    "HACKING":  ["31", "32", "33", "34", "35", "36"],
}

MOON_PHASES = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]

BANNER_LINES = [
    "██╗     ██╗   ██╗███╗   ██╗ █████╗ ██████╗ ",
    "██║     ██║   ██║████╗  ██║██╔══██╗██╔══██╗",
    "██║     ██║   ██║██╔██╗ ██║███████║██████╔╝",
    "██║     ██║   ██║██║╚██╗██║██╔══██║██╔══██╗",
    "███████╗╚██████╔╝██║ ╚████║██║  ██║██║  ██║",
    "╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝",
]


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pad():
    try:
        w = os.get_terminal_size().columns
    except Exception:
        w = 80
    return max(0, (w - 58) // 2)


def p(text, style=""):
    s = " " * pad()
    if style:
        console.print(f"[{style}]{s}{text}[/{style}]")
    else:
        console.print(f"{s}{text}")


def gradient_bar(width=50):
    colors = ["#2d1b69", "#4a2c8a", "#6b3fa0", "#8b52b8", "#a66bcc", "#8b52b8", "#6b3fa0", "#4a2c8a", "#2d1b69"]
    seg = max(1, width // len(colors))
    t = Text()
    for c in colors:
        t.append("━" * seg, style=c)
    return t


def animated_intro():
    clear()
    bars = [
        "░░░░░░░░░░░░░░░░░░░░",
        "▓▓░░░░░░░░░░░░░░░░░░",
        "▓▓▓▓░░░░░░░░░░░░░░░░",
        "▓▓▓▓▓▓░░░░░░░░░░░░░░",
        "▓▓▓▓▓▓▓▓░░░░░░░░░░░░",
        "▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░",
        "▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
    ]
    for i, bar in enumerate(bars):
        moon = MOON_PHASES[i % len(MOON_PHASES)]
        clear()
        console.print()
        p(f"{moon}  L U N A R  {moon}", "bold purple")
        console.print()
        p(f"[{bar}]", "magenta")
        p("Loading...", "dim")
        time.sleep(0.1)
    time.sleep(0.3)
    clear()


def print_banner():
    moon = random.choice(MOON_PHASES)
    s = " " * pad()
    console.print()
    for line in BANNER_LINES:
        console.print(f"[bold purple]{s}{line}[/bold purple]")
    console.print()
    console.print(f"{s}", end="")
    console.print(gradient_bar(45))
    p(f"{moon}  T O O L  F R A M E W O R K  {moon}", "bold magenta")
    p(f"v3.0  ·  {len(MODULES)} Modules  ·  Lunar Team", "dim italic")
    console.print(f"{s}", end="")
    console.print(gradient_bar(45))
    console.print()


def print_menu():
    cat_colors = {
        "NETWORK": "#c084fc",
        "OSINT":   "#a78bfa",
        "DISCORD": "#8b5cf6",
        "UTILITY": "#7c3aed",
        "HACKING": "#ef4444",
    }

    s = " " * pad()

    for category, keys in CATEGORIES.items():
        nc = cat_colors.get(category, "#a78bfa")

        console.print(f"{s}[bold #a66bcc]🌙 {category}[/bold #a66bcc] [dim #4a2c8a]{'─' * (46 - len(category))}[/dim #4a2c8a]")

        rows = []
        for key in keys:
            name, _ = MODULES[key]
            rows.append((key, name))

        for i in range(0, len(rows), 2):
            k1, n1 = rows[i]
            left = f"[{nc}][{k1}][/{nc}] {n1}"
            if i + 1 < len(rows):
                k2, n2 = rows[i + 1]
                plain_left = f"[{k1}] {n1}"
                padding = 24 - len(plain_left)
                right = f"[{nc}][{k2}][/{nc}] {n2}"
                console.print(f"{s}  {left}{' ' * max(padding, 2)}{right}")
            else:
                console.print(f"{s}  {left}")

        console.print()

    console.print(f"{s}[bold red]🌙 C2 PANEL[/bold red] [dim #4a2c8a]{'─' * 39}[/dim #4a2c8a]")
    console.print(f"{s}  [bold red][ > ][/bold red] C2 Panele Gec")
    console.print()

    console.print(f"{s}[dim #4a2c8a]{'─' * 52}[/dim #4a2c8a]")
    console.print(f"{s}  [dim magenta][[/dim magenta][white]00[/white][dim magenta]][/dim magenta] Ekrani Temizle      [dim magenta][[/dim magenta][white]99[/white][dim magenta]][/dim magenta] Cikis")
    console.print(f"{s}[dim #4a2c8a]{'─' * 52}[/dim #4a2c8a]")
    console.print()


def run_module(choice):
    if choice not in MODULES:
        console.print("[red]  Gecersiz secim.[/red]")
        return

    name, module_path = MODULES[choice]
    s = " " * pad()
    console.print()
    console.print(f"{s}", end="")
    console.print(gradient_bar(36))
    p(f"🌕 {name}", "bold white on #4a2c8a")
    console.print(f"{s}", end="")
    console.print(gradient_bar(36))

    try:
        module = __import__(module_path, fromlist=["run"])
        module.run()
    except ImportError as e:
        console.print(f"[red]  Modul yuklenemedi: {e}[/red]")
        console.print("[dim magenta]  pip install -r requirements.txt[/dim magenta]")
    except KeyboardInterrupt:
        console.print("\n[dim]  Iptal edildi.[/dim]")
    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")

    console.print(f"{s}", end="")
    console.print(gradient_bar(36))


def c2_panel():
    while True:
        clear()
        s = " " * pad()
        console.print()
        for line in BANNER_LINES:
            console.print(f"[bold red]{s}{line}[/bold red]")
        console.print()
        console.print(f"{s}", end="")
        console.print(gradient_bar(45))
        p("🌕  C 2   C O N T R O L   P A N E L  🌕", "bold red")
        console.print(f"{s}", end="")
        console.print(gradient_bar(45))
        console.print()

        console.print(f"{s}[bold red]🌙 EXPLOIT[/bold red] [dim #4a2c8a]{'─' * 41}[/dim #4a2c8a]")
        console.print(f"{s}  [bold red][1][/bold red] C2 Shell              [bold red][2][/bold red] VDS Manager")
        console.print(f"{s}  [bold red][3][/bold red] DDoS Panel            [bold red][4][/bold red] SSH Manager")
        console.print(f"{s}  [bold red][5][/bold red] Keylogger Gen         [bold red][6][/bold red] Persistence Gen")
        console.print(f"{s}  [bold red][7][/bold red] Botnet C2")
        console.print()
        console.print(f"{s}[dim #4a2c8a]{'─' * 52}[/dim #4a2c8a]")
        console.print(f"{s}  [dim magenta][[/dim magenta][white]0[/white][dim magenta]][/dim magenta] Ana menuye don")
        console.print(f"{s}[dim #4a2c8a]{'─' * 52}[/dim #4a2c8a]")
        console.print()

        try:
            choice = console.input("[bold red]  🌙 c2 [/bold red][bold white]> [/bold white]").strip()

            if choice == "0" or choice.lower() == "back":
                clear()
                break

            c2_mods = {
                "1": ("C2 Shell", "modules.c2_shell"),
                "2": ("VDS Manager", "modules.vds_manager"),
                "3": ("DDoS Panel", "modules.ddos_tool"),
                "4": ("SSH Manager", "modules.ssh_manager"),
                "5": ("Keylogger Gen", "modules.keylogger"),
                "6": ("Persistence Gen", "modules.persistence"),
                "7": ("Botnet C2", "modules.botnet"),
            }

            if choice in c2_mods:
                name, mod_path = c2_mods[choice]
                console.print()
                console.print(f"{s}", end="")
                console.print(gradient_bar(36))
                p(f"🌕 {name}", "bold white on #6b1010")
                console.print(f"{s}", end="")
                console.print(gradient_bar(36))

                try:
                    module = __import__(mod_path, fromlist=["run"])
                    module.run()
                except ImportError as e:
                    console.print(f"[red]  Modul yuklenemedi: {e}[/red]")
                except KeyboardInterrupt:
                    console.print("\n[dim]  Iptal edildi.[/dim]")
                except Exception as e:
                    console.print(f"[red]  Hata: {e}[/red]")

                console.print(f"{s}", end="")
                console.print(gradient_bar(36))
                console.print("\n[dim]  Enter'a basin...[/dim]")
                input()
            else:
                console.print("[red]  Gecersiz secim.[/red]")
                time.sleep(0.8)

        except KeyboardInterrupt:
            clear()
            break
        except EOFError:
            break


def main():
    animated_intro()

    while True:
        print_banner()
        print_menu()

        try:
            choice = console.input("[bold #a66bcc]  🌙 lunar [/bold #a66bcc][bold white]> [/bold white]").strip()

            if choice == "99":
                console.print("\n[bold purple]  🌑 Lunar kapaniyor...[/bold purple]")
                time.sleep(0.5)
                clear()
                break
            elif choice == "00":
                clear()
                continue
            elif choice == ">":
                c2_panel()
                continue
            elif choice in MODULES:
                run_module(choice)
                console.print("\n[dim]  Enter'a basin...[/dim]")
                input()
                clear()
            else:
                console.print("[red]  Gecersiz secim.[/red]")
                time.sleep(0.8)
                clear()

        except KeyboardInterrupt:
            console.print("\n\n[bold purple]  🌑 Lunar kapaniyor...[/bold purple]")
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()
