#!/usr/local/bin/perl

use CGI::Lite;
use DBI;
use MIME::Lite;

require ("/home/stmargarets/cgi-bin/common.pl");

my $email_to   = qq |Simon Chapman <simonchapman\@stm.demon.co.uk>|;
my $email_from = qq |peter\@mahnke.net|;
my $email_bcc  = qq |peter\@mahnke.net|;


my $dbh = DBI->connect("dbi:SQLite:dbname=/home/mystmgrts/commercial.db","","",{ RaiseError => 1, AutoCommit => 1 });

my $date      = `date +'%Y-%m-%d'`;
chop($date);

my $thisScript = qq |http://www.mystmargarets.com/cgi-bin/commercial.cgi|;



################################################################################
# read cgi post/get
if ($ENV{'CONTENT_LENGTH'} || $ENV{'QUERY_STRING'}) {

    $cgi = new CGI::Lite;
    %F = $cgi->parse_form_data;
    
    
} else {

	&printPage(&form());
	exit;
	
}

################################################################################
# What to do

if ($F{'a'} eq "Submit") {

	&save();
	&email();
	&printPage(&form());
	exit;
	
} elsif ($F{'a'} eq "view") {

	&printPage(&view());

} elsif ($F{'a'} eq "delete") {

	&delete();
	&printPage(&view());


} else {

	&printPage(&form());
	exit;

}	
exit;



################################################################################
sub delete {

	return (0) if (!$F{'id'});

	my $sth = $dbh->prepare("DELETE FROM contact WHERE id=?");
	$sth->execute($F{'id'});

	$msg_class = "notice";
	$msg = qq |<h4>Deleted</h4>
	<p>Successfully detleted id: $F{'id'}</p>|;
	
	return();
}

################################################################################
sub view {

	if ($F{'id'}) {
	
		# single view
		my $sql = qq |
	SELECT 	name, contact, size, business, usage, note, created_on
	FROM contact
	WHERE id = ?
		|;

		my $sth = $dbh->prepare($sql);

		$sth->execute($F{'id'});

		my ($name, $contact, $size, $business, $usage, $note, $created_on) = "";

		$sth->bind_columns (\$name, \$contact, \$size, \$business, \$usage, \$note, \$created_on);

		while ( $sth->fetch ) {
	
			$out = qq |
<h2>New commercial property contact [$F{'id'}]</h2>

<h3>Name</h3>

<p>$name</p>

<h3>Contact</h3>

<p>$contact</p>

<h3>Size requred</h3>

<p>$size</p>

<h3>Business nature</h3>

<p>$business</p>

<h3>Business usage type</h3>

<p>$usage</p>

<h3>Additional note</h3>

<p>$note</p>

<h3>Date</h3>

<p><em>$date</em></p>

<p><a href="$thisScript?a=view">View all</a></p>
			
			|;
	
		}


	} else {
	
		# full view 
		
		my $sql = qq |
	SELECT id, name, created_on
	FROM contact	
		|;
		my $sth = $dbh->prepare($sql);

		$sth->execute();

		my ($id, $name, $created_on ) = "";

		$sth->bind_columns (\$id, \$name, \$created_on);

		while ( $sth->fetch ) {
	
			$out .= qq |     <li><a href="$thisScript?a=view&amp;id=$id">$name</a> - <em>$created_on</em></li>\n|;
	
		}
	
		$out = qq |
<h2>New commercial property contacts</h2>

<ul>
$out
</ul>		
		|;

	}
	
	return($out);

}

################################################################################
sub email {


	my $email_subject = qq |mystmargarets.com - commercial property contact - $F{'name'}|;
	
	my $email_text = qq |

New commercial property contact

== Name == 

$F{'name'}

== Contact ==

$F{'contact'}

== Size requred ==

$F{'size'}

== Business nature ==

$F{'business'}

== Business usage type ==

$F{'usage'}

== Additional note == 

$F{'note'}

== Date ==

$date

view online: $thisScript?a=view&amp;id=$F{'id'}

	
	|;
		
	my $email_html = qq |
<h2>New commercial property contact</h2>

<h3>Name</h3>

<p>$F{'name'}</p>

<h3>Contact</h3>

<p>$F{'contact'}</p>

<h3>Size required</h3>

<p>$F{'size'}</p>

<h3>Business nature</h3>

<p>$F{'business'}</p>

<h3>Business usage type</h3>

<p>$F{'usage'}</p>

<h3>Additional note</h3>

<p>$F{'note'}</p>

<h3>Date</h3>

<p><em>$date</em></p>

<p><a href="$thisScript?a=view&amp;id=$F{'id'}">view online</a></p>
	
	|;


   ### Create the multipart "container":                                                                               
                         
    MIME::Lite->send("sendmail", "/usr/sbin/sendmail -t >& /dev/null");
    my $mail = MIME::Lite->new(
                           From    =>$email_from,
                           To      =>$email_to,
                           Bcc     =>$email_bcc,
                           Subject =>$email_subject,
                           Type    =>'multipart/alternative'
                           );
                                                    
    $mail->attach(
                 Type     =>'TEXT',
                 Data     =>$email_text
                 );

    ### Add the image part:                                                                                             
                         
    $mail->attach(
                 Type     =>'text/html',
                 Data     =>$email_html
                 );
    $mail->send;

	return();

}

################################################################################
sub save {

	if (!$F{'name'} || !$F{'contact'} || !$F{'business'}) {
		
		# missing required field
		
		$msg_class = "error";
		$msg = qq |<h4>Sorry</h4>
	<p>You didn't fill in all the required fields.  Please check your form and re-submit</p>|;
		
	}

	my $table = qq|
create table contact (
	id         integer primary key autoincrement,
	name       text, 
	contact    text,
	size       text,
	business   text,
	usage      text,
	note       text,
	created_on timestamp
);	
	|;
	
	my $test = $dbh->selectrow_array(qq|select id from contact where id=$F{'id'}|) if ($F{'id'});
	
	if ($test) {
	
		# update
	
		my $sql = qq |
	UPDATE contact
	SET 
		name     = ?,
		contact  = ?,
		size     = ?,
		business = ?,
		usage    = ?,
		note     = ?
	WHERE
		id = ?
		|;
		
		 my $sth = $dbh->prepare($sql);

    	$sth->execute($F{'name'}, $F{'contact'}, $F{'size'},$F{'business'}, $F{'usage'}, $F{'note'}, $F{'id'});

		
	
	
	} else {
	
		# insert

		# save into DB
		 my $sql = qq |
	INSERT INTO contact
	(name, contact, size, business, usage, note, created_on)
	VALUES (?,?,?,?,?,?,?)
		|;
    
	    my $sth = $dbh->prepare($sql);

    	$sth->execute($F{'name'}, $F{'contact'}, $F{'size'},$F{'business'}, $F{'usage'}, $F{'note'}, $date);

    	$F{'id'} = $dbh->func('last_insert_rowid')

	}
    
    
	$msg_class = "success";
	$msg = qq |<h4>Thank you.</h4>
	<p>We will be in touch when any suitable properties come on the market.</p>|;

	return();
    

}



################################################################################
sub form {


	my $out = qq |

<div class="span-12">

<h2>Looking for commerarial property in St Margarets?</h2>

<p>One of the aims of the St Margarets Traders Association is to ensure that our retail and commercial units are occupied and are successfully trading.  Availability of vacant commercial property is scarce in the area. To ensure that any units that become vacant are filled as quickly as possible the St Margarets Traders Association keeps a database of individuals and companies interested in commercial property in the area. Should a property come on to the market or about to come on to the market we then provide the landlord/business owner with the list of interested parties. The aim of this initiative is to ensure that properties are let as quickly as possible.</p>
 
<p><em>To register your interest in a commercial property in the area please enter your contact details below. We will then alert you to any units that come onto the market.</em></p>
 

<form id="contact" action="$thisScript" method="post">

<fieldset>

<legend></legend>

<input type="hidden" name="id" value="$F{'id'}" />

<p>
	<label for="name">Your name:</label><br />
	<input type="text" class="title" id="name" name="name" value="$F{'name'}" /><br />
	<em>required</em>
</p>
 
<p>
	<label for="contact">Contact details:</label><br />
	<textarea name="contact" id="contact" rows="3" cols="20" style="height: 5em;">$F{'contact'}</textarea><br />
	<em>required</em>
</p>

<p>
	<label for="size">Approx size of property you are interested in:</label><br />
	<input type="text" class="title" id="size" name="size" value="$F{'size'}" />
</p>
 
<p>
	<label for="business">Nature of business:</label><br />
	<input type="text" class="title" id="business" name="business" value="$F{'business'}" /><br />
	<em>required</em>
</p>
 
<p>
	<label for="usage">Type of business usage required (eg A1 A2 A3 etc)</label><br />
	<input type="text" class="title" id="usage" name="usage" value="$F{'usage'}" />
</p>

<p>
	<label for="note">Additional note:</label><br />
	<textarea name="note" id="note" rows="5" cols="20">$F{'note'}</textarea>
</p>


<p>
	<input type="submit" name="a" value="Submit" />
</p>
 
 
<p>Your details will be held confidentially and are only passed on to a landlord/property owner/agent should a suitable property come onto the market. Please note: St Margarets enjoys a full occupancy rate for its commercial property and is a much sort after area. Whilst we are aware of a few properties that my come onto the market in 2012 availability of units is scarce.</p>

</form>

</div>	
	
	|;

	return($out);

}


################################################################################
sub printPage {

	my $head   = &getInclude('/home/mystmgrts/html/html_head.incl');
    my $header = &getInclude('/home/mystmgrts/html/html_header_full.incl');
    my $nav    = &getInclude('/home/mystmgrts/html/html_nav_hor.incl');
    my $footer = &getInclude('/home/mystmgrts/html/html_footer.incl');

	$msg_class = "notice" if (!$msg_class && $msg);
	$msg = qq |
<div class="$msg_class span-12">
$msg
</div>
	| if ($msg);

	print <<EndofHTML;
Content-type: text/html

$head

	<title>Commercial property interest form :: My St Margarets </title>

 </head>

<body id="category">
 
	<div class="container">

		<div id="content" class="span-24 last">

$header

			<div id="entries" class="span-14">
			
$nav


$msg
			
$_[0]


       <!-- /entries --></div>

	<!-- / content --></div>

$footer

<!-- / container --></div>

	</body>
</html>
EndofHTML


}
