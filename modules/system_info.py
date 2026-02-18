import platform
import socket
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table

console = Console()


def run():
    uname = platform.uname()

    table = Table(title="🌕 Sistem Bilgileri", border_style="purple", show_header=True, header_style="bold magenta")
    table.add_column("Alan", style="bold white", min_width=20)
    table.add_column("Deger", style="#a78bfa")

    table.add_row("Isletim Sistemi", f"{uname.system} {uname.release}")
    table.add_row("OS Surumu", uname.version)
    table.add_row("Makine", uname.machine)
    table.add_row("Islemci", uname.processor or platform.processor())
    table.add_row("Bilgisayar Adi", uname.node)

    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        table.add_row("Hostname", hostname)
        table.add_row("Yerel IP", local_ip)
    except Exception:
        pass

    table.add_row("Python Surumu", platform.python_version())

    try:
        import psutil
        cpu_count = psutil.cpu_count(logical=True)
        cpu_physical = psutil.cpu_count(logical=False)
        cpu_percent = psutil.cpu_percent(interval=0.5)
        table.add_row("CPU Cekirdek", f"{cpu_physical} fiziksel / {cpu_count} mantiksal")
        table.add_row("CPU Kullanimi", f"%{cpu_percent}")

        mem = psutil.virtual_memory()
        table.add_row("Toplam RAM", f"{mem.total / (1024**3):.1f} GB")
        table.add_row("Kullanilan RAM", f"{mem.used / (1024**3):.1f} GB ({mem.percent}%)")
        table.add_row("Bos RAM", f"{mem.available / (1024**3):.1f} GB")

        disk = psutil.disk_usage("/")
        table.add_row("Toplam Disk", f"{disk.total / (1024**3):.1f} GB")
        table.add_row("Kullanilan Disk", f"{disk.used / (1024**3):.1f} GB ({disk.percent}%)")

        boot = datetime.fromtimestamp(psutil.boot_time())
        table.add_row("Acilis Zamani", boot.strftime("%Y-%m-%d %H:%M:%S"))

    except ImportError:
        table.add_row("CPU Sayisi", str(os.cpu_count()))
        table.add_row("Not", "psutil yuklu degil")
    except Exception:
        pass

    table.add_row("Kullanici", os.getlogin() if hasattr(os, 'getlogin') else os.environ.get("USERNAME", "N/A"))

    console.print()
    console.print(table)
