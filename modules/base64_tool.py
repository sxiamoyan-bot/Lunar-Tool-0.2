import base64
from rich.console import Console
from rich.panel import Panel

console = Console()


def run():
    mode = console.input("[bold white]  Islem (1=Encode, 2=Decode): [/bold white]").strip()

    if mode == "1":
        text = console.input("[bold white]  Encode edilecek metin: [/bold white]").strip()
        if not text:
            console.print("[red]  Metin bos olamaz.[/red]")
            return
        encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        console.print(Panel(encoded, title="🌕 Base64 Encoded", border_style="purple", padding=(1, 2)))

    elif mode == "2":
        text = console.input("[bold white]  Decode edilecek Base64: [/bold white]").strip()
        if not text:
            console.print("[red]  Metin bos olamaz.[/red]")
            return
        try:
            decoded = base64.b64decode(text).decode("utf-8")
            console.print(Panel(decoded, title="🌕 Base64 Decoded", border_style="purple", padding=(1, 2)))
        except Exception:
            console.print("[red]  Gecersiz Base64 verisi.[/red]")

    else:
        console.print("[red]  Gecersiz secim.[/red]")
