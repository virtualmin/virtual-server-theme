#!/usr/local/bin/perl
# Show the left-side menu of Virtualmin domains, plus modules

do './web-lib.pl';
do './ui-lib.pl';
&init_config();
&ReadParse();
&load_theme_library();
%text = &load_language($current_theme);
@admincats = ( "tmpl", "create", "backup" );

# Work out what categories we have
@modules = &get_visible_module_infos();
%cats = &list_categories(\@modules);
if (defined($cats{''})) {
	$cats{'others'} = $cats{''};
	delete($cats{''});
	}
@cats = sort { ($b eq "others" ? "" : $b) cmp ($a eq "others" ? "" : $a) } keys %cats;

&PrintHeader();
print <<EOF;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
<link rel='stylesheet' type='text/css' href='$gconfig{'webprefix'}/unauthenticated/style.css' />
<link rel="stylesheet" type="text/css" href="left.css" />
<script type='text/javascript' src='$gconfig{'webprefix'}/unauthenticated/toggleview.js'></script>
<!--[if gte IE 5.5000]>
  <script type='text/javascript' src='pngfix.js'></script>
<![endif]-->
</head>
<body bgcolor=#e8e8ea>
EOF

# Find out which modules we have
$hasvirt = &foreign_available("virtual-server");
if ($hasvirt) {
	%minfo = &get_module_info("virtual-server");
	%vconfig = &foreign_config("virtual-server");
	$hasvirt = 0 if ($minfo{'version'} < 2.99);
	}
$hasmail = &foreign_available("mailbox");

$image = $vconfig{'theme_image'} || $gconfig{'virtualmin_theme_image'};
if ($image) {
	# Show the hosting provider logo
	$link = $vconfig{'theme_link'} || $gconfig{'virtualmin_theme_link'};
	print "<a href='$link' target=_new>" if ($link);
	print "<img src='$vconfig{'theme_image'}' border=0>";
	print "</a><br>\n" if ($link);
	}

# Find editable domains
$mode = $in{'mode'} ? $in{'mode'} :
	$hasvirt ? "virtualmin" :
	$hasmail ? "mail" :
		   &get_product_name();
if ($mode eq "virtualmin" && $hasvirt) {
	# Get and sort the domains
	&foreign_require("virtual-server", "virtual-server-lib.pl");
	@alldoms = &virtual_server::list_domains();
	@doms = grep { &virtual_server::can_edit_domain($_) } @alldoms;
	if ($virtual_server::config{'domains_sort'} eq 'dom') {
		# By domain name
		@doms = sort { lc($a->{'dom'}) cmp lc($b->{'dom'}) } @doms;
		}
	elsif ($virtual_server::config{'domains_sort'} eq 'user') {
		# By username, with indents
		@doms = sort { lc($a->{'user'}) cmp lc($b->{'user'}) ||
			       $a->{'parent'} <=> $b->{'parent'} ||
			       $a->{'created'} <=> $b->{'created'} } @doms;
		foreach my $d (@doms) {
			local $show = $d->{'dom'};
			$show = "  ".$show if ($d->{'parent'});
			$show = "  ".$show if ($d->{'alias'});
			#$show = $show." ($d->{'user'})" if (!$d->{'parent'});
			$d->{'showdom'} = $show;
			}
		}

	# Work out which domain we are editing
	$sects = &get_right_frame_sections();
	if (defined($in{'dom'})) {
		$d = &virtual_server::get_domain($in{'dom'});
		}
	elsif (defined($in{'dname'})) {
		$d = &virtual_server::get_domain_by("dom", $in{'dname'});
		}
	elsif ($sects && $sects->{'dom'}) {
		$d = &virtual_server::get_domain($sects->{'dom'});
		$d = undef if (!&virtual_server::can_edit_domain($d));
		}

	# Fall back to first owned by this user, or first in list
	$d ||= &virtual_server::get_domain_by("user", $remote_user,
					      "parent", "");
	$d ||= $doms[0];
	}
else {
	$d = { 'id' => $in{'dom'} };
	}
$did = $d ? $d->{'id'} : undef;

# Show virtualmin / folders / webmin mode selector
if ($hasvirt || $hasmail) {
	print "<div class='mode'>";
	foreach $m ($hasvirt ? ( "virtualmin" ) : ( ),
		    $hasmail ? ( "mail" ) : ( ),
		    &get_product_name()) {
		if ($m ne $mode) {
			print "<a href='left.cgi?mode=$m&dom=$did'>";
			}
		else {
			print "<b>";
			}
		print "<img src=images/$m-small.gif border=0> ".ucfirst($m);
		if ($m ne $mode) {
			print "</a>\n";
			}
		else {
			print "</b>\n";
			}
		}
	print "</div>";
	}

print "<div class='menubody'>\n";
if ($hasvirt) {
	# Left form is for changing domain
	print "<form action=left.cgi>\n";
	$doneform = 1;
	}
elsif ($mode eq "mail") {
	# Left form is for searching a mail folder
	&foreign_require("mailbox", "mailbox-lib.pl");
	@folders = &mailbox::list_folders_sorted();
	$df = $mailbox::userconfig{'default_folder'};
	$dfolder = $df ? &mailbox::find_named_folder($df, \@folders) :
			 $folders[0];
	print "<script>\n";
	print "function GetMailFolder()\n";
	print "{\n";
	print "var url = ''+window.parent.frames[1].location;\n";
	print "var qm = url.indexOf('?');\n";
	print "if (qm > 0) {\n";
	print "    var params = url.substring(qm+1).split('&');\n";
	print "    for(var i=0; i<params.length; i++) {\n";
	print "        var nv = params[i].split('=');\n";
	print "        if (nv[0] == 'id') {\n";
	print "            if (nv[1] != '1') {\n";
	print "                document.forms[0].id.value = unescape(nv[1]);\n";
	print "                }\n";
	print "            }\n";
	print "        }\n";
	print "    }\n";
	print "}\n";
	print "</script>\n";
	print "<form action=mailbox/mail_search.cgi target=right onSubmit='GetMailFolder()'>\n";
	print &ui_hidden("simple", 1),"\n";
	print &ui_hidden("folder", $dfolder->{'index'}),"\n";
	print &ui_hidden("id", undef),"\n";
	$doneform = 1;
	}

# Show login and Virtualmin access level
print &text('left_login', $remote_user);
if (@doms) {
	$level = &virtual_server::master_admin() ? $text{'left_master'} :
		 &virtual_server::reseller_admin() ? $text{'left_reseller'} :
		 &virtual_server::extra_admin() ? $text{'left_extra'} :
		 $virtual_server::single_domain_mode ? $text{'left_single'} :
						       $text{'left_user'};
	print " ($level)";
	}

if ($mode eq "virtualmin" && @doms) {
	# Show Virtualmin servers this user can edit, plus links for various
	# functions within each
	print "<div class='domainmenu'>\n";
	if ($virtual_server::config{'display_max'} &&
	    @doms > $virtual_server::config{'display_max'}) {
		# Show text field for domain name
		print $text{'left_dname'},
		      &ui_textbox("dname", $d ? $d->{'dom'} : $in{'dname'}, 15);
		}
	else {
		# Show menu of domains
		print &ui_select("dom", $did,
			[ map { [ $_->{'id'}, &virtual_server::shorten_domain_name($_) ] } @doms ],
			1, 0, 0, 0, "onChange='form.submit()'");
		}
	print "<input type=image src=images/ok.gif></td> </tr>\n";
	foreach $a (@admincats) {
		print &ui_hidden($a, 1),"\n" if ($in{$a});
		}
	print "</div>\n";
	if (!$d) {
		if ($in{'dname'}) {
			print "\n";
			}
		}

	# Show generic creation link
	if ($virtual_server::module_info{'version'} >= 3.381 &&
	    (&virtual_server::can_create_master_servers() ||
	     &virtual_server::can_create_sub_servers())) {
		print "<div class='leftlink'><a href='virtual-server/domain_form.cgi?generic=1&gparent=$d->{'id'}' target=right>$text{'left_generic'}</a></div>\n";
		$shown_generic_create = 1;
		}

	if (!$d) {
		goto nodomain;
		}

	# Get actions and menus from Virtualmin
	$canconfig = &virtual_server::can_config_domain($d);
	@buts = &virtual_server::get_domain_actions($d);
	push(@buts, &virtual_server::feature_links($d));

	# Always show edit domain link
	if ($canconfig) {
		print "<div class='leftlink'><a href='virtual-server/edit_domain.cgi?dom=$d->{'id'}' target=right>$text{'left_edit'}</a></div>\n";
		}
	else {
		print "<div class='leftlink'><a href='virtual-server/view_domain.cgi?dom=$d->{'id'}' target=right>$text{'left_view'}</a></div>\n";
		}

	# Show 'objects' category actions
	my @incat = grep { $_->{'cat'} eq 'objects' } @buts;
	foreach my $b (@incat) {
		$url = "virtual-server/$b->{'page'}?dom=$d->{'id'}&".
		 join("&", map { $_->[0]."=".&urlize($_->[1]) }
			       @{$b->{'hidden'}});
		print "<div class='leftlink'><a href='$url' target=right>$b->{'title'}</a></div>\n";
		}

	# Show others by category (except those for creation, which appear
	# at the bottom)
	my @cats = &unique(map { $_->{'cat'} } @buts);
	foreach my $c (@cats) {
		next if ($c eq 'objects' || $c eq 'create');
		my @incat = grep { $_->{'cat'} eq $c } @buts;
		&print_category_opener("cat_$c", \@cats,
			$virtual_server::text{'cat_'.$c});
		print "<div class='itemhidden' id='cat_$c'>\n";
		foreach my $b (sort { ($a->{'title'} || $a->{'desc'}) cmp
				      ($b->{'title'} || $b->{'desc'})} @incat) {
			if ($b->{'mod'}) {
				$url = "$b->{'mod'}/$b->{'page'}";
				}
			else {
				$url = "virtual-server/$b->{'page'}?dom=$d->{'id'}&".
				 join("&", map { $_->[0]."=".&urlize($_->[1]) }
					       @{$b->{'hidden'}});
				}
			$title = $b->{'title'} || $b->{'desc'};
			&print_category_link($url, $title,
				     undef, undef, $b->{'target'});
			}
		print "</div>\n";
		}

	# Custom links for this domain
	@cl = defined(&virtual_server::list_visible_custom_links) ?
		&virtual_server::list_visible_custom_links($d) : ( );
	if (@cl) {
		# Work out categories, and show links under them
		@linkcats = &unique(map { $_->{'cat'} } @cl);
		foreach my $lc (@linkcats) {
			@catcl = grep { $_->{'cat'} eq $lc } @cl;
			$catclid = "cat_custom_".$lc;
			&print_category_opener($catclid, \@cats,
					       $catcl[0]->{'catname'} ||
						$text{'left_customlinks'});
			print "<div class='itemhidden' id='$catclid'>\n";
			foreach $l (@catcl) {
				&print_category_link($l->{'url'},
					     $l->{'desc'}, undef, undef,
					     $l->{'open'} ? "_new" : "right");
				}
			print "</div>\n";
			}
		}

	print "<hr>\n";
	nodomain:
	}
elsif ($mode eq "virtualmin") {
	# No domains
	print "<div class='leftlink'>";
	if (@alldoms) {
		print $text{'left_noaccess'};
		}
	else {
		print $text{'left_nodoms'};
		}
	print "</div>\n";

	# Show generic creation link
	if ($virtual_server::module_info{'version'} >= 3.381 &&
	    (&virtual_server::can_create_master_servers() ||
	     &virtual_server::can_create_sub_servers())) {
		print "<div class='leftlink'><a href='virtual-server/domain_form.cgi?generic=1' target=right>$text{'left_generic'}</a></div>\n";
		$shown_generic_create = 1;
		}
	}

if ($mode eq "virtualmin") {
	if (&virtual_server::can_edit_templates()) {
		# Show collapsible section for template links
		&print_category_opener("tmpl", \@admincats,
					   $text{'left_tmpl'});
		print "<div class='itemhidden' id='tmpl'>\n";
		($tlinks, $ttitles) = &virtual_server::get_template_pages();
		for($i=0; $i<@$tlinks; $i++) {
			&print_category_link(
				"virtual-server/$tlinks->[$i]",
				$ttitles->[$i]);
			}
		&print_category_link(
			"config.cgi?virtual-server",
			$text{'header_config'});
		&print_category_link(
			"virtual-server/check.cgi",
			$text{'left_check'});
		print "</div>\n";
		}

	# Creation/migration forms
	@createlinks = ( );
	if (&virtual_server::can_create_master_servers() ||
	    &virtual_server::can_create_sub_servers()) {
		($dleft, $dreason, $dmax, $dhide) =
			&virtual_server::count_domains("realdoms");
		($aleft, $areason, $amax, $ahide) =
			&virtual_server::count_domains("aliasdoms");
		if ($shown_generic_create) {
			# Skip top-level and sub-server links, as we've already
			# shown them.
			}
		elsif ($dleft == 0) {
			# Cannot add
			push(@createlinks,
			  "<div class='leftlink'>".
			  &virtual_server::text('index_noadd'.$dreason, $dmax).
			  "</div>\n");
			}
		elsif (!&virtual_server::can_create_master_servers() &&
		       &virtual_server::can_create_sub_servers()) {
			# Can just add sub-server
			push(@createlinks,
			     &category_link("virtual-server/domain_form.cgi",
					    $text{'left_addsub'}));
			}
		elsif (&virtual_server::can_create_master_servers()) {
			# Can add master or sub-server
			push(@createlinks,
			     &category_link("virtual-server/domain_form.cgi",
					    $text{'left_add'}));
			push(@createlinks,
			     &category_link("virtual-server/domain_form.cgi?".
					    "parentuser1=$d->{'user'}&add1=1",
					    $text{'left_addsub'}));
			}
		if (&virtual_server::can_create_sub_servers() &&
		    !$d->{'alias'} && !$d->{'subdom'} && $dleft &&
		    !$shown_generic_create) {
			# Can add sub-domain
			push(@createlinks,
			     &category_link("virtual-server/domain_form.cgi?".
					    "parentuser1=$d->{'user'}&add1=1&".
					    "subdom=$d->{'id'}",
					    $text{'left_addsubdom'}));
			}
		if (&virtual_server::can_create_sub_servers() &&
		    !$d->{'alias'} && $aleft &&
		    !$shown_generic_create) {
			# Can add alias domain
			push(@createlinks,
			     &category_link("virtual-server/domain_form.cgi?".
					    "to=$d->{'id'}",
					    $text{'left_addalias'}));
			}

		if ((&virtual_server::can_create_sub_servers() ||
		     &virtual_server::can_create_master_servers()) && $dleft &&
		    $virtual_server::virtualmin_pro) {
			# Can create servers from batch file
			push(@createlinks,
			   &category_link("virtual-server/mass_create_form.cgi",
					   $text{'left_cmass'}));
			}

		# Migration/import
		if (&virtual_server::can_import_servers()) {
			push(@createlinks,
			     &category_link("virtual-server/import_form.cgi",
					    $text{'left_import'}));
			}
		if (&virtual_server::can_migrate_servers()) {
			push(@createlinks,
			     &category_link("virtual-server/migrate_form.cgi",
					    $text{'left_migrate'}));
			}
		}
	if (@createlinks) {
	        &print_category_opener("create", \@admincats,
				       $text{'left_create'});
		print "<div class='itemhidden' id='create'>";
		foreach $cl (@createlinks) {
			print $cl;
			}
		print "</div>\n";		
		}

 	# Backup/restore forms
	if (&virtual_server::can_backup_domains()) {
		&print_category_opener("backup", \@admincats,
					$text{'left_backup'});
		print "<div class='itemhidden' id='backup'>";
		&print_category_link("virtual-server/backup_form.cgi",
				     $virtual_server::text{'index_backup'});
		&print_category_link("virtual-server/backup_form.cgi?sched=1",
				     $virtual_server::text{'index_sched'});
		&print_category_link("virtual-server/restore_form.cgi",
				     $virtual_server::text{'index_restore'});
		print "</div>\n";
		}

	# Normal Virtualmin menu
	print "<div class='linkwithicon'><img src=images/virtualmin-small.gif><b><div class='aftericon'><a href='virtual-server/index.cgi' target=right>$text{'left_virtualmin'}</a></b></div></div>\n";
	}

if ($mode eq "mail") {
	# Show mail folders
	foreach $f (@folders) {
		$fid = &mailbox::folder_name($f);
		print "<div class='leftlink'><a href='mailbox/index.cgi?id=$fid' target=right>$f->{'name'}</a></div>\n";
		}

	# Show search box
	print "<div class='leftlink'>$text{'left_search'} ",
	      &ui_textbox("search", undef, 10),"</div>\n";

	# Show manage folders, mail preferences and change password links
	%mconfig = %mailbox::config;
	if (!%mconfig) {
		%mconfig = &foreign_config("mailbox");
		}
	print "<hr>\n";

	# Folder list link
	print "<div class='linkwithicon'><img src=images/mail-small.gif>\n";
	$fprog = $mconfig{'mail_system'} == 4 &&
		 &get_webmin_version() >= 1.227 ? "list_ifolders.cgi"
					        : "list_folders.cgi";
	print "<div class='aftericon'><a target=right href='mailbox/$fprog'>$text{'left_folders'}</a></div></div>\n";

	print "<div class='linkwithicon'><img src=images/address-small.gif>\n";
	print "<div class='aftericon'><a target=right href='mailbox/list_addresses.cgi'>$text{'left_addresses'}</a></div></div>\n";

	# Preferences for read mail link
	if (!$mconfig{'noprefs'}) {
		print "<div class='linkwithicon'><img src=images/usermin-small.gif>\n";
		print "<div class='aftericon'><a target=right href='uconfig.cgi?mailbox'>$text{'left_prefs'}</a></div></div>\n";
		}

	# Change password link
	if (&foreign_available("changepass")) {
		print "<div class='linkwithicon'><img src=images/pass.gif>\n";
		print "<div class='aftericon'><a target=right href='changepass/'>$text{'left_pass'}</a></div></div>\n";
		}

	# Mail filter link
	if (&foreign_available("filter")) {
		print "<div class='linkwithicon'><img src=images/filter.gif>\n";
		print "<div class='aftericon'><a target=right href='filter/'>$text{'left_filter'}</a></div></div>\n";
		}
	}

if ($mode eq "webmin" || $mode eq "usermin") {
	# Show all modules under categories
	foreach $c (@cats) {
		# Show category opener, plus modules under it
		&print_category_opener($c, \@cats, $cats{$c});
  	print "<div class='itemhidden' id='$c'>";
		$creal = $c eq "others" ? "" : $c;
		@inmodules = grep { $_->{'category'} eq $creal } @modules;
		foreach $minfo (@inmodules) {
			&print_category_link("$minfo->{'dir'}/",
					     $minfo->{'desc'},
					     undef,
					     undef,
					     $minfo->{'noframe'} ? "_top" : "");
			}
		print "</div>\n";
		}
	print "<hr>\n";
	}

# Show change password link for resellers
if ($hasvirt &&
    $virtual_server::module_info{'version'} >= 3.121 &&
    &virtual_server::reseller_admin()) {
	print "<div class='linkwithicon'><img src=images/pass.gif>\n";
	print "<div class='aftericon'><a target=right href='virtual-server/edit_pass.cgi'>$text{'left_pass'}</a></div></div>\n";
	}

# Show bandwidth link for resellers
if ($hasvirt &&
    $virtual_server::module_info{'version'} >= 3.171 &&
    &virtual_server::reseller_admin()) {
	print "<div class='linkwithicon'><img src=images/bw.gif>\n";
	print "<div class='aftericon'><a target=right href='virtual-server/bwgraph.cgi'>$text{'left_bw'}</a></div></div>\n";
	}

# Show info link
print "<div class='linkwithicon'><img src=images/gohome.gif>\n";
print "<div class='aftericon'><a target=right href='right.cgi?open=system&open=status'>$text{'left_home'}</a></div></div>\n";

# Show logout link
&get_miniserv_config(\%miniserv);
if ($miniserv{'logout'} && !$ENV{'SSL_USER'} && !$ENV{'LOCAL_USER'} &&
    $ENV{'HTTP_USER_AGENT'} !~ /webmin/i) {
	print "<div class='linkwithicon'><img src=images/stock_quit.gif>\n";
	if ($main::session_id) {
		print "<div class='aftericon'><a target=_top href='session_login.cgi?logout=1'>$text{'main_logout'}</a></div>";
		}
	else {
		print "<div class='aftericon'><a target=_top href='switch_user.cgi'>$text{'main_switch'}</a></div>";
		}
	print "</div>\n";
	}

# Show link back to original Webmin server
if ($ENV{'HTTP_WEBMIN_SERVERS'}) {
	print "<div class='linkwithicon'><img src=images/webmin-small.gif>\n";
	print "<div class='aftericon'><a target=_top href='$ENV{'HTTP_WEBMIN_SERVERS'}'>$text{'header_servers'}</a></div>";
	}

print "</form>\n" if ($doneform);
print <<EOF;
</div>
</body>
EOF

# print_category_opener(name, &allcats, label)
# Prints out an open/close twistie for some category
sub print_category_opener
{
local ($c, $cats, $label) = @_;
local @others = grep { $_ ne $c } @$cats;
local $others = join("&", map { $_."=".$in{$_} } @others);
$others = "&$others" if ($others);
$others .= "&dom=$did";
$others .= "&mode=$mode";
$label = $c eq "others" ? "Others" : $label;

# Show link to close or open catgory
print "<div class='linkwithicon'>";
print "<a href=\"javascript:toggleview('$c','toggle$c')\" id='toggle$c'><img border='0' src='images/closed.gif' alt='[+]'></a>\n";
print "<div class='aftericon'><a href=\"javascript:toggleview('$c','toggle$c')\" id='toggle$c'><font color=#000000>$label</font></a></div></div>\n";
}


sub print_category_link
{
print &category_link(@_);
}

sub category_link
{
local ($link, $label, $image, $noimage, $target) = @_;
$target ||= "right";
return "<div class='linkindented'><a target=$target href=$link>$label</a></div>\n";
}
