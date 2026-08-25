import subprocess

# Read from router
p = subprocess.run(['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-o', 'LogLevel=ERROR', 'root@192.168.88.1', 'cat /usr/share/hostap/common.uc'], capture_output=True, text=True)
with open('common.uc', 'w', encoding='utf-8') as f:
    f.write(p.stdout)
print(f"Saved common.uc ({len(p.stdout)} bytes)")

# Copy into WSL OpenWrt source and rootfs overlay
cmd = 'cp "/mnt/c/Users/Malta Computer/Desktop/mikrotik/common.uc" /home/ubuntu/openwrt/package/network/services/hostapd/files/common.uc && mkdir -p /home/ubuntu/openwrt/files/usr/share/hostap && cp "/mnt/c/Users/Malta Computer/Desktop/mikrotik/common.uc" /home/ubuntu/openwrt/files/usr/share/hostap/common.uc'
subprocess.run(['wsl', 'bash', '-c', cmd])
print("Permanently integrated into OpenWrt build source and files overlay!")
