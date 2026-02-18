import requests
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()

COMMON_SUBDOMAINS = [
    "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1", "ns2",
    "dns", "dns1", "dns2", "mx", "mx1", "mx2", "blog", "dev", "staging",
    "api", "app", "admin", "portal", "vpn", "remote", "secure", "shop",
    "store", "test", "demo", "beta", "alpha", "cdn", "media", "img",
    "images", "static", "assets", "files", "docs", "wiki", "forum",
    "support", "help", "status", "monitor", "dashboard", "panel",
    "cloud", "git", "gitlab", "jenkins", "ci", "db", "database",
    "m", "mobile", "wap", "login", "auth", "sso", "oauth", "proxy",
    "relay", "gateway", "internal", "intranet", "extranet", "corp",
    "office", "crm", "erp", "hr", "finance", "billing", "pay",
    "checkout", "order", "track", "analytics", "stats", "log",
    "backup", "bak", "old", "new", "v2", "v3", "sandbox"
]


def run():
    domain = console.input("[bold white]  Domain (orn: example.com): [/bold white]").strip()
    if not domain:
        console.print("[red]  Domain bos olamaz.[/red]")
        return

    found = []

    with Progress(
        SpinnerColumn(spinner_name="moon"),
        TextColumn("[magenta]{task.description}[/magenta]"),
        BarColumn(bar_width=30, style="purple", complete_style="#a78bfa"),
        TextColumn("[bold white]{task.completed}/{task.total}[/bold white]"),
        console=console,
    ) as progress:
        task = progress.add_task("Alt domainler taraniyor...", total=len(COMMON_SUBDOMAINS))

        for sub in COMMON_SUBDOMAINS:
            subdomain = f"{sub}.{domain}"
            try:
                r = requests.get(f"http://{subdomain}", timeout=2, allow_redirects=False)
                found.append((subdomain, r.status_code))
            except Exception:
                pass
            progress.advance(task)

    if found:
        table = Table(title=f"🌕 Alt Domainler - {domain}", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("#", style="bold white", justify="center", width=4)
        table.add_column("Subdomain", style="#a78bfa", min_width=30)
        table.add_column("Durum", style="white", justify="center")

        for idx, (sub, code) in enumerate(found, 1):
            code_style = "#a78bfa" if 200 <= code < 300 else ("yellow" if 300 <= code < 400 else "red")
            table.add_row(str(idx), sub, f"[{code_style}]{code}[/{code_style}]")

        console.print()
        console.print(table)
        console.print(f"\n[#a78bfa]  {len(found)} alt domain bulundu.[/#a78bfa]")
    else:
        console.print("[dim]  Alt domain bulunamadi.[/dim]")
