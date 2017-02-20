#!/usr/local/bin/perl

###############
# get_property

# sam, please ask any questions... I think we should either
# 1. cron and database the listings and then use a cgi to build this page dynamically, or
# 2. have this script build a static page...
# sort of depends on what the page does... let me know what you want to do, but I don't think 3,4,5 page gets is very efficient.


use CGI::Lite;
use Encode;
use utf8;
use HTML::TreeBuilder::XPath;
use LWP::UserAgent;

require ("/home/stmargarets/cgi-bin/common.pl");


$L{'Churchill'} = qq |http://www.rightmove.co.uk/property-for-sale/find/Churchills-Estate-Agents/St-Margarets.html?locationIdentifier=BRANCH^34442&includeSSTC=true&_includeSSTC=on|;
$L{'Chase Buchanan'} = qq |http://www.rightmove.co.uk/property-for-sale/find/Chase-Buchanan/St-Margarets.html?locationIdentifier=BRANCH^48456&includeSSTC=true&_includeSSTC=on|;

$L{'Dexters'} = qq |http://www.rightmove.co.uk/property-for-sale/find/Dexters/St-Margarets.html?locationIdentifier=BRANCH^84809&includeSSTC=true&_includeSSTC=on|;

$L{'Gascoigne-Pees'} = qq |http://www.rightmove.co.uk/property-for-sale/find/Gascoigne-Pees/Twickenham.html?locationIdentifier=BRANCH^5063&includeSSTC=true&_includeSSTC=on|;

$L{'Hamptons'} = qq |http://www.rightmove.co.uk/property-for-sale/find/Hamptons-International-Sales/Richmond.html?locationIdentifier=BRANCH^37955&includeSSTC=true&_includeSSTC=on|;

################################################################
if ($ENV{'CONTENT_LENGTH'} || $ENV{'QUERY_STRING'}) {
    
    $cgi = new CGI::Lite;
    %F = $cgi->parse_form_data;
    
} else {
	&new_link();
	&print_page();
}


if ($F{'a'} =~ /new/) {

	&new_link();
	&print_page();
	
} elsif ($F{'a'} =~ /direct/) {

	&process_page(&ConnectionGet($F{'url'}),$F{'url'});
	&print_page();


} else {

	my $url = &process_index_page(&ConnectionGet($L{$F{'agent'}}));
	&process_page(&ConnectionGet($url), $url);
	&print_page();

}

exit;



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

	print STDERR qq |pip: $L{$F{'agent'}}|;

	my $in = HTML::TreeBuilder::XPath->new_from_content($_[0]);
	my @hrefs  = $in->findvalues('//a[@class="photo"]/@href');

	print STDERR qq |urls: $hrefs[0]\n|;

	return('http://www.rightmove.co.uk'.$hrefs[0]);
	
	

}

################################################################################
sub process_page {

	my $in = HTML::TreeBuilder::XPath->new_from_content($_[0]);

	my @title  = $in->findvalues('//title');
	my @descr  = $in->findvalues('//meta[@name="description"]/@content');
	my @img    = $in->findvalues('//img[@id="mainphoto"]/@src');
	my @logo   = $in->findvalues('//img[@id="branchlogo"]/@src');	
	my @price  = $in->findvalues('//div[@id="amount"]');
	$price[0] =~ s/[^0-9,]//g;
	my @agent  = $in->findvalues('//img[@id="branchlogo"]/@alt');
	my ($agent, $null) = split(/,/, $agent[0]); 
	
	$out .= qq |
	<div class="listing">	
		<h3>@title</h3>
		<p><img src="$img[0]" /></p>
		<p>$descr[0]</p>
		<p>$price[0]</p>
		<p><img src="$logo[0]" /><br />$agent</p>
		<p><a href="$_[1]">more information</a></p>
	</div>
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
    $getGARTNERmsg .= "getGartner GET GETTING PAGE: $u<p\>\n\n\n";

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
 
