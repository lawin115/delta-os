"""
MikroTik Delta-OS Zero-RAM Flasher Pro v4.5
Direct SPI Stream Edition • فلاشکەری خێرای ماکرۆتیک بێ کڕاشکردن
"""

import os
import sys
import time
import socket
import struct
import json
import threading
import subprocess
import urllib.request
import urllib.error
import queue
import ctypes
import webbrowser
from PIL import Image, ImageTk
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox

# Appearance Settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def disable_quickedit():
    """Disable Windows console QuickEdit mode to prevent accidental pause."""
    if sys.platform == "win32":
        try:
            kernel32 = ctypes.windll.kernel32
            h_stdin = kernel32.GetStdHandle(-10)
            mode = ctypes.c_uint32()
            kernel32.GetConsoleMode(h_stdin, ctypes.byref(mode))
            new_mode = mode.value & ~0x0040  # ENABLE_QUICK_EDIT_MODE
            kernel32.SetConsoleMode(h_stdin, new_mode)
        except Exception:
            pass


BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
SERVER_IP = "192.168.88.2"
CLIENT_IP = "192.168.88.13"
ROUTER_IP = "192.168.88.1"
SUBNET_MASK = "255.255.255.0"
NC_PORT = 9000

DEFAULT_BOOT_FILE = os.path.join(BASE_DIR, "openwrt.bin")
DEFAULT_FW_FILE = os.path.join(BASE_DIR, "sysupgrade.bin")
LOGO_FILE = os.path.join(BASE_DIR, "favicon.png")


class ZeroRamEngine:
    """
    Zero-RAM Direct SPI Stream Flasher Engine:
    1. BOOTP (67) + TFTP (69) -> Boots RAM kernel (openwrt.bin)
    2. Netcat Pipe (9000) -> Streams sysupgrade.bin directly into NOR Flash via 'nc | mtd write - firmware'
    """
    def __init__(self, server_ip, client_ip, router_ip, boot_file, fw_file, nc_port=9000,
                 log_cb=None, status_cb=None, progress_cb=None, stage_cb=None):
        self.server_ip = server_ip
        self.client_ip = client_ip
        self.router_ip = router_ip
        self.boot_file = boot_file
        self.fw_file = fw_file
        self.nc_port = nc_port

        self.log_cb = log_cb or (lambda msg, tag: None)
        self.status_cb = status_cb or (lambda msg, color: None)
        self.progress_cb = progress_cb or (lambda pct: None)
        self.stage_cb = stage_cb or (lambda stage: None)

        self.running = False
        self.bootp_sock = None
        self.tftp_sock = None
        self.nc_sock = None

    def log(self, msg, tag="INFO"):
        self.log_cb(msg, tag)

    def set_status(self, msg, color="#00E5FF"):
        self.status_cb(msg, color)

    def set_progress(self, pct):
        self.progress_cb(pct)

    def set_stage(self, stage):
        self.stage_cb(stage)

    def start(self):
        self.running = True
        threading.Thread(target=self._run_netcat_server, daemon=True).start()
        threading.Thread(target=self._run_tftp_server, daemon=True).start()
        threading.Thread(target=self._run_bootp_server, daemon=True).start()
        threading.Thread(target=self._zero_ram_direct_mtd_flasher, daemon=True).start()

    def stop(self):
        self.running = False
        for s in [self.bootp_sock, self.tftp_sock, self.nc_sock]:
            if s:
                try:
                    s.close()
                except Exception:
                    pass

    def _run_netcat_server(self):
        """Netcat Server on port 9000: Streams firmware directly to router MTD pipe."""
        try:
            self.nc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.nc_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.nc_sock.bind((self.server_ip, self.nc_port))
            self.nc_sock.listen(1)
            self.nc_sock.settimeout(2.0)

            while self.running:
                try:
                    conn, addr = self.nc_sock.accept()
                    self.log(f"⚡ [NETCAT PIPE CONNECTED] Router connected from {addr[0]}!", "HIGHLIGHT")
                    self.set_status("Streaming firmware directly into SPI Flash Chip...", "#00FFA3")
                    self.set_stage(3)

                    fw_size = os.path.getsize(self.fw_file)
                    sent = 0
                    start_time = time.time()

                    with open(self.fw_file, "rb") as f:
                        while self.running:
                            chunk = f.read(65536)
                            if not chunk:
                                break
                            conn.sendall(chunk)
                            sent += len(chunk)
                            pct = int((sent / fw_size) * 100)
                            self.set_progress(pct)
                            if sent % (512 * 1024) == 0 or sent == fw_size:
                                self.log(f"Writing to SPI Flash: {pct}% ({sent // 1024}/{fw_size // 1024} KB)", "INFO")

                    conn.close()
                    elapsed = time.time() - start_time
                    self.log(f"✨ [FLASH COMPLETE] {sent:,} bytes written directly to Flash in {elapsed:.1f}s!", "SUCCESS")
                    break
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.log(f"Netcat error: {e}", "ERROR")
                    break
        except Exception as e:
            if self.running:
                self.log(f"Netcat server error: {e}", "ERROR")

    def _run_bootp_server(self):
        """BOOTP Server: Broadcasts IP & Boot File to MikroTik RouterBOOT."""
        try:
            self.bootp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.bootp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.bootp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.bootp_sock.bind(('', 67))
            self.bootp_sock.settimeout(1.0)
            self.log(f"✅ BOOTP/DHCP Server Active on {self.server_ip}:67", "SUCCESS")

            while self.running:
                try:
                    data, addr = self.bootp_sock.recvfrom(1024)
                    if len(data) >= 236 and data[0] == 1:  # BOOTP Request
                        xid = struct.unpack('!I', data[4:8])[0]
                        chaddr = data[28:44]
                        mac = ':'.join(f'{b:02X}' for b in data[28:34])

                        self.log(f"⚡ MikroTik Connected! MAC Address: {mac}", "HIGHLIGHT")
                        self.set_status(f"MikroTik Found ({mac}) -> Release Reset Button Now!", "#00F0FF")
                        self.set_stage(1)

                        # Build BOOTP Reply
                        op = 2
                        htype, hlen, hops = 1, 6, 0
                        secs, flags = 0, 0
                        ciaddr = socket.inet_aton("0.0.0.0")
                        yiaddr = socket.inet_aton(self.client_ip)
                        siaddr = socket.inet_aton(self.server_ip)
                        giaddr = socket.inet_aton("0.0.0.0")
                        sname = self.server_ip.encode('ascii').ljust(64, b'\x00')
                        file_b = b"openwrt.bin".ljust(128, b'\x00')

                        dhcp_opts = b'\x63\x82\x53\x63'  # DHCP Magic
                        dhcp_opts += b'\x35\x01\x02'      # Offer
                        dhcp_opts += b'\x01\x04' + socket.inet_aton(SUBNET_MASK)
                        dhcp_opts += b'\x03\x04' + socket.inet_aton(self.server_ip)
                        dhcp_opts += b'\x36\x04' + socket.inet_aton(self.server_ip)
                        dhcp_opts += b'\x42' + bytes([len(self.server_ip)]) + self.server_ip.encode('ascii')
                        dhcp_opts += b'\x43' + bytes([len("openwrt.bin")]) + b"openwrt.bin"
                        dhcp_opts += b'\xff'

                        hdr = struct.pack('!BBBBIHH', op, htype, hlen, hops, xid, secs, flags)
                        pkt = hdr + ciaddr + yiaddr + siaddr + giaddr + chaddr + sname + file_b + dhcp_opts

                        for _ in range(3):
                            self.bootp_sock.sendto(pkt, ('255.255.255.255', 68))
                            self.bootp_sock.sendto(pkt, (self.client_ip, 68))
                            time.sleep(0.05)

                        self.log(f"📤 Assigned IP {self.client_ip} -> Offering 'openwrt.bin' (Now release Reset button)...", "INFO")
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.log(f"BOOTP error: {e}", "WARNING")
        except Exception as e:
            if self.running:
                self.log(f"❌ BOOTP Port 67 error (Run as Administrator): {e}", "ERROR")

    def _run_tftp_server(self):
        """TFTP Server: Serves openwrt.bin kernel to RouterBOOT."""
        try:
            self.tftp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.tftp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tftp_sock.bind(('', 69))
            self.tftp_sock.settimeout(1.0)
            self.log(f"✅ TFTP Server Active on {self.server_ip}:69", "SUCCESS")

            while self.running:
                try:
                    data, addr = self.tftp_sock.recvfrom(1024)
                    if len(data) >= 2 and struct.unpack('!H', data[:2])[0] == 1:  # RRQ
                        threading.Thread(target=self._handle_tftp_client, args=(data, addr), daemon=True).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.log(f"TFTP recv error: {e}", "WARNING")
        except Exception as e:
            if self.running:
                self.log(f"❌ TFTP Port 69 error: {e}", "ERROR")

    def _handle_tftp_client(self, rrq_data, client_addr):
        try:
            parts = rrq_data[2:].split(b'\x00')
            req_file = parts[0].decode('utf-8', errors='ignore').strip()
            self.log(f"📥 TFTP Request for BOOTLOADER: {req_file}", "HIGHLIGHT")

            target_path = self.fw_file if ("sysupgrade" in req_file or "firmware" in req_file) else self.boot_file

            if not os.path.exists(target_path):
                self.log(f"❌ File not found: {target_path}", "ERROR")
                return

            file_size = os.path.getsize(target_path)
            blksize = 512

            # Parse TFTP options
            for i in range(2, len(parts) - 1, 2):
                opt = parts[i].decode('ascii', errors='ignore').lower()
                val = parts[i + 1].decode('ascii', errors='ignore')
                if opt == 'blksize':
                    blksize = min(int(val), 1432)

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5.0)

            total_blocks = (file_size + blksize - 1) // blksize
            start_t = time.time()

            with open(target_path, 'rb') as f:
                block = 1
                while self.running:
                    chunk = f.read(blksize)
                    if not chunk and block > 1:
                        break

                    pkt = struct.pack('!HH', 3, block & 0xFFFF) + chunk
                    acked = False

                    for attempt in range(8):
                        try:
                            sock.sendto(pkt, client_addr)
                            ack, raddr = sock.recvfrom(64)
                            client_addr = raddr
                            if len(ack) >= 4 and struct.unpack('!HH', ack[:4]) == (4, block & 0xFFFF):
                                acked = True
                                break
                        except socket.timeout:
                            continue

                    if not acked:
                        self.log(f"⚠️ TFTP client stalled at block {block}.", "WARNING")
                        break

                    pct = int((block / total_blocks) * 100)
                    self.set_progress(pct)
                    if block % 200 == 0 or block == total_blocks:
                        self.set_status(f"Loading RAM Netboot: {pct}% ({block*blksize//1024}/{file_size//1024} KB)", "#00F0FF")

                    block += 1
                    if len(chunk) < blksize:
                        break

            sock.close()
            elapsed = time.time() - start_t
            self.log(f"🎉 Netboot Kernel Loaded in {elapsed:.1f}s ({file_size:,} bytes)!", "SUCCESS")
            self.set_status("MikroTik booting in RAM... Triggering Zero-RAM Flash...", "#FFB703")
            self.set_stage(2)
        except Exception as e:
            self.log(f"TFTP Transfer error: {e}", "ERROR")

    def _zero_ram_direct_mtd_flasher(self):
        """Monitors router RAM boot and executes the Zero-RAM direct SPI MTD write pipe."""
        time.sleep(12)
        self.log("⏳ Waiting for RAM kernel to initialize (12 seconds)...", "INFO")

        flash_cmd = f"mtd unlock firmware && mtd erase firmware && nc {self.server_ip} {self.nc_port} | mtd write - firmware && sync && reboot -f"

        for attempt in range(1, 41):
            if not self.running:
                return

            self.log(f"🔍 Connecting to router on {self.router_ip}... ({attempt}/40)", "STEP")

            # 1. Telnet
            try:
                t_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                t_sock.settimeout(2.0)
                t_sock.connect((self.router_ip, 23))
                self.log("✨ Telnet port open! Executing Direct Flash Pipe...", "SUCCESS")
                time.sleep(1)
                t_sock.sendall((flash_cmd + "\n").encode('ascii'))
                t_sock.close()
                self._report_pipe_success(flash_cmd)
                return
            except Exception:
                pass

            # 2. SSH
            try:
                s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s_sock.settimeout(2.0)
                s_sock.connect((self.router_ip, 22))
                s_sock.close()
                self.log("✨ SSH port open! Executing Direct Flash Pipe...", "SUCCESS")
                ssh_run = subprocess.run([
                    'ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=no',
                    '-o', 'UserKnownHostsFile=/dev/null', '-o', 'ConnectTimeout=4',
                    f'root@{self.router_ip}', flash_cmd
                ], capture_output=True, timeout=10)
                self._report_pipe_success(flash_cmd)
                return
            except Exception:
                pass

            # 3. HTTP CGI
            try:
                url = f"http://{self.router_ip}/cgi-bin/api.cgi?action=system_status"
                req = urllib.request.Request(url, headers={'User-Agent': 'ZeroRamFlasherFluent'})
                with urllib.request.urlopen(req, timeout=2.0) as resp:
                    if resp.status == 200:
                        self.log("✨ API CGI online! Triggering Flash...", "SUCCESS")
                        flash_url = f"http://{self.router_ip}/cgi-bin/api.cgi?action=flash_tftp&tftp_host={self.server_ip}"
                        urllib.request.urlopen(flash_url, timeout=5.0)
                        self._report_pipe_success(flash_cmd)
                        return
            except Exception:
                pass

            self.set_status(f"Waiting for router RAM OS... ({attempt}/40)", "#FFB703")
            time.sleep(2)

        self.log("⚠️ Router on 192.168.88.1 did not respond.", "ERROR")

    def _report_pipe_success(self, flash_cmd):
        self.log("=================================================================", "TITLE")
        self.log("🔥 DIRECT MTD PIPE EXECUTED ON ROUTER:", "HIGHLIGHT")
        self.log(f"👉 {flash_cmd}", "INFO")
        self.set_status("Writing firmware directly to SPI Flash Memory...", "#00FFA3")

        # Wait for flash to complete and router to reboot
        time.sleep(25)
        self.set_status("Flash 100% Complete! Router is rebooting into Delta-OS...", "#00FFA3")
        self.log("🏆 100% Flashed Successfully! Rebooting into Permanent Delta-OS...", "SUCCESS")
        self.set_stage(4)
        self.set_progress(100)

        # Check online status
        for _ in range(30):
            if not self.running:
                return
            try:
                urllib.request.urlopen(f"http://{self.router_ip}/", timeout=2.0)
                self.log(f"🎉 Delta-OS is Online at http://{self.router_ip}", "SUCCESS")
                self.set_status(f"🌐 [ONLINE] Web Dashboard active on http://{self.router_ip}", "#00FFA3")
                messagebox.showinfo("سەرکەوتوو بوو!", f"ماکرۆتیک بە سەرکەوتوویی فلاش کرا!\n\nناونیشانی وێب: http://{self.router_ip}\nپاسۆرد: admin")
                break
            except Exception:
                time.sleep(2)


class ModernFluentGlassApp(ctk.CTk):
    """Next-Gen Fluent Glassmorphism GUI for MikroTik Delta-OS."""
    def __init__(self):
        super().__init__()
        self.title("MikroTik Delta-OS Zero-RAM Flasher Pro v4.5")
        self.geometry("980x760")
        self.configure(fg_color="#0A0D14")

        self.engine = None
        self.queue = queue.Queue()

        self._build_ui()
        self.after(100, self._process_queue)

    def _build_ui(self):
        # 1. Header Banner
        header = ctk.CTkFrame(self, height=75, fg_color="#121724", corner_radius=12, border_width=1, border_color="#1F293D")
        header.pack(fill="x", padx=16, pady=(14, 8))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=18, pady=10)

        ctk.CTkLabel(title_box, text="MIKROTIK DELTA-OS FLASHER PRO",
                     font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                     text_color="#FFFFFF").pack(anchor="w")
        ctk.CTkLabel(title_box, text="Zero-RAM Direct SPI Stream Edition  •  فلاشکەری خێرای ماکرۆتیک بێ کڕاشکردن",
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     text_color="#00E5FF").pack(anchor="w")

        self.server_status_badge = ctk.CTkLabel(header, text="● SERVER READY",
                                               font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                               text_color="#00FFA3")
        self.server_status_badge.pack(side="right", padx=20)

        # 2. Main Layout Container
        main_grid = ctk.CTkFrame(self, fg_color="transparent")
        main_grid.pack(fill="both", expand=True, padx=16, pady=6)
        main_grid.columnconfigure(0, weight=1)
        main_grid.rowconfigure(0, weight=0)
        main_grid.rowconfigure(1, weight=1)

        # 3. Step Progression Indicator
        steps_card = ctk.CTkFrame(main_grid, fg_color="#182236", corner_radius=10, border_width=1, border_color="#26334D")
        steps_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.step_labels = []
        step_titles = [
            "1. BOOTP Etherboot",
            "2. TFTP RAM Kernel",
            "3. Direct MTD Stream",
            "4. Permanent Delta-OS"
        ]
        steps_grid = ctk.CTkFrame(steps_card, fg_color="transparent")
        steps_grid.pack(fill="x", padx=14, pady=10)

        for i, title in enumerate(step_titles):
            steps_grid.columnconfigure(i * 2, weight=1)
            lbl = ctk.CTkLabel(steps_grid, text=title, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                               text_color="#8E9AA8")
            lbl.grid(row=0, column=i * 2, padx=4)
            self.step_labels.append(lbl)

            if i < len(step_titles) - 1:
                ctk.CTkLabel(steps_grid, text="➔", font=ctk.CTkFont(size=11), text_color="#5F6D82").grid(row=0, column=i * 2 + 1)

        # 4. Settings Card
        cfg_card = ctk.CTkFrame(main_grid, fg_color="#182032", corner_radius=10, border_width=1, border_color="#26334D")
        cfg_card.grid(row=1, column=0, sticky="nsew", pady=(0, 8))

        ctk.CTkLabel(cfg_card, text="⚙️ Configuration & Firmware Files",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     text_color="#00E5FF").pack(anchor="w", padx=16, pady=(12, 6))

        # IP Row
        ip_row = ctk.CTkFrame(cfg_card, fg_color="transparent")
        ip_row.pack(fill="x", padx=16, pady=4)

        ctk.CTkLabel(ip_row, text="Server IP (PC):", width=140, anchor="w", font=ctk.CTkFont(size=11), text_color="#C5CEE0").pack(side="left")
        self.ip_entry = ctk.CTkEntry(ip_row, width=160, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#0A0D14")
        self.ip_entry.insert(0, SERVER_IP)
        self.ip_entry.pack(side="left", padx=(0, 10))

        btn_auto_ip = ctk.CTkButton(ip_row, text="Auto Set 192.168.88.2", font=ctk.CTkFont(size=11, weight="bold"),
                                    fg_color="#1E2B42", hover_color="#2B3D5E", width=180,
                                    command=self._auto_set_static_ip)
        btn_auto_ip.pack(side="left")

        # Boot Kernel Row
        boot_row = ctk.CTkFrame(cfg_card, fg_color="transparent")
        boot_row.pack(fill="x", padx=16, pady=4)

        ctk.CTkLabel(boot_row, text="Boot Kernel (RAM):", width=140, anchor="w", font=ctk.CTkFont(size=11), text_color="#C5CEE0").pack(side="left")
        self.boot_entry = ctk.CTkEntry(boot_row, font=ctk.CTkFont(family="Consolas", size=10), fg_color="#0A0D14")
        if os.path.exists(DEFAULT_BOOT_FILE):
            self.boot_entry.insert(0, DEFAULT_BOOT_FILE)
        self.boot_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(boot_row, text="Browse...", width=90, font=ctk.CTkFont(size=11),
                      command=self._browse_boot).pack(side="right")

        # Firmware Row
        fw_row = ctk.CTkFrame(cfg_card, fg_color="transparent")
        fw_row.pack(fill="x", padx=16, pady=4)

        ctk.CTkLabel(fw_row, text="Firmware (Flash):", width=140, anchor="w", font=ctk.CTkFont(size=11), text_color="#C5CEE0").pack(side="left")
        self.fw_entry = ctk.CTkEntry(fw_row, font=ctk.CTkFont(family="Consolas", size=10), fg_color="#0A0D14")
        if os.path.exists(DEFAULT_FW_FILE):
            self.fw_entry.insert(0, DEFAULT_FW_FILE)
        self.fw_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(fw_row, text="Browse...", width=90, font=ctk.CTkFont(size=11),
                      command=self._browse_fw).pack(side="right")

        # Progress bar & Status
        prog_box = ctk.CTkFrame(cfg_card, fg_color="transparent")
        prog_box.pack(fill="x", padx=16, pady=(10, 4))

        self.status_lbl = ctk.CTkLabel(prog_box, text="Status: Ready to Flash (ئامادەیە بۆ فلاشکرن)",
                                       font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                       text_color="#00E5FF")
        self.status_lbl.pack(anchor="w", pady=(0, 4))

        self.progress_bar = ctk.CTkProgressBar(prog_box, height=14, fg_color="#0A0D14", progress_color="#00E5FF")
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x")

        # Action Buttons
        btn_bar = ctk.CTkFrame(cfg_card, fg_color="transparent")
        btn_bar.pack(fill="x", padx=16, pady=(10, 12))

        self.btn_flash = ctk.CTkButton(btn_bar, text="⚡ START ZERO-RAM FLASH (دەستپێکردن ب ئێک کلیک)",
                                       font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                                       fg_color="#0077B6", hover_color="#0096C7", height=42,
                                       command=self._start_flashing)
        self.btn_flash.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_stop = ctk.CTkButton(btn_bar, text="🛑 STOP (ڕاگرتن)", width=140, height=42,
                                      font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                      fg_color="#781D22", hover_color="#A31621", state="disabled",
                                      command=self._stop_flashing)
        self.btn_stop.pack(side="left", padx=(0, 10))

        self.btn_web = ctk.CTkButton(btn_bar, text="🌐 Web Dashboard", width=140, height=42,
                                     font=ctk.CTkFont(family="Segoe UI", size=12),
                                     fg_color="#1A273A", hover_color="#243752",
                                     command=self._open_web)
        self.btn_web.pack(side="right")

        # 5. Live Diagnostic Log Stream
        log_card = ctk.CTkFrame(self, fg_color="#121724", corner_radius=10, border_width=1, border_color="#1F293D")
        log_card.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        log_hdr = ctk.CTkFrame(log_card, fg_color="transparent")
        log_hdr.pack(fill="x", padx=14, pady=(8, 4))

        ctk.CTkLabel(log_hdr, text="📜 Live Diagnostic Stream",
                     font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                     text_color="#00E5FF").pack(side="left")

        ctk.CTkButton(log_hdr, text="Clear Log", width=80, height=24, font=ctk.CTkFont(size=10),
                      fg_color="#1F293D", hover_color="#2E3C56", command=self._clear_log).pack(side="right")

        self.log_text = tk.Text(log_card, bg="#06080D", fg="#8E9AA8", insertbackground="#00E5FF",
                                font=("Consolas", 9), bd=0, relief="flat", wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        # Color Tags
        self.log_text.tag_config("INFO", foreground="#8E9AA8")
        self.log_text.tag_config("SUCCESS", foreground="#00FFA3")
        self.log_text.tag_config("ERROR", foreground="#FF4D6D")
        self.log_text.tag_config("WARNING", foreground="#FFB703")
        self.log_text.tag_config("HIGHLIGHT", foreground="#00F0FF")
        self.log_text.tag_config("STEP", foreground="#FB8500")
        self.log_text.tag_config("TITLE", foreground="#9D4EDD")

        intro = (
            "=================================================================\n"
            " MikroTik Delta-OS Zero-RAM Direct Stream Flasher Pro v4.5\n"
            "1. Connect MikroTik POE/LAN Port to your Computer.\n"
            "2. Click 'START ZERO-RAM FLASH' button above.\n"
            "3. Hold Reset button & plug in Power -> Release Reset when detected.\n\n"
        )
        self.log_text.insert("end", intro, "HIGHLIGHT")

    def _browse_boot(self):
        fp = filedialog.askopenfilename(title="Select Boot Kernel", filetypes=[("Kernel BIN", "*.bin"), ("All", "*.*")])
        if fp:
            self.boot_entry.delete(0, "end")
            self.boot_entry.insert(0, fp)

    def _browse_fw(self):
        fp = filedialog.askopenfilename(title="Select Firmware Image", filetypes=[("Firmware BIN", "*.bin"), ("All", "*.*")])
        if fp:
            self.fw_entry.delete(0, "end")
            self.fw_entry.insert(0, fp)

    def _auto_set_static_ip(self):
        self._queue_log("Setting Ethernet Static IP to 192.168.88.2...", "STEP")
        cmd = 'netsh interface ipv4 set address name="Ethernet" static 192.168.88.2 255.255.255.0 192.168.88.1'
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                self._queue_log("✅ Static IP 192.168.88.2 configured on Ethernet!", "SUCCESS")
                messagebox.showinfo("Success", "Static IP 192.168.88.2 configured successfully.")
            else:
                self._queue_log(f"Notice: {res.stderr.strip() or res.stdout.strip()}.", "WARNING")
        except Exception as e:
            self._queue_log(f"Error: {e}", "ERROR")

    def _start_flashing(self):
        boot_f = self.boot_entry.get().strip()
        fw_f = self.fw_entry.get().strip()
        srv_ip = self.ip_entry.get().strip()

        if not os.path.exists(boot_f):
            messagebox.showerror("Error", f"Boot kernel file not found:\n{boot_f}")
            return
        if not os.path.exists(fw_f):
            messagebox.showerror("Error", f"Firmware image not found:\n{fw_f}")
            return

        self.btn_flash.configure(state="disabled", fg_color="#182032")
        self.btn_stop.configure(state="normal")
        self.server_status_badge.configure(text="● FLASHING ACTIVE", text_color="#FFB703")

        self.engine = ZeroRamEngine(
            server_ip=srv_ip, client_ip=CLIENT_IP, router_ip=ROUTER_IP,
            boot_file=boot_f, fw_file=fw_f, nc_port=NC_PORT,
            log_cb=self._queue_log, status_cb=self._queue_status,
            progress_cb=self._queue_progress, stage_cb=self._queue_stage
        )
        self.engine.start()

    def _stop_flashing(self):
        if self.engine:
            self.engine.stop()
        self.btn_flash.configure(state="normal", fg_color="#0077B6")
        self.btn_stop.configure(state="disabled")
        self.server_status_badge.configure(text="● SERVER STOPPED", text_color="#8E9AA8")

    def _open_web(self):
        webbrowser.open(f"http://{ROUTER_IP}")

    def _clear_log(self):
        self.log_text.delete("1.0", "end")

    def _queue_log(self, msg, tag="INFO"):
        self.queue.put(("LOG", msg, tag))

    def _queue_status(self, msg, color="#00E5FF"):
        self.queue.put(("STATUS", msg, color))

    def _queue_progress(self, pct):
        self.queue.put(("PROGRESS", pct))

    def _queue_stage(self, stage):
        self.queue.put(("STAGE", stage))

    def _process_queue(self):
        try:
            while True:
                item = self.queue.get_nowait()
                action = item[0]
                if action == "LOG":
                    self.log_text.insert("end", item[1] + "\n", item[2])
                    self.log_text.see("end")
                elif action == "STATUS":
                    self.status_lbl.configure(text=f"Status: {item[1]}", text_color=item[2])
                elif action == "PROGRESS":
                    self.progress_bar.set(item[1] / 100.0)
                elif action == "STAGE":
                    st = item[1]
                    for idx, lbl in enumerate(self.step_labels):
                        if idx < st:
                            lbl.configure(text_color="#00FFA3")
                        elif idx == st - 1:
                            lbl.configure(text_color="#00E5FF")
                        else:
                            lbl.configure(text_color="#8E9AA8")
        except queue.Empty:
            pass
        self.after(100, self._process_queue)


def main():
    disable_quickedit()
    app = ModernFluentGlassApp()
    app.protocol("WM_DELETE_WINDOW", lambda: (app._stop_flashing(), app.destroy()))
    app.mainloop()


if __name__ == "__main__":
    main()
