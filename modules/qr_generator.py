import qrcode
import os
from rich.console import Console

console = Console()


def run():
    data = console.input("[bold white]  Metin veya URL: [/bold white]").strip()
    if not data:
        console.print("[red]  Icerik bos olamaz.[/red]")
        return

    filename = console.input("[bold white]  Dosya adi (varsayilan: qrcode.png): [/bold white]").strip()
    if not filename:
        filename = "qrcode.png"
    if not filename.endswith(".png"):
        filename += ".png"

    try:
        with console.status("[magenta]  QR kod olusturuluyor...[/magenta]", spinner="moon"):
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#6c3ce0", back_color="white")
            img.save(filename)

        full_path = os.path.abspath(filename)
        console.print(f"\n[#a78bfa]  QR kod olusturuldu: {full_path}[/#a78bfa]")

        console.print("\n[bold white]  Terminal Onizleme:[/bold white]")
        qr_terminal = qrcode.QRCode(box_size=1, border=1)
        qr_terminal.add_data(data)
        qr_terminal.make(fit=True)
        qr_terminal.print_ascii(invert=True)

    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")
