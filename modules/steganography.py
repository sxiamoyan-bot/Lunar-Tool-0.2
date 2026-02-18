import os
from rich.console import Console
from rich.panel import Panel

console = Console()


def encode_message(image_path, message, output_path):
    try:
        from PIL import Image
    except ImportError:
        console.print("[red]  Pillow yuklu degil. pip install Pillow[/red]")
        return False

    try:
        img = Image.open(image_path)
        if img.mode != "RGB":
            img = img.convert("RGB")

        binary_msg = ''.join(format(ord(c), '08b') for c in message)
        binary_msg += '00000000' * 3

        pixels = list(img.getdata())
        width, height = img.size

        if len(binary_msg) > len(pixels) * 3:
            console.print("[red]  Mesaj resme sigmayacak kadar buyuk.[/red]")
            return False

        new_pixels = []
        bit_idx = 0

        for pixel in pixels:
            r, g, b = pixel[0], pixel[1], pixel[2]
            if bit_idx < len(binary_msg):
                r = (r & ~1) | int(binary_msg[bit_idx])
                bit_idx += 1
            if bit_idx < len(binary_msg):
                g = (g & ~1) | int(binary_msg[bit_idx])
                bit_idx += 1
            if bit_idx < len(binary_msg):
                b = (b & ~1) | int(binary_msg[bit_idx])
                bit_idx += 1
            new_pixels.append((r, g, b))

        new_img = Image.new("RGB", (width, height))
        new_img.putdata(new_pixels)
        new_img.save(output_path)
        return True

    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")
        return False


def decode_message(image_path):
    try:
        from PIL import Image
    except ImportError:
        console.print("[red]  Pillow yuklu degil. pip install Pillow[/red]")
        return None

    try:
        img = Image.open(image_path)
        if img.mode != "RGB":
            img = img.convert("RGB")

        pixels = list(img.getdata())
        binary = ""

        for pixel in pixels:
            binary += str(pixel[0] & 1)
            binary += str(pixel[1] & 1)
            binary += str(pixel[2] & 1)

        message = ""
        null_count = 0
        for i in range(0, len(binary), 8):
            byte = binary[i:i + 8]
            if len(byte) < 8:
                break
            char = chr(int(byte, 2))
            if char == '\x00':
                null_count += 1
                if null_count >= 3:
                    break
            else:
                null_count = 0
                message += char

        return message

    except Exception as e:
        console.print(f"[red]  Hata: {e}[/red]")
        return None


def run():
    console.print()
    console.print(f"  [bold purple]🌙 STEGANOGRAPHY[/bold purple]")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
    console.print(f"   [#a78bfa][1][/#a78bfa] Mesaj Gom (Encode)")
    console.print(f"   [#a78bfa][2][/#a78bfa] Mesaj Cikar (Decode)")
    console.print(f"   [#a78bfa][0][/#a78bfa] Geri don")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

    choice = console.input("\n[bold white]  Secim: [/bold white]").strip()

    if choice == "0":
        return

    if choice == "1":
        image_path = console.input("[bold white]  Resim dosyasi: [/bold white]").strip()
        if not os.path.exists(image_path):
            console.print("[red]  Dosya bulunamadi.[/red]")
            return

        message = console.input("[bold white]  Gizlenecek mesaj: [/bold white]").strip()
        if not message:
            console.print("[red]  Mesaj gerekli.[/red]")
            return

        output_path = console.input("[bold white]  Cikti dosyasi (varsayilan stego.png): [/bold white]").strip()
        if not output_path:
            output_path = "stego.png"

        with console.status("[magenta]  Mesaj gomuluyor...[/magenta]", spinner="moon"):
            if encode_message(image_path, message, output_path):
                console.print(f"\n[#a78bfa]  🌕 Mesaj basariyla gomuldu![/#a78bfa]")
                console.print(f"[dim]  Cikti: {os.path.abspath(output_path)}[/dim]")
                console.print(f"[dim]  Mesaj uzunlugu: {len(message)} karakter[/dim]")

    elif choice == "2":
        image_path = console.input("[bold white]  Stego resim dosyasi: [/bold white]").strip()
        if not os.path.exists(image_path):
            console.print("[red]  Dosya bulunamadi.[/red]")
            return

        with console.status("[magenta]  Mesaj cikariliyor...[/magenta]", spinner="moon"):
            message = decode_message(image_path)

        if message:
            console.print(Panel(
                message,
                title="🌕 Gizli Mesaj",
                border_style="purple",
                padding=(1, 2)
            ))
        else:
            console.print("[dim]  Mesaj bulunamadi veya bos.[/dim]")

    else:
        console.print("[red]  Gecersiz secim.[/red]")
