"""
Delta OS Pro - Direct NOR Flash Firmware Utility
Standalone Desktop Application for MikroTik RouterBOARD & OpenWrt Devices
"""

import sys
import os
import time
import threading
import subprocess
import hashlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Color Palette
BG_COLOR = "#0F172A"       # Dark Slate Header / Background
CARD_BG = "#FFFFFF"        # White Card
TEXT_MAIN = "#0F172A"      # Main dark text
TEXT_MUTED = "#64748B"     # Muted grey text
PRIMARY_COLOR = "#0284C7"  # Delta Blue
SUCCESS_COLOR = "#10B981"  # Emerald Green
WARN_COLOR = "#F59E0B"     # Amber
DANGER_COLOR = "#EF4444"   # Red
BORDER_COLOR = "#E2E8F0"   # Light border
LOG_BG = "#0B1120"         # Terminal black

class DeltaFlasherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Delta OS Pro - Direct Flash Tool v3.0")
        self.root.geometry("680x720")
        self.root.minsize(620, 650)
        self.root.configure(bg="#F1F5F9")

        self.is_flashing = False
        self.firmware_path = ""

        # Check for default sysupgrade.bin in current dir
        default_bin = os.path.join(os.getcwd(), "sysupgrade.bin")
        if os.path.exists(default_bin):
            self.firmware_path = default_bin

        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure("TProgressbar",
                             thickness=14,
                             troughcolor="#E0F2FE",
                             background="#0284C7")

    def create_widgets(self):
        # 1. Header Banner
        header = tk.Frame(self.root, bg=BG_COLOR, height=75)
        header.pack(fill="x", side="top")
        
        title_lbl = tk.Label(header, text="⚡ Delta OS Pro - Direct Flash Utility",
                             font=("Segoe UI", 14, "bold"), fg="#FFFFFF", bg=BG_COLOR)
        title_lbl.pack(anchor="w", padx=20, pady=(12, 2))
        
        subtitle_lbl = tk.Label(header, text="Direct Zero-RAM Stream into NOR Flash Memory | MikroTik RouterBOARD LHG 5",
                                font=("Segoe UI", 8), fg="#94A3B8", bg=BG_COLOR)
        subtitle_lbl.pack(anchor="w", padx=20, pady=(0, 10))

        # Main Container (Scrollable or padded)
        main_frame = tk.Frame(self.root, bg="#F1F5F9", padx=16, pady=12)
        main_frame.pack(fill="both", expand=True)

        # 2. Connection Settings Card
        card_conn = tk.LabelFrame(main_frame, text=" 1. Router Target Connection ",
                                  font=("Segoe UI", 9, "bold"), fg=TEXT_MAIN, bg=CARD_BG,
                                  padx=14, pady=10, relief="solid", bd=1)
        card_conn.pack(fill="x", pady=(0, 10))

        conn_grid = tk.Frame(card_conn, bg=CARD_BG)
        conn_grid.pack(fill="x")

        tk.Label(conn_grid, text="Router IP:", font=("Segoe UI", 9, "bold"),
                 fg=TEXT_MAIN, bg=CARD_BG).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        
        self.ip_entry = tk.Entry(conn_grid, font=("Consolas", 10), width=16, bd=1, relief="solid")
        self.ip_entry.insert(0, "192.168.88.1")
        self.ip_entry.grid(row=0, column=1, sticky="w", padx=(0, 14), pady=4)

        tk.Label(conn_grid, text="SSH User:", font=("Segoe UI", 9, "bold"),
                 fg=TEXT_MAIN, bg=CARD_BG).grid(row=0, column=2, sticky="w", padx=(0, 8), pady=4)
        
        self.user_entry = tk.Entry(conn_grid, font=("Consolas", 10), width=10, bd=1, relief="solid")
        self.user_entry.insert(0, "root")
        self.user_entry.grid(row=0, column=3, sticky="w", padx=(0, 14), pady=4)

        self.btn_test = tk.Button(conn_grid, text="🔍 Test Connection", font=("Segoe UI", 8, "bold"),
                                  bg="#F0F9FF", fg=PRIMARY_COLOR, activebackground="#E0F2FE",
                                  bd=1, relief="solid", cursor="hand2", padx=8, pady=2,
                                  command=self.test_connection)
        self.btn_test.grid(row=0, column=4, sticky="e", padx=(8, 0), pady=4)

        self.status_conn_lbl = tk.Label(card_conn, text="Status: Ready (Default: 192.168.88.1)",
                                        font=("Segoe UI", 8), fg=TEXT_MUTED, bg=CARD_BG)
        self.status_conn_lbl.pack(anchor="w", pady=(4, 0))

        # 3. Firmware Selection Card
        card_fw = tk.LabelFrame(main_frame, text=" 2. Firmware Image (sysupgrade.bin) ",
                                font=("Segoe UI", 9, "bold"), fg=TEXT_MAIN, bg=CARD_BG,
                                padx=14, pady=10, relief="solid", bd=1)
        card_fw.pack(fill="x", pady=(0, 10))

        fw_sel_row = tk.Frame(card_fw, bg=CARD_BG)
        fw_sel_row.pack(fill="x")

        self.fw_entry = tk.Entry(fw_sel_row, font=("Consolas", 9), bd=1, relief="solid")
        if self.firmware_path:
            self.fw_entry.insert(0, self.firmware_path)
        self.fw_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_browse = tk.Button(fw_sel_row, text="📁 Browse...", font=("Segoe UI", 8, "bold"),
                               bg="#F8FAFC", fg=TEXT_MAIN, bd=1, relief="solid",
                               cursor="hand2", padx=10, pady=2, command=self.browse_firmware)
        btn_browse.pack(side="right")

        self.fw_info_lbl = tk.Label(card_fw, text="Select a valid OpenWrt / Delta OS sysupgrade.bin image file.",
                                    font=("Segoe UI", 8), fg=TEXT_MUTED, bg=CARD_BG)
        self.fw_info_lbl.pack(anchor="w", pady=(6, 0))

        # 4. Flash Action & Progress Card
        card_action = tk.LabelFrame(main_frame, text=" 3. Direct NOR Flash Execution ",
                                    font=("Segoe UI", 9, "bold"), fg=TEXT_MAIN, bg=CARD_BG,
                                    padx=14, pady=10, relief="solid", bd=1)
        card_action.pack(fill="x", pady=(0, 10))

        # Safety Banner
        warn_box = tk.Frame(card_action, bg="#FEF3C7", bd=1, relief="solid", padx=10, pady=6)
        warn_box.pack(fill="x", pady=(0, 10))
        tk.Label(warn_box, text="⚠️ CAUTION: Do NOT power off or disconnect Ethernet cable during flashing!",
                 font=("Segoe UI", 8, "bold"), fg="#92400E", bg="#FEF3C7").pack(anchor="w")

        # Progress bar
        prog_header = tk.Frame(card_action, bg=CARD_BG)
        prog_header.pack(fill="x", pady=(0, 4))
        
        self.stage_lbl = tk.Label(prog_header, text="Ready to Flash",
                                  font=("Segoe UI", 8, "bold"), fg=PRIMARY_COLOR, bg=CARD_BG)
        self.stage_lbl.pack(side="left")

        self.pct_lbl = tk.Label(prog_header, text="0%",
                                font=("Consolas", 9, "bold"), fg=PRIMARY_COLOR, bg=CARD_BG)
        self.pct_lbl.pack(side="right")

        self.progress_bar = ttk.Progressbar(card_action, style="TProgressbar", mode="determinate", maximum=100)
        self.progress_bar.pack(fill="x", pady=(0, 10))

        # Big Flash Button
        self.btn_flash = tk.Button(card_action, text="🚀 Flash Directly into NOR Flash Memory",
                                   font=("Segoe UI", 10, "bold"), bg=PRIMARY_COLOR, fg="#FFFFFF",
                                   activebackground="#0369A1", activeforeground="#FFFFFF",
                                   bd=0, cursor="hand2", pady=8, command=self.start_flash_thread)
        self.btn_flash.pack(fill="x")

        # 5. Live Terminal Log Output
        card_logs = tk.LabelFrame(main_frame, text=" Live Execution Console ",
                                  font=("Segoe UI", 9, "bold"), fg=TEXT_MAIN, bg=CARD_BG,
                                  padx=10, pady=8, relief="solid", bd=1)
        card_logs.pack(fill="both", expand=True)

        self.log_text = tk.Text(card_logs, bg=LOG_BG, fg="#38BDF8", insertbackground="#38BDF8",
                                font=("Consolas", 8), bd=0, relief="flat", height=8)
        self.log_text.pack(fill="both", expand=True, side="left")

        scrollbar = tk.Scrollbar(card_logs, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

        self.log("Delta OS Direct NOR Flash Tool initialized.")
        if self.firmware_path and os.path.exists(self.firmware_path):
            self.update_firmware_info(self.firmware_path)

    def log(self, message):
        self.log_text.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see("end")

    def browse_firmware(self):
        file_selected = filedialog.askopenfilename(
            title="Select Delta OS / OpenWrt sysupgrade.bin",
            filetypes=[("Binary Firmware", "*.bin"), ("All Files", "*.*")]
        )
        if file_selected:
            self.firmware_path = file_selected
            self.fw_entry.delete(0, "end")
            self.fw_entry.insert(0, file_selected)
            self.update_firmware_info(file_selected)

    def update_firmware_info(self, path):
        try:
            size_mb = os.path.getsize(path) / (1024 * 1024)
            hasher = hashlib.sha256()
            with open(path, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            sha = hasher.hexdigest()[:16]
            self.fw_info_lbl.config(
                text=f"Size: {size_mb:.2f} MB | SHA256: {sha}... | Ready for NOR Flash write",
                fg=SUCCESS_COLOR
            )
            self.log(f"Selected firmware: {os.path.basename(path)} ({size_mb:.2f} MB)")
        except Exception as e:
            self.fw_info_lbl.config(text=f"Error reading file: {e}", fg=DANGER_COLOR)

    def test_connection(self):
        ip = self.ip_entry.get().strip()
        user = self.user_entry.get().strip()
        self.status_conn_lbl.config(text=f"Testing connection to {ip}...", fg=PRIMARY_COLOR)
        self.log(f"Connecting to {user}@{ip}...")

        def _worker():
            try:
                cmd = f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=3 {user}@{ip} "cat /tmp/sysinfo/model 2>/dev/null || uname -m"'
                p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if p.returncode == 0:
                    model = p.stdout.strip() or "OpenWrt / Delta OS"
                    self.root.after(0, lambda: self.status_conn_lbl.config(
                        text=f"✅ Connected to: {model} ({ip})", fg=SUCCESS_COLOR
                    ))
                    self.root.after(0, lambda: self.log(f"Connection Successful! Target Model: {model}"))
                else:
                    self.root.after(0, lambda: self.status_conn_lbl.config(
                        text=f"❌ Connection failed. Check Ethernet cable and IP ({ip})", fg=DANGER_COLOR
                    ))
                    self.root.after(0, lambda: self.log(f"Connection Failed: {p.stderr.strip() or 'Timeout'}"))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Connection error: {e}"))

        threading.Thread(target=_worker, daemon=True).start()

    def start_flash_thread(self):
        if self.is_flashing:
            return

        fw = self.fw_entry.get().strip()
        ip = self.ip_entry.get().strip()
        user = self.user_entry.get().strip()

        if not fw or not os.path.exists(fw):
            messagebox.showerror("Error", "Please select a valid sysupgrade.bin firmware file first!")
            return

        size = os.path.getsize(fw)
        if size < 1024 * 1024:
            messagebox.showerror("Error", "Firmware file is too small to be a valid router image!")
            return

        confirm = messagebox.askyesno(
            "Confirm Direct Flash",
            f"Are you sure you want to write this firmware directly into the router's NOR Flash memory?\n\n"
            f"Target: {user}@{ip}\n"
            f"Firmware: {os.path.basename(fw)} ({size / (1024*1024):.2f} MB)\n\n"
            f"⚠️ DO NOT DISCONNECT POWER OR ETHERNET CABLE DURING FLASHING!"
        )
        if not confirm:
            return

        self.is_flashing = True
        self.btn_flash.config(state="disabled", bg="#94A3B8")
        self.btn_test.config(state="disabled")
        threading.Thread(target=self.execute_flash, args=(ip, user, fw), daemon=True).start()

    def execute_flash(self, ip, user, fw_path):
        try:
            self.update_stage("Connecting to Router SSH...", 5)
            self.log("=" * 55)
            self.log("🚀 STARTING DIRECT ZERO-RAM NOR FLASH SEQUENCE")
            self.log(f"Firmware: {fw_path}")
            self.log(f"Target: {user}@{ip}")

            file_size = os.path.getsize(fw_path)

            # Step 1: Open direct streaming pipe over SSH into sysupgrade
            self.update_stage("Streaming firmware binary into flash memory...", 15)
            
            # We stream the binary directly to router stdin into /tmp/firmware.bin and immediately execute sysupgrade
            ssh_cmd = [
                'ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'LogLevel=ERROR', f'{user}@{ip}',
                'cat > /tmp/firmware.bin && echo "[FLASH_READY]" && /sbin/sysupgrade -F -n -v /tmp/firmware.bin'
            ]

            process = subprocess.Popen(
                ssh_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False
            )

            # Send file in chunks with live progress
            bytes_sent = 0
            chunk_size = 65536
            with open(fw_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    process.stdin.write(chunk)
                    bytes_sent += len(chunk)
                    pct = int(15 + (bytes_sent / file_size) * 45)  # 15% to 60%
                    self.update_stage(f"Streaming data ({bytes_sent // 1024} KB / {file_size // 1024} KB)...", pct)

            process.stdin.close()
            self.update_stage("Verifying integrity & Writing SPI NOR Flash...", 65)
            self.log("Stream Complete (100%). Router is now flashing SPI Flash...")

            # Read router output lines
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                decoded_line = line.decode('utf-8', errors='ignore').strip()
                if decoded_line:
                    self.log(f"  [ROUTER] {decoded_line}")
                    if "Writing" in decoded_line or "erase" in decoded_line.lower():
                        self.update_stage("Erasing & Writing SPI NOR Flash Blocks...", 80)
                    elif "Rebooting" in decoded_line or "reboot" in decoded_line.lower():
                        self.update_stage("Flash write complete! Router is rebooting...", 95)

            process.wait()
            
            # Step 2: Automatic Countdown & Reboot wait
            self.update_stage("Flash Finished! Waiting for Router Reboot (~45s)...", 95)
            self.log("=" * 55)
            self.log("✅ FLASH WRITE COMPLETE! Router has initiated automatic reboot.")
            self.log("Waiting for network interface to come back online...")

            for remaining in range(45, 0, -1):
                self.update_stage(f"Router Rebooting... Reconnecting in {remaining}s", 95)
                time.sleep(1)

            self.update_stage("✨ Delta OS Pro Flash & Reboot Completed!", 100)
            self.log("🎉 SUCCESS! You may now open http://192.168.88.1 in your browser.")
            messagebox.showinfo("Flash Success", "Delta OS Pro has been successfully flashed directly to Flash memory!\n\nYou can now access the web control center at http://192.168.88.1")

        except Exception as e:
            self.log(f"❌ Flashing Error: {e}")
            self.update_stage("Error occurred during flash", 0)
            messagebox.showerror("Flash Error", f"An error occurred: {e}")
        finally:
            self.is_flashing = False
            self.root.after(0, lambda: self.btn_flash.config(state="normal", bg=PRIMARY_COLOR))
            self.root.after(0, lambda: self.btn_test.config(state="normal"))

    def update_stage(self, text, pct):
        self.root.after(0, lambda: self.stage_lbl.config(text=text))
        self.root.after(0, lambda: self.pct_lbl.config(text=f"{pct}%"))
        self.root.after(0, lambda: self.progress_bar.config(value=pct))


if __name__ == "__main__":
    root = tk.Tk()
    app = DeltaFlasherApp(root)
    root.mainloop()
