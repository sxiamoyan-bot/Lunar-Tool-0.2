import requests
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()


def run():
    url = console.input("[bold white]  Webhook URL: [/bold white]").strip()
    if not url or "discord" not in url.lower():
        console.print("[red]  Gecersiz Discord webhook URL.[/red]")
        return

    message = console.input("[bold white]  Mesaj: [/bold white]").strip()
    if not message:
        console.print("[red]  Mesaj bos olamaz.[/red]")
        return

    count = console.input("[bold white]  Mesaj sayisi (varsayilan 5): [/bold white]").strip()
    count = int(count) if count.isdigit() and 0 < int(count) <= 100 else 5

    delay = console.input("[bold white]  Aralik saniye (varsayilan 0.5): [/bold white]").strip()
    try:
        delay = float(delay) if delay else 0.5
    except ValueError:
        delay = 0.5

    sent = 0
    failed = 0

    with Progress(
        SpinnerColumn(spinner_name="moon"),
        TextColumn("[magenta]{task.description}[/magenta]"),
        BarColumn(bar_width=30, style="purple", complete_style="#a78bfa"),
        TextColumn("[bold white]{task.completed}/{task.total}[/bold white]"),
        console=console,
    ) as progress:
        task = progress.add_task("Gonderiliyor...", total=count)

        for i in range(count):
            try:
                payload = {"content": message}
                r = requests.post(url, json=payload, timeout=10)
                if r.status_code == 204:
                    sent += 1
                elif r.status_code == 429:
                    retry_after = r.json().get("retry_after", 1)
                    progress.update(task, description=f"Rate limit! {retry_after}s bekleniyor...")
                    time.sleep(retry_after)
                    r = requests.post(url, json=payload, timeout=10)
                    if r.status_code == 204:
                        sent += 1
                    else:
                        failed += 1
                else:
                    failed += 1
            except Exception:
                failed += 1

            progress.advance(task)
            if i < count - 1:
                time.sleep(delay)

    console.print(f"\n[#a78bfa]  Gonderildi: {sent}[/#a78bfa] | [red]Basarisiz: {failed}[/red]")
