#!/bin/sh

IPTABLES=/sbin/iptables

for (( i=193; $i <= 208; i=$i+1 ))
do
	echo "81.18.138.$i	"`$IPTABLES -L traffic_inb_$i -vxn |tail -n 1 |awk '{print $2"\t"$3}'`
done

