#!/bin/bash
IFACE=ens1f0np0
INTERVAL=1

while true; do
    START=$(ethtool -S "$IFACE" | grep 'rx_packets_phy:' | awk '{print $2}' | tr -d '\r')
    sleep "$INTERVAL"
    END=$(ethtool -S "$IFACE" | grep 'rx_packets_phy:' | awk '{print $2}' | tr -d '\r')
    PPS=$((END - START))
    echo $PPS
done
