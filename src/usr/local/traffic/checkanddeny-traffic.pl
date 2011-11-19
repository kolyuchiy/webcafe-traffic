#!/usr/bin/perl

use strict;
use lib qw(/usr/local/traffic);
use DBI;
use Traffic;

my $IPTABLES="/sbin/iptables";

for (my $i=193; $i <= 208; $i++) {
	my $bytes = qx#$IPTABLES -L traffic_inb_$i -vxn |grep RETURN |head -n 1#;
	chomp $bytes;
	next if ($bytes =~ /^$/);
	my @z = split /\s+/, $bytes;
	$bytes = $z[2];

	my $bytes_limit = qx#/usr/local/traffic/showlimit-traffic.pl $i#;
	my $begin;
	chomp $bytes_limit;
	($bytes_limit, $begin) = split /\t/, $bytes_limit;

	next if ($bytes_limit =~ /^0$/);
	if ($bytes > $bytes_limit) {
		close_traffic('limitcheck', $i);
		print "$i closed session\n";
	}
	print "$i\t$bytes\t$bytes_limit\n"
}

sub close_traffic {
	my $admin = $_[0];
	my $comp = $_[1];
	my $bytes;
	open IN, "sudo /usr/local/traffic/reset-traffic.sh $comp |";
	while (<IN>) {
		split;
		my $comp = $_[0];
		$bytes = $_[1];
	};
	close IN;
	qx#sudo /usr/local/traffic/deny-traffic.sh $comp#;
	insert_transaction($admin, 'close', $comp, $bytes);
	insert_session($admin, $comp, $bytes);
}

