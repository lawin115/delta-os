#!/bin/bash
set -e
WIN_DIR="/mnt/c/Users/delta/Desktop/mikrotik"
OPENWRT_DIR="/home/ubuntu/openwrt"

mkdir -p "$OPENWRT_DIR/files/etc/config"
mkdir -p "$OPENWRT_DIR/files/etc/delta"
mkdir -p "$OPENWRT_DIR/files/etc/init.d"
mkdir -p "$OPENWRT_DIR/files/etc/rc.d"
mkdir -p "$OPENWRT_DIR/files/usr/sbin"
mkdir -p "$OPENWRT_DIR/files/www/cgi-bin"
mkdir -p "$OPENWRT_DIR/files/www/client"

# 1. Copy Web Interface & APIs
cp -fv "$WIN_DIR/index.html" "$OPENWRT_DIR/files/www/index.html"
cp -fv "$WIN_DIR/client.html" "$OPENWRT_DIR/files/www/client.html"
cp -fv "$WIN_DIR/client.html" "$OPENWRT_DIR/files/www/client/index.html"
cp -fv "$WIN_DIR/api.cgi" "$OPENWRT_DIR/files/www/api.cgi"
cp -fv "$WIN_DIR/api.cgi" "$OPENWRT_DIR/files/www/cgi-bin/api.cgi"
chmod +x "$OPENWRT_DIR/files/www/api.cgi" "$OPENWRT_DIR/files/www/cgi-bin/api.cgi"
cp -fv "$WIN_DIR/favicon.png" "$OPENWRT_DIR/files/www/favicon.png"
cp -fv "$WIN_DIR/version.json" "$OPENWRT_DIR/files/www/version.json"

# 2. Copy Network, Wireless, Firewall & DHCP Configs
cp -fv "$WIN_DIR/network.config" "$OPENWRT_DIR/files/etc/config/network"
cp -fv "$WIN_DIR/wireless.config" "$OPENWRT_DIR/files/etc/config/wireless"
cp -fv "$WIN_DIR/firewall.config" "$OPENWRT_DIR/files/etc/config/firewall"
cp -fv "$WIN_DIR/dhcp.config" "$OPENWRT_DIR/files/etc/config/dhcp"
cp -fv "$WIN_DIR/network.config" "$OPENWRT_DIR/files/etc/delta/network.config"
cp -fv "$WIN_DIR/wireless.config" "$OPENWRT_DIR/files/etc/delta/wireless.config"
cp -fv "$WIN_DIR/firewall.config" "$OPENWRT_DIR/files/etc/delta/firewall.config"
cp -fv "$WIN_DIR/dhcp.config" "$OPENWRT_DIR/files/etc/delta/dhcp.config"

# 3. Copy LED Service & Scripts
cp -fv "$WIN_DIR/mikrotik-leds.init" "$OPENWRT_DIR/files/etc/init.d/mikrotik-leds"
chmod +x "$OPENWRT_DIR/files/etc/init.d/mikrotik-leds"
cp -fv "$WIN_DIR/mikrotik-leds.sh" "$OPENWRT_DIR/files/etc/mikrotik-leds.sh"
cp -fv "$WIN_DIR/mikrotik-leds.sh" "$OPENWRT_DIR/files/usr/sbin/mikrotik-leds"
chmod +x "$OPENWRT_DIR/files/etc/mikrotik-leds.sh" "$OPENWRT_DIR/files/usr/sbin/mikrotik-leds"
ln -sf ../init.d/mikrotik-leds "$OPENWRT_DIR/files/etc/rc.d/S99mikrotik-leds"

# 3.1 Copy Persistent Config Service
cp -fv "$WIN_DIR/persistent_config.init" "$OPENWRT_DIR/files/etc/init.d/persistent_config"
chmod +x "$OPENWRT_DIR/files/etc/init.d/persistent_config"
ln -sf ../init.d/persistent_config "$OPENWRT_DIR/files/etc/rc.d/S12persistent_config"

# 3.2 Copy MNDP Daemon (MikroTik WinBox Discovery)
cp -fv "$WIN_DIR/mndpd" "$OPENWRT_DIR/files/usr/sbin/mndpd"
chmod +x "$OPENWRT_DIR/files/usr/sbin/mndpd"
cp -fv "$WIN_DIR/mndpd.init" "$OPENWRT_DIR/files/etc/init.d/mndpd"
chmod +x "$OPENWRT_DIR/files/etc/init.d/mndpd"
ln -sf ../init.d/mndpd "$OPENWRT_DIR/files/etc/rc.d/S95mndpd"

# 4. Fast Preinit & DTS
mkdir -p "$OPENWRT_DIR/files/lib/preinit"
cp -fv "$WIN_DIR/00_preinit.conf" "$OPENWRT_DIR/files/lib/preinit/00_preinit.conf"
cp -fv "$WIN_DIR/01_user_led" "$OPENWRT_DIR/files/lib/preinit/01_user_led"
chmod +x "$OPENWRT_DIR/files/lib/preinit/01_user_led"
cp -fv "$WIN_DIR/ar9344_mikrotik_routerboard-lhg-5nd.dts" "$OPENWRT_DIR/target/linux/ath79/dts/ar9344_mikrotik_routerboard-lhg-5nd.dts"

# 5. Copy Banner & System rc.local
cp -fv "$WIN_DIR/banner" "$OPENWRT_DIR/files/etc/banner"
chmod +x "$OPENWRT_DIR/files/etc/banner"
echo "v2.6" > "$OPENWRT_DIR/files/etc/delta_version"

cat > "$OPENWRT_DIR/files/etc/rc.local" << 'EOF'
# Turn off user LED immediately when boot completes (Solid -> OFF)
for u in /sys/class/leds/*user; do
    [ -d "$u" ] && { echo none > "$u/trigger" 2>/dev/null; echo 0 > "$u/brightness" 2>/dev/null; }
done

exit 0
EOF
# 6. Copy Superchannel ath9k patches
mkdir -p "$OPENWRT_DIR/package/kernel/mac80211/patches/ath"
cp -fv "$WIN_DIR/407-mikrotik-eeprom-accept-all.patch" "$OPENWRT_DIR/package/kernel/mac80211/patches/ath/"
cp -fv "$WIN_DIR/408-ath9k-superchannel-5mhz-steps.patch" "$OPENWRT_DIR/package/kernel/mac80211/patches/ath/"

echo "=== ALL CUSTOM FILES COPIED AND CONFIGURED SUCCESSFULLY ==="
