#!/usr/local/bin/perl


################################################################################
################################################################################
#
#  directory setup
#
#    written by Peter Mahnke on 17 May 2005
#    based on directory.cgi
#
#
#
#
################################################################################
################################################################################

use CGI::Lite;
use DateTime;
use DBI;
use utf8;

require ("/home/stmargarets/cgi-bin/common.pl");
require ("/home/gartner/html/scholastic/common_text.pl");

#$F{'charset'} = "utf-8";
$F{'flavor'}  = "xhtml1";
$relDir = "directory"; # for image information
$CATtype;              # category list on sidebar

$rootDir = "/home/stmargarets/directory";


# Image Dir
$imageDir = "/home/stmargarets/html/images/directory/";

# create a key
$datekey      = `date +'%Y%m%d%H%M'`;
chop($datekey);

# get the date
$date      = `date +'%Y-%m-%d'`;
chop($date);

$thisScript = "/cgi-bin/directory.cgi";

my $dbh = DBI->connect("dbi:SQLite:dbname=/home/stmargarets/db/stmgrts.db","","",{ PrintError => 1, AutoCommit => 0 });


my ($sql, $sth);




################################################################################
if ($ENV{'CONTENT_LENGTH'} || $ENV{'QUERY_STRING'}) {

    $cgi = new CGI::Lite;
    $cgi->add_timestamp(0);
    $cgi->set_directory ('/home/stmargarets/html/images/directory/');
    # $cgi->filter_filename (\&imagefilename);
    
    %F = $cgi->parse_form_data;
    
    foreach (keys %F) {
	
    	if (ref($F{$_}) eq "ARRAY") {
	    
	    # array?
	    @all_values = $cgi->get_multiple_values ($F{$_});
	    
	    foreach $opt (@all_values) {
		$F{$_} .= "$opt\|";
	    }
            next;
	    
        }
	$F{$_} =~ s/\&\&\&\&\&/\n/g;
	$F{$_} =~ s/
	    //g; # funny ^M
	$F{$_} = &clean4textile($F{$_}) if (/(name|short_desc|long_desc|venue_detail|hours)/);
	
	
    }
    
    $msg .= $cgi->get_error_message;

    $F{'name'} =~ s/(\n|\r)//g;

    if ($F{'flag_venue'} eq 'yes') {                                                                                                      				
    	$F{'flag_venue'} = 1;
    } else {
        $F{'flag_venue'} = 0;
    }
    
    if ($F{'flag_display'} eq 'yes') {                                                                                                    
    	$F{'flag_display'} = 1;
    } else {
        $F{'flag_display'} = 0;
    }
    
    if ($F{'flag_stma'} eq 'yes') {                                                                                              
        $F{'flag_stma'} = 1;
    } else {
        $F{'flag_stma'} = 0;
    }

    if ($F{'flag_food'} eq 'yes') {                                                                                              
        $F{'flag_food'} = 1;
    } else {
        $F{'flag_food'} = 0;
    }


    # deal with the renaming of files
    if ($F{'file'}) {
	my $inFile  = $imageDir.$F{'file'};
	my $fileType = substr ($F{'file'}, rindex($F{'file'}, ".") + 1, 3);
	$F{'name'} = &cleanImageName($F{'name'});
	my $outFile = $imageDir.$F{'key'}."_".$F{'name'}.".".$fileType;
	rename ($inFile,$outFile );
	$msg .= "$inFile $fileType $outFile";
    }
    
    # deal with funny category underscores(Spaces) and aNd(ampersands)
    $F{'category'} =~ s/_/ /g;
    $F{'category'} =~ s/aNd/&/g;

    
} else {

    # nothing submitted... so PANIC!!!
    $TITLE = "All";
    $H1    = "All";
    &printPage(&formatIndex);
    exit;

}


################################################################################
################################################################################
# WHAT TO DO
if ($F{'action'} eq "save") {
    
    
    if (!$F{'key'}) {
	$F{'key'} = $datekey;
	&saveNewListing($F{'key'});
    } else {
	$msg .= "Key $F{'key'} present<br \>\n";
	&updateListing($F{'key'});
    }
    $dbh->commit();
    $F{'action'} = "getlisting";
    &printPage(&formatListing($F{'key'}));
    exit;
    
} elsif ($F{'action'} eq "getlisting") {
    
    &printPage(&formatListing($F{'key'}));
    exit;
    
} elsif ($F{'action'} eq "edit") {
    
    $POPUPjs = &getEditJS;
    &printListingForm($F{'key'});
    exit;
    
} elsif ($F{'action'} eq "image") {
    
    &printPage(&printUploadForm($F{'key'},$F{'name'}));
    exit;
    
} elsif ($F{'action'} eq "upload") {
    
    my $img = &getImage($F{'key'}, $F{'name'}.'_mystm', 'span-4', $relDir, $imageDir);
    $msg .= "<p>uploaded $img</p>";
    $F{'action'} = "getlisting";
    &printPage(&formatListing($F{'key'}));
    exit;
    
    
} elsif ($F{'action'} eq "editlist") {
    
    $msg .= "<a href\=\"?action\=new\"></a>";
    &printPage(&processText(&formatEditList()));
    exit;
    
} elsif ($F{'action'} eq "urllist") {
    
    &printURLlist(&formatURLlist());
    exit;
    
} elsif ($F{'action'} eq "new") {
    
    &printListingForm;
    exit;

} elsif ($F{'action'} eq "food") {

	&formatFoodList();
	exit;	
        
} elsif ($F{'action'} eq "venuelist") {
    
    &saveVenue(&formatVenueList);
    exit;
    
} elsif ($F{'action'} eq "filter") {
    
    
    $TITLE = " $F{'category'}";
    $H1    = " $F{'category'}";
    &printPage(&formatListing($F{'category'}));
    exit;
    
} else {
    
    $TITLE = " All";
    &printPage(&formatIndex);
    exit;
    
}
exit;


################################################################################
sub printURLlist {

    open (LIST, ">/home/stmargarets/urllist_directory.txt");
    print LIST $_[0];
    close (LIST);

		print <<EndofHTML;
Content-type: text/html

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org\tR/xhtml1/DTD/xhtml1-transitional.dtd">
<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head><title>Events URL List</title></head>
<body>
<h1>Google URL List Saved</h1>

<pre>
$_[0]
</pre>

</body>
</html>
EndofHTML

    return();

}

################################################################################
sub getCatOptionList {
	
	# gets list of categories based on a directory id
	my ($secondary, $main, $list, $cat_id, $category, $type, $sth) = "";
	
	if ($_[0]) {
		
		# get existing categories, if they exist...
		
		$sth = $dbh->prepare("SELECT dc.directory_category_id, dcl.name, dc.category_type 
		 					FROM directory_category AS dc 
							LEFT JOIN directory_category_list AS dcl 
							 	ON dc.directory_category_id=dcl.id
							LEFT JOIN directory AS d ON d.id = dc.directory_id
							WHERE d.id=? AND
							flag_smta
							ORDER BY dcl.name");

		$sth->execute($_[0]);

	
		$sth->bind_columns (\$cat_id, \$category, \$type);

		while ( $sth->fetch ) {
	
			if ($type) {
				# this is the main cat
				$main = "<option value\=\"$cat_id\" selected\=\"selected\">$category<\/option>\n";
				 
			} else {
				$secondary .= "<option value\=\"$cat_id\" selected\=\"selected\">$category<\/option>\n";
			}
		}
	}
	
	
	$list .= "<option value\=\"\"><\/option>\n"; # add a blank line
	
	# get list of all categories
	$sth = $dbh->prepare("SELECT DISTINCT id, name 
		 					FROM directory_category_list 
							ORDER BY name");

	$sth->execute();

	$sth->bind_columns (\$cat_id, \$category);

	while ( $sth->fetch ) {
	
		$list .= "<option value\=\"$cat_id\">$category<\/option>\n";

	}
	
	return($list, $main, $secondary);
	
}

################################################################################
sub printListingForm {

	# for editing the page

	my ($key, $name, $address1, $address2, $city, $postcode, $phone, $email, $website, $short_desc, $long_desc, $venue_detail, $hours, $promo, $flag_venue, $checked_flag_venue, $category_list, $cat_primary, $cat_secondary, $line, $img, $flag_display, $flag_smta, $checked_flag_display, $checked_flag_smta, $trader_img, $twitter, $flag_food, $vshort_desc, $small_img );

	# TODO - deal with cat list... get venue details from 
	if ($_[0]) {

		my $sth = $dbh->prepare("SELECT id, name, address1, address2, city, postcode, phone, email, website, short_description, long_description, venue_detail, hours, promo, flag_venue, flag_display, flag_smta, twitter, flag_food, vshort_desc
							FROM directory
							WHERE id=?");

		$sth->execute( $_[0] );
		
		$sth->bind_columns (\$key, \$name, \$address1, \$address2, \$city, \$postcode, \$phone, \$email, \$website, \$short_desc, \$long_desc,  \$venue_detail, \$hours, \$promo, \$flag_venue, \$flag_display, \$flag_smta, \$twitter, \$flag_food, \$vshort_desc);

		while ( $sth->fetch ) {

			$key = $datekey if (!$key);

			$img = &getImage($key, $name, '', $relDir, $imageDir);
			$img = "    <tr>\n        <td></td>\n        <td>$img<br />stmgrts image</td>\n    </tr>\n" if ($img);

			$trader_img = &getImage($key, $name.'_mystm', '', $relDir, $imageDir);
			$trader_img = "    <tr>\n        <td></td>\n        <td>$trader_img<br />traders image</td>\n    </tr>\n" if ($trader_img);
			
			$small_img = &getImage($key, $name.'_sm', '', $relDir, $imageDir);
			$small_img = "    <tr>\n        <td></td>\n        <td>$small_img</td>\n    </tr>\n" if ($small_img);			

			$checked_flag_venue = "checked\=\"checked\"" if ($flag_venue);
			$checked_flag_display = "checked\=\"checked\"" if ($flag_display);
			$checked_flag_smta = "checked\=\"checked\"" if ($flag_smta);
			$checked_flag_food = "checked\=\"checked\"" if ($flag_food);

		}
	
	}

	# get category information
	($category_list, $cat_primary, $cat_secondary) = &getCatOptionList($_[0]);
	
	my $clean_name = $name;
	$clean_name =~ s/\&/aNd/g;
	my $trader_name = $clean_name."_mystm";
	my $food_name = $clean_name."_sm";

	$line .=<<EndofText;

<h2>Directory Entry : $name [$key]</h2>

<form method="post" action="$thisScript">

    <input type="hidden" name="action" value="save" />
    <input type="hidden" name="key" value="$key" />
    <input type="hidden" name="type" value="$F{'type'}" />
<table>
    <tr>
        <td><strong>Name</strong></td>
        <td><input type="text" name="name" value="$name" size="50" /></td>
    </tr>

$img

$trader_img

$small_img
    <tr>
        <td><strong>Address</strong></td>
        <td><input type="text" name="address1" value="$address1" size="50" /><br />
            <input type="text" name="address2" value="$address2" size="50" />
        </td>
    </tr>

    <tr>
        <td><strong>City</strong></td>
        <td><select name="city">
                <option value="$city" selected="selected">$city</option>
                <option value="St Margarets">St Margarets</option>
                <option value="Twickenham">Twickenham</option>
                <option value="East Twickenham">East Twickenham</option>
		<option value="East Sheen">East Sheen</option>
                <option value="Richmond">Richmond</option>
                <option value="Ham">Ham</option>
                <option value="Barnes">Barnes</option>
                <option value="Petersham">Petersham</option>
                <option value="Strawberry Hill">Strawberry Hill</option>
                <option value="Kew">Kew</option>
                <option value="Brentford">Brentford</option>
                <option value="Hampton">Hampton</option>
                <option value="Hampton Hill">Hampton Hill</option>
                <option value="East Molesey">East Molesey</option>
                <option value="Teddington">Teddington</option>
                <option value="Isleworth">Isleworth</option>
		<option value="London">London</option>
            </select>
        </td>
    </tr>

    <tr>
        <td><strong>postcode</strong></td>
        <td><input type="text" name="postcode" value="$postcode" size="50" /></td>
    </tr>

    <tr>
        <td><strong>phone</strong></td>
        <td><input type="text" name="phone" value="$phone" size="50" /></td>
    </tr>

    <tr>
        <td><strong>twitter</strong></td>
        <td><input type="text" name="twitter" value="$twitter" size="50" /></td>
    </tr>

    <tr>
        <td><strong>email</strong></td>
        <td><input type="text" name="email" value="$email" size="50" /></td>
    </tr>

    <tr>
        <td><strong>website</strong></td>
        <td><input type="text" name="website" value="$website" size="50" /></td>
    </tr>

   <tr>
        <td><strong>very short description</strong></td>
        <td><textarea name="vshort_desc" cols="35" rows="2">$vshort_desc</textarea></td>
    </tr>

    <tr>
        <td><strong>short description</strong></td>
        <td><textarea name="short_desc" cols="35" rows="5">$short_desc</textarea></td>
    </tr>

    <tr>
        <td><strong>long description</strong></td>
        <td><textarea name="long_desc" cols="35" rows="15">$long_desc</textarea></td>
    </tr>

    <tr>
        <td><strong>venue detail</strong></td>
        <td><textarea name="venue_detail" cols="35" rows="15">$venue_detail</textarea></td>
    </tr>

    <tr>
        <td><strong>categories primary</strong></td>
        <td><select size="1" name="maincategory">
$cat_primary
$category_list
			</select><br />
            <input type="text" name="catText" size="50" value="$F{'cat'}" /></td>
    </tr>

   <tr>
        <td><strong>categories secondary</strong></td>
        <td><select multiple="multiple" size="3" name="category">
$cat_secondary
$category_list
			</select><br />
    </tr>

    <tr>
        <td><strong>hours</strong></td>
        <td><textarea name="hours" cols="35" rows="5">$hours</textarea></td>
    </tr>

    <tr>
        <td><strong>promo</strong></td>
        <td><input type="text" name="promo" value="$promo" size="50" /></td>
    </tr>

    <tr>
        <td><strong>venue flag</strong></td>
        <td><input type="checkbox" name="flag_venue" value="yes" $checked_flag_venue /></td>
    </tr>

    <tr>
        <td><strong>display flag</strong></td>
        <td><input type="checkbox" name="flag_display" value="yes" $checked_flag_display /></td>
    </tr>

    <tr>
        <td><strong>st margarets traders association flag</strong></td>
        <td><input type="checkbox" name="flag_smta" value="yes" $checked_flag_smta /></td>
    </tr>

    <tr>
        <td><strong>food listing?</strong></td>
        <td><input type="checkbox" name="flag_food" value="yes" $checked_flag_food /></td>
    </tr>
    
    
    <tr>
        <td></td>
        <td><input type="submit" /></td>
    </tr>
</table>

<h3>Images</h3>

<p><a href="$thisScript?action=image&amp;key=$key&amp;name=$clean_name" onclick="rawPopUp('$thisScript?action=image&amp;key=$key&amp;name=$clean_name', '300', '500', 'resizable=yes,scrollbars=no,toolbar=no', 'image'); return false;">upload stmgrts image</a></p>

<p><a href="$thisScript?action=image&amp;key=$key&amp;name=$trader_name" onclick="rawPopUp('$thisScript?action=image&amp;key=$key&amp;name=$trader_name', '300', '500', 'resizable=yes,scrollbars=no,toolbar=no', 'image'); return false;">upload TRADERS image</a></p>

<p><a href="$thisScript?action=image&amp;key=$key&amp;name=$food_name" onclick="rawPopUp('$thisScript?action=image&amp;key=$key&amp;name=$food_name', '300', '500', 'resizable=yes,scrollbars=no,toolbar=no', 'image'); return false;">upload small (110px wide) image</a></p>


</form>

EndofText

	
	
	&printPage($line);

}

################################################################################
sub updateListing {


	# append new cats if typed in other field
	# need to add new cats somehow $F{'category'} .= "$F{'catText'}\|" if ($F{'catText'});
	
	my @cats = split(/\|/, $F{'category'});
	
	# update directory table 
	my $sql = qq | 
	
UPDATE directory 
SET 
	name=?, 
	address1=?, 
	address2=?, 
	city=?, 
	postcode=?, 
	phone=?, 
	email=?, 
	website=?, 
	vshort_desc=?,
	short_description=?, 
	long_description=?, 
	venue_detail=?, 
	hours=?, 
	promo=?, 
	flag_venue=?, 
	flag_display=?,
	flag_smta=?,
	flag_food=?,
	twitter=?
WHERE 
	id=? 
	|;
	
	$sth = $dbh->prepare($sql);
	
	$sth->execute ($F{'name'}, $F{'address1'}, $F{'address2'}, $F{'city'}, $F{'postcode'}, $F{'phone'}, $F{'email'}, $F{'website'}, $F{'vshort_desc'}, $F{'short_desc'}, $F{'long_desc'}, $F{'venue_detail'}, $F{'hours'}, $F{'promo'}, $F{'flag_venue'}, $F{'flag_display'}, $F{'flag_smta'}, $F{'flag_food'}, $F{'twitter'}, $F{'key'});
	
	
	$msg .= qq |
	    <p>saving Event: $F{'key'} $F{'name'}</p><p><a href="$thisScript?action=edit&amp;key=$F{'key'}">edit</a></p>\n
	    |;

	# delete existing category assignments
	$sth = $dbh->prepare("DELETE FROM directory_category WHERE directory_id=?");
	$sth->execute( $F{'key'} );

	# create category if added
	$dbh->do("INSERT INTO directory_category_list (name, flag_display) VALUES ('$F{'catText'}', 1)") if ($F{'catText'});

	# insert new category assignments
	$sth = $dbh->prepare("INSERT INTO directory_category (directory_id, directory_category_id, category_type) VALUES (?,?,?)");
	
	# main cat
	$sth->execute( $F{'key'}, $F{'maincategory'}, '1' );
	
	# sub cats
	if (@cats) {
	    foreach (@cats) {
		$sth->execute( $F{'key'}, $_, '0' );
		$msg .= qq |<p>sub categories $_</p>\n|;
	    }
	}
	$dbh->commit();

	return();

}

################################################################################
sub saveNewListing {

    $msg .= "saving Event<br />";
    
    # append new cats if typed in other field
    my @cats = split(/\|/, $F{'category'});
    
    my $sql = qq |
	INSERT INTO directory
	(id, name, address1, address2, city, postcode, 
	 phone, email, website, vshort_desc, short_description, 
	 long_description, venue_detail, hours, promo, flag_venue, flag_display, 
	 flag_smta, flag_food, twitter)
	VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
	|;
    
    my $sth = $dbh->prepare($sql);

    $sth->execute($F{'key'}, $F{'name'}, $F{'address1'}, $F{'address2'},$F{'city'}, $F{'postcode'}, $F{'phone'}, $F{'email'}, $F{'website'}, $F{'vshort_desc'}, $F{'short_desc'}, $F{'long_desc'}, $F{'venue_detail'}, $F{'hours'}, $F{'promo'}, $F{'flag_venue'}, $F{'flag_display'}, $F{'flag_smta'}, $F{'flag_food'}, $F{'twitter'});
    
    # insert new category assignments
    
    # create category if added
    if ($F{'catText'}) {
	$dbh->do("INSERT INTO directory_category_list (name, flag_display) VALUES ('$F{'catText'}', 1)");
	
	$F{'maincategory'} = $dbh->func('last_insert_rowid');
    }
    
    $sth = $dbh->prepare("INSERT INTO directory_category (directory_id, directory_category_id, category_type) 
							VALUES (?,?,?)");
    # main cat
    $sth->execute( $F{'key'}, $F{'maincategory'}, '1' );
    
    # sub cats
    if (@cats) {
		foreach (@cats) {
		    $sth->execute( $F{'key'}, $_, '0' );
	    	$msg .= qq |<p>sub categories $_</p>\n|;
		}
    }
        
    return();
    
}

################################################################################
sub formatFoodList {

	# create a little food list for mystmargarets
	    
    my ($events, $sth) = "";
    
	$sth = $dbh->prepare("SELECT id, name, vshort_desc
			FROM directory
			WHERE 
			flag_food AND flag_display
			ORDER BY random()");

	$sth->execute();
	
	my ($id, $name, $vshort_desc, $img, $output) = "";
		
	$sth->bind_columns (\$id, \$name, \$vshort_desc);

	my $i = 0;
	my $cats;
	while ( $sth->fetch ) {

		# blurb
	    $vshort_desc = &processText($vshort_desc);

		$name =~ s/\n//;

 		# image
		$img = &getImage($id, $name.'_sm', '', $relDir, $imageDir);
		$img =~ s/<img/<img class="span-3"/;

		# name
		$name = &processText($name);
		$name =~ s/<p>//g; # remove <p></p> tags around the name
		$name =~ s/<\/p>//g; # remove <p></p> tags around the name

		# output
		$output .= <<ENDofTest;

<!-- start listing $id:$name --><div class="foodrole append-bottom span-9">
	<div class="span-3">
    $img
	</div>
		
	<div class="span-6 last">
	    <h3><a href="\/directory\/food\/$id">$name</a></h3>
    	$vshort_desc
	</div>
<!-- END listing $id:$name --></div>

ENDofTest

	}
	
	print <<EndofHTML;
Content-type: text/html

<div id="food" class="span-9">
$output
</div>
EndofHTML

	return();
	
	print <<EndofHTML;
Content-type: text/html

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en"> 
 
  <head> 
   <meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> 
   <meta http-equiv="X-UA-Compatible" content="IE=edge"> 
 
    <!-- heading font --> 
    <link href='http://fonts.googleapis.com/css?family=Vollkorn' rel='stylesheet' type='text/css' /> 
 
	<link rel="shortcut icon" href="/images/heart_125_transparent.png" /> 
   
	<link rel="stylesheet" href="http://www.mahnke.net/css/blueprint/blueprint/screen.css" type="text/css" media="screen, projection" /> 
	<link rel="stylesheet" href="http://www.mahnke.net/css/blueprint/blueprint/print.css" type="text/css" media="print" />    
	<!--[if IE]><link rel="stylesheet" href="http://www.mahnke.net/css/blueprint/blueprint/ie.css" type="text/css" media="screen, projection" /><![endif]--> 
 
		
	<link rel="stylesheet" href="http://mystmargarets.com/styles-site.css" type="text/css" /> 
</head> 
<body class="main-index"> 
 
	<div class="container showgrid"> 
 
		<div id="content" class="span-24 last"> 

		<div class="span-19">
		<p>some stuff here</p>
		</div>
 
<div id="food" class="span-9">
$output
</div>
</div>
</body>
</html>	
EndofHTML

   	return();	

}

################################################################################
sub formatDTtosave {

	# $F{'year'}$F{'month'}$F{'day'} $F{'hour'}:$F{'min'}

	my $dt;

	if ($_[3]) {

		# there is an hour... so make add the time

		# make min 00 if none
		$_[4] = "00" if (!$_[4]);

		$dt = "$_[0]$_[1]$_[2] $_[3]:$_[4]";

	} else {

		$dt = "$_[0]$_[1]$_[2]";

	}

	return($dt);
}

################################################################################
sub getVenueEvents {

	my ($sql, $sth, $out, $cat_name, $e_id, $host_name, $event_name, $s_d, $s_t, $e_d, $e_t);

	$FLAGsimple = 1; # get simple date icons
	
	$sql = qq |
	SELECT 
		emc.category_name, e.id, d.name, e.name, e.start_date, e.start_time, e.end_date, e.end_time
	FROM events             e
		LEFT JOIN directory d       ON (e.host_id = d.id or e.venue_id = d.id)
		LEFT JOIN event_maincategory emc ON e.id = emc.id 
	WHERE
		(start_date >= '$date'      OR 
		end_date >= '$date')       AND
		e.flag_display IS NOT NULL AND
		d.id = ?
	ORDER BY
	        e.start_date
	|;
	
	$sth = $dbh->prepare($sql);
	
	$sth->execute($_[0]);

	$sth->bind_columns (\$cat_name, \$e_id, \$host_name, \$event_name, \$s_d, \$s_t, \$e_d, \$e_t);

	while ( $sth->fetch ) {
	
		my $sd        = $s_d." ".$s_t;
		my $ed        = $e_d." ".$e_t;
		my $date        = &prepareDateIcon($sd, $ed) if ($sd);

		$out .= <<ENDofTest;
<li><a href="http://stmgrts.org.uk/event/$cat_name/$e_id">$host_name :: $event_name</a><br />$date<br /></li>
ENDofTest

	}	
	
	return($out);

}

################################################################################
sub encodeCat {

	# encode category for urls
	# input category, output encoded string
	my $encodeCat  = $_[0];
   	$encodeCat     =~ s/ /_/g;
   	$encodeCat     =~ s/&/aNd/g;
 	return($encodeCat);
 	
}

################################################################################
sub decodeCat {

	# decode category for urls
	# input category, output encoded string
	my $decodeCat  = $_[0];
   	$decodeCat     =~ s/_/ /g;
   	$decodeCat     =~ s/aNd/\&amp\;/g;
 	return($decodeCat);
 	
}

################################################################################
sub encodeURL {
	
	my $urlname = $_[0];
	$urlname =~ s/\& /\&amp\; /g;
	return($urlname);

}

################################################################################
sub formatListing {


	# processes both filter (category) request as well as a single listing request

	my ($events, $sth) = "";
		
	if ($F{'action'} eq "filter") {

		$sth = $dbh->prepare("SELECT d.id, d.name, address1, address2, city, postcode, phone, email, website, long_description, hours, dcl.name, dc.category_type
							FROM directory AS d
							LEFT JOIN directory_category AS dc ON d.id = dc.directory_id
							LEFT JOIN directory_category_list AS dcl ON dc.directory_category_id=dcl.id
						WHERE 
							dcl.name=? AND d.flag_display AND d.flag_smta
						ORDER BY 
							d.name");

	
	} else {
	
		$events = &getVenueEvents($_[0]);
	
		$sth = $dbh->prepare("SELECT d.id, d.name, address1, address2, city, postcode, phone, email, website, long_description, hours, dcl.name, dc.category_type
							FROM directory AS d
							LEFT JOIN directory_category AS dc ON d.id = dc.directory_id
							LEFT JOIN directory_category_list AS dcl ON dc.directory_category_id=dcl.id
						WHERE 
							d.id=? AND d.flag_display AND d.flag_smta");

		
	
	}
	
	$sth->execute( $_[0] );
	
	my ($entry, $key, $name, $address1, $address2, $city, $postcode, $phone, $email, $website, $description, $hours, $category, $cat_type, $initial_cat, $encodeInitialCat, $encodeCat);
		
	$sth->bind_columns (\$key, \$name, \$address1, \$address2, \$city, \$postcode, \$phone, \$email, \$website, \$description, \$hours, \$category, \$cat_type);

	my $i = 0;
	my $cats;
	while ( $sth->fetch ) {

	    $address1       .= "<br />\n" if ($address2);
	    $address2       .= "<br />\n" if ($city);
	    $city            = "$city <br />\n" if ($postcode);
	    $phone           = "<p><strong>phone</strong><br />\n$phone</p>\n" if ($phone);
	    $email           = "<p><strong>email</strong><br />\n<a href\=\"mailto:$email\">$email</a></p>\n" if ($email);
		
		if ($website) {
			my $u = $website;
			$website =~ s/http:\/\/(.[^\/]*)\//\1/i;	
			$website =~ s/http:\/\/(.*)/\1/i;	
		    $website = qq|<p><strong>website</strong><br />\n<a href\=\"$u\">$website</a></p>\n|;
		}
	    $description     =~ s/&&&&&/\n/g;
	    $description     = &processText($description);

	    if ($cat_type) {
		$initial_cat     = $category;
		$encodeInitialCat = &encodeCat($initial_cat);
	    } else {
		$encodeCat       = &encodeCat($category);
	    }
	    $cats           .= "<a href\=\"\/directory\/$encodeCat\">$category<\/a> \| ";
	    #$description     = &processText($description);
	    $hours           = "<p><strong>hours</strong></p>\n".&processText($hours) if ($hours);
    	
	    if ($key != $last_key) {
    	 	$entry .= &formatListingHTML($key, $name, $address1, $address2, $city, $postcode, $phone, $email, $website, $description, $hours, $category, $cat_type, $initial_cat, $encodeInitialCat, $encodeCat, $cats, $events);
    	 	undef $cats;
	    }
	    $last_key = $key;
    	
	}
	
   	$entry .= &formatListingHTML($key, $name, $address1, $address2, $city, $postcode, $phone, $email, $website, $description, $hours, $category, $cat_type, $initial_cat, $encodeInitialCat, $encodeCat, $cats, $events) if ($key != $last_key);
	
   	return($entry);
	
}

################################################################################
sub formatListingHTML {

	my ($key, $name, $address1, $address2, $city, $postcode, $phone, $email, $website, $description, $hours, $category, $cat_type, $initial_cat, $encodeInitialCat, $encodeCat, $cats, $events);
	
	$key              = $_[0];
	$name             = $_[1];
 	$address1         = $_[2];
	$address2         = $_[3];
	$city             = $_[4];
	$postcode         = $_[5];
	$phone            = $_[6];
	$email            = $_[7];
	$website          = $_[8];
	$description      = $_[9];
	$hours            = $_[10];
	$category         = $_[11];
	$cat_type         = $_[12];
	$initial_cat      = $_[13];
	$encodeInitialCat = $_[14];
	$encodeCat        = $_[15];
	$cats             = $_[16];
	$events           = qq ~
	
	<p><strong>upcoming events from <a href="http://stmgrts.org.uk/events/">stmgrts.org.uk</a></strong></p>
	<ul>
	$_[17]
	</ul>
	
	~ if ($_[17] && $_[17] != -1 );

	# ORIG INPUT $key, $name, $address1, $address2, $city, $postcode, $phone, $email, $website, $description, $category, $hours, $promo

	my $img            = &getImage($key, $name.'_mystm', 'span-4', $relDir, $imageDir);

	my $map            = "<p><a href\=\"http://maps.google.co.uk?q=$_[5]\">map</a></p>" if ($postcode);
	
	$map            =~ s/ Public House//;
	
	$keywords .= "$name, $initial_cat, ";
	$TITLE = "$initial_cat : $name";
	$H1 = "$initial_cat";
	
	my $PARAopen;
	my $PARAclose;
	if ($address1 || $address2 || $city || $postcode) {
	    $PARAopen  = "<p><strong>location</strong><br />\n";
	    $PARAopen  = "<p><strong>address</strong><br />\n" if ($postcode);
	    $PARAclose = "</p>";
	    $keywords .= "$city, $postcode, ";
	}
	
	$keyword =~ s/ /, /g;
	$keyword =~ s/, , /, /g;
	
	# remove trailing ' |' from category	
	chop($cats);
	chop($cats);
	
	my $entry;
	
	if ($F{'action'} eq "filter") {
	
		# small listing (category page)

		my $more = qq ~<p><a href="\/directory\/$encodeInitialCat\/$key">For full listing&#8230;</a></p>~ if ($hours||$events);
	
		$entry .= qq ~

<!-- start listing $key:$name -->

<div class="span-14 prepend-top ">
   
    <div class="span-4">

    	<!-- image $key $name-->
    	$img

    </div>

    <div class="span-10 last">

    	<h2><a href="\/directory\/$encodeInitialCat\/$key">$name</a></h2>
    
    	<!-- description -->
	    $description

		<div class="span-6 border">

		    <!-- email -->
		    $email

	    	<!-- phone -->
		    $phone

	    	<!-- website -->
	    	$website
		
	    	<!-- categories -->
		    <p>$cats</p>

			<!-- more detailed listing link -->
			$more

		</div>
		
		<div class="span-4 last">

	    	<!-- start address -->
	    	$PARAopen
   	    		$address1
    	   		$address2
       			$city
       			$postcode
    		$PARAclose
    		<!-- end address -->

		    <!-- map -->
		    $map

		</div>
    </div>
</div>

<!-- END listing $key:$name -->
      <hr /> 
      <hr class="space" /> 
	~;
	} else {
	
		# full listing (single listing)
	
		$entry .= qq ~

<!-- start listing $key:$name -->

<div class="span-14 prepend-top ">
   
    <div class="span-4">

    	<!-- image $key $name-->
    	$img

    </div>

    <div class="span-10 last">

    	<h2><a href="\/directory\/$encodeInitialCat\/$key">$name</a></h2>
    
    	<!-- description -->
	    $description

		<div class="span-6 border">

		    <!-- email -->
		    $email

	    	<!-- website -->
	    	$website
		
	    	<!-- phone -->
		    $phone

		</div>
		
		<div class="span-4 last">

	    	<!-- start address -->
	    	$PARAopen
   	    		$address1
    	   		$address2
       			$city
       			$postcode
    		$PARAclose
    		<!-- end address -->

		    <!-- map -->
		    $map

		</div>
		
		<hr class="space" />
		
	    <!-- hours -->
	    $hours

    </div>

	<!-- events -->
	$events

   	<!-- categories -->
    <p>$cats</p>

</div>

<!-- END listing $key:$name -->
      <hr /> 
      <hr class="space" /> 
	~;

	}
	
	return($entry);

}

################################################################################
sub formatIndex {

	$sql = qq |
SELECT distinct d.id, d.name, dcl.name, dc.category_type
FROM directory AS d
LEFT JOIN directory_category AS dc ON d.id = dc.directory_id
LEFT JOIN directory_category_list AS dcl ON dc.directory_category_id=dcl.id
WHERE d.flag_display AND d.flag_smta
ORDER BY dcl.name ASC
	|;

	$sth = $dbh->prepare($sql);

	$sth->execute();
	
	my ($key, $name, $category, $cat_type, $encodeCat, $out, %CAT, $lastCat, $count, $totalCount, $encodeURL);
		
	$sth->bind_columns (\$key, \$name,\$category, \$cat_type);

	while ( $sth->fetch ) {
	
		$count++;
		
		$encodeCat = &encodeCat($category);
		$encodeURL = &encodeURL($category);
		
		if ($cat_type) {
			# encode main cat for url
			$initCatEncode = &encodeCat($category);
			$totalCount++;
		}
		
		if ($category ne $lastCat) {
		
			# new or initial cat
			$out .= "<\/ul>\n" if ($out);
			$out .= "<h3\><a href\=\"\/directory\/$encodeURL\">$category</a><\/h3\>\n<ul\>\n";
			$cat .= "<li><a href\=\"\/directory\/$encodeURL\">$category [$count]</a></li>";
			undef $count;
		
		}
		
		$out .= "<li\><a href\=\"\/directory\/$initCatEncode\/$key\"\>$name<\/a\><\/li\>\n\n"; # rewrite version 
		# $out .= "<li\><a href\=\"$thisScript?action=getlisting&amp;key=$key\"\>$name<\/a\><\/li\>\n"; # get version
		
		$lastCat = $category;

	}

	$out .= "\n<\/ul>\n\n";

	$CATtype = <<EndofText;
					<h2>Category Filter</h2>
					<div id="cat_filter">
                        <ul>
                            <li><a href\=\"\/directory\">All [$totalCount]</a></li>
                            $cat
                        </ul>
                    </div>
EndofText

	return($out);

}

################################################################################
sub getCategoryMenu {
	
	$sql = qq |
SELECT      dcl.id, dcl.name, count(distinct d.id) 
FROM        directory_category       AS dc
LEFT JOIN   directory_category_list  AS dcl   ON   dc.directory_category_id=dcl.id
LEFT JOIN   directory                AS d     ON   dc.directory_id=d.id
WHERE d.flag_display AND d.flag_smta
GROUP BY    dcl.name	
	|;
	
	$sth = $dbh->prepare($sql);

	$sth->execute();

	my ($id, $category, $cat_total, $total, $out, $encodeCat, $encodeURL) = "";

	$sth->bind_columns (\$id, \$category, \$cat_total);

	while ( $sth->fetch ) {
		
		if ($category) {
			$total += $cat_total;
		}
		
		$decodeCat = &decodeCat($category);
		$encodeURL = &encodeURL(&encodeCat($category));
		$cat .= "<li><a href\=\"\/directory\/$encodeURL\">$decodeCat [$cat_total]</a></li>" if ($cat_total > 0);
		
	}
	
	$out = qq ~
	<div id="directory_menu" class="span-5">
	    <h2>Category Filter</h2>
	    <div id="cat_filter">
	    <ul>
	    <li><a href\=\"\/directory\">All [$total]</a></li>
	    $cat
	    </ul>
	    </div>
	    </div>
	    ~;

		return($out);
	
	
}

################################################################################
sub formatSimpleListing {

    my $key            = $_[0];
    my $name           = $_[1];
    my $address1       = "$_[2]<br />\n" if ($_[2]);
    my $address2       = "$_[3]<br />\n" if ($_[3]);
    my $city           = "$_[4]<br />\n" if ($_[4]);
    my $postcode       = $_[5];
    my $phone          = "<p>$_[6]</p>\n" if ($_[6]);
    my $email          = "<p><a href\=\"mailto:$_[7]\">$_[7]</a></p>\n" if ($_[7]);
    my $website        = "<p><a href\=\"$_[8]\">$_[8]</a></p>\n" if ($_[8]);
    my $description    = &processText($_[9]);
       $description    = substr ($description, 0, index ($description, "<\/p\>")+ 4);
    my ($cats, $prime) = &processCategory($_[10], 'html');
    my (@cats) = split (/\|/, $_[10]);
    my $hours          = "<p><strong>hours</strong></p>".&processText($_[11]) if ($_[11]);
    my $promo          = $_[12];
    my $events         = $_[13];
	my $img            = &getImage($key, $name.'_mystm', 'span-4', $relDir, $imageDir);
	# my $map = "<a href\=\"http://maps.google.co.uk?q=$address1+$address2+$city+$postcode\">map</a>" if ($postcode);
    my $map            = "<p><a href\=\"http://maps.google.co.uk?q=$_[1],+$_[2],+$_[3],+$_[4],+$_[5]\">map</a></p>" if ($postcode);
	   $map            =~ s/ Public House//;
    my $PARAopen;
    my $PARAclose;

    $keywords .= "$_[1], ";

    if ($address1 || $address2 || $city || $postcode) {
    	$PARAopen  = "<p><strong>location</strong><br />\n";
    	#$PARAopen  = "<p><strong>address</strong><br />\n" if ($postcode);
    	$PARAclose = "</p>";
    	$keywCity{$_[4]} = $_[4];
    }

    $keyword =~ s/ /, /g;
    $keyword =~ s/, , /, /g;

    foreach (@cats) {
	$$_{$name} .= "<li\><a href\=\"\/directory\/$prime\/$key\"\>$name<\/a\><\/li\>\n";
    }


    return();

}

################################################################################
sub formatVenueList {

	# gets all the items in the database flagged as a venue

	$sth = $dbh->prepare(qq|
SELECT d.id, d.name, dcl.name
			     FROM directory AS d
			     LEFT JOIN directory_category AS dc ON d.id = dc.directory_id
			     LEFT JOIN directory_category_list AS dcl ON dc.directory_category_id=dcl.id
			     WHERE 
			     d.flag_venue AND 
			     d.flag_display AND 
			     dcl.flag_display 
			     ORDER BY d.name ASC|);

	$sth->execute();
	
	my ($key, $name, $category, $encodeCat, $entry);
		
	$sth->bind_columns (\$key, \$name, \$category);

	while ( $sth->fetch ) {

 	   my $encodeCat = &encodeCat($cat);
 	   $entry .= "$name\thttp://www.stmgrts.org.uk/directory/$encodeCat/$key\n";

	}

	return($entry);

}

################################################################################
sub formatIncludeList {

	# page for newsletter
	
	$sth = $dbh->prepare("SELECT d.id, d.name, dcl.name
							FROM directory AS d
							LEFT JOIN directory_category AS dc ON d.id = dc.directory_id
							LEFT JOIN directory_category_list AS dcl ON dc.directory_category_id=dcl.id
						WHERE 
							d.flag_venue='1' AND d.flag_display AND d.flag_smta
							dc.category_type='1' 
						ORDER BY d.name ASC");

	$sth->execute();
	
	my ($key, $name, $category, $encodeCat, $entry);
		
	$sth->bind_columns (\$key, \$name, \$category);

	while ( $sth->fetch ) {

		$encodeCat = &encodeCat($category);

		$entry .= <<ENDofTest;
<li><a href="/directory/$encodeCat/$key" title\=\"See more details on $name\">$name</a></li>
ENDofTest

	}

	return($entry);

}

################################################################################
sub formatEditList {

	# page of all listings for me to use to find things to edit...

	$sth = $dbh->prepare("SELECT d.id, d.name, dcl.name, d.flag_display
							FROM directory AS d
							LEFT JOIN directory_category AS dc ON d.id = dc.directory_id
							LEFT JOIN directory_category_list AS dcl ON dc.directory_category_id=dcl.id
							WHERE dc.category_type='1' 
							ORDER BY d.flag_display DESC, d.name ASC");

	$sth->execute();

	my ($key, $name, $category, $encodeCat, $entry, $flag_display);

	$sth->bind_columns (\$key, \$name, \$category, \$flag_display);

	while ( $sth->fetch ) {

		$encodeCat = &encodeCat($category);

		$entry .= <<ENDofTest;
	<li><a href="$thisScript?action\=edit\&amp\;key\=$key">$name</a> [key: $key] [category: $category] [display: $flag_display] [<a href="/directory/$encodeCat/$key">view</a>]</li>
ENDofTest
	
	}
	
	$entry  = qq |\n<p><a href="?action=new">NEW</a></p>\n\n<ul>\n| . $entry . qq |\n</ul>\n\n<p><a href="?action=new">NEW</a></p>|;

	return($entry);


}

################################################################################
sub formatURLlist {
	
	# page for Google to know what to index

	$sth = $dbh->prepare("SELECT distinct d.id, d.name, dcl.name
							FROM directory AS d
							LEFT JOIN directory_category AS dc ON d.id = dc.directory_id
							LEFT JOIN directory_category_list AS dcl ON dc.directory_category_id=dcl.id
							WHERE d.flag_venue='1' AND d.flag_display='1'  
									AND dcl.flag_display='1' AND dcl.flag_smta
								ORDER BY d.name ASC");

	$sth->execute();

	my ($key, $name, $category, $encodeCat, $entry);

	$sth->bind_columns (\$key, \$name, \$category);

	while ( $sth->fetch ) {

		$encodeCat = &encodeCat($category);

		$entry .= <<ENDofTest;
http://www.stmgrts.org.uk/directory/$encodeCat/$key  changefreq=daily priority=0.6
ENDofTest

	}

	return($entry);

}

################################################################################
sub printPage {

	my $head   = &getInclude('/home/mystmgrts/html/html_head.incl');
    my $header = &getInclude('/home/mystmgrts/html/html_header_full.incl');
    my $nav    = &getInclude('/home/mystmgrts/html/html_side_column.incl');
    my $footer = &getInclude('/home/mystmgrts/html/html_footer.incl');

    $WINDOWname = "main";
    $WINDOWname = "child" if ($F{'action'} eq "image");

	my $catList = &getCategoryMenu();
	$nav =~ s/<!-- include local subnav here -->/$catList/; # add directory menu to side column
    $nav =~ s/&(?!#?[xX]?(?:[0-9a-fA-F]+|\w{1,8});)/&amp;/g;

	# build keywords for city then postcode
	foreach (sort keys %keywCity) {
		$keywords .= "$_, ";
	}

    $keyword =~ s/ /, /g;
    $keyword =~ s/, , /, /g;
    
    $_[0] =~ s/&(?!#?[xX]?(?:[0-9a-fA-F]+|\w{1,8});)/&amp;/g;
    
    my $n = int(rand(3))+1;
    my $banner_img = qq|/images/banner_traders$n.jpg|;

		print <<EndofHTML;
Content-type: text/html

$head

        <title>$TITLE :: My St Margarets </title>

        <script type="text/javascript">
$POPUPjs
        </script>

 </head>

<body id="category">
 
	<div class="container">

		<div id="content" class="span-24 last">

$header

			<div id="entries" class="span-14">
			
			<div id="intro">
					<img src="$banner_img" class="span-14" alt="Support your local traders -- look for the heart logo..." />
			<!-- /intro --></div>

			
                    <h2>Traders :: $H1</h2>

$_[0]


<p>$help</p>


<p>$msg</p>

       <!-- /entries --></div>
$nav

	<!-- messages -->
	
<pre>
$msg
</pre>

	<!-- / content --></div>

$footer

<!-- / container --></div>

	</body>
</html>
EndofHTML


}

################################################################################
sub getCatList{

	# get all category listings
	$sth = $dbh->prepare("SELECT id, name FROM  directory_category_list ORDER BY name ASC");
	
	#SELECT dir_name, dir_name FROM directory_maincategory WHERE id=?");

	$sth->execute();

	my ($cat_id, $name, $out) = "";

	$sth->bind_columns (\$cat_id, \$name);

	while ( $sth->fetch ) {

		$out .= "<option value\=\"$cat_id\"\>$name</option\>\n";

	}

	return($out);

}

################################################################################
sub processCategory {

	# turn '|' seperated list into something more appealing

	my $out;
	my $primary;
	my (@cats) = split (/\|/, $_[0]);
	my $FLAGfilter = 0;

	foreach (@cats) {

	    my $encode = $_; # create an encoded version with _ for spaces
	    $encode =~ s/ /_/g;

		if ($_[1] eq "form") {

			$out .= "<option value\=\"$encode\" selected\=\"selected\">$_</option>\n";

		} elsif ($_[1] eq "html") {

		    $out .= "<a href\=\"\/directory\/$encode\">$_<\/a> \| ";
		    $primary = "$_" if (!$primary);

		} elsif ($_[1] eq "raw") {

		    $primary = "$_" if (!$primary);
		    $out .= "$_\|";
		    $CAT{$_}++;

		    if ($F{'action'} eq "filter" && $F{'category'} eq $_ ) {
			$FLAGfilter = 1;
		    }

		} else {

		    $out .= "don't know what to do<br/>";

		}

	    }

	# remove trailing \|
	if ($_[1] eq "html") {
	    chop($out);
	    chop($out);
	}

	return (0,0) if ($_[1] eq "raw" && $F{'action'} eq "filter" && !$FLAGfilter);

	return ($out, $primary);

}

################################################################################
sub getLatLong {

    use LWP::Simple;

    $_[0] =~ s/<(.[^>]*)>//g;

    my @google = split('\n', get("http://maps.google.co.uk/?q=$_[0]"));
    $msg .= "googleurl http://maps.google.co.uk/?q=$_[0]  ";
    foreach (@google) {
	
		# parse page for <center lat="51.454405" lng="-0.319508"/>
		# parse page for center: {lat: 51.467302,lng: -0.333446}
		#if (/<center lat\=\"(.[^\"]*)\" lng\=\"(.[^\"]*)/) {
		if (/center: \{lat: (.[^,]*),lng: (.[^\}]*)/) {
	    	my $lat = $1;
	    	my $lng = $2;
	    	$msg .= "lat $lat lng $lng  ";
	    	return ($lng.','.$lat);
		}
	
    }
    
}

################################################################################
sub printMap {


    my $point = &getLatLong($_[0]);

    my $mapHTML =<<EOF;

<!-- Google Map for $_[0] at $point-->

    <div id="map" style="width: 300px; height: 200px"></div>
    <script type="text/javascript">
    //<![CDATA[
    
    var map = new GMap(document.getElementById("map"));
    map.addControl(new GSmallMapControl());
    map.centerAndZoom(new GPoint($point), 1);
    var marker = new GMarker(new GPoint($point));
    map.addOverlay(marker);
    
    //]]>
    </script>

EOF

    return($mapHTML);

}
