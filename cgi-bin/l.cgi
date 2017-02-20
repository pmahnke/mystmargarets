#!/usr/local/bin/perl

##############################################################
##############################################################
#
# l.cgi
#
#  gets an link and returns it
#
#  input: 
#         z = zone_id
#         n = random number
#
##############################################################
##############################################################


use CGI::Lite;
use DBI;

my $dbh = DBI->connect("dbi:Pg:dbname=ads","pmahnke","hi11top",{ RaiseError => 1, AutoCommit => 1 });
my $date      = `date +'%Y-%m-%d'`;
chop($date);


################################################################
if ($ENV{'CONTENT_LENGTH'} || $ENV{'QUERY_STRING'}) {

    $cgi = new CGI::Lite;
    %F = $cgi->parse_form_data;
    
} else {
    
    # nothing submitted... so PANIC!!!
    exit;
   
}

if ($F{'z'}) {

    &get_link();
    exit;

}

exit;



###############################################
sub get_link {

    # requires zone_id
    my ($sql, $sth, $banner_id, $url);

    $F{'n'} = undef() if (!$F{'n'});

    $sql = qq |
SELECT id, url
FROM banners
WHERE id IN
(SELECT banner_id
 FROM tracker
 WHERE zone_id = ? AND 
 bkey = ? 
 ORDER BY ts DESC  
 LIMIT 1)|;

#print STDERR qq |SELECT id, url FROM banners WHERE id IN (SELECT banner_id FROM tracker WHERE zone_id = $F{'z'} AND  bkey = '$F{'n'}' ORDER BY ts DESC  LIMIT 1)|;

    $sth = $dbh->prepare($sql);

    $sth->execute($F{'z'}, $F{'n'});

    $sth->bind_columns (\$banner_id, \$url);

    while ( $sth->fetch ) {
	
	# add priority logic?
	
    }

print STDERR $url;

 if ($url) {
     print "Status: 302 Found\nLocation: $url\n\n";
     
     &tracker('link', $banner_id, $F{'z'}, $ENV{'REMOTE_ADDR'}, $ENV{'HTTP_REFERER'}, $F{'n'});
     
} else {
    print "Status: 302 Found\nLocation: $ENV{'HTTP_REFERER'}\n\n";
}

}

########################################################
sub tracker {

    my ($sql, $sth);

    my $now = "now()";
    
    $sql = qq |
INSERT INTO tracker
(type, banner_id, zone_id, ip, refer, bkey, ts)
VALUES
(?,?,?,?,?,?,?)
    |;

$sth = $dbh->prepare($sql);
$sth->execute($_[0], $_[1], $_[2], $_[3], $_[4], $_[5], $now);

#print STDERR qq |INSERT INTO tracker (type, banner_id, zone_id, ip, refer, bkey, ts) VALUES ('$_[0]', $_[1], $_[2], '$_[3]', '$_[4]', '$_[5]', '$now');|;

return();
 
}
