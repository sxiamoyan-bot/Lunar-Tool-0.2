import requests
import re
from rich.console import Console
from rich.table import Table

console = Console()

TECH_SIGNATURES = {
    "WordPress": ["/wp-content/", "/wp-includes/", "wp-json"],
    "Joomla": ["/administrator/", "Joomla!", "/media/jui/"],
    "Drupal": ["Drupal", "/sites/default/", "drupal.js"],
    "Laravel": ["laravel_session", "X-Powered-By: Laravel"],
    "Django": ["csrfmiddlewaretoken", "__admin__", "djdt"],
    "React": ["react", "_reactRoot", "react-dom"],
    "Angular": ["ng-version", "ng-app", "angular.js"],
    "Vue.js": ["vue.js", "__vue__", "v-cloak"],
    "Next.js": ["__NEXT_DATA__", "_next/static", "next/router"],
    "Nuxt.js": ["__NUXT__", "_nuxt/"],
    "jQuery": ["jquery", "jQuery"],
    "Bootstrap": ["bootstrap.min.css", "bootstrap.min.js"],
    "Tailwind": ["tailwindcss", "tw-"],
    "Cloudflare": ["cf-ray", "cloudflare", "__cf_bm"],
    "Nginx": ["nginx"],
    "Apache": ["Apache", "apache"],
    "PHP": ["X-Powered-By: PHP", ".php"],
    "ASP.NET": ["X-AspNet-Version", "ASP.NET", ".aspx"],
    "Node.js": ["X-Powered-By: Express", "node"],
    "Ruby on Rails": ["X-Runtime", "ruby", "rails"],
    "Shopify": ["shopify", "cdn.shopify.com"],
    "Wix": ["wix.com", "X-Wix"],
    "Squarespace": ["squarespace"],
    "Magento": ["magento", "Mage.Cookies"],
    "Google Analytics": ["google-analytics.com", "gtag", "UA-"],
    "Google Tag Manager": ["googletagmanager.com", "GTM-"],
    "reCAPTCHA": ["recaptcha", "g-recaptcha"],
    "Varnish": ["X-Varnish", "Via: varnish"],
    "CDN": ["cdn", "akamai", "fastly", "cloudfront"],
}


def run():
    url = console.input("[bold white]  URL: [/bold white]").strip()
    if not url:
        console.print("[red]  URL gerekli.[/red]")
        return

    if not url.startswith("http"):
        url = "https://" + url

    try:
        with console.status("[magenta]  Teknolojiler taraniyor...[/magenta]", spinner="moon"):
            headers_req = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            r = requests.get(url, headers=headers_req, timeout=10, allow_redirects=True, verify=False)
            body = r.text.lower()
            resp_headers = str(r.headers).lower()
            combined = body + resp_headers

        found = []
        for tech, signatures in TECH_SIGNATURES.items():
            for sig in signatures:
                if sig.lower() in combined:
                    found.append(tech)
                    break

        table = Table(title=f"🌕 Teknoloji Tespiti - {url}", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("#", style="bold white", justify="center", width=4)
        table.add_column("Teknoloji", style="#a78bfa", min_width=20)

        server = r.headers.get("Server", "Bilinmiyor")
        powered = r.headers.get("X-Powered-By", "-")

        console.print()

        if found:
            for idx, tech in enumerate(found, 1):
                table.add_row(str(idx), tech)
            console.print(table)

        info_table = Table(title="🌕 Sunucu Bilgileri", border_style="purple", show_header=True, header_style="bold magenta")
        info_table.add_column("Alan", style="bold white", min_width=15)
        info_table.add_column("Deger", style="#a78bfa")
        info_table.add_row("Server", server)
        info_table.add_row("X-Powered-By", powered)
        info_table.add_row("Status", str(r.status_code))
        info_table.add_row("Content-Type", r.headers.get("Content-Type", "-"))
        info_table.add_row("Cookies", str(len(r.cookies)))
        console.print(info_table)

        console.print(f"\n[#a78bfa]  {len(found)} teknoloji tespit edildi.[/#a78bfa]")

    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")
