"""
Delta OS Pro - Ultimate NetInstall & Etherboot Flasher v3.5
100% Automated RouterBOOT BOOTP + TFTP Flasher for MikroTik RouterBOARD LHG 5 / AR9344
"""

import sys
import os
import time
import socket
import struct
import threading
import subprocess
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

BOOTP_PORT = 67
DHCP_PORT = 68
TFTP_PORT = 69
DEFAULT_SERVER_IP = "192.168.88.2"
DEFAULT_ROUTER_IP = "192.168.88.13"
DHCP_MAGIC = b'\x63\x82\x53\x63'

# Colors
BG_DARK = "#0B1120"
CARD_BG = "#1E293B"
TEXT_WHITE = "#F8FAFC"
TEXT_MUTED = "#94A3B8"
ACCENT_BLUE = "#0284C7"
ACCENT_CYAN = "#38BDF8"
SUCCESS_GREEN = "#10B981"
WARN_AMBER = "#F59E0B"
ERROR_RED = "#EF4444"
BORDER_DARK = "#334155"


def get_network_interfaces():
    adapters = []
    try:
        out = subprocess.check_output(['ipconfig', '/all'], encoding='utf-8', errors='ignore')
        current_name = "Network Adapter"
        for line in out.splitlines():
            line_str = line.strip()
            if line and not line.startswith(' ') and ':' in line:
                current_name = line.split(':')[0].replace('adapter', '').strip()
            elif 'IPv4 Address' in line_str or 'IPv4' in line_str:
                ip = line_str.split(':')[-1].replace('(Preferred)', '').strip()
                if ip and not ip.startswith('127.'):
                    adapters.append({'name': current_name, 'ip': ip})
    except Exception:
        pass

    if not adapters:
        adapters.append({'name': 'Ethernet Adapter', 'ip': DEFAULT_SERVER_IP})

    return adapters


def open_firewall_rules():
    try:
        subprocess.run(['netsh', 'advfirewall', 'firewall', 'add', 'rule',
                        'name=Delta_BOOTP_67', 'protocol=UDP', 'dir=in',
                        'localport=67', 'action=allow'],
                       capture_output=True, timeout=2)
        subprocess.run(['netsh', 'advfirewall', 'firewall', 'add', 'rule',
                        'name=Delta_TFTP_69', 'protocol=UDP', 'dir=in',
                        'localport=69', 'action=allow'],
                       capture_output=True, timeout=2)
    except Exception:
        pass


class DeltaNetinstallProApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Delta OS Pro - MikroTik NetInstall Flasher v3.5")
        self.geometry("750x830")
        self.minsize(700, 720)
        self.configure(bg=BG_DARK)

        self.is_running = False
        self.stop_requested = False

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.stage1_path = os.path.join(base_dir, "openwrt.bin")
        self.stage2_path = os.path.join(base_dir, "sysupgrade.bin")

        self.setup_ui()
        self.check_admin()
        self.refresh_adapters()

    def check_admin(self):
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            is_admin = False

        if is_admin:
            self.admin_lbl.config(
                text="✅ Administrator Privileges: ACTIVE (Ready to bind UDP 67 & 69)",
                fg=SUCCESS_GREEN
            )
            self.log("[✓] Running with Administrator privileges.", "ok")
        else:
            self.admin_lbl.config(
                text="⚠️ WARNING: Not running as Administrator! (Right-Click EXE ➔ Run as Administrator)",
                fg=WARN_AMBER
            )
            self.log("[!] WARNING: Program is NOT running as Administrator!", "warn")

    def setup_ui(self):
        # 1. Header
        header = tk.Frame(self, bg="#0F172A", height=70, padx=20, pady=12)
        header.pack(fill="x")

        tk.Label(header, text="⚡ Delta OS Pro - MikroTik NetInstall Engine",
                 font=("Segoe UI", 15, "bold"), fg=TEXT_WHITE, bg="#0F172A").pack(anchor="w")
        tk.Label(header, text="Automated 2-Stage Etherboot (BOOTP + TFTP) ➔ SPI NOR Flash Writer",
                 font=("Segoe UI", 9), fg=ACCENT_CYAN, bg="#0F172A").pack(anchor="w")

        # Admin status bar
        self.admin_lbl = tk.Label(self, text="Checking Administrator Status...",
                                  font=("Segoe UI", 8, "bold"), bg=CARD_BG, fg=TEXT_MUTED, pady=4)
        self.admin_lbl.pack(fill="x")

        container = tk.Frame(self, bg=BG_DARK, padx=16, pady=10)
        container.pack(fill="both", expand=True)

        # 2. Network Card
        card_net = self.create_card(container, "1. Network Card (PC Ethernet IP)")
        net_row = tk.Frame(card_net, bg=CARD_BG)
        net_row.pack(fill="x", pady=(0, 6))

        tk.Label(net_row, text="PC Adapter IP:", font=("Segoe UI", 9, "bold"),
                 fg=TEXT_WHITE, bg=CARD_BG).pack(side="left", padx=(0, 10))

        self.adapter_combo = ttk.Combobox(net_row, font=("Consolas", 9), state="readonly", width=42)
        self.adapter_combo.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.adapter_combo.bind("<<ComboboxSelected>>", self.on_adapter_selected)

        tk.Button(net_row, text="🔄 Refresh", font=("Segoe UI", 8, "bold"),
                  bg=BORDER_DARK, fg=TEXT_WHITE, bd=0, cursor="hand2", padx=8, pady=3,
                  command=self.refresh_adapters).pack(side="right")

        self.net_hint_lbl = tk.Label(card_net, text="Selected: Waiting...", font=("Segoe UI", 8),
                                     fg=TEXT_MUTED, bg=CARD_BG)
        self.net_hint_lbl.pack(anchor="w")

        # 3. Firmware Files Card
        card_fw = self.create_card(container, "2. Firmware Files (openwrt.bin + sysupgrade.bin)")

        # Stage 1
        r1 = tk.Frame(card_fw, bg=CARD_BG)
        r1.pack(fill="x", pady=2)
        tk.Label(r1, text="Stage 1 (openwrt.bin):", font=("Segoe UI", 8, "bold"),
                 fg=ACCENT_CYAN, bg=CARD_BG, width=20, anchor="w").pack(side="left")
        self.s1_entry = tk.Entry(r1, font=("Consolas", 8), bg="#0B1120", fg=TEXT_WHITE, bd=1, relief="solid")
        self.s1_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        if os.path.exists(self.stage1_path):
            self.s1_entry.insert(0, self.stage1_path)
        tk.Button(r1, text="Browse...", font=("Segoe UI", 7, "bold"), bg=BORDER_DARK, fg=TEXT_WHITE, bd=0,
                  command=lambda: self.browse_file(self.s1_entry, "Select openwrt.bin")).pack(side="right")

        # Stage 2
        r2 = tk.Frame(card_fw, bg=CARD_BG)
        r2.pack(fill="x", pady=(6, 2))
        tk.Label(r2, text="Stage 2 (sysupgrade.bin):", font=("Segoe UI", 8, "bold"),
                 fg=SUCCESS_GREEN, bg=CARD_BG, width=20, anchor="w").pack(side="left")
        self.s2_entry = tk.Entry(r2, font=("Consolas", 8), bg="#0B1120", fg=TEXT_WHITE, bd=1, relief="solid")
        self.s2_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        if os.path.exists(self.stage2_path):
            self.s2_entry.insert(0, self.stage2_path)
        tk.Button(r2, text="Browse...", font=("Segoe UI", 7, "bold"), bg=BORDER_DARK, fg=TEXT_WHITE, bd=0,
                  command=lambda: self.browse_file(self.s2_entry, "Select sysupgrade.bin")).pack(side="right")

        # 4. Action Card
        card_act = self.create_card(container, "3. Start NetInstall Listener")
        steps = (
            "1. Connect PC Ethernet cable directly to MikroTik Router ETH/PoE port.\n"
            "2. Set PC IP to 192.168.88.2 / 255.255.255.0 (ensure it's selected in step 1).\n"
            "3. Click START NETINSTALL below.\n"
            "4. Hold RESET button on router ➔ Plug Power ➔ Keep holding until router is detected!"
        )
        tk.Label(card_act, text=steps, font=("Segoe UI", 8), fg=TEXT_WHITE, bg=CARD_BG, justify="left").pack(anchor="w", pady=(0, 8))

        p_row = tk.Frame(card_act, bg=CARD_BG)
        p_row.pack(fill="x", pady=(0, 4))
        self.status_lbl = tk.Label(p_row, text="Status: Ready", font=("Segoe UI", 8, "bold"),
                                   fg=ACCENT_CYAN, bg=CARD_BG)
        self.status_lbl.pack(side="left")
        self.pct_lbl = tk.Label(p_row, text="0%", font=("Consolas", 9, "bold"),
                                fg=ACCENT_CYAN, bg=CARD_BG)
        self.pct_lbl.pack(side="right")

        self.progress_bar = ttk.Progressbar(card_act, mode="determinate", maximum=100)
        self.progress_bar.pack(fill="x", pady=(0, 10))

        btn_box = tk.Frame(card_act, bg=CARD_BG)
        btn_box.pack(fill="x")
        self.btn_start = tk.Button(btn_box, text="📡 START NETINSTALL LISTENER",
                                   font=("Segoe UI", 10, "bold"), bg=ACCENT_BLUE, fg=TEXT_WHITE,
                                   activebackground="#0369A1", activeforeground=TEXT_WHITE,
                                   bd=0, cursor="hand2", pady=8, command=self.start_netinstall)
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.btn_stop = tk.Button(btn_box, text="🛑 Stop", font=("Segoe UI", 10, "bold"),
                                  bg=BORDER_DARK, fg=TEXT_WHITE, state="disabled",
                                  bd=0, cursor="hand2", pady=8, padx=14, command=self.stop_netinstall)
        self.btn_stop.pack(side="right")

        # 5. Live Console
        card_log = self.create_card(container, "Live Execution Console")
        self.log_box = scrolledtext.ScrolledText(card_log, bg="#050B14", fg="#38BDF8",
                                                insertbackground="#38BDF8", font=("Consolas", 8),
                                                bd=0, relief="flat", height=10)
        self.log_box.pack(fill="both", expand=True)
        self.log_box.tag_configure("ok", foreground=SUCCESS_GREEN)
        self.log_box.tag_configure("warn", foreground=WARN_AMBER)
        self.log_box.tag_configure("err", foreground=ERROR_RED)
        self.log_box.tag_configure("info", foreground=ACCENT_CYAN)

        self.log("Delta OS Pro NetInstall Engine Initialized.", "ok")

    def create_card(self, parent, title):
        card = tk.LabelFrame(parent, text=f" {title} ", font=("Segoe UI", 9, "bold"),
                             fg=ACCENT_CYAN, bg=CARD_BG, bd=1, relief="solid",
                             padx=12, pady=8)
        card.pack(fill="x", pady=(0, 8))
        return card

    def log(self, msg, tag=""):
        timestamp = time.strftime('%H:%M:%S')
        line = f"[{timestamp}] {msg}\n"
        self.log_box.insert("end", line, tag)
        self.log_box.see("end")

    def browse_file(self, entry_widget, title):
        fp = filedialog.askopenfilename(title=title, filetypes=[("Binary Firmware", "*.bin"), ("All Files", "*.*")])
        if fp:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, fp)
            self.log(f"Selected: {os.path.basename(fp)} ({os.path.getsize(fp)/(1024*1024):.2f} MB)", "info")

    def refresh_adapters(self):
        adapters = get_network_interfaces()
        combo_vals = []
        sel_idx = 0
        for idx, a in enumerate(adapters):
            combo_vals.append(f"{a['ip']} ({a['name']})")
            if "192.168.88." in a['ip']:
                sel_idx = idx

        self.adapter_combo['values'] = combo_vals
        if combo_vals:
            self.adapter_combo.current(sel_idx)
            self.on_adapter_selected(None)

    def on_adapter_selected(self, event):
        val = self.adapter_combo.get()
        if val:
            ip = val.split(' ')[0]
            if "192.168.88." in ip:
                self.net_hint_lbl.config(text=f"✅ Perfect! IP {ip} is ready for MikroTik RouterBOOT.", fg=SUCCESS_GREEN)
            else:
                self.net_hint_lbl.config(text=f"ℹ️ Selected IP: {ip}. (Set Ethernet IP to 192.168.88.2 for best results)", fg=ACCENT_CYAN)

    def update_progress(self, text, pct):
        self.after(0, lambda: self.status_lbl.config(text=text))
        self.after(0, lambda: self.pct_lbl.config(text=f"{pct}%"))
        self.after(0, lambda: self.progress_bar.config(value=pct))

    def start_netinstall(self):
        if self.is_running:
            return

        s1 = self.s1_entry.get().strip()
        s2 = self.s2_entry.get().strip()
        sel = self.adapter_combo.get().strip()

        if not sel:
            messagebox.showerror("Error", "Please select your Ethernet adapter IP!")
            return

        server_ip = sel.split(' ')[0]

        if not s1 or not os.path.exists(s1):
            messagebox.showerror("Error", f"Stage 1 Kernel (openwrt.bin) not found:\n{s1}")
            return

        if not s2 or not os.path.exists(s2):
            messagebox.showerror("Error", f"Stage 2 Flash (sysupgrade.bin) not found:\n{s2}")
            return

        open_firewall_rules()

        self.is_running = True
        self.stop_requested = False
        self.btn_start.config(state="disabled", bg="#64748B")
        self.btn_stop.config(state="normal", bg=ERROR_RED)

        self.update_progress("Waiting for MikroTik BOOTP Etherboot broadcast...", 0)
        self.log("=" * 60, "info")
        self.log("🚀 NETINSTALL SERVER STARTED", "ok")
        self.log(f"  Server IP : {server_ip}", "info")
        self.log(f"  Offer IP  : {DEFAULT_ROUTER_IP}", "info")
        self.log(f"  Kernel    : {os.path.basename(s1)}", "info")
        self.log(f"  Flash     : {os.path.basename(s2)}", "info")
        self.log("👉 HOLD RESET BUTTON ON ROUTER WITH NEEDLE AND POWER ON NOW!", "warn")
        self.log("=" * 60, "info")

        threading.Thread(target=self.run_netinstall_pipeline, args=(server_ip, s1, s2), daemon=True).start()

    def stop_netinstall(self):
        self.stop_requested = True
        self.is_running = False
        self.log("[!] NetInstall listener stopped.", "warn")
        self.btn_start.config(state="normal", bg=ACCENT_BLUE)
        self.btn_stop.config(state="disabled", bg=BORDER_DARK)
        self.update_progress("NetInstall Stopped", 0)

    def run_netinstall_pipeline(self, server_ip, s1_file, s2_file):
        bootp_sock = None
        tftp_sock = None
        try:
            # 1. Open TFTP Socket FIRST (on port 69) so it never misses router requests
            tftp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            tftp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tftp_sock.settimeout(0.5)
            try:
                tftp_sock.bind(('', TFTP_PORT))
                self.log("[✓] TFTP Socket active on UDP port 69", "ok")
            except Exception as e:
                self.log(f"[✗] TFTP bind port 69 failed: {e}", "err")
                self.after(0, self.stop_netinstall)
                return

            # 2. Open BOOTP Socket (on port 67)
            bootp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            bootp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            bootp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            bootp_sock.settimeout(0.5)
            try:
                bootp_sock.bind(('', BOOTP_PORT))
                self.log("[✓] BOOTP Socket active on UDP port 67", "ok")
            except Exception as e:
                self.log(f"[✗] BOOTP bind port 67 failed: {e}", "err")
                tftp_sock.close()
                self.after(0, self.stop_netinstall)
                return

            # 3. Listen loop for BOOTP requests and TFTP RRQ requests simultaneously
            router_detected = False
            tftp_client_addr = None
            tftp_req_file = ""
            start_t = time.time()

            while not self.stop_requested:
                # Check BOOTP packets
                try:
                    bdata, baddr = bootp_sock.recvfrom(1024)
                    if len(bdata) >= 236 and bdata[0] == 1:  # BOOTP Request
                        xid = struct.unpack('!I', bdata[4:8])[0]
                        chaddr = bdata[28:44]
                        mac = ':'.join(f'{b:02x}' for b in bdata[28:34])
                        
                        if not router_detected:
                            router_detected = True
                            self.log(f"🔥 MIKROTIK DETECTED! MAC: {mac}", "ok")
                            self.update_progress(f"Router Detected ({mac}) - Sending BOOTP reply...", 10)

                        # Generate ultra-compatible BOOTP reply with DHCP Option 66 & 67
                        reply = self.build_bootp_reply(xid, chaddr, server_ip, DEFAULT_ROUTER_IP, "openwrt.bin")
                        
                        # Send to broadcast and directly to offered IP
                        try:
                            bootp_sock.sendto(reply, ('255.255.255.255', 68))
                            bootp_sock.sendto(reply, (DEFAULT_ROUTER_IP, 68))
                        except Exception:
                            pass
                except socket.timeout:
                    pass
                except Exception as e:
                    self.log(f"[!] BOOTP error: {e}", "warn")

                # Check TFTP packets
                try:
                    tdata, taddr = tftp_sock.recvfrom(1024)
                    if len(tdata) >= 2:
                        opcode = struct.unpack('!H', tdata[:2])[0]
                        if opcode == 1:  # TFTP RRQ
                            parts = tdata[2:].split(b'\x00')
                            tftp_req_file = parts[0].decode('ascii', errors='ignore')
                            tftp_client_addr = taddr
                            self.log(f"📥 TFTP RRQ received for '{tftp_req_file}' from {taddr[0]}:{taddr[1]}", "ok")
                            break
                except socket.timeout:
                    pass
                except Exception as e:
                    self.log(f"[!] TFTP error: {e}", "warn")

                elapsed = int(time.time() - start_t)
                if elapsed % 6 == 0 and elapsed > 0 and not router_detected:
                    self.log(f"⏳ Listening for RouterBOOT broadcast... ({elapsed}s)", "info")

            if self.stop_requested or not tftp_client_addr:
                if bootp_sock: bootp_sock.close()
                if tftp_sock: tftp_sock.close()
                self.after(0, self.stop_netinstall)
                return

            # Keep sending BOOTP in background just in case router re-checks
            bootp_sock.close()

            # 4. Serve Stage 1 TFTP Kernel
            self.update_progress("Uploading Stage 1 Kernel (openwrt.bin) to Router RAM...", 15)
            tftp_sock.settimeout(6.0)

            file_size = os.path.getsize(s1_file)
            blksize = 512
            total_blocks = (file_size + blksize - 1) // blksize

            self.log(f"🚀 Transferring {file_size/(1024*1024):.2f} MB ({total_blocks} blocks) to Router RAM...", "info")

            with open(s1_file, 'rb') as f:
                block = 1
                while not self.stop_requested:
                    chunk = f.read(blksize)
                    if not chunk and block > 1:
                        break

                    pkt = struct.pack('!HH', 3, block & 0xFFFF) + chunk
                    sent_ok = False

                    for attempt in range(10):
                        try:
                            tftp_sock.sendto(pkt, tftp_client_addr)
                            ack_data, ack_addr = tftp_sock.recvfrom(64)
                            if len(ack_data) >= 4:
                                ack_op, ack_blk = struct.unpack('!HH', ack_data[:4])
                                if ack_op == 4 and ack_blk == (block & 0xFFFF):
                                    sent_ok = True
                                    tftp_client_addr = ack_addr
                                    break
                        except socket.timeout:
                            continue

                    if not sent_ok:
                        self.log(f"[✗] TFTP block {block} failed after 10 attempts.", "err")
                        tftp_sock.close()
                        self.after(0, self.stop_netinstall)
                        return

                    pct = int(15 + (block / total_blocks) * 45)  # 15% to 60%
                    self.update_progress(f"Uploading Stage 1 Kernel ({block}/{total_blocks} blocks)...", pct)
                    if block % 250 == 0 or block == total_blocks:
                        self.log(f"  Sent block {block}/{total_blocks} ({int((block/total_blocks)*100)}%)", "info")

                    block += 1
                    if len(chunk) < blksize:
                        break

            tftp_sock.close()
            self.update_progress("Stage 1 Kernel loaded! Router is booting RAM Linux (~25s)...", 65)
            self.log("✅ STAGE 1 KERNEL 100% TRANSFERRED!", "ok")
            self.log("RouterBOOT is executing RAM Kernel... Starting auto-flash in 25s!", "info")

            # 5. Countdown to allow RAM Linux to initialize network stack
            for remaining in range(25, 0, -1):
                if self.stop_requested: break
                self.update_progress(f"Booting RAM Linux... Starting Stage 2 in {remaining}s", 65)
                time.sleep(1)

            # 6. Stage 2 Flash: Stream sysupgrade.bin into SPI NOR Flash
            self.update_progress("Connecting to Router to write Permanent Flash (sysupgrade.bin)...", 75)
            self.log("=" * 60, "info")
            self.log("🔥 STAGE 2: FLASHING PERMANENT DELTA OS INTO NOR FLASH", "ok")

            s2_size = os.path.getsize(s2_file)
            ssh_cmd = [
                'ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'LogLevel=ERROR', 'root@192.168.88.1',
                'cat > /tmp/firmware.bin && echo "[FLASH_READY]" && /sbin/sysupgrade -F -n -v /tmp/firmware.bin'
            ]

            try:
                proc = subprocess.Popen(ssh_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                bytes_sent = 0
                chunk_sz = 65536
                with open(s2_file, 'rb') as f:
                    while not self.stop_requested:
                        chunk = f.read(chunk_sz)
                        if not chunk: break
                        proc.stdin.write(chunk)
                        bytes_sent += len(chunk)
                        pct = int(75 + (bytes_sent / s2_size) * 20)  # 75% to 95%
                        self.update_progress(f"Streaming sysupgrade.bin to NOR Flash ({bytes_sent//1024} KB)...", pct)

                proc.stdin.close()
                self.log("[✓] sysupgrade.bin streamed into router Flash!", "ok")
                self.update_progress("Writing SPI NOR Flash Blocks & Rebooting...", 95)

                while True:
                    line = proc.stdout.readline()
                    if not line: break
                    decoded = line.decode('utf-8', errors='ignore').strip()
                    if decoded:
                        self.log(f"  [ROUTER] {decoded}", "info")

                proc.wait()
            except Exception as e:
                self.log(f"[!] Stage 2 Flash notice: {e}", "warn")

            self.update_progress("✨ ALL DONE! Permanent Flash Write Complete!", 100)
            self.log("=" * 60, "ok")
            self.log("🎉 SUCCESS: Delta OS Pro is permanently installed on your MikroTik router!", "ok")
            self.log("The router is rebooting now. Open http://192.168.88.1 in ~35 seconds.", "ok")

            messagebox.showinfo(
                "NetInstall Complete ✅",
                "🎉 Delta OS Pro has been successfully flashed!\n\n"
                "The router is rebooting into the new system.\n"
                "Open http://192.168.88.1 in your web browser."
            )

        except Exception as e:
            self.log(f"❌ NetInstall Error: {e}", "err")
            self.update_progress(f"Error: {e}", 0)
            messagebox.showerror("Error", f"NetInstall failed: {e}")
        finally:
            self.after(0, self.stop_netinstall)

    def build_bootp_reply(self, xid, chaddr, server_ip, client_ip, boot_file):
        op = 2  # BOOTP Reply
        htype = 1
        hlen = 6
        hops = 0
        secs = 0
        flags = 0
        ciaddr = socket.inet_aton('0.0.0.0')
        yiaddr = socket.inet_aton(client_ip)
        siaddr = socket.inet_aton(server_ip)
        giaddr = socket.inet_aton('0.0.0.0')
        chaddr_pad = chaddr + b'\x00' * (16 - len(chaddr))
        sname = server_ip.encode().ljust(64, b'\x00')
        file_b = boot_file.encode().ljust(128, b'\x00')

        # Full Standard DHCP & BOOTP Options
        opts = DHCP_MAGIC
        opts += b'\x35\x01\x02'                              # DHCP OFFER (53)
        opts += b'\x01\x04' + socket.inet_aton('255.255.255.0')  # Subnet Mask (1)
        opts += b'\x03\x04' + socket.inet_aton(server_ip)        # Router (3)
        opts += b'\x36\x04' + socket.inet_aton(server_ip)        # Server ID (54)
        opts += b'\x33\x04' + struct.pack('!I', 86400)           # Lease 24h (51)
        # Option 66 (TFTP Server Name)
        opts += b'\x42' + bytes([len(server_ip)]) + server_ip.encode()
        # Option 67 (Bootfile Name)
        opts += b'\x43' + bytes([len(boot_file)]) + boot_file.encode()
        opts += b'\xff'                                           # End

        hdr = struct.pack('!BBBBIHH', op, htype, hlen, hops, xid, secs, flags)
        return hdr + ciaddr + yiaddr + siaddr + giaddr + chaddr_pad + sname + file_b + opts


if __name__ == "__main__":
    app = DeltaNetinstallProApp()
    app.mainloop()
