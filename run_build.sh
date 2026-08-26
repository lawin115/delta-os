#!/bin/bash
set -e

# Fix WSL space in Windows PATH causing find -execdir security error
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

cd /home/ubuntu/openwrt

echo "=============================================="
echo "  Delta OS - Starting OpenWrt Firmware Build"
echo "=============================================="

# 1. Sync custom files
bash "/mnt/c/Users/Malta Computer/Desktop/mikrotik/sync_files.sh"

# 2. Force fresh rebuild of initramfs kernel so new files/ are embedded into openwrt.bin
echo "[*] Cleaning old initramfs cache to ensure fresh embedding..."
rm -f build_dir/target-mips_24kc_musl/linux-ath79_mikrotik/vmlinux-initramfs* 2>/dev/null || true
rm -rf build_dir/target-mips_24kc_musl/root-ath79 2>/dev/null || true
rm -f bin/targets/ath79/mikrotik/*initramfs* 2>/dev/null || true
rm -f bin/targets/ath79/mikrotik/*sysupgrade* 2>/dev/null || true

# 3. Compile OpenWrt
echo "[*] Building OpenWrt with $(nproc) cores..."
make -j$(nproc)

echo "=============================================="
echo "  Build Finished! Copying images..."
echo "=============================================="

MIKROTIK_WIN="/mnt/c/Users/Malta Computer/Desktop/mikrotik"
mkdir -p "$MIKROTIK_WIN"

# Copy all device binaries
cp -fv bin/targets/ath79/mikrotik/* "$MIKROTIK_WIN/" 2>/dev/null || true

# Explicitly copy LHG 5nD / RouterBOARD images to openwrt.bin and sysupgrade.bin
if [ -f "bin/targets/ath79/mikrotik/openwrt-ath79-mikrotik-mikrotik_routerboard-lhg-5nd-initramfs-kernel.bin" ]; then
    cp -fv "bin/targets/ath79/mikrotik/openwrt-ath79-mikrotik-mikrotik_routerboard-lhg-5nd-initramfs-kernel.bin" "$MIKROTIK_WIN/openwrt.bin"
fi

if [ -f "bin/targets/ath79/mikrotik/openwrt-ath79-mikrotik-mikrotik_routerboard-lhg-5nd-squashfs-sysupgrade.bin" ]; then
    cp -fv "bin/targets/ath79/mikrotik/openwrt-ath79-mikrotik-mikrotik_routerboard-lhg-5nd-squashfs-sysupgrade.bin" "$MIKROTIK_WIN/sysupgrade.bin"
fi

echo "=== FIRMWARE BUILD & DEPLOY COMPLETED SUCCESSFULLY ==="
ls -lh "$MIKROTIK_WIN"/openwrt.bin "$MIKROTIK_WIN"/sysupgrade.bin
