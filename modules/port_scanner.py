import socket
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()

COMMON_PORTS = {
    20: "FTP Data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
    445: "SMB", 993: "IMAPS", 995: "POP3S", 3306: "MySQL", 3389: "RDP",
    5432: "PostgreSQL", 5900: "VNC", 6379: "Redis", 8080: "HTTP-Alt",
    8443: "HTTPS-Alt", 27017: "MongoDB"
}


def run():
    target = console.input("[bold white]  Hedef IP/Domain: [/bold white]").strip()
    if not target:
        console.print("[red]  Hedef bos olamaz.[/red]")
        return

    mode = console.input("[bold white]  Tarama modu (1=Yaygin, 2=Aralik): [/bold white]").strip()

    if mode == "2":
        start_p = console.input("[bold white]  Baslangic portu: [/bold white]").strip()
        end_p = console.input("[bold white]  Bitis portu: [/bold white]").strip()
        try:
            ports = list(range(int(start_p), int(end_p) + 1))
        except ValueError:
            console.print("[red]  Gecersiz port araligi.[/red]")
            return
    else:
        ports = list(COMMON_PORTS.keys())

    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        console.print("[red]  Host cozumlenemedi.[/red]")
        return

    open_ports = []

    with Progress(
        SpinnerColumn(spinner_name="moon"),
        TextColumn("[magenta]{task.description}[/magenta]"),
        BarColumn(bar_width=30, style="purple", complete_style="#a78bfa"),
        TextColumn("[bold white]{task.completed}/{task.total}[/bold white]"),
        console=console,
    ) as progress:
        task = progress.add_task(f"{ip} taraniyor...", total=len(ports))

        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    service = COMMON_PORTS.get(port, "Unknown")
                    open_ports.append((port, service))
                sock.close()
            except Exception:
                pass
            progress.advance(task)

    if open_ports:
        table = Table(title=f"🌕 Acik Portlar - {target} ({ip})", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("Port", style="#a78bfa", justify="center")
        table.add_column("Servis", style="white")
        table.add_column("Durum", style="bold #a78bfa", justify="center")

        for port, service in open_ports:
            table.add_row(str(port), service, "ACIK")

        console.print()
        console.print(table)
        console.print(f"\n[#a78bfa]  {len(open_ports)} acik port bulundu.[/#a78bfa]")
    else:
        console.print("[dim]  Acik port bulunamadi.[/dim]")
