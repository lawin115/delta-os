import re

# 1. Fix api.cgi
with open('api.cgi', 'r', encoding='utf-8') as f:
    api = f.read()

# Remove dangerous mount remount 52M
api = api.replace('mount -o remount,size=52M /tmp >/dev/null 2>&1\n', '')
api = api.replace('mount -o remount,size=52M /tmp >/dev/null 2>&1', '')

with open('api.cgi', 'w', encoding='utf-8', newline='\n') as f:
    f.write(api)

# 2. Fix mikrotik-leds.sh (eliminate wifi reload loop)
with open('mikrotik-leds.sh', 'r', encoding='utf-8') as f:
    leds = f.read()

old_wifi_reload_loop = """        # 3. Every 16 seconds thereafter until connected:
        if [ "$DISCONN_TICKS" -gt 12 ] && [ $((DISCONN_TICKS % 16)) -eq 0 ]; then
            /sbin/wifi reload >/dev/null 2>&1
        fi"""

new_wifi_reload_safe = """        # 3. Disconnected state: do not spam wifi reload to prevent kernel crash
        if [ "$DISCONN_TICKS" -eq 30 ]; then
            # Soft trigger single rescan once after 30s
            iw dev "$IFACE" scan >/dev/null 2>&1 &
        fi"""

if old_wifi_reload_loop in leds:
    leds = leds.replace(old_wifi_reload_loop, new_wifi_reload_safe)
else:
    # generic regex replace for any wifi reload inside loop
    leds = re.sub(r'if \[ "\$DISCONN_TICKS" -gt 12 \].*?/sbin/wifi reload >/dev/null 2>&1\s+fi', new_wifi_reload_safe, leds, flags=re.DOTALL)

with open('mikrotik-leds.sh', 'w', encoding='utf-8', newline='\n') as f:
    f.write(leds)

print("System stability fixes successfully applied!")
