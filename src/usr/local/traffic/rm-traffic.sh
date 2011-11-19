#!/bin/sh

IPTABLES=/sbin/iptables

$IPTABLES -D FORWARD -j traffic
$IPTABLES -F traffic 

for (( i=193; $i <= 208; i=$i+1 ))
do
	$IPTABLES -F traffic_inb_$i
	$IPTABLES -X traffic_inb_$i
done

$IPTABLES -X traffic

