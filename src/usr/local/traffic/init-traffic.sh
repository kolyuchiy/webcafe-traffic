#!/bin/sh

IPTABLES=/sbin/iptables

$IPTABLES -N traffic 
$IPTABLES -A traffic -j RETURN

for (( i=193; $i <= 208; i=$i+1 ))
do
	$IPTABLES -N traffic_inb_$i
	$IPTABLES -A traffic_inb_$i -j DROP
	$IPTABLES -I traffic -d 81.18.138.$i -j traffic_inb_$i
done

$IPTABLES -I traffic -p tcp -d 81.18.138.225 -j ACCEPT
$IPTABLES -I traffic -p tcp -s 81.18.138.225 -j ACCEPT

$IPTABLES -I FORWARD -j traffic
$IPTABLES -I OUTPUT -j traffic

/usr/local/traffic/restore-traffic.pl

