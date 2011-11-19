#!/usr/bin/perl

use strict;
use strict;
use lib qw(/usr/local/traffic);
use Traffic;
use CGI qw/:standard/;
use DBI;

my $MEGABYTE = 1000000;

print header(-charset => 'utf-8', -expires => '-1d'),
	 start_html("Подсчет траффика");

my $admin = remote_user();
print '<h1>' . $admin . '</h1>';

print '<ul>
<li><a href="/cgi-bin/traffic.cgi">Показать список компов</a></li>
<li><a href="/cgi-bin/traffic.cgi?action=transactions">Просмотр транзакций</a></li>
<li><a href="/cgi-bin/traffic.cgi?action=sessions">Просмотр сессий</a></li>
<!-- <li><a href="/cgi-bin/traffic.cgi?action=init">Загрузить правила файрвола</a></li>
<li><a href="/cgi-bin/traffic.cgi?action=rm">Удалить правила файрвола</a></li> -->
</ul>';

my $action = param('action') ? param('action') : 'show';

if      ($action =~ /^show$/) {

	show_traffic();

#} elsif ($action =~ /^reset$/) {
#
#	my $comp = param('comp');
#	if ($comp =~ /^[1-8]$/) {
#		reset_traffic($admin, $comp);
#	} else {
#		print 'Неправильный номер компа';
#	}
#
} elsif ($action =~ /^open$/) {


	my $comp = param('comp');
	my $bytes_limit = param('bytes_limit');
	if ($comp =~ /^[0-9]+$/
	&&  $bytes_limit =~ /^[0-9]+$/) {
		$bytes_limit *= $MEGABYTE;
		my $status = qx#sudo /usr/local/traffic/status-traffic.sh $comp#;
		if ($status =~ /RETURN/) {
			print 'Сессия уже открыта';
		} elsif ($status =~ /DROP/) {
			open_traffic($admin, $comp, $bytes_limit);
		} else {
			print 'Неизвестная ошибка';
		}
	} else {
		print 'Неправильный номер компа или не правильно указан лимит по трафику';
	}

} elsif ($action =~ /^close$/) {

	my $comp = param('comp');
	if ($comp =~ /^[0-9]+$/) {
		my $status = qx#sudo /usr/local/traffic/status-traffic.sh $comp#;
		if ($status =~ /RETURN/) {
			close_traffic($admin, $comp);
		} elsif ($status =~ /DROP/) {
			print 'Сессия уже закрыта';
		} else {
			print 'Неизвестная ошибка';
		}
	} else {
		print 'Неправильный номер компа';
	}

#} elsif ($action =~ /^rm$/) {
#
#	rm_traffic();
#
#} elsif ($action =~ /^init$/) {
#
#	init_traffic();
#
} elsif ($action =~ /^transactions$/) {

	show_transactions();
	
} elsif ($action =~ /^sessions$/) {

	show_sessions();
	
} else {
	print 'Случилось что-то странное';
}

print end_html;

############################################################

sub show_traffic {
	my $data_source = "dbi:mysql:traffic";
	my $dbh = DBI->connect($data_source, 'root', '')
		or die "Can’t connect to $data_source: $DBI::errstr";

	my $sth = $dbh->prepare( qq{
			SELECT sum(bytes) as bytes
			FROM sessions
			WHERE end > NOW() - CURTIME()
			AND admin <> 'admin'
			}) or die "Can’t prepare statement: $DBI::errstr";

	my $rc = $sth->execute
		or die "Can’t execute statement: $DBI::errstr";

	my ($bytes) = $sth->fetchrow_array;
	$sth->finish;
	$dbh->disconnect;

	print "<p>Всего закрыто трафика за сегодня: ".$bytes/$MEGABYTE."M</p>";


	open IN, "sudo /usr/local/traffic/show-traffic.sh |";
	print "<table border='1'>";
	print "<tr><th>Компьютер</th><th>Трафик в мегабайтах</th><th>Состояние</th><th>Лимит в мегабайтах</th><th></th><th>Начало</th><th>Осталось мегабайт</th></tr>";
	while (<IN>) {
		split;
		my $ipaddr = $_[0];
		my $bytes = $_[1];
		my @t = split /\./, $ipaddr;
		my $comp = $t[3];
		my $state = $_[2];
		my $color;
		my $bytes_limit = 0;
		my $bytes_left = 0;
		my $begin;
		if ($state =~ /RETURN/) {
			$state = 'открыт ' . get_admin_name($comp, $state);
			$color = 'green';
			$bytes_limit = qx#/usr/local/traffic/showlimit-traffic.pl $comp#;
			$bytes_left = $bytes_limit - $bytes;
			($bytes_limit, $begin) = split /\t/, $bytes_limit;
		} else {
			$state = 'закрыт';
			$color = 'gray';
		}

		print "<tr style='background-color: $color'>";
		print "<td>$ipaddr</td><td>".$bytes/$MEGABYTE."</td><td>$state</td>";
#		print "<td>", 
#			start_form(-method => 'get'), 
#			hidden('action', 'reset'), 
#			hidden('comp', "$comp"),
#			submit('Сбросить'),
#			end_form,
#		      "</td>";
		print "<td>", 
			start_form(-method => 'get'), 
			hidden('action', 'open'), 
			hidden('comp', "$comp"),
			textfield('bytes_limit', $bytes_limit/$MEGABYTE, 8),
			submit('Открыть'),
			end_form,
		      "</td>";
		print "<td>", 
			start_form(-method => 'get'), 
			hidden('action', 'close'), 
			hidden('comp', "$comp"),
			submit('Закрыть'),
			end_form,
		      "</td>",
		      "<td>".$begin."</td>",
		      "<td>".$bytes_left/$MEGABYTE."</td>";
		print "</tr>";
	};
	print "</table>";
	close IN;
}

sub reset_traffic {
	my $admin = $_[0];
	my $comp = $_[1];
	open IN, "sudo /usr/local/traffic/reset-traffic.sh $comp |";
	print "<table border='1'>";
	while (<IN>) {
		split;
		my $comp = $_[0];
		my $bytes = $_[1];
		print "<tr><td>$comp</td><td>".$bytes/$MEGABYTE."</td></tr>";
		insert_transaction($admin, 'reset', $comp, $bytes);
	};
	print "</table>";
	close IN;
}

sub open_traffic {
	my $admin = $_[0];
	my $comp = $_[1];
	my $bytes = 0;
	my $bytes_limit = $_[2];
	qx#sudo /usr/local/traffic/allow-traffic.sh $comp#;
	insert_transaction($admin, 'open', $comp, $bytes, $bytes_limit);
	print "ok";
}

sub close_traffic {
	my $admin = $_[0];
	my $comp = $_[1];
	my $bytes;
	open IN, "sudo /usr/local/traffic/reset-traffic.sh $comp |";
	print "<table border='1'>";
	print "<tr><th>Компьютер</th><th>Трафик в мегабайтах</th></tr>";
	while (<IN>) {
		split;
		my $comp = $_[0];
		$bytes = $_[1];
		print "<tr><td>$comp</td><td>".$bytes/$MEGABYTE."</td></tr>";
	};
	print "</table>";
	close IN;
	qx#sudo /usr/local/traffic/deny-traffic.sh $comp#;
	insert_transaction($admin, 'close', $comp, $bytes);
	insert_session($admin, $comp, $bytes);
}

sub rm_traffic {
	qx#sudo /usr/local/traffic/rm-traffic.sh#;
}

sub init_traffic {
	qx#sudo /usr/local/traffic/init-traffic.sh#;
}

sub show_transactions {
	my $data_source = "dbi:mysql:traffic";
	my $dbh = DBI->connect($data_source, 'root', '')
		or die "Can’t connect to $data_source: $DBI::errstr";

	my $sth = $dbh->prepare( q{
			SELECT DATE_FORMAT(time, '%d %M %Y %H:%i:%s'), admin, type, comp, bytes, bytes_limit
			FROM transactions
			ORDER BY TIME DESC
			}) or die "Can’t prepare statement: $DBI::errstr";

	my $rc = $sth->execute
		or die "Can’t execute statement: $DBI::errstr";

	print "<table border='1'>";
	print "<tr><th>Время</th><th>Админ</th><th>Тип</th><th>Компьютер</th><th>Трафик в мегабайтах</th><th>Лимит в мегабайтах</th></tr>";
	while (my ($time, $admin, $type, $comp, $bytes, $bytes_limit) = $sth->fetchrow_array) {
		print "<tr>";
		print "<td>$time</td><td>$admin</td><td>$type</td><td>$comp</td><td>".$bytes/$MEGABYTE."</td><td>".$bytes_limit/$MEGABYTE."</td>";
		print "</tr>";
	}
	print "</table>";

	# check for problems which may have terminated the fetch early
	die $sth->errstr if $sth->err;

	$dbh->disconnect;
}

sub show_sessions {
	my $data_source = "dbi:mysql:traffic";
	my $dbh = DBI->connect($data_source, 'root', '')
		or die "Can’t connect to $data_source: $DBI::errstr";

	my $from = (param('from') =~ /^\d+-\d+-\d+\s+\d+:\d+$/) ? param('from') : '';
	my $to = (param('to') =~ /^\d+-\d+-\d+\s+\d+:\d+$/) ? param('to') : '';
	my $admin = (param('admin') =~ /^\w+$/) ? param('admin') : '';

	my $sth;
	my $sth1;
	my $rc1;
	my $total;
	my $total_bytes_limit;
	if ($from && $to && $admin) {
		print "<p>Сессии от $from до $to админа $admin<p>";
		$sth = $dbh->prepare(" 
				SELECT DATE_FORMAT(begin, '%d %M %Y %H:%i:%s'), 
					DATE_FORMAT(end, '%d %M %Y %H:%i:%s'), admin, comp, bytes,
					(end - begin) / 60, bytes_limit
				FROM sessions
				WHERE end > '$from'
				AND   end < '$to'
				AND   admin = '$admin'
				ORDER BY end DESC
				") or die "Can’t prepare statement: $DBI::errstr";
		$sth1 = $dbh->prepare(" 
				SELECT sum(bytes) as bytes, sum(bytes_limit) as total_bytes_limit
				FROM sessions
				WHERE end > '$from'
				AND   end < '$to'
				AND   admin = '$admin'
				ORDER BY end DESC
				") or die "Can’t prepare statement: $DBI::errstr";
		$rc1 = $sth1->execute
			or die "Can’t execute statement: $DBI::errstr";
		($total, $total_bytes_limit) = $sth1->fetchrow_array;
	} else {
		$sth = $dbh->prepare( q{
				SELECT DATE_FORMAT(begin, '%d %M %Y %H:%i:%s'), 
					DATE_FORMAT(end, '%d %M %Y %H:%i:%s'), admin, comp, bytes,
					(end - begin) / 60, bytes_limit
				FROM sessions
				ORDER BY end DESC
				}) or die "Can’t prepare statement: $DBI::errstr";
	}

	my $rc = $sth->execute
		or die "Can’t execute statement: $DBI::errstr";

	if ($from && $to && $admin) {
		print qq{ 
<form method="get" action="traffic.cgi">
<input type="hidden" name="action" value="sessions"/>
От: <input type="text" name="from" value="$from"/> до: <input type="text" name="to" value="$to"/> 
Админ: <input type="text" name="admin" value="$admin"/>
<input type="submit" name="submit" value="Фильтр"/>
</form>}; 
		print "<p>Итого: ".$total/$MEGABYTE."Мб, Всего лимит: ".$total_bytes_limit/$MEGABYTE."Мб</p>";
	} else {
		print ' 
<form method="get" action="traffic.cgi">
<input type="hidden" name="action" value="sessions"/>
От: <input type="text" name="from" value="2005-01-01 00:00"/> до: <input type="text" name="to" value="2005-01-02 00:00"/> 
Админ: <input type="text" name="admin" value="admin"/>
<input type="submit" name="submit" value="Фильтр"/>
</form>'; 
	}

	print "<table border='1'>";
	print "<tr><th>Начало</th><th>Конец</th><th>Админ</th><th>Компьютер</th><th>Трафик в мегабайтах</th><th>Время в минутах</th><th>Лимит</th></tr>";
	while (my ($begin, $end, $admin, $comp, $bytes, $time, $bytes_limit) = $sth->fetchrow_array) {
		print "<tr>";
		print "<td>$begin</td><td>$end</td><td>$admin</td><td>$comp</td><td>".$bytes/$MEGABYTE."</td><td>$time</td><td>".$bytes_limit/$MEGABYTE."</td>";
		print "</tr>";
	}
	print "</table>";

	# check for problems which may have terminated the fetch early
	die $sth->errstr if $sth->err;

	$dbh->disconnect;
}

