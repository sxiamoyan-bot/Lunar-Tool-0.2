import socket
from rich.console import Console
from rich.table import Table

console = Console()


def run():
    ip = console.input("[bold white]  IP Adresi: [/bold white]").strip()
    if not ip:
        console.print("[red]  IP gerekli.[/red]")
        return

    with console.status("[magenta]  Reverse DNS sorgulanıyor...[/magenta]", spinner="moon"):
        results = []

        try:
            hostname, aliases, addrs = socket.gethostbyaddr(ip)
            results.append(("PTR", hostname))
            for alias in aliases:
                results.append(("Alias", alias))
        except socket.herror:
            pass
        except Exception:
            pass

        try:
            fqdn = socket.getfqdn(ip)
            if fqdn != ip:
                results.append(("FQDN", fqdn))
        except Exception:
            pass

    if results:
        table = Table(title=f"🌕 Reverse DNS - {ip}", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("Tip", style="bold white", justify="center", width=8)
        table.add_column("Domain", style="#a78bfa")

        for rtype, domain in results:
            table.add_row(rtype, domain)

        console.print()
        console.print(table)
    else:
        console.print(f"[dim]  {ip} icin reverse DNS kaydi bulunamadi.[/dim]")
