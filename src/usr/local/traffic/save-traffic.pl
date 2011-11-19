#!/usr/bin/perl

use strict;
use DBI;

my $data_source = "dbi:mysql:traffic";
my $dbh = DBI->connect($data_source, 'root', '')
	or die "Can’t connect to $data_source: $DBI::errstr";

$dbh->do("DELETE FROM iptables")
	or die "Can’t execute statement: $DBI::errstr";

open IN, "sudo /usr/local/traffic/show-traffic.sh |";
while (<IN>) {
	chomp; split;
	my $ipaddr = $_[0];
	my $bytes = $_[1];
	my @t = split /\./, $ipaddr;
	my $comp = $t[3];
	my $state = qx#sudo /usr/local/traffic/status-traffic.sh $comp#;
	chomp $state;

	print "$comp\t$state\t$bytes\n";	
	$dbh->do("INSERT INTO iptables (comp, state, bytes) VALUES ('$comp', '$state', $bytes)")
		or die "Can’t execute statement: $DBI::errstr";
};
close IN;

$dbh->disconnect;

