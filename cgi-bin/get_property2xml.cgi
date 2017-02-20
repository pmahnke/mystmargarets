#!/usr/local/bin/perl

###############
# get_property
#
# actual script that sam is calling
#
# sam, please ask any questions... I think we should either
# 1. cron and database the listings and then use a cgi to build this page dynamically, or
# 2. have this script build a static page...
# sort of depends on what the page does... let me know what you want to do, but I don't think 3,4,5 page gets is very efficient.


use CGI::Lite;
use Encode;
use utf8;
use HTML::TreeBuilder::XPath;
use LWP::UserAgent;
use DBI;

require ("/home/stmargarets/cgi-bin/common.pl");

my $dbh = DBI->connect("dbi:SQLite:dbname=/home/mystmgrts/property.db","","",{ PrintError => 1, AutoCommit => 1 });


my ($sql, $sth, $date);

# brought by Chase in Sept 2012 - $L{'Churchill Sales'} = qq |http://www.rightmove.co.uk/property-for-sale/find/Churchills-Estate-Agents/St-Margarets.html?locationIdentifier=BRANCH^34442&includeSSTC=true&_includeSSTC=on|;

$L{'Chase Buchanan'} = qq |http://www.rightmove.co.uk/property-for-sale/find/Chase-Buchanan/St-Margarets.html?locationIdentifier=BRANCH^48456&includeSSTC=true&_includeSSTC=on|;

$L{'Dexters'} = qq |http://www.rightmove.co.uk/property-for-sale/find/Dexters/St-Margarets.html?locationIdentifier=BRANCH^84809&includeSSTC=true&_includeSSTC=on|;

$L{'Churchill Lettings'} = qq |http://www.rightmove.co.uk/property-to-rent/find/Churchills-Lettings/St-Margarets.html?locationIdentifier=BRANCH^33744&includeLetAgreed=true&_includeLetAgreed=on|;

$L{'Fitz-Gibbon'} = qq |http://www.rightmove.co.uk/property-to-rent/find/Fitz-Gibbon/Twickenham.html?locationIdentifier=BRANCH^56906&includeLetAgreed=true&_includeLetAgreed=on|;

$L{'Chase Buchanan Lettings'} = qq |http://www.rightmove.co.uk/property-to-rent/find/Chase-Buchanan/Twickenham---Lettings.html?locationIdentifier=BRANCH^48798&includeLetAgreed=true&_includeLetAgreed=on|;


$L{'Chase Buchanan'}{'email'} = qq|mailto:stmargarets\@chasebuchanan.co.uk|;
$L{'Chase Buchanan Lettings'}{'email'} = qq|mailto:stmargarets\@chasebuchanan.co.uk|;
$L{'Dexters'}{'email'} = qq|mailto:stmargaretssales\@dexters.co.uk|;
$L{'Churchill Lettings'}{'email'} = qq|st.margarets\@churchillslettings.co.uk|;
$L{'Fitz-Gibbon'}{'email'} = qq|mailto:sales\@fitzgibbon.co.uk|;

$L{'Chase Buchanan'}{'type'} = "sales";
$L{'Chase Buchanan Lettings'}{'type'} = "lettings";
$L{'Dexters'}{'type'} =  "sales";
$L{'Churchill Lettings'}{'type'} =  "lettings";
$L{'Fitz-Gibbon'}{'type'} =  "lettings";



################################################################
if ($ENV{'CONTENT_LENGTH'} || $ENV{'QUERY_STRING'}) {
    
    $cgi = new CGI::Lite;
    %F = $cgi->parse_form_data;
    
} else {

	my $out;
	
	if (&check_db_date()) { # && !$ARGV[0]) {
	
		# use db data
		$out = &read_db();
	
	} else {
		
		# need to get new data
		foreach my $a (keys %L) {

			my ($url, $desc) = &process_index_page(&ConnectionGet($L{$a}));
			$out .= &process_page(&ConnectionGet($url), $url, $a, $desc);
		}
	}
	&print_xml($out);}
	exit;

if ($F{'a'} =~ /new/) {

	&new_link();
	&print_page();
	
} elsif ($F{'a'} =~ /direct/) {

	&process_page(&ConnectionGet($F{'url'}),$F{'url'});
	&print_page();


} else {

	my $out;
	foreach my $a (keys %L) {

	    print STDERR qq |GETTING AGENT $L{$a}\n|;

	    my ($url, $desc) = &process_index_page(&ConnectionGet($L{$a}));
	    $out .= &process_page(&ConnectionGet($url), $url, $a, $desc);
	}
	
	&print_xml($out);
	
}

exit;


################################################################################
sub check_db_date {

	# check db to see if we need to get a new page
	$date = $dbh->selectrow_array(qq|SELECT date('now')|);
	my $now = $dbh->selectrow_array(qq|SELECT last_update FROM info where last_update = date('now')|);
	return($now);
	
}

################################################################################
sub update_db_date {

	$dbh->selectrow_array(qq|update info set last_update = date('now');|);
	return();
}


################################################################################
sub read_db {

	my ($agent, $agent_logo, $agent_url, $agent_email, $title, $decr, $image, $url, $price, $date, $out, $type);
	
	my $sql = qq |
	SELECT agent, agent_logo, agent_url, agent_email, title, decr, image, url, price, type
	FROM property 
	WHERE date = date('now') 
	|;
	
	$sth = $dbh->prepare($sql);
	$sth->execute();
	
	$sth->bind_columns (\$agent, \$agent_logo, \$agent_url, \$agent_email, \$title, \$desc, \$image, \$url, \$price, \$type);
	
	while ( $sth->fetch ) {

	    $desc =~ s/\?/\&pound\;/g;
	
	
		$out .= qq |
	<listing>	
		<title>$title</title>
		<img><![CDATA[$image]]></img>
		<description>$desc</description>
		<agent>$agent</agent>
    	<agentlogo><![CDATA[$agent_logo]]></agentlogo>
    	<agenturl><![CDATA[$agent_url]]></agenturl>
    	<agentemail><![CDATA[$agent_email]]></agentemail>
		<moreurl><![CDATA[$url]]></moreurl>
		<price>$price</price>
		<type>$type</type>
	</listing>|;
	
	}


	return($out);
	

}

################################################################################
sub new_link {

	$out = qq |
<form method="post">
	<fieldset>	
	<p>
		<label for="url">url</label><br />
		<input type="text" class="text" id="url" name="url" value="$F{'url'}" />
	</p>
	
	<p>
		<input type="submit" name="a" value="direct" />
	</p>
	</fieldset>
</form>	

<form method="post">
	<fieldset>	
<ul>
  <li><a href="?agent=Churchill">Churchill</a></li>
  <li><a href="?agent=Chase Buchanan">Chase Buchanan</a></li>
  <li><a href="?agent=Dexters">Dexters</a></li>
  <li><a href="?agent=Gascoigne-Pees">Gascoigne-Pees</a></li>
  <li><a href="?agent=Hamptons">Hamptons</a></li>
</ul>

	</fieldset>
</form>	

	|;
	
	return();
}


################################################################################
sub process_index_page {

    # http://www.rightmove.co.uk/property-for-sale/find/Chase-Buchanan/St-Margarets.html?locationIdentifier=BRANCH^48456&includeSSTC=true&_includeSSTC=on
	
    my $url = $_[0];
    my $out;

    print STDERR qq |pip: $L{$F{'agent'}} and url $url\n|;
    
    my $in = HTML::TreeBuilder::XPath->new_from_content($url);
    my @hrefs  = $in->findvalues('//a[@class="photo"]/@href');
    my @exists = $in->exists('//span[@class="propertystatus sold"]');
    my @desc   = $in->findvalues('//p[@class="description"');
    
    
    my $i=0;
    foreach (@hrefs) {
		
	print STDERR qq |looking at $_ and exists? $exists[$i]\n|;
	
	if (/property-(for-sale|to-rent)/ && !$exists[$i]) {
	    $out = $_;
	    $out = substr($out, 0, rindex($out, "html") + 4); 
	    print STDERR qq |PARSE: got $_ and changed it to $out\n|;
	    last;
	}	
	$i++;
    }
    
    print STDERR qq |urls: $out\n|;
    
    return('http://www.rightmove.co.uk'.$out, $desc[$i]);
    

}

################################################################################
sub process_page {

	my $in = HTML::TreeBuilder::XPath->new_from_content($_[0]);

	my @title  = $in->findvalues('//title');
	my @descr  = $in->findvalues('//meta[@property="og:description"]/@content');
	my @img    = $in->findvalues('//img[@id="mainphoto"]/@src');

	my @logo   = $in->findvalues('//img[@id="branchlogo"]/@src');
	my @price  = $in->findvalues('//div[@id="amount"]');
	$price[0]  =~ s/[^0-9,]//g;
	my @freq   = $in->findvalues('//span[@id="rentalfrequency"]');
	$price[0] .= ' '.$freq[0]; 
	my @agent  = $in->findvalues('//img[@id="branchlogo"]/@alt');
	my ($agent, $null) = split(/,/, $agent[0]); 
	
	my $moreurl = substr($_[1], 0, rindex($_[1], ";")) . 'l';
	

	# overide fitz-gibbons crappy logo
	$logo[0] = qq|http://www.mystmargarets.com/images/fitz-gibbon_SMALL.jpg| if ($agent =~ /Fitz/);

	
	my $out = qq |
	 <listing>	
	    <title>@title</title>
	    <img><![CDATA[$img[0]]]></img>
	    <description>$_[3] $descr[0]</description>
	    <agent>$agent</agent>
	    <agentlogo><![CDATA[$logo[0]]]></agentlogo>
	    <agenturl><![CDATA[$L{$_[2]}]]></agenturl>
	    <agentemail><![CDATA[$L{$_[2]}{'email'}]]></agentemail>
	    <moreurl><![CDATA[$moreurl]]></moreurl>
	    <price><![CDATA[$price[0]]]></price>
	    <type>$L{$_[2]}{'type'}</type>
	 </listing>|;
	
	
	my $sql = qq |
	INSERT INTO property 
	(agent, agent_logo, agent_url, agent_email, title, decr, image, url, price, date, type)
	VALUES
	(?,?,?,?,?,?,?,?,?,?,?)	
	|;
	$sth = $dbh->prepare($sql);
	$sth->execute($agent, $logo[0], $L{$_[2]}, $L{$_[2]}{'email'}, @title, $_[3], $img[0], $moreurl, $price[0], $date, $L{$_[2]}{'type'});
	
	&update_db_date();

	return($out);

}

sub print_xml {

	print qq |Content-type: text/xml

<?xml version="1.0" encoding="utf-8"?>
<property>
$_[0]
</property>
|;

	return();
}

################################################################################   
sub print_page {

    my $head   = &getInclude('/home/mystmgrts/html/html_head.incl');
    my $header = &getInclude('/home/mystmgrts/html/html_header_small.incl');
    my $nav    = &getInclude('/home/mystmgrts/html/html_nav_hor.incl');
    my $footer = &getInclude('/home/mystmgrts/html/html_footer.incl');
    $out =~ s/&(?!#?[xX]?(?:[0-9a-fA-F]+|\w{1,8});)/&amp;/g; # clean ampersands
    my $banner_img = qq|/images/banner_traders$n.jpg|;


	print <<EndofHTML;
Content-type: text/html

$head
        <title>Property :: My St Margarets </title>
        <style type="text/css">
        div#menu li { display: inline; }
        </style>
 </head>

<body id="category">
 
	<div class="container">

		<div id="content" class="span-24 last">

$header
$nav

			<div id="entries" class="span-19">
			
			<div id="intro">
					<img src="$banner_img" class="span-14" alt="add a banner here?" />
			<!-- /intro --></div>

			
                    <h2>Traders :: $H1</h2>

$out



       <!-- /entries --></div>
		<div id="side_column_right" class="span-5 last">
		<!-- /side_column_right --></div>

	<!-- / content --></div>

$footer

<!-- / container --></div>

	</body>
</html>
EndofHTML

	exit;



}
 
 
 
 
 
 
 
 
 
################################################################################
sub ConnectionGet {

    # Create a user agent object
    my $ua = new LWP::UserAgent;
    $ua->agent("$user_agent");

    # Create a request
    # parse URL to go to server we are authenticated on
    my $u = $_[0];
    return if ($u =~ /HASH/);
    print STDERR qq "getGartner GET GETTING PAGE: $u\n";

    my $req = new HTTP::Request('GET', $u);

    # Pass request to user agent and get response
    my $res = $ua->request($req);

    my $Output = $res->content;

    # Check output
    if ($res->is_success) {
		$getGARTNERmsg .= "getGartner: CONNECT GET SUCCESS: ", $res->status_line, "<p\>\n\n\n";
		return($Output);
		
    } else {
		$getGARTNERmsg .= "getGartner: CONNECT GET FAILED: ", $res->status_line, "<p\>\n\n\n";
		return($Output, $_[0]); # return error info and url attempted
    }
    
}                        # end of sub Connection 
 
