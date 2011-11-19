#!/bin/sh

IPTABLES=/sbin/iptables
comp=$1
bytes=${2:-0}

$IPTABLES -F traffic_inb_$comp
$IPTABLES -I traffic_inb_$comp --set-counters 0 $bytes -j RETURN

