#!/usr/local/bin/perl

##############################################################
##############################################################
#
# ad.cgi
#
#  modified
#   - 8 Oct 2008 - added summary table for tracker
#   - 4 Jan 2010 - hid banners older than 30 days
#                  hid sites with is_display flag
#
##############################################################
##############################################################


use CGI::Lite;
use DBI;

my $dbh = DBI->connect("dbi:Pg:dbname=ads","pmahnke","hi11top",{ RaiseError => 1, AutoCommit => 1    });
my $date      = `date +'%Y-%m-%d'`;
chop($date);
my $thisScript = "/cgi-bin/ads.cgi";
my $msg; 

# directories
my $rel_path = "/images/promos/"; # what a web browser needs to know
my $abs_path = "/home/mystmgrts/html".$rel_path;  # what this app needs to know

################################################################
if ($ENV{'CONTENT_LENGTH'} || $ENV{'QUERY_STRING'}) {

    $cgi = new CGI::Lite;
    $cgi->add_timestamp(0);
    $cgi->set_directory ('/tmp/');
    $cgi->filter_filename (\&clean_filename);
    %F = $cgi->parse_form_data;
    
    $relDir .= "/".$F{'site'}."/";
    $imageDir .= $relDir;
    
    &checkDir($imageDir);

} else {

    # nothing submitted... so PANIC!!!
    exit;

}

if ($F{'a'} eq "contacts") {

    &print_page(&contacts_read());

} elsif ($F{'a'} eq "contact_edit") {

	&print_page(&contact_edit());

} elsif ($F{'a'} eq "contact_new") {

	&print_page(&contact_new());

} elsif ($F{'a'} eq "contact_save") {

	&contact_save(); #save the contact
	&print_page(&contacts_read());
    
} elsif ($F{'a'} eq "advertisers") {

	&print_page(&advertisers_read());

} elsif ($F{'a'} eq "advertiser_view") {

	&print_page(&advertiser_view());
	
} elsif ($F{'a'} eq "advertiser_edit") {

	&print_page(&advertiser_edit());

} elsif ($F{'a'} eq "advertiser_new") {

	&print_page(&advertiser_new());

} elsif ($F{'a'} eq "advertiser_save") {

	&advertiser_save();

	if ($F{'c_id'} && $F{'ad_id'}) {
		# changing contact to new person
		&print_page(&advertisers_read());
		exit;

	} else {
		# new contact
		&print_page(&contact_new());	
	}
	
} elsif ($F{'a'} eq "advertiser_contact_save") {
	
	&advertisers_contacts_save(); # save the contact
	&print_page(&advertiser_edit());
	

} elsif ($F{'a'} eq "banners") {

	&print_page(&banners_read());

} elsif ($F{'a'} eq "banner_edit") {

	&print_page(&banner_edit());
	
} elsif ($F{'a'} eq "banner_new") {

	&print_page(&banner_new());
	
} elsif ($F{'a'} eq "banner_zone_save") {

	&print_page(&banner_zone_save());	

} elsif ($F{'a'} eq "banner_zone_remove") {

	&print_page(&banner_zone_remove());
	
} elsif ($F{'a'} eq "zones") {

	&print_page(&zones_read());

} elsif ($F{'a'} eq "zone_edit") {

	&print_page(&zone_edit());

} elsif ($F{'a'} eq "zone_new") {

	&print_page(&zone_new());

} elsif ($F{'a'} eq "zone_save") {

	&print_page(&zone_save());
	
} elsif ($F{'a'} eq "reset_tracker") {

	&print_page(&reset_tracker());
	
} elsif ($F{'a'} eq "sites") {

	&print_page(&sites_read());

} elsif ($F{'a'} eq "site_edit") {

	&print_page(&site_edit());
	
} elsif ($F{'a'} eq "site_new") {

	&print_page(&site_new());

} elsif ($F{'a'} eq "site_view") {

	&print_page(&site_view());

} elsif ($F{'a'} eq "site_save") {

	&print_page(&site_save());

} elsif ($F{'a'} eq "stats") {
	
	&print_page(&stats());
	
} elsif ($F{'a'} eq "stat_detail") {
	
	&print_page(&stat_detail());

} elsif ($F{'a'} eq "banner_save") {
	
	&banner_save();
	
	if ($F{'file_pointer'}) {
		
		# image was just uploaded

		# check that we can move it were we want
		$F{'tmp_file'} = "/tmp/".$F{'file_pointer'}; # location of uploaded file
		$F{'new_file'} = $abs_path.$F{'file_pointer'}; # location where there file will go
		$F{'rel_file'} = $rel_path.$F{'file_pointer'}; # location where there file will go

		if (&checkFile($F{'new_file'})) {

			# file already exists... so need to ask user
			# to rename or overwrite
			&print_page(&overwriteOrUpload);
			
		} else {

			# move the file to the target directory
			`mv $F{'tmp_file'} $F{'new_file'}`;
			&banner_save_img();
	
		}
	
	}
	
	&print_page(&banners_read());


} elsif ($F{'a'} eq "overwrite") {

    # user elected to overwrite the existing file...
	# move the file to the target directory
	
	my $tmpFile = "/tmp/".$F{'file_pointer'};
	my $newFile = $abs_path.$F{'file_pointer'};

	`mv $tmpFile $newFile`;
	`rm $tmpFile` if (-e "$tmpFile");

	$F{'msg'} = "success";	
	$msg .= "Replaced banner $F{'file_pointer'} $tmpFile $newFile\n";

	&banner_save_img();
	&print_page(&banners_read());
    
    

} elsif ($F{'a'} eq "rename") {

      # user elected to rename the file

	if (!$F{'new_file_pointer'}) {

		# user didn't give a new filename... so make one up
		my ($file, $ext) = split (".", $F{'file_pointer'});
		$F{'new_file_pointer'} = $file."_new.".$ext;

	}

	my $tmpFile = "/tmp/".$F{'file_pointer'};
    my $newFile = $abs_path.$F{'new_file_pointer'};

	`mv $tmpFile $newFile`;
	`rm $tmpFile` if (-e "$tmpFile");
	
	$F{'file_pointer'} = $F{'new_file_pointer'};
	
	$F{'msg'} = "success";	
    $msg .= "Saved new banner $F{'new_file_pointer'}\n";

	&banner_save_img();
	&print_page(&banners_read());
    


} else {
	
	&print_page(&start);
	exit;

}
    
exit;    
    

################################################################################    
sub start {

	#my ($sql, $sth, $out);
	
	$sql = qq |
	SELECT
	FROM 
	LEFT JOIN
	WHERE
	
	|;
	$out .= "<h1>start page</h1>";
	foreach (keys %F) {
		$out .= "$_ $F{$_}<br />\n";
	}
	return($out);
}
    
    
################################################################################    
sub contacts_read {

	my ($sql, $sth, $out);
	my ($id, $name, $email, $phone);
	
	$sql = qq |
	SELECT id, name, email, phone  
	FROM contacts
	ORDER BY 2
	|;

	$sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$name, \$email, \$phone);

	$out .= "\n<h1>Contacts</h1>\n\n";

    while ( $sth->fetch ) {

		$out .= qq |<li><a href="?a=contact_edit&amp;c_id=$id">$name</a></li>\n|;
    }
    
	$out .= qq |<li><a href="?a=contact_new">Add new contact</a></li>\n|;

	return($out);
	
}


################################################################################    
sub contact_edit {

	my ($sql, $sth, $out);
	my ($id, $name, $email, $phone);
	
	$sql = qq |
	SELECT id, name, email, phone  
	FROM contacts
	WHERE id = ? |;
	
	$sth = $dbh->prepare($sql);
    $sth->execute($F{'c_id'});
    $sth->bind_columns (\$id, \$name, \$email, \$phone);

	$out .= "\n<h1>Edit Contact</h1>\n\n";

    while ( $sth->fetch ) {
			
		$out .= qq |
		<fieldset>
		<legend>Edit</legend>
			<form method="post"  action="$thisScript">
				<input type="hidden" name="c_id" value="$id" />
				
				<p><label for="name">Name</label><br />
				<input type="text"  name="name" value="$name" class="text" /></p>
				
				<p><label for="email">e-mail</label><br />
				<input type="text"  name="email" value="$email" class="text" /></p>
				
				<p><label for="phone">Phone</label><br />
				<input type="text"  name="phone" value="$phone" class="text" /></p>
				
				<p><button type="submit" name="a" value="contact_save"  class="button positive"> <img src="/images/icons/tick.png" alt=""/> Save </button></p>
				

			</form>
		</fieldset>
		|;

    }
    
	return($out);
	
}


################################################################################    
sub contact_new {

	# form for creating a new contact

	my ($out, $action);

	$action = "contact_save";
	$action = "advertiser_contact_save" if ($F{'ad_id'} && $F{'c_id'});


    # add new
    $out .= qq |
    
	<h1>Add Contact</h1>
	
	<fieldset>
       	<legend>Add</legend>
		<form method="post"  action="$thisScript">
			<input type="hidden" name="c_id" value="new" />
			<input type="hidden" name="ad_id" value="$F{'ad_id'}" />
			
			<p><label for="name">Name</label><br />
			<input type="text"  name="name" value="$name" class="text" /></p>
				
			<p><label for="email">e-mail</label><br />
			<input type="text"  name="email" value="$email" class="text" /></p>
				
			<p><label for="phone">Phone</label><br />
			<input type="text"  name="phone" value="$phone" class="text" /></p>
				
			<p><button type="submit" name="a" value="$action" class="button positive"> <img src="/images/icons/tick.png" alt=""/> Save </button></p>

		</form>
	</fieldset>		
		|;


	return($out);
	
}


################################################################################   
sub contact_save {

	my ($sql, $sth, $out);

	# check if there is an id for either the name or email
	# currently will just update
	$F{'c_id'} = &contact_check() if ($F{'c_id'} =~ /new/i);
	
	if ($F{'c_id'} =~ /new/i) {
		
		#insert
		$sql = qq |INSERT INTO contacts (name, email, phone) VALUES (?,?,?)|;
		$sth = $dbh->prepare($sql);
		$sth->execute($F{'name'}, $F{'email'}, $F{'phone'});
	
		# get new id...
		$sql = qq |SELECT id FROM contacts WHERE name = '$F{'name'}' AND email = '$F{'email'}' |;
	print STDERR $sql;
	    $F{'c_id'} = $dbh->selectrow_array($sql);
	print STDERR $F{'c_id'};
		$F{'msg'} = "success";	
		$msg = qq|Contact <em>$F{'name'}</em> added.|;
	    
    } elsif ($F{'c_id'}) {
		
		# update
		$sql = qq |UPDATE contacts SET name = ?, email = ?, phone = ? WHERE id = ?|;
		$sth = $dbh->prepare($sql);
		$sth->execute($F{'name'}, $F{'email'}, $F{'phone'}, $F{'c_id'});
		$F{'msg'} = "success";	
		$msg = qq|Contact <em>$F{'name'}</em> updated.|;
	}

	return();


}


################################################################################    
sub contact_check {

	my ($sql, $sth, $id);
	
	$sql = qq |SELECT id FROM contacts WHERE name = '$F{'name'}' OR email = '$F{'email'}'|;
print STDERR $sql;
	$id = $dbh->selectrow_array($sql);
print STDERR $F{'c_id'};
    $F{'c_id'} = $id if ($id);
    
    return($F{'c_id'});

} 


################################################################################    
sub contact_select {

	my ($sql, $sth, $out);
	my ($id, $name, $email, $phone);
	
	$sql = qq |
	SELECT id, name, email, phone  
	FROM contacts
	ORDER BY name
	|;

	$sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$name, \$email, \$phone);

    while ( $sth->fetch ) {

		my $default = qq |selected="selected"| if ($id == $_[0]);
		$out .= qq |<option value="$id" $default>$name - $email</option>\n|;
    }
    
	$out = qq |<select name="c_id">\n<option></option>\n$out\n</select>\n|;

	return($out);
	
}


################################################################################    
sub advertisers_read {


#CREATE TABLE advertisers (
#id integer primary key autoincrement,
#name text, 
#contact_id integer );

	my ($sql, $sth, $out);
	my ($id, $name, $c_id, $c_name);
	
	$sql = qq |
	SELECT a.id, a.name, c.id, c.name  
	FROM advertisers a
	LEFT JOIN contacts c ON a.contact_id = c.id
	ORDER BY 2
	|;

	if ($F{'ad_id'}) {
	
		$sql .= qq | WHERE a.id = $F{'ad_id'} |;
	
	}

	$sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$name, \$c_id, \$c_name);

	$out = "\n<h1>Advertisers</h1>\n\n";

	#$out .= qq |<ul>\n$out\n<li><a href="?a=advertiser_new">Add new advertiser</a></li>\n</ul>\n\n|;

    while ( $sth->fetch ) {

		$out .= qq |<li><a href="?a=advertiser_view&amp;ad_id=$id&amp;c_id=$c_id">$name</a> [ <a href="?a=advertiser_edit&amp;ad_id=$id&amp;c_id=$c_id">edit</a> ]|;
		$out .= qq | [contact: <a href="?a=contact_edit&amp;c_id=$c_id">$c_name</a>]| if ($c_name);

		$out .= qq|</li>\n|;
    }
    
   	$out = qq |<ul>\n$out\n</ul>\n<p><a href="?a=advertiser_new">Add new advertiser</a></p>\n|;

	return($out);
	
}


################################################################################    
sub advertiser_edit {


#CREATE TABLE advertisers (
#id integer primary key autoincrement,
#name text, 
#contact_id integer );

	my ($sql, $sth, $out);
	my ($id, $name, $c_id, $c_name);
	
	$sql = qq |
	SELECT a.id, a.name, c.id, c.name  
	FROM advertisers a
	LEFT JOIN contacts c ON a.contact_id = c.id
	WHERE a.id = ? 
	|;
	
	$sth = $dbh->prepare($sql);
    $sth->execute($F{'ad_id'});
    $sth->bind_columns (\$id, \$name, \$c_id, \$c_name);

	$out .= "\n<h1>Advertisers</h1>\n\n";

    while ( $sth->fetch ) {

		my $contact_select = &contact_select($c_id);
			
		my $edit_contact = qq |<p>or, edit <a href="?a=contacts_edit&amp;c_id=$c_id">$c_name</a></p>| if ($c_id);

	
		$out .= qq |
		<fieldset>
		<legend>Edit</legend>
			<form method="post"  action="$thisScript">
				<input type="hidden" name="ad_id" value="$id" />
				
				<p><label for="name">Name</label><br />
				<input type="text"  name="name" value="$name" class="text" /></p>
				
				<h3>Change/select contact</h3>
				$contact_select
				
				$edit_contact
				
				<p><button type="submit" name="a" value="advertiser_save"  class="button positive"> <img src="/images/icons/tick.png" alt=""/> Save </button></p>
				

			</form>
		</fieldset>
		|;

    }
    

	return($out);
	
}


################################################################################    
sub advertiser_view {


	my ($sql, $sth, $out);
	my ($id, $name, $c_id, $c_name);
	
	$sql = qq |
	SELECT a.id, a.name, c.id, c.name  
	FROM advertisers a
	LEFT JOIN contacts c ON a.contact_id = c.id
	WHERE a.id = ? 
	|;
	
	$sth = $dbh->prepare($sql);
    $sth->execute($F{'ad_id'});
    $sth->bind_columns (\$id, \$name, \$c_id, \$c_name);

	$out .= "\n<h1>Advertiser</h1>\n\n";

    while ( $sth->fetch ) {

		my $banners = &banner_list('advertiser_id', $id);
	
		$out .= qq |
		
			<h2>$name [$id]</h2>
				
			<p>Contact: $c_name</p>
			
			$banners
			
		|;

    }
    

	return($out);
	
}


################################################################################    
sub advertiser_new {

    $out .= qq |

	<h1>Add New Advertiser</h1>
	
	<fieldset>
       	<legend>Add</legend>
		<form method="post"  action="$thisScript">
			<input type="hidden" name="ad_id" value="new" />
			
			<p><label for="name">Name</label><br />
			<input type="text"  name="name" value="$name" class="text" /></p>

			<p><label for="c_id">Pick an existing contact<label>
			$contact_select</p>

			<p><button type="submit" name="a" value="advertiser_save" class="button positive"> <img src="/images/icons/tick.png" alt=""/> Save </button></p>

		</form>
	</fieldset>		
	|;


	return($out);
	
}


################################################################################   
sub advertiser_save {

	my ($sql, $sth, $out);

	# check if there is an id for either the name or email
	# currently will just update
	$F{'ad_id'} = &advertiser_check() if ($F{'ad_id'} eq "new");
	
	if ($F{'ad_id'} eq "new") {
		
		#insert
		$sql = qq |INSERT INTO advertisers (name) VALUES (?)|;
		$sth = $dbh->prepare($sql);
		$sth->execute($F{'name'});
	
		# get new id...
		$sql = qq |SELECT id FROM advertisers WHERE name = '$F{'name'}' |;
	    $F{'ad_id'} = $dbh->selectrow_array($sql);
		
		$F{'msg'} = "success";	
		$msg = qq|Advertiser <em>$F{'name'}</em> added.|;
	    
    } elsif ($F{'ad_id'} && $F{'c_id'}) {
	
		# update
		$sql = qq |UPDATE advertisers SET name = ?, contact_id = ? WHERE id = ?|;
		$sth = $dbh->prepare($sql);
		$sth->execute($F{'name'}, $F{'c_id'}, $F{'ad_id'});
		
		$F{'msg'} = "success";
		$msg = qq|Advertiser <em>$F{'name'}</em> updated.|;

    } elsif ($F{'ad_id'}) {
		
		# update
		$sql = qq |UPDATE advertisers SET name = ? WHERE id = ?|;
		$sth = $dbh->prepare($sql);
		$sth->execute($F{'name'}, $F{'ad_id'});
		
		$F{'msg'} = "success";
		$msg = qq|Advertiser <em>$F{'name'}</em> updated.|;

	}

	return();

}


################################################################################   
sub advertisers_contacts_save {

	my ($sql, $sth, $out);

	$sql = qq |SELECT id FROM advertisers WHERE name = '$F{'name'}' AND contact_id = $F{'c_id'} WHERE id = $F{'ad_id'}|;
	
	return if ($dbh->selectrow_array($sql)); # nothing needed to do

	# update
	$sql = qq |UPDATE advertisers SET contact_id = ? WHERE id = ?|;
	$sth = $dbh->prepare($sql);
    $sth->execute($F{'c_id'}, $F{'ad_id'});
    
    $F{'msg'} = "success";
    $msg = qq|Advertiser <em>$F{'name'}</em> updated.|;
	

	return();


}


################################################################################    
sub advertiser_check {

	my ($sql, $sth, $id);
	
	$sql = qq |SELECT id FROM advertisers WHERE name = '$F{'name'}'|;
	$id = $dbh->selectrow_array($sql);
    $F{'ad_id'} = $id if ($id);
    
    return($F{'ad_id'});

} 

################################################################################    
sub advertiser_select {

	my ($sql, $sth, $out);
	my ($id, $name);

	$sql = qq |
	SELECT id, name
	FROM advertisers
	ORDER BY 2
	|;

	$sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$name);

    while ( $sth->fetch ) {

		my $default = qq |selected="selected"| if ($id == $_[0]);
		$out .= qq |<option value="$id" $default>$name</option>\n|;
    }
    
	$out = qq |<select name="ad_id">\n<option></option>\n$out\n</select>\n|;

	return($out);
	
}


################################################################################    
sub banner_list {

	my ($sql, $sth, $out);
	my ($id, $name, $file_pointer, $url, $w, $h, $is_display, $start, $end, $ad_id, $a_name);
	
	$sql = qq |
	SELECT b.id, b.name, b.file_pointer, b.url, b.width, b.height, b.is_display, b.start_date, b.end_date, a.id, a.name 
	FROM banners b
	LEFT JOIN advertisers a ON a.id = b.advertiser_id
	WHERE $_[0] = ? |;
	
	$sth = $dbh->prepare($sql);
    $sth->execute($_[1]);
    $sth->bind_columns (\$id, \$name, \$file_pointer, \$url, \$w, \$h, \$is_display, \$start, \$end, \$ad_id, \$a_name);

	$out .= "\n<h2>Banners</h2>\n\n";

    while ( $sth->fetch ) {

		$is_display = "is visible";
		$is_display = "not visible" if (!$is_display);
		
		my $zones = &banners_zones('banner_id', $id);
		
		$out .= qq |
				<a href="$url"><img src="$file_pointer" width="$w" height="$h" class="push-0" /></a>
				<li>$name [ <a href="?a=banner_edit&amp;b_id=$id">edit</a> ]<ul>
					<li>file: $file_pointer</li>
					<li>url: <a href="$url">$url</a></li>
					<li>dimensions: $w x $h</li>
					<li>display? $is_display</li>
					<li>start date: $start</li>
					<li>end date: $end</li>
					<li>zones:<ul>$zones</ul></li>
				</ul></li>
		|;
		
    }
    
	$out = qq |
	<div class="span-14">
	$out
	</div>
	|;

	return($out);
	

}


################################################################################    
sub banners_read {


	my ($sql, $sth, $out);
	my ($id, $name, $file_pointer, $url, $w, $h, $is_display, $start, $end, $ad_id, $a_name);
	
	
	
	$sql = qq |
	SELECT b.id, b.name, b.file_pointer, b.url, b.width, b.height, b.is_display, b.start_date, b.end_date, a.id, a.name 
	FROM banners b
	LEFT JOIN advertisers a ON a.id = b.advertiser_id
	|;
	
	if ($F{'b_id'}) {
	
		# single banner
		$sql .= qq | WHERE b.id = $F{'b_id'} |;

	} elsif ($F{'extra'} eq "old") {
	
		# older list
		$sql .= qq | WHERE b.end_date <= now()::date - '30 days'::interval ORDER BY 2 |;

	} else {
	
		# normal list
		$sql .= qq | WHERE b.end_date > now()::date - '30 days'::interval ORDER BY 2|;
	}

	$sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$name, \$file_pointer, \$url, \$w, \$h, \$is_display, \$start, \$end, \$ad_id, \$a_name);

	$out .= "\n<h1>Banners</h1>\n\n";

    while ( $sth->fetch ) {

		
		$is_display = "is visible";
		$is_display = "not visible" if (!$is_display);
		 
		$zones = &banners_zones('banner_id', $id);
		
		$out .= qq |
		    <div class="span-14 panel">
		    <a href="$url"><img src="$file_pointer" width="$w" height="$h" class="push-0" /></a>
		    <ul>
			<li><a href="?a=advertiser_edit&amp;ad_id=$ad_id">$a_name</a> - <a href="?a=banner_edit&amp;b_id=$id">$name</a><ul>
				<li>file: $file_pointer</li>
				<li>url: <a href="$url">$url</a></li>
				<li>dimensions: $w x $h</li>
				<li>display? $is_display</li>
				<li>start date: $start</li>
				<li>end date: $end</li>
				<li><a href="$thisScript?a=stat_detail&amp;img=$file_pointer&amp;id=$id&amp;name=$name">stats</a></li>
				<li>zones:<ul>$zones</ul></li>
			</ul></li>
			</ul>
			</div>
		|;
		
	    }
    
	$out .= qq |\n\n<p><a href="?a=banner_new">Add new banner</a></p>\n\n|;
	if ($F{'extra'} eq "old") {
		$out .= qq |\n\n<p><a href="?a=banners&amp;extra=new">Get new banners</a></p>\n\n|;
	} else {
		$out .= qq |\n\n<p><a href="?a=banners&amp;extra=old">Get old banners</a></p>\n\n|;
	}
	return($out);
	
}


################################################################################    
sub banner_edit {


#CREATE TABLE banners (
#id integer primary key autoincrement,
#advertiser_id integer, 
#name text, 
#file_pointer text, 
#url text, 
#width integer, 
#height integer, 
#is_display boolean, 
#start_date date,
#end_date date );

	my ($sql, $sth, $out);
	my ($id, $name, $file_pointer, $url, $w, $h, $is_display, $start_date, $end_date, $ad_id, $a_name, $advertiser_select, $hidden_ad);
	
	$sql = qq |
	SELECT b.id, b.name, b.file_pointer, b.url, b.width, b.height, b.is_display, b.start_date, b.end_date, a.id, a.name 
	FROM banners b
	LEFT JOIN advertisers a ON a.id = b.advertiser_id
	WHERE b.id = ?
	|;
	
	$sth = $dbh->prepare($sql);
    $sth->execute($F{'b_id'});
    $sth->bind_columns (\$id, \$name, \$file_pointer, \$url, \$w, \$h, \$is_display, \$start_date, \$end_date, \$ad_id, \$a_name);

	$out .= "\n<h1>Banner edit</h1>\n\n";

    while ( $sth->fetch ) {

		my $F_is_display = qq |checked="checked"|;
		$F_is_display = "" if (!$is_display);
		
		if (!$ad_id) {
			$advertiser_select = "<p><label for\=\"ad_id\">Advertiser<\/label><\/p>\n\n".&advertiser_select();
		} else {
			$hidden_ad = qq |<input type="hidden" name="ad_id" value="$ad_id" />|;
		}
		
		$out .= qq |
		<fieldset>
		<legend>Edit for $a_name</legend>
		<a href="$url"><img src="$file_pointer" width="$w" height="$h" class="push-0"/></a>
		<p class="push-5"><a href="$thisScript?a=stat_detail&amp;img=$file_pointer&amp;id=$id&amp;name=$name">stats</a></p>
		
	
		<form method="post" enctype="multipart/form-data" action="$thisScript">
				<input type="hidden" name="b_id" value="$id" />
				$hidden_ad
				
				<p><label for="name">Name</label><br />
				<input type="text"  name="name" value="$name" class="text" /></p>
				
				<p><label for="url">url</label><br />
				<input type="text"  name="url" value="$url" class="text" /><br /><em>format: http://www.example.com or https://www.example.com</em></p>
				
				$advertiser_select
						
				<p><label for="is_display">Display?</label><br />
				<input type="checkbox"  name="is_display" value="true" $F_is_display /> check for Yes</p>
				
				<p><label for="start_date">Start Date</label><br />
				<input type="text"  name="start_date" value="$start_date" class="text datepicker" /></p>
				
				<p><label for="end_date">End Date</label><br />
				<input type="text"  name="end_date" value="$end_date" class="text datepicker" /></p>
				
				
				<p><strong>Advertiser</strong><br />
				<a href="?a=advertiser_edit&amp;ad_id=$ad_id">$a_name</a></p>
				
				<p><label for="name">File</label><br />
				<input type="file" name="file_pointer" value="" class="file" /><br /><em>currently: $file_pointer <br /> width: $w height: $h</em> </p>

				
				<p><button type="submit" name="a" value="banner_save"  class="button positive"> <img src="/images/icons/tick.png" alt=""/> Save </button></p>

			</form>
		</fieldset>
		|;

    }
    
		
	$out = qq |
	<div class="span-14">
	$out
	</div>
		
	|;
	return($out);
	
}


################################################################################    
sub banner_save {

	# save non-image information

#CREATE TABLE banners (
#id integer primary key autoincrement,
#advertiser_id integer, 
#name text, 
#file_pointer text, 
#url text, 
#width integer, 
#height integer, 
#is_display boolean, 
#start_date date,
#end_date date );

	my ($sql, $sth, $out);

	$F{'is_display'} = "false" if (!$F{'is_display'});

	if (!$F{'b_id'} || $F{'b_id'} eq "new") {
	
		$sql = qq |
		INSERT INTO banners
		(advertiser_id, name, url, is_display, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?)|;
		$sth = $dbh->prepare($sql);
		$sth->execute($F{'ad_id'}, $F{'name'}, $F{'url'}, $F{'is_display'}, $F{'start_date'}, $F{'end_date'});
	
	  	# get new id...
		$F{'name'} =~ s/\'/\'\'/g;
   		$sql = qq |SELECT id FROM banners WHERE name = '$F{'name'}' AND url = '$F{'url'}' AND advertiser_id = $F{'ad_id'} |;
		print STDERR $sql;
		$F{'b_id'} = $dbh->selectrow_array($sql);
		
		$F{'msg'} = "success";
		$msg .= "Added banner $name";
      
	} else {
	
		# exists
		
		# check if need to update
	   	$sql = qq |UPDATE banners SET advertiser_id=?, name=?, url=?, is_display=?, start_date=?, end_date=? WHERE id=?|;
	   	
	   	$sth = $dbh->prepare($sql);
	    $sth->execute($F{'ad_id'}, $F{'name'}, $F{'url'}, $F{'is_display'}, $F{'start_date'}, $F{'end_date'}, $F{'b_id'});
	    
	    $F{'msg'} = "success";
	    $msg .= "Updated banner $name";

	}

	return();
		
}	


################################################################################    
sub banner_save_img {

	# save non-image information

#CREATE TABLE banners (
#id integer primary key autoincrement,
#advertiser_id integer, 
#name text, 
#file_pointer text, 
#url text, 
#width integer, 
#height integer, 
#is_display boolean, 
#start_date date,
#end_date date );

	my ($sql, $sth, $out);

	if (!$F{'b_id'}) {
		
		$msg .= "No banner?";
		return();
      
	} else {
	
		# exists
		
		my $file = $rel_path.$F{'file_pointer'};
		
		my ($w, $h) = &getFileSize($abs_path.$F{'file_pointer'});
		
		# check if need to update
	   	$sql = qq |
	   	UPDATE banners 
	   	SET file_pointer=?, width=?, height=?
	   	WHERE id=?
	   	|;
	   	$sth = $dbh->prepare($sql);
	    $sth->execute($file, $w, $h, $F{'b_id'});
	    
	    $F{'msg'} = "success";
	    $msg .= "Updated banner image <em>$F{'file_pointer'}</em>.\n";

	}
	
	return();
		
}	



################################################################################    
sub banner_new {

    $advertiser_select = "<p><label for\=\"ad_id\">Advertiser<\/label><\/p>\n\n".&advertiser_select();

    $out .= qq |
<h1>Banner New</h1>
<div class="span-14">
	<fieldset>
       	<legend>Add new banner</legend>
 			<form method="post" enctype="multipart/form-data" action="$thisScript">
			<input type="hidden" name="b_id" value="new" />
			
				<p><label for="name">Name</label><br />
				<input type="text"  name="name" value="" class="text" /></p>
				
				<p><label for="url">URL</label><br />
				<input type="text" name="url" value="" class="text" /></p>

				<p><label for="file_pointer">File</label><br />
				<input type="file" name="file_pointer" value="" class="text" /></p>

				$advertiser_select
				
				<p><label for="is_display">Display?</label><br />
				<input type="radio"  name="is_display" value="true"  /></p>
				
				<p><label for="start_date">Start Date</label><br />
				<input type="text"  name="start_date" value="$date" class="text" /></p>
				
				<p><label for="end_date">End Date</label><br />
				<input type="text"  name="end_date" value="$date" class="text" /></p>
				
			<p><button type="submit" name="a" value="banner_save" class="button positive"> <img src="/images/icons/tick.png" alt=""/> Save </button></p>

		</form>
	</fieldset>
</div>
	|;

	return($out);
	
}


################################################################################    
sub banner_select {

	my ($sql, $sth, $out);
	my ($id, $name, $file_pointer);

	$sql = qq |
	SELECT id, name, file_pointer  
	FROM banners
	ORDER BY 2
	|;

	$sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$name, \$file_pointer);

    while ( $sth->fetch ) {

		my $default = qq |selected="selected"| if ($id == $_[0]);
		$out .= qq |<option value="$id" $default>$name</option>\n|;
    }
    
	$out = qq |<select name="b_id">\n<option></option>\n$out\n</select>\n|;

	return($out);
	
}




################################################################################   
sub banners_zones {

	my ($sql, $sth, $out);
	my ($b_id, $z_id, $priority, $z_name, $z_desc);
	
	$sql = qq |
	SELECT banner_id, zone_id, priority, z.name, z.description 
	FROM banners_zones bz
	LEFT JOIN zones z ON bz.zone_id = z.id
	WHERE $_[0] = $_[1] 
	|;
	$sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$b_id, \$z_id, \$priority, \$z_name, \$z_desc);

    while ( $sth->fetch ) {

		$out .= qq |
		<li><a href="?a=zone_edit&amp;z_id=$z_id">$z_name - $z_desc</a> [priority: $priority]</li>
		|;

	}
	
	return($out);
}





################################################################################    
sub zones_read {

#CREATE TABLE zones (
#id integer primary key autoincrement,
#name text, 
#description text, 
#width integer, 	
#height integer ); 

	my ($sql, $sth, $out);
	my ($id, $name, $desc, $w, $h, $s_id, $s_name);
	
	$sql = qq |
	SELECT z.id, z.name, z.description, z.width, z.height, s.id, s.name 
	FROM zones	 z
	LEFT JOIN zones_sites zs ON z.id = zs.zone_id
	LEFT JOIN sites s ON s.id = zs.site_id
	|;

	if ($F{'z_id'}) {
		$sql .= qq | WHERE z.id = $F{'z_id'} |;
	} else {
		$sql .= qq | WHERE s.is_display |;
	}
	$sql .= qq | ORDER BY s.name, z.id |;


print STDERR $sql;	

	$sth = $dbh->prepare($sql);
	$sth->execute();
	$sth->bind_columns (\$id, \$name, \$desc, \$w, \$h, \$s_id, \$s_name);

	$out .= "\n<h1>Zones</h1>\n\n";

    while ( $sth->fetch ) {

		$zones = &banners_zones('zone_id', $id);
		
		$out .= qq |
		<div class="output">
			<li><a href="?a=sites&amp;s_id=$s_id">$s_name</a> - <a href="?a=zone_edit&amp;z_id=$id">$name</a><ul>
				<li>description: $desc</li>
				<li>url: <a href="$url">$url</a></li>
				<li>dimension limits: $w x $h</li>
				<li>zones:<ul>$zones</ul></li>
			</ul></li>
		</div>
		|;
		
    }
		
	$out = qq |
		<div class="span-14">
		<p><a href="?a=zone_new">New Zone</a><p>
		</div>
	<div class="span-14">
	$out
	</div>
	|;
	
	return($out);
	
}


################################################################################    
sub zone_edit {

#CREATE TABLE zones (
#id integer primary key autoincrement,
#name text, 
#description text, 
#width integer, 	
#height integer ); 

    my ($sql, $sth, $out);
    my ($id, $name, $desc, $w, $h, $s_id, $s_name, $hidden_site, $select_site);
    
    $sql = qq |
	SELECT z.id, z.name, z.description, z.width, z.height, s.id, s.name 
	FROM zones	 z
	LEFT JOIN zones_sites zs ON z.id = zs.zone_id
	LEFT JOIN sites s ON s.id = zs.site_id
	WHERE z.id = ?
	|;
    
    $sth = $dbh->prepare($sql);
    $sth->execute($F{'z_id'});
    $sth->bind_columns (\$id, \$name, \$desc, \$w, \$h, \$s_id, \$s_name);
    
    $out .= "\n<h1>Zone Edit</h1>\n\n";
    
    while ( $sth->fetch ) {

	if ($F{'s_id'} || $s_id) {
	    $hidden_site = qq |<input type="hidden" name="s_id" value="$F{'s_id'}" />|;
	} else {
	    $select_site = "<p><label for\=\"s_id\">Site<\/label><\/p>\n\n".&site_select();
	}
	
	$out .= qq |
		<fieldset>
		<legend>Edit Zone [$id] for <a href="?a=sites&amp;s_id=$s_id">$s_name [$s_id]</a></legend>

 			<form method="post"  action="$thisScript">
				<input type="hidden" name="z_id" value="$id" />
				$hidden_site 
				
				<p><label for="name">Name</label><br />
				<input type="text"  name="name" value="$name" class="text" /></p>
				
				$select_site
				
				<p><label for="desc">Description</label><br />
				<input type="text"  name="desc" value="$desc" class="text" /></p>
				
				<p><label for="width">Width Limit</label><br />
				<input type="text" name="width" value="$w" class="text" /></p>
				
				<p><label for="height">Height Limit</label><br />
				<input type="text"  name="height" value="$h" class="text" /></p>

				<p><button type="submit" name="a" value="zone_save"  class="button positive"> <img src="/images/icons/tick.png" alt=""/> Save </button></p>
				

			</form>
		</fieldset>
		|;

    }
    
	$out = qq |
	<div class="span-14 panel">
	$out
	</div>
		
	|;

	return($out);
	
}


################################################################################    
sub zone_new {
    
    my $hidden_site = qq |<input type="hidden" name="s_id" value="$F{'s_id'}" />| if ($F{'s_id'});
    my $site_text = qq |<p><em>for site $F{'s_name'}</em></p>| if ($F{'s_name'});
    
    $out .= qq |
<h1>Zone New</h1>
<div class="span-14 panel">
	<fieldset>
       	<legend>Add</legend>
		<form method="post"  action="$thisScript">
			<input type="hidden" name="z_id" value="new" />
			$hidden_site
			
			        $site_text
	
				<p><label for="name">Name</label><br />
				<input type="text"  name="name" value="" class="text" /></p>
		
				<p><label for="desc">Description</label><br />
				<input type="text"  name="desc" value="$desc" class="text" /></p>
				
				<p><label for="width">Width Limit</label><br />
				<input type="text" name="width" value="$file_pointer" class="text" /><br />$width</p>
				
				<p><label for="height">Height Limit</label><br />
				<input type="text"  name="height" value="$height" class="text" /></p>
				
				<p><button type="submit" name="a" value="zone_save" class="button positive"> <img src="/images/icons/tick.png" alt=""/> Save </button></p>

		</form>
	</fieldset>
</div>
	|;

	
	return($out);
	
}


################################################################################   
sub zone_save {

    my ($sql, $sth, $out);
    
    $F{'height'} = undef() if (!$F{'height'});
    $F{'width'}  = undef() if (!$F{'width'});
    
    $F{'name'} =~ s/'/''/g;
    $F{'desc'} =~ s/'/''/g;


    if ($F{'z_id'} eq "new") {
	
		#insert
		$sql = qq |INSERT INTO zones (name, description, width, height) VALUES (?, ?, ?, ?)|;
		$sth = $dbh->prepare($sql);
		$sth->execute($F{'name'}, $F{'desc'}, $F{'width'}, $F{'height'});

		# get new id...
		$sql = qq |SELECT id FROM zones WHERE name = '$F{'name'}' AND description = '$F{'desc'}' |;
		$F{'z_id'} = $dbh->selectrow_array($sql);
	
		$F{'msg'} .= "success";
		$msg = qq|Zone <em>$F{'name'}</em> $F{'z_id'} added.|;
	
    } elsif ($F{'z_id'}) {
	
		# update
		$sql = qq |UPDATE zones SET name = ?, description = ?, width = ?, height = ? WHERE id = ?|;
		$sth = $dbh->prepare($sql);
		$sth->execute($F{'name'}, $F{'desc'}, $F{'width'}, $F{'height'}, $F{'z_id'});
	
		$F{'msg'} = "success";
		$msg = qq|Zone <em>$F{'name'}</em> updated.|;
    }

    # create zone_site linkage
    
    if ($F{'z_id'} && $F{'s_id'}) {
	
		# remove any previous links for this zone		
		$sql = qq |DELETE FROM zones_sites WHERE zone_id = $F{'z_id'}|;
		$dbh->do($sql);
	
		# insert new linkage
		$sql = qq |INSERT INTO zones_sites (zone_id, site_id) VALUES (?, ?)|;
		$sth = $dbh->prepare($sql);
		$sth->execute($F{'z_id'}, $F{'s_id'});
	
		$F{'msg'} .= "success";
		$msg .= qq|Zone to site linked <em>$F{'name'}</em> updated.|;
	
	
    }
    
    return(&zones_read());
    
}


################################################################################   
sub banner_zone_save {


	my ($sql, $sth, $out);
	
	if ($F{'z_id'} && $F{'b_id'}) {

		# remove any previous links for this zone		
		$sql = qq |DELETE FROM banners_zones WHERE banner_id = $F{'b_id'} AND zone_id = $F{'z_id'}|;
		$dbh->do($sql);

		# insert new linkage
		$sql = qq |INSERT INTO banners_zones (zone_id, banner_id) VALUES (?, ?)|;
		$sth = $dbh->prepare($sql);
		$sth->execute($F{'z_id'}, $F{'b_id'});
		
		$F{'msg'} = "success";
		$msg .= qq|Zone to banner linked updated.|;
		
		&set_tracker();
		$msg .= qq|<br />Zone and banner linked added to the tracker.|;
		
		
	
	}

	return(&site_view());

}



################################################################################   
sub reset_tracker {

	if ($F{'z_id'} && $F{'b_id'}) {
		&set_tracker();
		$msg .= qq|<br />Zone and banner linked added to the tracker.|;
	}

	return(&site_view());

}


################################################################################   
sub banner_zone_remove {


	my ($sql, $sth, $out);
	
	if ($F{'z_id'} && $F{'b_id'}) {

		# remove any previous links for this zone		
		$sql = qq |DELETE FROM banners_zones WHERE banner_id = $F{'b_id'} AND zone_id = $F{'z_id'}|;
		$dbh->do($sql);

		
		$F{'msg'} = "error";
		$msg .= qq|Zone to banner link removed.|;
		
	
	} else {
	
		$F{'msg'} = "error";
		$msg .= qq|Can't remove  banner_id = $F{'b_id'} AND zone_id = $F{'z_id'}|;
	
	}

	return(&site_view());

}



################################################################################   
sub zones_sites {

	my ($sql, $sth, $out);
	my ($z_id, $s_id, $s_name, $z_name, $z_desc);
	
	$sql = qq |
	SELECT zone_id, site_id, s.name, z.name, z.description 
	FROM zones_sites zs
	LEFT JOIN sites s ON zs.site_id = s.id
	LEFT JOIN zones z ON zs.zone_id = z.id
	WHERE $_[0] = $_[1] 
	|;
	
	$sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$z_id, \$s_id, \$s_name, \$z_name, \$z_desc);

    while ( $sth->fetch ) {

		$out .= qq |
		<li><a href="?a=zone_edit&amp;z_id=$z_id&amp;s_id=$s_id">$z_name</a> - $z_desc</li>
		|;

	}
	
	return($out);
}


################################################################################   
sub banners_zones_sites {

	my ($sql, $sth, $out);
	my ($b_id, $file_pointer, $url, $b_name, $z_id, $s_id, $s_name, $z_name, $z_desc, $is_active);
	
	$sql = qq |
	SELECT z.id, s.id, s.name, z.name, z.description, b.id, b.file_pointer, b.url, b.name, (case when b.is_display and b.end_date > now()::date then 1 else 0 end)
	FROM zones_sites        zs
	LEFT JOIN sites          s ON zs.site_id = s.id
	LEFT JOIN zones          z ON zs.zone_id = z.id
	LEFT JOIN banners_zones bz ON bz.zone_id = z.id
	LEFT JOIN banners        b ON b.id = bz.banner_id
	WHERE $_[0] = $_[1] 
	ORDER BY z.id
	|;
	
	$sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$z_id, \$s_id, \$s_name, \$z_name, \$z_desc, \$b_id, \$file_pointer, \$url, \$b_name, \$is_active);

	my $banner_select = &banner_select;

    while ( $sth->fetch ) {

		if ($is_active) {
			$is_active = qq | - live banner|;
		} else {
			if ($url) {
				$is_active = qq | - inactive banner|;
			} else {
				$is_active = qq ||;
			}
		}

		$out .= qq |
		
		<div class="span-14 clear panel">
		
			<a href="$url"><img src="$file_pointer" class="push-0"></a>
			
			<h3><a href="?a=zone_edit&amp;z_id=$z_id">$z_name</a></h3>
			
			<h4><a href="?a=banner_edit&amp;b_id=$b_id">$b_name</a> $is_active</h4>
			
			<form method="post">
			
				<input type="hidden" name="z_id" value="$z_id" />
				<input type="hidden" name="s_id" value="$s_id" />
				
				<p><label for="b_id">Add a banner</label>
				$banner_select 
				</p>
				
				<p>
				
				<button type="submit" name="a" value="banner_zone_save"  class="button positive"> <img src="/images/icons/tick.png" alt=""/> Save </button>
				
				<a href="?a=banner_zone_remove&amp;b_id=$b_id&amp;z_id=$z_id&amp;s_id=$s_id" class="button negative"> <img src="/images/icons/cross.png" alt=""/> Remove </a>
				</p>
				
			</form>
			
			<p><a href="?a=reset_tracker&amp;s_id=$s_id&amp;b_id=$b_id&amp;z_id=$z_id">Reset Tracker</a></p>
			
		</div>
		|;

	}
	
	return($out);
}








################################################################################    
sub site_view {

#CREATE TABLE sites (
#id integer primary key autoincrement,
#name text, 
#description text, 
#is_display boolean,
#contact_id integer ); 

	my ($sql, $sth, $out);
	my ($id, $name, $desc, $c_id, $c_name, $is_display);
	
	$sql = qq |
	SELECT s.id, s.name, s.description, c.id, c.name, s.is_display
	FROM sites s
	LEFT JOIN contacts c ON s.contact_id = c.id
	WHERE s.id = $F{'s_id'}
	|;
	
	$sth = $dbh->prepare($sql);
	$sth->execute();
	$sth->bind_columns (\$id, \$name, \$desc, \$c_id, \$c_name, \$is_display);

	$out .= "\n<h1>Site View</h1>\n\n";

    while ( $sth->fetch ) {
		
		my $zones = &banners_zones_sites('site_id', $id);
		
		$is_display = "YES";
		$is_display = "NO" if (!$is_display);
		
		$out .= qq |
				
			<li>name: <a href="?a=site_edit&amp;s_id=$id">$name</a>
			<li>desc: $desc</li>
			<li>displayed? $is_display</li>
			<li>contact: <a href="?a=contact_edit&amp;c_id=$c_id">$c_name</a></li>
			<li>zones:<ul>$zones<li><a href="?a=zone_new&amp;s_id=$id&amp;s_name=$name">add zone</a></li></ul></li>
			</ul></li>
		|;
		
	}
    
		
	$out = qq |
	<div class="span-14">
	$out
	</div>
	
	<p><a href="?a=site_new">Add a site</a></p>
	
	|;
	
	return($out);
	
}



################################################################################    
sub sites_read {

#CREATE TABLE sites (
#id integer primary key autoincrement,
#name text, 
#description text, 
#contact_id integer ); 

	my ($sql, $sth, $out);
	my ($id, $name, $desc, $c_id, $c_name, $is_display, $where);

	if ($F{'s_id'}) {
	
		$where .= qq | WHERE s.id = $F{'s_id'} |;
	
	}
	
	$sql = qq |
	SELECT s.id, s.name, s.description, c.id, c.name, s.is_display 
	FROM sites s
	LEFT JOIN contacts c ON s.contact_id = c.id
	$where
	ORDER BY 6 DESC, 2
	|;

	print STDERR $sql;

	$sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$name, \$desc, \$c_id, \$c_name, \$is_display);

	$out .= "\n<h1>Sites</h1>\n\n";

    while ( $sth->fetch ) {
		
		my $zones = &zones_sites('site_id', $id);
		$is_display = "YES" if ($is_display);
		$is_display = "NO" if (!$is_display);
		
		$out .= qq |
				
			<li>name: <a href="?a=site_view&amp;s_id=$id">$name</a> [ <a href="?a=site_edit&amp;s_id=$id">edit</a>]
			<li>desc: $desc</li>
			<li>displayed? $is_display</li>
			<li>contact: <a href="?a=contact_edit&amp;c_id=$c_id">$c_name</a></li>
			<li>zones:<ul>$zones<li><a href="?a=zone_new&amp;s_id=$id&amp;s_name=$name">add zone</a></li></ul></li>
			</ul></li>
		|;
		
	}
    
		
	$out = qq |
	<div class="span-14">
	$out
	</div>
	
	<p><a href="?a=site_new">Add a site</a></p>
	
	|;
	
	return($out);
	
}


################################################################################   
sub site_save {

	my ($sql, $sth, $out);
	
	$F{'is_display'} = "0" if (!$F{'is_display'});
	$F{'is_display'} = "1" if ($F{'is_display'});
	
	if ($F{'s_id'} eq "new") {
	    
	    #insert
	    
		$sql = qq |INSERT INTO sites (name, description, is_display) VALUES (?,?,?)|;
		$sth = $dbh->prepare($sql);
		$sth->execute($F{'name'}, $F{'desc'}, $F{'is_display'});
		
		# get new id...
		$sql = qq |SELECT id FROM sites WHERE name = '$F{'name'}' AND description = '$F{'name'}' |;
		$F{'s_id'} = $dbh->selectrow_array($sql);
		$msg = qq|<div class="span-24 success">Site <em>$F{'name'}</em> added.</div>|;
		
	    } elsif ($F{'s_id'}) {
		
		# update
		print STDERR qq |UPDATE sites SET name = $F{'name'}, description = $F{'desc'}, is_display = $F{'is_display'} WHERE id = $F{'s_id'}\n\n|;

		$sql = qq |UPDATE sites SET name = ?, description = ?, is_display = ? WHERE id = ?|;
		$sth = $dbh->prepare($sql);
		$sth->execute($F{'name'}, $F{'desc'}, $F{'is_display'}, $F{'s_id'});
		$msg = qq|<div class="span-24 success">Site <em>$F{'name'}</em> updated.</div>|;
		print STDERR qq|<div class="span-24 success">Site <em>$F{'name'}</em> updated.</div>|;
	    }
	
	return(&sites_read());

}


################################################################################    
sub site_edit {


#CREATE TABLE sites (
#id integer primary key autoincrement,
#name text, 
#description text, 
#contact_id integer ); 


    my ($sql, $sth, $out);
    my ($id, $name, $desc, $c_id, $c_name, $is_display);
    
    $sql = qq |
	SELECT s.id, s.name, s.description, c.id, c.name, s.is_display 
	FROM sites s
	LEFT JOIN contacts c ON s.contact_id = c.id
	WHERE s.id = ?
	|;
	
	
    $sth = $dbh->prepare($sql);
    $sth->execute($F{'s_id'});
    $sth->bind_columns (\$id, \$name, \$desc, \$c_id, \$c_name, \$is_display);
    
    $out .= "\n<h1>Site Edit</h1>\n\n";
    
    while ( $sth->fetch ) {
	
	my $zones = &zones_sites('site_id', $id);
	
	my $is_display_checked = "";
	$is_display_checked = qq|checked="checked"| if ($is_display);

	$out .= qq |
		<fieldset>
		<legend>Edit $name [$id]</legend>

 			<form method="post"  action="$thisScript">
				<input type="hidden" name="s_id" value="$id" />
				
				<p><label for="name">Name</label><br />
				<input type="text" id="name" name="name" value="$name" class="text" /></p>
				
				<p><label for="desc">Description</label><br />
				<input type="text" id="desc" name="desc" value="$desc" class="text" /></p>

				<p><label for="is_display">Display in this site on other pages?</label><br />
				<input type="checkbox" id="is_display" name="is_display" value="1" $is_display_checked/>$is_display</p>
				
				<p><a href="?a=contacts_edit&amp;c_id=$c_id">$c_name</a></p>
				
				<p><button type="submit" name="a" value="site_save"  class="button positive"> <img src="/images/icons/tick.png" alt=""/> Save </button></p>
				

			</form>
		</fieldset>
		
		<h2>Zones for this site</h2>
		$zones
		
		|;

    }
    
		
	$out = qq |
	<div class="span-14">
	$out
	</div>
	|;

	return($out);
	
}


################################################################################    
sub site_new {

    
    $out .= qq |
<div class="span-14">
	<fieldset>
       	<legend>Add</legend>
		<form method="post"  action="$thisScript">
			<input type="hidden" name="s_id" value="new" />
			
				<p><label for="name">Name</label><br />
				<input type="text"  name="name" value="" class="text" /></p>
				
				<p><label for="desc">Description</label><br />
				<input type="text"  name="desc" value="" class="text" /></p>

				<p><label for="is_display">Display</label><br />
				<input type="checkbox"  name="is_display" value="1" /></p>

				
				<p>contact add</p>
								
			<p><button type="submit" name="a" value="site_save" class="button positive"> <img src="/images/icons/tick.png" alt=""/> Save </button></p>

		</form>
	</fieldset>
</div>
	|;

	return($out);
	
}


################################################################################    
sub site_select {
	
	my ($sql, $sth, $out);
	my ($id, $name);

	$sql = qq |
	SELECT id, name
	FROM sites
	WHERE is_display
	|;

	$sth = $dbh->prepare($sql);
	$sth->execute();
	$sth->bind_columns (\$id, \$name);
	
	while ( $sth->fetch ) {
	    
	    my $default = qq |selected="selected"| if ($id == $_[0]);
	    $out .= qq |<option value="$id" $default>$name</option>\n|;
	}
	
	$out = qq |<select name="s_id">\n<option></option>\n$out\n</select>\n|;
	
	return($out);
	
}







################################################################################   
sub print_page {


	print <<EndofHTML;
Content-type: text/html

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
   "http://www.w3.org/TR/html4/strict.dtd">

<html lang="en">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">

	<title>stmgrts ad server</title>
  	
  	<!-- Framework CSS -->
	<link rel="stylesheet" href="http://www.mahnke.net/css/blueprint/blueprint/screen.css" type="text/css" media="screen, projection" /> 
	<link rel="stylesheet" href="http://www.mahnke.net/css/blueprint/blueprint/print.css" type="text/css" media="print" />    
	<!--[if IE]><link rel="stylesheet" href="http://www.mahnke.net/css/blueprint/blueprint/ie.css" type="text/css" media="screen, projection" /><![endif]--> 


  <link type="text/css" href="http://stmgrts.org.uk/javascript/css/custom-theme/jquery-ui-1.7.2.custom.css" rel="stylesheet" />                          
  <script type="text/javascript" src="http://stmgrts.org.uk/javascript/jquery-1.4.2.min.js"></script>                                                    
  <script type="text/javascript" src="http://stmgrts.org.uk/javascript/jquery.ui.core.js"></script>                                                      
  <script type="text/javascript" src="http://stmgrts.org.uk/javascript/jquery.ui.datepicker.js"></script>                                                                   
  <script type="text/javascript">                                                                                                                                           
        window.onload = (                                                                                                                                                   
                                                                                                                                                                            
                function(){                                                                                                                                                 
                                                                                                                                                                            
                        \$.datepicker.setDefaults({                                                                                                                         
                                dateFormat: 'yy-mm-dd',                                                                                                                     
                                altFormat: 'yy-mm-dd'                                                                                                                       
                                });                                                                                                                                         
                                                                                                                                                                            
                        \$('.datepicker').datepicker();                                                                                                                     
                                                                                                                                                                            
                }                                                                                                                                                           
        );                                                                                                                                                                  
                                                                                                                                                                            
        </script>  
        
        <style type="text/css">
        .panel {
        	padding: 2em;
        	background-color: #AFD775;
        	-moz-border-radius:5px;-webkit-border-radius:5px;border-radius:5px;
        }

		.output {
			padding: 10px;
        	background-color: #95CBE9;
        	-moz-border-radius:5px;-webkit-border-radius:5px;border-radius:5px;	
        	margin-bottom: 1em;
		}
        /* = footer */
div#footer {
	background-color: #d6f9c2;
	-moz-border-radius:5px;-webkit-border-radius:5px;border-radius:5px;
}

div#footer p {
	font-size: small;
	padding-right: 1em;
	padding-top: 0.5em;
	text-align: right;
	color: #666666;
}
        </style>

	
</head>

<body>

<div class="container"> 
 
<div id="content" class="span-24 last"> 
 
<div id="banner" class="span-24 last"> 
 
<div id="header" class="span-18"> 
 
<h1 id="banner-header"  class="append-bottom"><a href="http://www.mystmargarets.com/" accesskey="1"><img src="/images/mystmgargarets_logo_300.jpg"  width="300" height="87" alt="My St Margarets" /></a></h1> 
 
<h2 id="banner-description"></h2> 
 
<!-- / header --></div> 
 
<!-- SEARCH --> 
<div id="search" class="span-6 last"> 
 
<h2>Search</h2> 

<form method="get" action="http://www.mahnke.net/peter/MT/mt-search.cgi"> 
<input type="hidden" name="IncludeBlogs" value="18" /> 
<input id="search_text" name="search" size="20" /><br /> 
<input id="search_submit" type="submit" value="Search" /> 
</form> 

<!-- / search --></div> 
 
 
 
<!-- / banner --></div> 
 
<div id="entries" class="span-14"> 
 
	<div id="sidebar" class="span-4">
		<ul>
			<li><a href="?a=advertisers">Advertisers</a></li>
			<li><a href="?a=contacts">Contacts</a></li>
			<li><a href="?a=banners">Banners</a></li>
			<li><a href="?a=zones">Zones</a></li>
			<li><a href="?a=sites">Sites</a></li>
			<li><a href="?a=stats">Stats</a></li>
		</ul>
		
$_[1]
		
	</div><!-- /sidebar -->

	<div id="content" class="column prepend-1 span-9 last">

<div class="span-9 $F{'msg'}">$msg</div>

$_[0]


	</div><!-- /content  -->

<div id="footer" class="span-24 last"> 
  <p>Copyright &copy; 2009-2010 - MyStMargarets.com</p> 
</div> 

<!-- / container --></div> 
 
</body> 
</html>
EndofHTML

	exit;

}


################################################################################   
sub stats {

#id integer primary key autoincrement,
#type text, 
#zone_id integer, 
#banner_id integer,
#ip text,
#refer text, 
#ts timestamp
#, bkey text);

    my ($sql, $sth, $out);
    my ($id, $count, $clicks,  $name, $date, $fp);
    my (%B, %Z, %IP, %R);
    
    # dates
    if ($F{'date'} eq 'two month ago') {
        $date = qq| AND (ds >= current_date - '3 month'::interval) AND   (ds <= current_date - '2 month'::interval) |;
		&stats_past($date);
    }elsif ($F{'date'} eq 'last month') {
        $date = qq| AND (ds >= current_date - '2 month'::interval) AND   (ds <= current_date - '1 month'::interval) |;
		&stats_past($date);
    } elsif  ($F{'date'} eq 'this month') {
		$date = qq| AND (ds >= current_date - '1 month'::interval) |;
		&stats_past($date);
        $date = qq| AND (ts >= current_date - '1 month'::interval) |;
		&stats_today($date);
    } elsif  ($F{'date'} eq 'last week') {
        $date = qq| AND (ds >= current_date - '2 week'::interval) AND   (ds <= current_date - '1 week'::interval) |;
		&stats_past($date);
    } elsif  ($F{'date'} eq 'this week') {
        $date = qq| AND (ds >= current_date - '1 week'::interval) |;
		&stats_past($date);
        $date = qq| AND (ts >= current_date - '1 week'::interval) |;
		&stats_today($date);
    } elsif  ($F{'date'} eq 'yesterday') {
        $date = qq| AND (ds >= current_date - '2 day'::interval) AND (ds <= current_date - '1 day'::interval) |;
		&stats_past($date);
        $date = qq| AND (ts >= current_date - '2 day'::interval) AND (ts <= current_date - '1 day'::interval) |;
		&stats_today($date);
    } else {
		$date = qq| AND (ts >= current_date - '1 day'::interval) |;
		&stats_today($date);
    }	


sub stats_today {
	
	my $date = $_[0];
	
    # views of banners
    $sql = qq |
select b.id
,      b.name
,      b.file_pointer
,      count(*)
from   tracker t
,      banners b
where  b.id = t.banner_id
and    t.type = 'image'
$date
group by 1, 2, 3
|;

    $sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$name, \$fp, \$count);
    
    while ( $sth->fetch ) {
	
		$B{$id}           = $name;
		$B{$id}{'count'} += $count;
		$B{$id}{'fp'}     = $fp;
    }
    
    # clicks of banners
    $sql = qq |
select b.id
,      b.name
,      count(t.id)
from   tracker t
,      banners b
where  b.id = t.banner_id
and    t.type = 'link'
$date
group by 1, 2

	|;
    
    $sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$name, \$count);
    
    while ( $sth->fetch ) {
	
		$B{$id}{'link'} += $count;
	
    }
    
    # views of zones
    $sql = qq |
	SELECT z.id, count(distinct t.id), z.name
	FROM tracker t
	LEFT JOIN zones z ON t.zone_id = z.id
	WHERE type = 'image'
	$date
	GROUP BY z.id, z.name
	ORDER BY z.name
	|;
    
    $sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$count, \$name);
    
    while ( $sth->fetch ) {
	
	$Z{$id} = $name;
	$Z{$id}{'count'} += $count;
	
    }
    
    # clicks of zones
    $sql = qq |
	SELECT z.id, count(distinct t.id), z.name
	FROM tracker t
	LEFT JOIN zones z ON t.zone_id = z.id
	WHERE type = 'link'
	$date
	GROUP BY z.id, z.name
	ORDER BY z.name
	|;
    
    $sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$count, \$name);
    
    while ( $sth->fetch ) {
	
		$Z{$id}{'link'} += $count;
	
    }
	
    # views of ip
    $sql = qq |
	SELECT count(distinct t.id)
	FROM tracker t
	WHERE type = 'image'
	$date
	|;
    
    $sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$count);
    
    while ( $sth->fetch ) {
	
		$IP{'count'} += $count;
	
    }
    
    # clicks of ip
    $sql = qq |
	SELECT count(distinct t.id)
	FROM tracker t
	WHERE type = 'link'
	$date
	|;
    
    $sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$count);
    
    while ( $sth->fetch ) {
	
		$IP{'link'} += $count;
	
    }
    
}

sub stats_past {
	
	my $date = $_[0];
	
    # views of banners
	$sql = qq |
	select     b.id
		,      b.name
		,      b.file_pointer
		,      sum(views)
		,      sum(clicks) 
	from tracker_summary ts
	,    banners b
	where 
		ts.banner_id = b.id
		$date
	group by 1,2,3
	order by 1
	|;

	#print STDERR "$sql\n";
	#$msg .= "$sql\n";

    $sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$name, \$fp, \$count, \$clicks);
    
    while ( $sth->fetch ) {
	
		$B{$id} = $name;
		$B{$id}{'count'} = $count;
		$B{$id}{'fp'}    = $fp;
		$B{$id}{'link'}  = $clicks;
    }
    
    # views of zones
	$sql = qq |
	select     z.id
		,      z.name
		,      sum(views)
		,      sum(clicks) 
	from tracker_summary ts
	,    zones z 
	where 
		ts.zone_id = z.id
		$date
	group by 1, 2 
	order by 1
	|;
	
	#print STDERR "$sql\n";
	#$msg .= "$sql\n";
    
    $sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$name, \$count, \$clicks);
    
    while ( $sth->fetch ) {
	
		$Z{$id} = $name;
		$Z{$id}{'count'} = $count;
		$Z{$id}{'link'} = $clicks;
	
    }
}



	# build up page
    
    $out .= qq |

	<form method="post" action="$thisScript?">
	<p><label for="date">Date range</label>
	<select name="date">
	<option value="$F{'date'}">$F{'date'}</option>
	<option value=""></option>
	<option value="today">today</option>
	<option value="yesterday">yesterday</option>
	<option value="this week">this week</option>
	<option value="last week">last week</option>
	<option value="this month">this month</option>
	<option value="last month">last month</option>
	<option value="two months ago">two months ago</option>
	</select></p>
	<p><button type="submit" name="a" value="stats"  class="button positive"> <img src="/images/icons/tick.png" alt=""/> Get stats! </button></p>
	</form>
<hr>

	<table>
	<tr>
	<th colspan="2">Banners</th>
	<th>Views</th>
	<th>Clicks</th>
	<th>Percent</th>
	</tr>
	|;
    
    foreach (sort keys %B) {
	
		my $pct = int($B{$_}{'link'} / $B{$_}{'count'} * 10000) if ( $B{$_}{'count'} );
		$pct = $pct/100 if ($pct);
		
		next if ($B{$_} =~ /HASH/);
		
		$out .= qq |
	    
	    <tr>
	    <td><a href="$thisScript?a=stat_detail&amp;img=$B{$_}{'fp'}&amp;id=$_&amp;name=$B{$_}"><img src="$B{$_}{'fp'}" height="50" /></a></td>
	    <td>$B{$_}</td>
	    <td>$B{$_}{'count'}</td>
	    <td>$B{$_}{'link'}</td>
	    <td>$pct %</td>
	    </tr>
	    |;
	
    }
    
    $out .= qq |
	<tr>
	<th>Zones</th>
	</tr>
	|;
    
    foreach (sort keys %Z) {
	
	my $pct = int($Z{$_}{'link'} / $Z{$_}{'count'} * 10000) if ($Z{$_}{'count'});
	$pct = $pct/100 if ($pct);
	
	
	$out .= qq |
	    
	    <tr>
	    <td>$Z{$_}</td>
	    <td>$Z{$_}{'count'}</td>
	    <td>$Z{$_}{'link'}</td>
	    <td>$pct %</td>
	    </tr>
	    |;
	
    }
    
    $out .= qq |
	<tr>
	<th>IP</th>
	</tr>
	|;
    
    foreach (sort keys %IP) {
	
	my $pct = int($IP{$_}{'link'} / $IP{$_}{'count'} * 10000) if ($IP{$_}{'count'});
	$pct = $pct/100 if ($pct);
	
	$out .= qq |
	    
	    <tr>
	    <td>users</td>
	    <td>$IP{'count'}</td>
	    <td>$IP{'link'}</td>
	    <td>$pct %</td>
	    </tr>
	    |;
	last;
	
    }

    $out .= qq |
	    </table>
	    |;

    
    return($out);
    
}






################################################################################   
sub checkFile {


	# check if file exists, if yes then see to overwrite or rename
	#  input is the full file name
	#  output, returns 1 if the file exists, returns 0 if the file doesn't

	if (-e "$_[0]") {

		return(1);

	} else {

		return(0);

	}

}


################################################################################   
sub checkDir {

	# check that the image directory exists... if not, create it
	if (!-d "$_[0]") {

		$msg .= `mkdir -p $_[0]`;

	}

	return();

}


################################################################################   
sub renameFile {

	# deal with the renaming of files
	if ($F{'file_pointer'}) {
		my $inFile  = $abs_path.$F{'file_pointer'};
		my $fileType = substr ($F{'file_pointer'}, rindex($F{'file_pointer'}, ".") + 1, 3);
		rename ($inFile,$F{'newname'} );
		$msg .= "$inFile $fileType $F{'newname'}";
	}

}


################################################################################   
sub newimage {

  
    my $line =<<EndofText;
    
<form method="post" enctype="multipart/form-data" action="$thisScript">

  <input type="hidden" name="a" value="upload" />
  <input type="hidden" name="newname" value="$F{'newname'}" />

<h2>Choose A File</h2>

<p>To upload an image, click on the browse button to locate the file on your hard drive.</p>

<p><label for="file">File:</label> <input type="file" name="file" /></p>

<p><input onclick="window.close()" type="button" value="cancel" />
<input type="submit" value="upload" /></p>

</form>

EndofText

	return($line);

}


################################################################################   
sub overwriteOrUpload {

	my $line =<<EndofText;

<form method="post" action="$thisScript">

  <input type="hidden" name="file_pointer" value="$F{'file_pointer'}" />
  <input type="hidden" name="b_id" value="$F{'b_id'}" />

<h2>Overwrite or Rename</h2>

<p><img src="$F{'rel_file'}" /></p>

<p>$F{'file_pointer'} already exists.  Do you want to overwrite or rename it?</p>

<p><label for="new_file_pointer">New Name:</label> <input type="text" name="new_file_pointer" value="$F{'file_pointer'}" /></p>

<p><input type="submit"  name="a" value="overwrite" />
<input type="submit" name="a" value="rename" /></p>

</form>

EndofText

	return($line);

}



################################################################################   
sub getFileSize {

	# get the width and height of an image
	#  input is the full file name
	#  output is two variables, 0 - width in pixels, 1 - height in pixels
	
        my $f = $_[0]."[0]"; # to handle animated gifs
	print STDERR qq|/usr/bin/identify -format "%wx%h" $f|;
	my $size = `/usr/bin/identify -format "%wx%h" $f`;
	

	chop($size);

	$size = substr($size, 0, 7);

	my ($w,$h) = split ("x", $size);

	return($w,$h);

}











################################################################################
sub set_tracker {

	# insert a new record into the tracker to force the new url...

    my ($sql, $sth);

    my $now = "now()";
    
    $sql = qq |
INSERT INTO tracker
(type, banner_id, zone_id, ip, refer, bkey, ts)
VALUES
(?,?,?,?,?,?,?)
    |;

$sth = $dbh->prepare($sql);
$sth->execute('image', $F{'b_id'}, $F{'z_id'}, '127.0.0.1', 'ads.cgi', $F{'z_id'}, $now);

return();
 
}








################################################################################
sub stat_detail {
	
	
	my $sql = qq ~
	select 
		to_char(ts, 'YYYY WW'), 
		sum(case when type='image' then 1 else 0 end), 
		sum(case when type='link' then 1 else 0 end)
	from   tracker
	where  banner_id = $F{'id'}
	group by 1
	order by 1
	~;
	
	$sql = qq ~
	select 
		to_char(ds, 'YYYY WW'), 
		sum(views), 
		sum(clicks) 
	from tracker_summary 
	where 
		banner_id = $F{'id'}
	group by 1 
	order by 1
	~;
	
	my ($chart,$table) = &gchart($sql, "$F{'name'}", "views|clicks");



	# monthly chart
	$sql = qq ~
	select 
		to_char(ds, 'YYYY MM'), 
		sum(views), 
		sum(clicks) 
	from tracker_summary 
	where 
		banner_id = $F{'id'}
	group by 1 
	order by 1
	~;
	
	my ($chart_m,$table_m) = &gchart($sql, "$F{'name'}", "views|clicks");

	
	my $out = qq ~
	
	<h2>$F{'name'}</h2>

	<div><img src="$F{'img'}" class="left" /></div>

       	$chart

	<table>
	<tr><th>Week Year</th><th>Views</th><th>Clicks</th></tr>
	$table
	</table>


       	$chart_m

	<table>
	<tr><th>Month Year</th><th>Views</th><th>Clicks</th></tr>
	$table_m
	</table>
	
	<pre>
	$sql
	</pre>
	
	~;
	
	return($out);
	
}









#################################################################################
sub gchart {
	

	my ($cat, $count, $sum, $t_count, $t_sum, $title, $stitle, $mag_count, $mag_sum, $mag, $all_count, $week, $w, $month, $m, $gc_data_1, $gc_data_2, $gc_axis_x, $gc_min_1, $gc_max_1, $gc_min_2, $gc_max_2, $gc_axis_x, $gc_axis_years, $FLAG_adj, $prev_y, $y_a, $gc_x1, $gc_x2, $output, $table) = "";

	$sth = $dbh->prepare($_[0]);
	$sth->execute ();
	$sth->bind_columns (\$week, \$count, \$sum);

	while ( $sth->fetch ) {


	   	#($month, $m, $y) = &nice_month($month);
		($y, $w) = split (" ", $week);
	   	$t_count += $count;
	   	$t_sum   += $sum;

#		if ($m == $current_month && $y == $current_year) {
#			$count = int($count*$date_pct);
#			$sum = int($sum*$date_pct);
#			$FLAG_adj = "*";
#		}
		$gc_axis_x .= "|".$w;
		$gc_data_1 .= "$count,";
		$gc_min_1 = $count if ($count < $gc_min_1 || !$gc_min_1);
		$gc_max_1 = $count if ($count > $gc_max_1);
		$gc_data_2 .= "$sum,";
		$gc_min_2 = $sum if ($sum < $gc_min_2 || !$gc_min_2);
		$gc_max_2 = $sum if ($sum > $gc_max_2);

        # year axis
        $y_a = "";
		$y_a = $y if ($y != $prev_y);
		$gc_axis_years .= "|$y_a";
		$prev_y = $y;

		$table .= qq |<tr><td>$w $y</td><td align\=\"right\">$count</td><td align\=\"right\">$sum</td></tr>\n|;

	}

	#$t_sum = &decimals($t_sum);

	$FLAG_adj = qq~<em>* this month's figures estimated</em>~ if ($FLAG_adj);
	$table .= qq|<tr class\=\"total\"><td>total<\/td><td align\=\"right\">$t_count<\/td><td align\=\"right\">$t_sum<\/td><\/tr><tr><td colspan\=\"3\" align\=\"right\">$FLAG_adj</tr></table>\n|;

 	$gc_x1 = &g_labels($gc_max_1);
   	$gc_x2 = &g_labels($gc_max_2);
	$gc_max_1 = &max_10($gc_max_1);
	$gc_max_2 = &max_10($gc_max_2);
    $gc_min_1 = 0;
    $gc_min_2 = 0;

	#$gc_axis_years = &gc_years;

	chop($gc_data_1);
	chop($gc_data_2);

	my $chart = qq ~
	http://chart.apis.google.com/chart?cht=lc&chds=$gc_min_1,$gc_max_1,$gc_min_2,$gc_max_2&chd=t:$gc_data_1|$gc_data_2&chs=700x300&chco=009900,0000ff&chxt=x,y,r,x&chxl=0:$gc_axis_x|1:|$gc_x1|2:|$gc_x2|3:$gc_axis_years&chls=2,1,0|2,1,0&chdl=$_[2]&chtt=$_[1]+Overall+by+Week
	~;

	my $sparkline = qq~
	http://chart.apis.google.com/chart?cht=lc&chds=$gc_min_1,$gc_max_1,$gc_min_2,$gc_max_2&chd=t:$gc_data_1|$gc_data_2&chs=300x100&chco=009900,0000ff&chtt=$_[1]+Overall+by+Week
	~;


	$output = qq ~
	<p><img src="$chart" /></p>
	~;
	
	return($output, $table);
	
}

#################################################################################
sub gchart_twoline {
	
	# pass $sql, 0 - title, 1 - axis lables

	my ($cat, $count, $sum, $t_count, $t_sum, $title, $stitle, $mag_count, $mag_sum, $mag, $all_count, $month, $m, $gc_data_1, $gc_data_2, $gc_axis_x, $gc_min_1, $gc_max_1, $gc_min_2, $gc_max_2, $gc_axis_x, $gc_axis_years, $FLAG_adj, $prev_y, $y_a, $gc_x1, $gc_x2, $output, $table) = "";

	$sth = $dbh->prepare($_[0]);
	$sth->execute ();
	$sth->bind_columns (\$month, \$count, \$sum);

	while ( $sth->fetch ) {


	   	($month, $m, $y) = &nice_month($month);
	   	$t_count += $count;
	   	$t_sum   += $sum;

		$gc_axis_x .= "|".&simple_date($month);
		$gc_data_1 .= "$count,";
		$gc_min_1 = $count if ($count < $gc_min_1 || !$gc_min_1);
		$gc_max_1 = $count if ($count > $gc_max_1);
		$gc_data_2 .= "$sum,";
		$gc_min_2 = $sum if ($sum < $gc_min_2 || !$gc_min_2);
		$gc_max_2 = $sum if ($sum > $gc_max_2);

       	# year axis
		$y_a = "";
		$y_a = $y if ($y != $prev_y);
		$gc_axis_years .= "|$y_a";
		$prev_y = $y;

		# build table
		$table .= qq ~<tr><td>$month $year</td><td>$count</td><td>$sum</td></tr>\n~;

	}

	$t_sum = &decimals($t_sum);

   $gc_x1 = &g_labels($gc_max_1);
   $gc_x2 = &g_labels($gc_max_2);
	$gc_max_1 = &max_10($gc_max_1);
	$gc_max_2 = &max_10($gc_max_2);


   $gc_min_1 = 0;
   $gc_min_2 = 0;

	chop($gc_data_1);
	chop($gc_data_2);

	my $chart = qq ~
	http://chart.apis.google.com/chart?cht=lc&chds=$gc_min_1,$gc_max_1,$gc_min_1,$gc_max_1&chd=t:$gc_data_1|$gc_data_2&chs=800x300&chco=009900,0000ff&chxt=x,y,r,x&chxl=0:$gc_axis_x|1:|$gc_x1|2:|$gc_x1|3:$gc_axis_years&chls=2,1,0|2,1,0&chdl=$_[2]&chtt=$_[1]+Overall+by+Month
	~;

	$output = qq ~
	<p><img src="$chart" /></p>
	~;
	
	return($output, $table);
	
}



#################################################################################
sub g_labels {

   # in put max
   my $max = $_[0] * 1.1;
   my $n_labels = 5;
   my $n = 0;
   my $output = "";
   for ($n=0; $n < $n_labels; $n++) {
       my $dp = ($max/$n_labels) * $n;
       $output .= int($dp)."|";
   }
	$output .= int($max);
   return ($output);
}

#################################################################################
sub pct {

	return() if (!$_[1]);

	my $pct = ($_[0]/$_[1]) * 100;
	$pct    = &decimals($pct);

	return($pct);
	
}


#################################################################################
sub dec {

	return() if (!$_[1]);

	my $d = ($_[0]/$_[1]);
	$d    = &decimals($d);
	
	return($d);
	
}


#################################################################################
sub decimals {

	# adds decimals to currency
	my $out;
	
	my ($n, $d) = split (/\./, $_[0]);

	$d = substr($d, 0, 2) if (length($d) > 2);

	if (length($d) == 0) {
		# no decimal... add 00
       $out = $n.".00";
   } elsif(length($d) == 1) {
       # only one, so add 0
       $out = $n.".".$d."0";
   } else {
       # its ok
       $out = $n.".".$d;
   }

   return($out);

}


#################################################################################
sub nice_month {
		
	# takes YYYY MM Month > returns YYYY Month
	my ($y,$mm, $mon) = split (" ", $_[0]);
	my $out = "$mon $y";
	return($out, $mm, $y);
	
}


#################################################################################
sub simple_date {	
	
	# takes Month YYYY > returns Mon
	my ($mon, $y) = split (" ", $_[0]);
	my $out = substr ($mon, 0, 3);
	return($out);
	
}


#################################################################################
sub min_10 {
	
	my $o = $_[0] * 0.9;
	$o = int ($o);
	return ($o);
	
}


#################################################################################
sub max_10 {
	
	my $o = $_[0] * 1.1;
	$o = int ($o);
	return ($o);
	
}


###############################################################################
sub clean_filename {
	
	my $file = shift;
 	$file =~ s/ /_/g;
 	$file =~ s/,//g;
 	$file =~ s/\(//g;
	$file =~ s/\)//g;
	$file =~ s/( |,|\\|\/|\:|\*|\?|\<|\>|\||\[|\]|\(|\)|\{|\}|\+|\*|\^|\$|\?)/_/g;

    return $file;
	
}
