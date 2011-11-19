
package Traffic;

use strict;

BEGIN {
	use Exporter ();
	our (@ISA, @EXPORT);

	@ISA = qw(Exporter);
	@EXPORT = qw(&insert_transaction &insert_session &get_admin_name);
}

sub insert_transaction {
	my $admin = $_[0];
	my $type = $_[1];
	my $comp = $_[2];
	my $bytes = $_[3];
	my $bytes_limit = $_[4];
	if (!($bytes_limit =~ /^[0-9]+$/)) {$bytes_limit = 0; }

	my $data_source = "dbi:mysql:traffic";
	my $dbh = DBI->connect($data_source, 'root', '')
		or die "Can’t connect to $data_source: $DBI::errstr";

#	print "INSERT INTO transactions VALUES (now(), " . $dbh->quote($admin) . ", '$type', '$comp', $bytes, $bytes_limit)";
	$dbh->do("INSERT INTO transactions VALUES (now(), " . $dbh->quote($admin) . ", '$type', '$comp', $bytes, $bytes_limit)")
		or die "Can’t execute statement: $DBI::errstr";

	$dbh->disconnect;
}

sub insert_session {
#	my $admin = $_[0];
	my $comp = $_[1];
	my $bytes = $_[2];
	my $data_source = "dbi:mysql:traffic";
	my $dbh = DBI->connect($data_source, 'root', '')
		or die "Can’t connect to $data_source: $DBI::errstr";

	my $sth = $dbh->prepare( qq{
			SELECT time, admin, type, comp, bytes, bytes_limit
			FROM transactions
			WHERE type = 'open'
			AND   comp = '$comp'
			ORDER BY time DESC
			LIMIT 1
			}) or die "Can’t prepare statement: $DBI::errstr";

	my $rc = $sth->execute
		or die "Can’t execute statement: $DBI::errstr";

	my ($time, $admin, $z, $z, $z, $bytes_limit) = $sth->fetchrow_array;
	$sth->finish;

	$dbh->do("INSERT INTO sessions VALUES ($time, now(), " . $dbh->quote($admin) . ", '$comp', $bytes, $bytes_limit)")
		or die "Can’t execute statement: $DBI::errstr";

	$dbh->disconnect;
}

sub get_admin_name {
	my $comp = $_[0];
	my $state = $_[1];

	if ($state =~ /RETURN/) {
		my $data_source = "dbi:mysql:traffic";
		my $dbh = DBI->connect($data_source, 'root', '')
			or die "Can’t connect to $data_source: $DBI::errstr";

		my $sth = $dbh->prepare( qq{
				SELECT time, admin, type, comp, bytes
				FROM transactions
				WHERE type = 'open'
				AND   comp = '$comp'
				ORDER BY time DESC
				LIMIT 1
				}) or die "Can’t prepare statement: $DBI::errstr";

		my $rc = $sth->execute
			or die "Can’t execute statement: $DBI::errstr";

		my ($time, $admin, $z, $z, $z) = $sth->fetchrow_array;
		$sth->finish;

		return $admin;
	} else {
		return "ОШИБКА";
	}
}

END { }
1;

