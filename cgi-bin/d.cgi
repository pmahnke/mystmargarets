#!/usr/bin/perl

##############################################################
##############################################################
#
# d.cgi
#
#  gets an image and returns is
#
#  input z = zone_id
#
##############################################################
##############################################################


use CGI::Lite;
use DBI;

my $dbh = DBI->connect("dbi:SQLite:dbname=/var/www/ads.db","pmahnke","hi11top",{ RaiseError => 1, AutoCommit => 1 });
my $web_img_path = "http://www.mystmargarets.com"; # traders.stmgrts.org.uk";
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

    &get_image();
    exit;

}

exit;





###############################################
sub get_image {

    # requires zone_id
    my ($sql, $sth, $banner_id, $f, $url);

    $sql = qq |
SELECT b.id, file_pointer
FROM banners b
LEFT JOIN banners_zones bz ON b.id=bz.banner_id
WHERE bz.zone_id = ? AND 
(b.start_date >= '$date' OR b.end_date >= '$date') AND 
b.is_display IS NOT NULL
|;

    $sth = $dbh->prepare($sql);

    $sth->execute($F{'z'});

    $sth->bind_columns (\$banner_id, \$f);

    while ( $sth->fetch ) {
	
	# add priority logic?
	
    }



    $url = $web_img_path.$f;
    print "Status: 302 Moved\nLocation: $url\n\n";
    
    &tracker('image', $banner_id, $F{'z'}, $ENV{'REMOTE_ADDR'}, $ENV{'HTTP_REFERER'});

}

########################################################
sub tracker {

    my ($sql, $sth);

    $now = $dbh->selectrow_array("SELECT date('now')");

    $sql = qq |
INSERT INTO tracker
(type, banner_id, zone_id, ip, refer, ts)
VALUES
(?, ?, ?, ?, ?, ?)
    |;

$sth = $dbh->prepare($sql);
$sth->execute($_[0], $_[1], $_[2], $_[3], $_[4], $now);

return();
 
}

sub null {

    $f = $dbh->selectrow_array($sql);

    $sth = $dbh->prepare($sql);

    $sth->execute();

    $sth->bind_columns (\$file);

    while ( $sth->fetch ) {

	
    }

}
