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

    # Ensure wlan0 interface is created and active on phy0
    if ! iw dev 2>/dev/null | grep -q "Interface wlan0"; then
        iw phy phy0 interface add wlan0 type managed >/dev/null 2>&1
        ip link set wlan0 up >/dev/null 2>&1
    fi

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

        # SMART AUTO-RECONNECT & MULTI-TOWER FAILOVER ENGINE:
        # 1. At 4 seconds of disconnection: trigger full Superchannel active 4900-6100 MHz frequency sweep
        if [ "$DISCONN_TICKS" -eq 4 ]; then
            ALL_SUPERCHANNEL="4900 4905 4910 4915 4920 4925 4930 4935 4940 4945 4950 4955 4960 4965 4970 4975 4980 4985 4990 4995 5000 5005 5010 5015 5020 5025 5030 5035 5040 5045 5050 5055 5060 5065 5070 5075 5080 5085 5090 5095 5100 5105 5110 5115 5120 5125 5130 5135 5140 5145 5150 5155 5160 5165 5170 5175 5180 5185 5190 5195 5200 5205 5210 5215 5220 5225 5230 5235 5240 5245 5250 5255 5260 5265 5270 5275 5280 5285 5290 5295 5300 5305 5310 5315 5320 5325 5330 5335 5340 5345 5350 5355 5360 5365 5370 5375 5380 5385 5390 5395 5400 5405 5410 5415 5420 5425 5430 5435 5440 5445 5450 5455 5460 5465 5470 5475 5480 5485 5490 5495 5500 5505 5510 5515 5520 5525 5530 5535 5540 5545 5550 5555 5560 5565 5570 5575 5580 5585 5590 5595 5600 5605 5610 5615 5620 5625 5630 5635 5640 5645 5650 5655 5660 5665 5670 5675 5680 5685 5690 5695 5700 5705 5710 5715 5720 5725 5730 5735 5740 5745 5750 5755 5760 5765 5770 5775 5780 5785 5790 5795 5800 5805 5810 5815 5820 5825 5830 5835 5840 5845 5850 5855 5860 5865 5870 5875 5880 5885 5890 5895 5900 5905 5910 5915 5920 5925 5930 5935 5940 5945 5950 5955 5960 5965 5970 5975 5980 5985 5990 5995 6000 6005 6010 6015 6020 6025 6030 6035 6040 6045 6050 6055 6060 6065 6070 6075 6080 6085 6090 6095 6100"
            iw dev "$IFACE" scan freq $ALL_SUPERCHANNEL >/dev/null 2>&1 || iw dev "$IFACE" scan >/dev/null 2>&1 || /sbin/wifi reload >/dev/null 2>&1
        fi

        # 2. At 10 seconds: trigger Multi-Tower Auto Failover if enabled
        if [ "$DISCONN_TICKS" -eq 10 ]; then
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
                /sbin/wifi reload >/dev/null 2>&1 || ubus call network.wireless reload >/dev/null 2>&1
            fi
        fi

        # 3. Every 14 seconds thereafter until connected:
        if [ "$DISCONN_TICKS" -gt 10 ] && [ $((DISCONN_TICKS % 14)) -eq 0 ]; then
            /sbin/wifi reload >/dev/null 2>&1
        fi
        ;;
    esac

    sleep 1
    # Re-assert the policy after all other LED updates and API activity.
    user_led_off
done
