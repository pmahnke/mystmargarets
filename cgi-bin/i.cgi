#!/usr/local/bin/perl

##############################################################
##############################################################
#
# i.cgi
#
#  gets an image and returns is
#
#  input: 
#         z = zone_id
#         n = random number
#
##############################################################
##############################################################


use CGI::Lite;
use DBI;

my $dbh = DBI->connect("dbi:Pg:dbname=ads","pmahnke","hi11top",{ RaiseError => 1, AutoCommit => 1    });
my $web_img_path = "http://www.mystmargarets.com"; # traders.stmgrts.org.uk";
my $date      = `date +'%Y-%m-%d'`;
chop($date);


################################################################
if ($ENV{'CONTENT_LENGTH'} || $ENV{'QUERY_STRING'}) {

    $cgi = new CGI::Lite;
    %F = $cgi->parse_form_data;
    
} else {
    
    # nothing submitted... so PANIC!!!
    print "Status: 302 Found\nLocation: /images/1.gif\n\n";
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
ORDER BY random() LIMIT 1
|;

    $sth = $dbh->prepare($sql);
    $sth->execute($F{'z'});
    $sth->bind_columns (\$banner_id, \$f);

    while ( $sth->fetch ) {
	
		# add priority logic?
	
    }
	
	if ($f) {

	    $url = $web_img_path.$f;
    	print "Status: 302 Found\nLocation: $url\n\n";
       	
    	&tracker('image', $banner_id, $F{'z'}, $ENV{'REMOTE_ADDR'}, $ENV{'HTTP_REFERER'}, $F{'n'});
    
    } else {
    
       	print "Status: 302 Found\nLocation: /images/1.gif\n\n";
       		
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
(?, ?, ?, ?, ?, ?, ?)
    |;

$sth = $dbh->prepare($sql);
$sth->execute($_[0], $_[1], $_[2], $_[3], $_[4], $_[5], $now);

return();
 
}
