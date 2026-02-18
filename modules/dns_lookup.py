import dns.resolver
from rich.console import Console
from rich.table import Table

console = Console()


def run():
    domain = console.input("[bold white]  Domain: [/bold white]").strip()
    if not domain:
        console.print("[red]  Domain bos olamaz.[/red]")
        return

    record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "SRV"]

    table = Table(title=f"🌕 DNS - {domain}", border_style="purple", show_header=True, header_style="bold magenta")
    table.add_column("Tip", style="bold magenta", justify="center", width=8)
    table.add_column("Kayit", style="#a78bfa")
    table.add_column("TTL", style="dim white", justify="center", width=8)

    found_any = False

    with console.status("[magenta]  DNS kayitlari sorgulanıyor...[/magenta]", spinner="moon"):
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                for rdata in answers:
                    found_any = True
                    table.add_row(rtype, str(rdata), str(answers.rrset.ttl))
            except dns.resolver.NoAnswer:
                pass
            except dns.resolver.NXDOMAIN:
                console.print(f"[red]  Domain bulunamadi: {domain}[/red]")
                return
            except Exception:
                pass

    console.print()
    if found_any:
        console.print(table)
    else:
        console.print("[dim]  DNS kaydi bulunamadi.[/dim]")
