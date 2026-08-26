import subprocess, time

script = """
DEV="wlan0"
[ -d /sys/class/net/pppoe-wan ] && DEV="pppoe-wan"
RX0=$(cat /sys/class/net/$DEV/statistics/rx_bytes 2>/dev/null || echo 0)
T0=$(date +%s)
wget --no-check-certificate -q -O /dev/null "https://speed.cloudflare.com/__down?bytes=5000000"
T1=$(date +%s)
RX1=$(cat /sys/class/net/$DEV/statistics/rx_bytes 2>/dev/null || echo 0)
BYTES=$((RX1 - RX0))
DT=$((T1 - T0))
[ "$DT" -lt 1 ] && DT=1
MBPS=$(awk -v b="$BYTES" -v s="$DT" 'BEGIN{ printf "%.2f", (b * 8) / (s * 1000000) }')
echo "DEV:$DEV BYTES:$BYTES ELAPSED:${DT}s MBPS:$MBPS"
"""

p = subprocess.run(['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-o', 'LogLevel=ERROR', 'root@192.168.88.1', script], capture_output=True, text=True)
print(p.stdout)
