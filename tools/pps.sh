#!/bin/bash
IFACE=eth0
INTERVAL=1

while true; do
    START=$(ethtool -S "$IFACE" | grep rx_packets | awk '{print $2}')
    sleep "$INTERVAL"
    END=$(ethtool -S "$IFACE" | grep rx_packets | awk '{print $2}')
    PPS=$((END - START))
    echo "PPS: $PPS"
done