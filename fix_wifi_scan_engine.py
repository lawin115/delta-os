import re

with open('api.cgi', 'r', encoding='utf-8') as f:
    api = f.read()

# Replace wifi_scan block in api.cgi
old_scan_pattern = r'    wifi_scan\).*?echo "\$SCAN_RAW" \| awk \''

new_scan_head = """    wifi_scan)
        WDEV=$(iw dev 2>/dev/null | awk '$1 == "Interface" {print $2; exit}')
        [ -z "$WDEV" ] && WDEV="wlan0"
        
        ip link set "$WDEV" up 2>/dev/null
        
        # Trigger fast active multi-channel survey scan across 5GHz band
        iw dev "$WDEV" scan freq 5180 5200 5220 5240 5260 5280 5300 5320 5500 5505 5520 5540 5560 5575 5580 5600 5620 5640 5660 5680 5700 5720 5745 5765 5785 5805 5825 5845 5865 2>/dev/null || iw dev "$WDEV" scan 2>/dev/null || true
        
        # Read full live BSS table
        SCAN_RAW=$(iw dev "$WDEV" scan dump 2>/dev/null)
        [ -z "$SCAN_RAW" ] && SCAN_RAW=$(iw dev "$WDEV" scan 2>/dev/null)

        echo "$SCAN_RAW" | awk '"""

api = re.sub(old_scan_pattern, new_scan_head, api, flags=re.DOTALL)

with open('api.cgi', 'w', encoding='utf-8', newline='\n') as f:
    f.write(api)

print("Active 5GHz Site Survey scanner successfully updated in api.cgi!")
