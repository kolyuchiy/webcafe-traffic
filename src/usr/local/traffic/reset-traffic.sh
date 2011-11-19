#!/bin/sh

IPTABLES=/sbin/iptables

comp=$1
echo "81.18.138.$comp	"`$IPTABLES -L -Z traffic_inb_$comp -vxn |grep RETURN |head -n 1 |awk '{print $2}'`

