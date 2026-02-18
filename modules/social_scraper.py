import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

PLATFORMS = {
    "Instagram": "https://www.instagram.com/{}/",
    "Twitter": "https://twitter.com/{}/",
    "GitHub": "https://github.com/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "Reddit": "https://www.reddit.com/user/{}/",
    "YouTube": "https://www.youtube.com/@{}",
    "Pinterest": "https://www.pinterest.com/{}/",
    "Twitch": "https://www.twitch.tv/{}",
    "LinkedIn": "https://www.linkedin.com/in/{}/",
    "Spotify": "https://open.spotify.com/user/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "Medium": "https://medium.com/@{}",
    "DeviantArt": "https://www.deviantart.com/{}",
    "Flickr": "https://www.flickr.com/people/{}/",
    "Steam": "https://steamcommunity.com/id/{}",
    "Roblox": "https://www.roblox.com/user.aspx?username={}",
    "Telegram": "https://t.me/{}",
    "VK": "https://vk.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "Patreon": "https://www.patreon.com/{}",
}


def run():
    username = console.input("[bold white]  Kullanici adi: [/bold white]").strip()
    if not username:
        console.print("[red]  Kullanici adi gerekli.[/red]")
        return

    found = []
    not_found = []

    with console.status(f"[magenta]  {len(PLATFORMS)} platform taraniyor...[/magenta]", spinner="moon"):
        for platform_name, url_template in PLATFORMS.items():
            url = url_template.format(username)
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                r = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
                if r.status_code == 200:
                    found.append((platform_name, url))
                else:
                    not_found.append(platform_name)
            except Exception:
                not_found.append(platform_name)

    if found:
        table = Table(title=f"🌕 {username} - Bulunan Profiller", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("#", style="bold white", justify="center", width=4)
        table.add_column("Platform", style="#a78bfa", min_width=15)
        table.add_column("URL", style="white")

        for idx, (plat, url) in enumerate(found, 1):
            table.add_row(str(idx), plat, url)

        console.print()
        console.print(table)
        console.print(f"\n[#a78bfa]  {len(found)}/{len(PLATFORMS)} platformda bulundu.[/#a78bfa]")
    else:
        console.print(f"[dim]  '{username}' hicbir platformda bulunamadi.[/dim]")
