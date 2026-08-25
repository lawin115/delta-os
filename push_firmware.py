import socket, sys, os, subprocess, threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

FILE_PATH = r"c:\Users\Malta Computer\Desktop\mikrotik\sysupgrade.bin"

if not os.path.exists(FILE_PATH):
    print(f"[-] Error: {FILE_PATH} not found!")
    sys.exit(1)

size = os.path.getsize(FILE_PATH)
print("=" * 60)
print(f"[*] DELTA OS DIRECT FIRMWARE PUSHER ({size/1024/1024:.2f} MB)")
print("=" * 60)

# Find available port
PORT = 8088
for p in [8088, 8888, 9000, 9090, 7777, 0]:
    try:
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.bind(("0.0.0.0", p))
        PORT = test_sock.getsockname()[1]
        test_sock.close()
        break
    except Exception:
        continue

class FirmwareHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        return FILE_PATH
    def log_message(self, format, *args):
        print(f"[+] Router HTTP Request: {self.client_address[0]} - {args[0]}")

# Start local HTTP server in background
httpd = HTTPServer(("0.0.0.0", PORT), FirmwareHandler)
server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
server_thread.start()

# Detect local IP
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('192.168.88.1', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '192.168.88.2'
    finally:
        s.close()
    return ip

local_ip = get_local_ip()

print(f"[+] HTTP Firmware Server LIVE on http://{local_ip}:{PORT}/sysupgrade.bin")
print(f"[*] Attempting automated Direct SSH Upgrade on 192.168.88.1...")

cmd_upgrade = f"wget -O /tmp/sysupgrade.bin http://{local_ip}:{PORT}/sysupgrade.bin && echo '[+] Download Complete! Flashing...' && sysupgrade -n /tmp/sysupgrade.bin"
ssh_cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-o', 'ConnectTimeout=3', '-o', 'LogLevel=ERROR', 'root@192.168.88.1', cmd_upgrade]

try:
    p = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate(timeout=15)
    print(out)
    if "Flashing" in out or "sysupgrade" in out:
        print("[✅] FIRMWARE FLASHING INITIATED ON ROUTER! Router will reboot in ~30 seconds.")
        sys.exit(0)
except Exception:
    pass

print("\n[*] If SSH is not connected or in U-Boot mode, you can:")
print(f"  1) On router terminal run: wget -O /tmp/sysupgrade.bin http://{local_ip}:{PORT}/sysupgrade.bin && sysupgrade -n /tmp/sysupgrade.bin")
print("  2) Or run NetInstall tool: python delta_flash.py")
print("=" * 60)
print("[*] Server is waiting for download... (Press Ctrl+C to stop)")

try:
    while True:
        threading.Event().wait(1)
except KeyboardInterrupt:
    print("\n[*] Server stopped.")
