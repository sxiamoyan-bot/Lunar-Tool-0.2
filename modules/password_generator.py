import string
import secrets
from rich.console import Console

console = Console()


def run():
    length = console.input("[bold white]  Sifre uzunlugu (varsayilan 16): [/bold white]").strip()
    length = int(length) if length.isdigit() and int(length) > 0 else 16
    length = min(length, 128)

    count = console.input("[bold white]  Kac sifre (varsayilan 5): [/bold white]").strip()
    count = int(count) if count.isdigit() and int(count) > 0 else 5
    count = min(count, 20)

    include_special = console.input("[bold white]  Ozel karakterler dahil mi? (e/h, varsayilan e): [/bold white]").strip().lower()
    use_special = include_special != "h"

    chars = string.ascii_letters + string.digits
    if use_special:
        chars += string.punctuation

    console.print()
    for i in range(count):
        while True:
            password = ''.join(secrets.choice(chars) for _ in range(length))
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in string.punctuation for c in password) if use_special else True
            if has_upper and has_lower and has_digit and has_special:
                break

        score = 0
        if length >= 8: score += 1
        if length >= 12: score += 1
        if length >= 16: score += 1
        if use_special: score += 1
        if length >= 20: score += 1

        strength_map = {1: ("Zayif", "red"), 2: ("Orta", "yellow"), 3: ("Iyi", "#a78bfa"), 4: ("Guclu", "magenta"), 5: ("Cok Guclu", "bold #a78bfa")}
        strength, color = strength_map.get(score, ("Bilinmiyor", "white"))

        console.print(f"  [bold white]{i+1}.[/bold white] [magenta]{password}[/magenta]  [{color}]{strength}[/{color}]")

    console.print(f"\n[#a78bfa]  {count} sifre olusturuldu. (Uzunluk: {length})[/#a78bfa]")
