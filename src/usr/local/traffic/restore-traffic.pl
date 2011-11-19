#!/usr/bin/perl

use strict;
use DBI;

my $data_source = "dbi:mysql:traffic";
my $dbh = DBI->connect($data_source, 'root', '')
	or die "Can’t connect to $data_source: $DBI::errstr";

my $sth = $dbh->prepare( q{
		SELECT comp, state, bytes FROM iptables
	}) or die "Can’t prepare statement: $DBI::errstr";
my $rc = $sth->execute
	or die "Can’t execute statement: $DBI::errstr";

while (my ($comp, $state, $bytes) = $sth->fetchrow_array) {
	print "$comp\t$state\t$bytes\n";
	if ($state =~ 'RETURN') {
		qx#sudo /usr/local/traffic/allow-traffic.sh $comp $bytes#;
	}
}

# check for problems which may have terminated the fetch early
die $sth->errstr if $sth->err;
$dbh->disconnect;

