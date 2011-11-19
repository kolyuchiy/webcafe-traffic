#!/bin/sh

IPTABLES=/sbin/iptables
comp=$1

$IPTABLES -F traffic_inb_$comp
$IPTABLES -I traffic_inb_$comp -j DROP

