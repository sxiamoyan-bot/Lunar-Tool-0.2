import socket
import struct
import time
import os
from rich.console import Console
from rich.table import Table

console = Console()


def run():
    console.print()
    console.print(f"  [bold purple]🌙 PACKET SNIFFER[/bold purple]")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
    console.print(f"   [#a78bfa][1][/#a78bfa] Raw Socket Sniffer (Admin gerekli)")
    console.print(f"   [#a78bfa][2][/#a78bfa] Scapy Sniffer")
    console.print(f"   [#a78bfa][0][/#a78bfa] Geri don")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

    choice = console.input("\n[bold white]  Secim: [/bold white]").strip()

    if choice == "0":
        return

    if choice == "1":
        count = console.input("[bold white]  Kac paket yakalansin (varsayilan 50): [/bold white]").strip()
        count = int(count) if count.isdigit() else 50

        try:
            if os.name == "nt":
                host = socket.gethostbyname(socket.gethostname())
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
                s.bind((host, 0))
                s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
            else:
                s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))

            table = Table(title="🌕 Yakalanan Paketler", border_style="purple", show_header=True, header_style="bold magenta")
            table.add_column("#", style="bold white", justify="center", width=5)
            table.add_column("Kaynak", style="white", min_width=16)
            table.add_column("Hedef", style="#a78bfa", min_width=16)
            table.add_column("Protokol", style="magenta", justify="center", width=10)
            table.add_column("Boyut", style="dim", justify="center", width=8)

            protocols = {1: "ICMP", 6: "TCP", 17: "UDP"}

            console.print(f"\n[#a78bfa]  Yakalama baslatildi ({count} paket)...[/#a78bfa]")
            console.print("[dim]  Ctrl+C ile durdurun.[/dim]\n")

            for i in range(count):
                try:
                    raw, addr = s.recvfrom(65535)

                    if os.name == "nt":
                        ip_header = raw[:20]
                    else:
                        ip_header = raw[14:34]

                    iph = struct.unpack("!BBHHHBBH4s4s", ip_header)
                    protocol = iph[6]
                    src = socket.inet_ntoa(iph[8])
                    dst = socket.inet_ntoa(iph[9])
                    proto_name = protocols.get(protocol, str(protocol))

                    table.add_row(str(i + 1), src, dst, proto_name, str(len(raw)))
                except Exception:
                    continue

            if os.name == "nt":
                s.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
            s.close()

            console.print(table)
            console.print(f"\n[#a78bfa]  {count} paket yakalandi.[/#a78bfa]")

        except PermissionError:
            console.print("[red]  Yonetici/root yetkisi gerekli![/red]")
        except Exception as e:
            console.print(f"[red]  Hata: {e}[/red]")

    elif choice == "2":
        try:
            from scapy.all import sniff, IP, TCP, UDP, ICMP
        except ImportError:
            console.print("[red]  scapy yuklu degil. pip install scapy[/red]")
            return

        count = console.input("[bold white]  Kac paket (varsayilan 30): [/bold white]").strip()
        count = int(count) if count.isdigit() else 30
        filt = console.input("[bold white]  Filtre (bos=hepsi, orn: tcp, udp, icmp): [/bold white]").strip()

        packets_data = []

        def packet_handler(pkt):
            if IP in pkt:
                proto = "?"
                if TCP in pkt:
                    proto = "TCP"
                elif UDP in pkt:
                    proto = "UDP"
                elif ICMP in pkt:
                    proto = "ICMP"
                packets_data.append((pkt[IP].src, pkt[IP].dst, proto, len(pkt)))

        console.print(f"\n[#a78bfa]  Yakalama baslatildi...[/#a78bfa]")

        try:
            sniff(count=count, filter=filt or None, prn=packet_handler, store=False)
        except PermissionError:
            console.print("[red]  Yonetici/root yetkisi gerekli![/red]")
            return

        if packets_data:
            table = Table(title="🌕 Scapy Paketler", border_style="purple", show_header=True, header_style="bold magenta")
            table.add_column("#", style="bold white", justify="center", width=5)
            table.add_column("Kaynak", style="white", min_width=16)
            table.add_column("Hedef", style="#a78bfa", min_width=16)
            table.add_column("Protokol", style="magenta", justify="center", width=10)
            table.add_column("Boyut", style="dim", justify="center", width=8)

            for idx, (src, dst, proto, size) in enumerate(packets_data, 1):
                table.add_row(str(idx), src, dst, proto, str(size))

            console.print(table)
            console.print(f"\n[#a78bfa]  {len(packets_data)} paket yakalandi.[/#a78bfa]")

    else:
        console.print("[red]  Gecersiz secim.[/red]")
