#!/usr/bin/perl

use strict;
use DBI;

my $comp = $ARGV[0];
my $data_source = "dbi:mysql:traffic";
my $dbh = DBI->connect($data_source, 'root', '')
	or die "Can’t connect to $data_source: $DBI::errstr";

my $sth = $dbh->prepare( qq{
	SELECT DATE_FORMAT(time, '%Y-%m-%d %H:%i:%s'), admin, type, comp, bytes, bytes_limit
	FROM transactions
	WHERE type = 'open'
	AND   comp = '$comp'
	ORDER BY time DESC
	LIMIT 1
}) or die "Can’t prepare statement: $DBI::errstr";

my $rc = $sth->execute
	or die "Can’t execute statement: $DBI::errstr";

my ($time, $z, $z, $z, $z, $bytes_limit) = $sth->fetchrow_array;
$sth->finish;
$dbh->disconnect;

if ($bytes_limit =~ /^[0-9]+$/) {
	print "$bytes_limit\t$time\n";
} else {
	print "0\n";
}

