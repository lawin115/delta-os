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

        # Check if we are currently running on Backup Tower, and monitor for Primary Tower return
        if [ -f "/tmp/delta_failover_active" ]; then
            FAILOVER_TICKS=$(( ${FAILOVER_TICKS:-0} + 1 ))
            # Every 30 seconds on backup, check if Primary AP has come back online
            if [ "$FAILOVER_TICKS" -ge 30 ]; then
                FAILOVER_TICKS=0
                PRIM_SSID=$(uci -q get wireless.@wifi-iface[0].primary_ssid)
                if [ -n "$PRIM_SSID" ]; then
                    PRIM_SCAN=$(iw dev "$IFACE" scan 2>/dev/null || iw dev "$IFACE" scan dump 2>/dev/null)
                    if echo "$PRIM_SCAN" | grep -q "SSID: $PRIM_SSID"; then
                        # Primary AP is back online! Failback to Primary Tower
                        PRIM_KEY=$(uci -q get wireless.@wifi-iface[0].primary_key)
                        uci set wireless.@wifi-iface[0].ssid="$PRIM_SSID" 2>/dev/null
                        [ -n "$PRIM_KEY" ] && uci set wireless.@wifi-iface[0].key="$PRIM_KEY" 2>/dev/null
                        uci commit wireless
                        rm -f /tmp/delta_failover_active 2>/dev/null
                        /sbin/wifi reload >/dev/null 2>&1
                    fi
                fi
            fi
        fi

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

        # 1. At 6 seconds of disconnection: trigger standard background scan
        if [ "$DISCONN_TICKS" -eq 6 ]; then
            iw dev "$IFACE" scan >/dev/null 2>&1 &
        fi

        # 2. At 12 seconds: trigger Multi-Tower Auto Failover if enabled
        if [ "$DISCONN_TICKS" -eq 12 ]; then
            AUTO_FO=$(uci -q get wireless.@wifi-iface[0].auto_failover)
            BACKUP_SSID=$(uci -q get wireless.@wifi-iface[0].backup_ssid)
            if [ "$AUTO_FO" = "1" ] && [ -n "$BACKUP_SSID" ] && [ ! -f "/tmp/delta_failover_active" ]; then
                BACKUP_KEY=$(uci -q get wireless.@wifi-iface[0].backup_key)
                uci set wireless.@wifi-iface[0].ssid="$BACKUP_SSID" 2>/dev/null
                [ -n "$BACKUP_KEY" ] && uci set wireless.@wifi-iface[0].key="$BACKUP_KEY" 2>/dev/null
                uci commit wireless
                echo "1" > /tmp/delta_failover_active
                /sbin/wifi reload >/dev/null 2>&1
            else
                /sbin/wifi reload >/dev/null 2>&1
            fi
        fi

        # 3. Disconnected state: do not spam wifi reload to prevent kernel crash
        if [ "$DISCONN_TICKS" -eq 30 ]; then
            # Soft trigger single rescan once after 30s
            iw dev "$IFACE" scan >/dev/null 2>&1 &
        fi
        ;;
    esac

    sleep 1
    # Re-assert the policy after all other LED updates and API activity.
    user_led_off
done
