#!/bin/sh
# MikroTik SXT Dynamic LED Manager
# Controls the power LED and the five RSSI signal-bar LEDs.
#
# The live board is the LHG 5nD NOR variant.  Its real green:lan LED is on
# GPIO14.  LAN state is handled below from the carrier and byte counters so
# the behavior is deterministic on this board.

# Single-instance lock - kill previous copies before running
LOCK_FILE="/var/run/mikrotik-leds.pid"
if [ -f "$LOCK_FILE" ]; then
    OLD_PID=$(cat "$LOCK_FILE" 2>/dev/null)
    [ -n "$OLD_PID" ] && kill -9 "$OLD_PID" 2>/dev/null
fi
echo $$ > "$LOCK_FILE"

LED_DIR="/sys/class/leds"

# 1. Power LED: Solid ON
[ -d "$LED_DIR/blue:power" ] && echo 1 > "$LED_DIR/blue:power/brightness" 2>/dev/null

# 2. User LED: Solid OFF
for user_led in white:user green:user; do
    if [ -e "$LED_DIR/$user_led/brightness" ]; then
        echo none > "$LED_DIR/$user_led/trigger" 2>/dev/null
        echo 0 > "$LED_DIR/$user_led/brightness" 2>/dev/null
    fi
done

# 3. LAN LED (Ethernet): Kernel netdev trigger (Link=ON, RX/TX=Blink, Unplugged=OFF)
for lan in green:lan eth; do
    if [ -d "$LED_DIR/$lan" ]; then
        echo netdev > "$LED_DIR/$lan/trigger" 2>/dev/null
        echo eth0 > "$LED_DIR/$lan/device_name" 2>/dev/null
        echo 1 > "$LED_DIR/$lan/link" 2>/dev/null
        echo 1 > "$LED_DIR/$lan/rx" 2>/dev/null
        echo 1 > "$LED_DIR/$lan/tx" 2>/dev/null
        echo 50 > "$LED_DIR/$lan/interval" 2>/dev/null
    fi
done

user_led_off() {
    for user_led in white:user green:user; do
        if [ -e "$LED_DIR/$user_led/brightness" ]; then
            echo none > "$LED_DIR/$user_led/trigger" 2>/dev/null
            echo 0 > "$LED_DIR/$user_led/brightness" 2>/dev/null
        fi
    done
}

set_leds() {
    local l1=$1 l2=$2 l3=$3 l4=$4 l5=$5
    [ -d "$LED_DIR/green:rssilow" ] && echo "$l1" > "$LED_DIR/green:rssilow/brightness" 2>/dev/null
    [ -d "$LED_DIR/green:rssimediumlow" ] && echo "$l2" > "$LED_DIR/green:rssimediumlow/brightness" 2>/dev/null
    [ -d "$LED_DIR/green:rssimedium" ] && echo "$l3" > "$LED_DIR/green:rssimedium/brightness" 2>/dev/null
    [ -d "$LED_DIR/green:rssimediumhigh" ] && echo "$l4" > "$LED_DIR/green:rssimediumhigh/brightness" 2>/dev/null
    [ -d "$LED_DIR/green:rssihigh" ] && echo "$l5" > "$LED_DIR/green:rssihigh/brightness" 2>/dev/null
}

# Ensure all RSSI LEDs are clean of any default kernel triggers
for led in green:rssilow green:rssimediumlow green:rssimedium green:rssimediumhigh green:rssihigh; do
    [ -d "$LED_DIR/$led" ] && echo "none" > "$LED_DIR/$led/trigger" 2>/dev/null
done

DISCONN_TICKS=0

while true; do
    user_led_off

    # Find active wifi interface
    IFACE=$(iw dev 2>/dev/null | awk '$1 == "Interface" {print $2; exit}')
    [ -z "$IFACE" ] && IFACE="wlan0"

    # In managed mode, only a real association may light the bars.
    SIGNAL=$(iw dev "$IFACE" link 2>/dev/null | awk '/^\tsignal:/ {print $2; exit}')

    case "$SIGNAL" in
        -[0-9]*)
        # Connected! Reset disconnected counter (NO scanning while connected to prevent ping spikes)
        DISCONN_TICKS=0

        # Signal is in negative dBm, e.g. -65
        # Stronger signals have higher algebraic value (-50 > -65 > -85)
        if [ "$SIGNAL" -ge -55 ]; then
            set_leds 1 1 1 1 1
        elif [ "$SIGNAL" -ge -65 ]; then
            set_leds 1 1 1 1 0
        elif [ "$SIGNAL" -ge -75 ]; then
            set_leds 1 1 1 0 0
        elif [ "$SIGNAL" -ge -85 ]; then
            set_leds 1 1 0 0 0
        elif [ "$SIGNAL" -ge -95 ]; then
            set_leds 1 0 0 0 0
        else
            set_leds 0 0 0 0 0
        fi
        ;;
        *)
        # Not connected - turn all signal LEDs off
        set_leds 0 0 0 0 0
        DISCONN_TICKS=$((DISCONN_TICKS + 1))

        # SMART AUTO-SCAN & RECONNECT ENGINE:
        # Only kicks in when wifi signal is lost (e.g. AP frequency changed)
        if [ "$DISCONN_TICKS" -eq 3 ] || [ $((DISCONN_TICKS % 6)) -eq 0 ]; then
            # 1. Ask wpa_supplicant to scan all 5GHz channels immediately
            wpa_cli -i "$IFACE" scan >/dev/null 2>&1 || \
            wpa_cli -p "/var/run/wpa_supplicant-$IFACE" scan >/dev/null 2>&1 || \
            iw dev "$IFACE" scan trigger >/dev/null 2>&1

            # 2. Tell wpa_supplicant to immediately reassociate to the AP on the new channel
            wpa_cli -i "$IFACE" reassociate >/dev/null 2>&1 || \
            wpa_cli -p "/var/run/wpa_supplicant-$IFACE" reassociate >/dev/null 2>&1
        fi

        # If disconnected for over 24 seconds (driver stuck on dead channel), trigger a wifi reload
        if [ "$DISCONN_TICKS" -ge 24 ] && [ $((DISCONN_TICKS % 24)) -eq 0 ]; then
            ubus call network.wireless notify_atf >/dev/null 2>&1 || wifi up radio0 >/dev/null 2>&1
        fi
        ;;
    esac

    sleep 1
    # Re-assert the policy after all other LED updates and API activity.
    user_led_off
done
