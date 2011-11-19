#!/bin/sh

iptables -L FORWARD |grep traffic >/dev/null

