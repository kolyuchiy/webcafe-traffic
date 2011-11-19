#!/bin/sh

IPTABLES=/sbin/iptables
comp=$1

$IPTABLES -L traffic_inb_$comp |tail -n 1 |awk '{print $1}'

