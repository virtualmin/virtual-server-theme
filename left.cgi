#!/usr/bin/perl
# Show the left-side menu of Virtualmin domains, plus modules

do './web-lib.pl';
do './ui-lib.pl';
&init_config();
&ReadParse();
%text = &load_language($current_theme);
@admincats = ( "tmpl", "create", "backup" );

# Work out what categories we have
@modules = &get_visible_module_infos();
%cats = &list_categories(\@modules);
$cats{'others'} = $cats{''};
delete($cats{''});
@cats = sort { ($b eq "others" ? "" : $b) cmp ($a eq "others" ? "" : $a) } keys %cats;

&PrintHeader();
print <<EOF;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
$tconfig{'headhtml'}
<link rel="stylesheet" type="text/css" href="left.css" />
<script type='text/javascript' src='toggleview.js'></script>
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
	$hasvirt = 0 if ($minfo{'version'} < 2.99);
	}
$hasmail = &foreign_available("mailbox");

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
	if (defined($in{'dom'})) {
		$d = &virtual_server::get_domain($in{'dom'});
		}
	elsif (defined($in{'dname'})) {
		$d = &virtual_server::get_domain_by("dom", $in{'dname'});
		}
	else {
		$d = &virtual_server::get_domain_by("user", $remote_user,
						    "parent", "");
		$d ||= $doms[0];
		}
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
	print "<br>\n";
	}

if ($hasvirt) {
	# Left form is for changing domain
	print "<form action=left.cgi>\n";
	$doneform = 1;
	}
elsif ($mode eq "mail") {
	# Left form is form a mail server
	&foreign_require("mailbox", "mailbox-lib.pl");
	@folders = &mailbox::list_folders_sorted();
	$df = $mailbox::userconfig{'default_folder'};
	$dfolder = $df ? &mailbox::find_named_folder($df, \@folders) :
			 $folders[0];
	print "<form action=mailbox/mail_search.cgi target=right>\n";
	print &ui_hidden("simple", 1),"\n";
	print &ui_hidden("folder", $dfolder->{'index'}),"\n";
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
	if (!$d) {
		if ($in{'dname'}) {
			print "\n";
			}
		goto nodomain;
		}
	print "</div>\n";

	$canconfig = &virtual_server::can_config_domain($d);
	if (defined(&virtual_server::get_domain_actions)) {
		# Get actions and menus from Virtualmin
		@buts = &virtual_server::get_domain_actions($d);

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

		# Show others by category (except those for creation)
		my @cats = &unique(map { $_->{'cat'} } @buts);
		foreach my $c (@cats) {
			next if ($c eq 'objects' || $c eq 'create');
			my @incat = grep { $_->{'cat'} eq $c } @buts;
			&print_category_opener("cat_$c", \@cats,
				$virtual_server::text{'cat_'.$c});
			print "<div class='itemhidden' id='cat_$c'>\n";
			foreach my $b (@incat) {
				$url =
				 "virtual-server/$b->{'page'}?dom=$d->{'id'}&".
				 join("&", map { $_->[0]."=".&urlize($_->[1]) }
					       @{$b->{'hidden'}});
				&print_category_link($url, $b->{'title'});
				}
			print "</div>\n";
			}
		}
	else {
		# Use built-in links ..

		# Users and aliases links
		if (&virtual_server::can_domain_have_users($d) &&
		    &virtual_server::can_edit_users()) {
			print "<div class='leftlink'><a href='virtual-server/list_users.cgi?dom=$d->{'id'}' target=right>$text{'left_users'}</a></div>\n";
			}
		if ($d->{'mail'} && &virtual_server::can_edit_aliases()) {
			print "<div class='leftlink'><a href='virtual-server/list_aliases.cgi?dom=$d->{'id'}' target=right>$text{'left_aliases'}</a></div>\n";
			}

		# Editing options
		if (&virtual_server::database_feature($d) &&
		    &virtual_server::can_edit_databases()) {
			print "<div class='leftlink'><a href='virtual-server/list_databases.cgi?dom=$d->{'id'}' target=right>$text{'left_databases'}</a></div>\n";
			}
		if (!$d->{'parent'} && &virtual_server::can_edit_admins()) {
			print "<div class='leftlink'><a href='virtual-server/list_admins.cgi?dom=$d->{'id'}' target=right>$text{'left_admins'}</a></div>\n";
			}
		if ($d->{'web'} && &virtual_server::can_edit_scripts() &&
		    !$d->{'subdom'}) {
			print "<div class='leftlink'><a href='virtual-server/list_scripts.cgi?dom=$d->{'id'}' target=right>$text{'left_scripts'}</a></div>\n";
			}
		if ($canconfig) {
			print "<div class='leftlink'><a href='virtual-server/edit_domain.cgi?dom=$d->{'id'}' target=right>$text{'left_edit'}</a></div>\n";
			}
		else {
			print "<div if='leftlink'><a href='virtual-server/view_domain.cgi?dom=$d->{'id'}' target=right>$text{'left_view'}</a></div>\n";
			}
		if ($d->{'unix'} && &virtual_server::can_edit_limits($d) && !$d->{'alias'}) {
			print "<div class='leftlink'><a href='virtual-server/edit_limits.cgi?dom=$d->{'id'}' target=right>$text{'left_limits'}</a></div>\n";
			}
		if ($virtual_server::config{'bw_active'} && !$d->{'parent'} &&
		    &virtual_server::can_monitor_bandwidth($d)) {
			print "<div class='leftlink'><a href='virtual-server/bwgraph.cgi?dom=$d->{'id'}&mode=2' target=right>$text{'left_bw'}</a></div>\n";
			}
		if (&virtual_server::can_delete_domain($d)) {
			print "<div class='leftlink'><a href='virtual-server/delete_domain.cgi?dom=$d->{'id'}' target=right>$text{'left_delete'}</a></div>\n";
			}
		}

	# Feature and plugin links
	@links = &virtual_server::feature_links($d);
	@flinks = grep { !$_->{'plugin'} && !$_->{'other'} } @links;
	@plinks = grep { $_->{'plugin'} } @links;
	@olinks = grep { $_->{'other'} } @links;
	foreach $lt (\@flinks, \@plinks, \@olinks) {
		if (@$lt) {
			if ($lt eq \@flinks || $lt eq \@olinks) {
				print "<div class='leftlink'><hr></div>\n";
				}
			foreach $l (sort { $a->{'desc'} cmp $b->{'desc'} }
					 @$lt) {
				print "<div class='leftlink'><a href='$l->{'mod'}/$l->{'page'}' target=right>$l->{'desc'}</a></div>\n";
				}
			}
		}

	print "<div class='leftlink'><hr></div>\n";
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
	if (&virtual_server::can_create_master_servers() ||
	    &virtual_server::can_create_sub_servers()) {
	   &print_category_opener("create", \@admincats,
				   $text{'left_create'});
    print "<div class='itemhidden' id='create'>";
		($dleft, $dreason, $dmax) = &virtual_server::count_domains(
						"realdoms");
		($aleft, $areason, $amax) = &virtual_server::count_domains(
						"aliasdoms");
		if ($dleft == 0) {
			# Cannot add
			print "<div class='leftlink'>",&virtual_server::text('index_noadd'.$dreason, $dmax),"</div>\n";
			}
		elsif (!&virtual_server::can_create_master_servers() &&
		       &virtual_server::can_create_sub_servers()) {
			# Can just add sub-server
			&print_category_link("virtual-server/domain_form.cgi", $text{'left_addsub'});
			}
		elsif (&virtual_server::can_create_master_servers()) {
			# Can add master or sub-server
			&print_category_link("virtual-server/domain_form.cgi",
					     $text{'left_add'});
			&print_category_link("virtual-server/domain_form.cgi?parentuser1=$d->{'user'}&add1=1", $text{'left_addsub'});
			}
		if (&virtual_server::can_create_sub_servers() &&
		    !$d->{'alias'} && !$d->{'subdom'} && $dleft) {
			# Can add sub-domain
			&print_category_link("virtual-server/domain_form.cgi?parentuser1=$d->{'user'}&add1=1&subdom=$d->{'id'}", $text{'left_addsubdom'});
			}
		if (&virtual_server::can_create_sub_servers() &&
		    !$d->{'alias'} && $aleft) {
			# Can add alias domain
			&print_category_link("virtual-server/domain_form.cgi?to=$d->{'id'}", $text{'left_addalias'});
			}
		if ((&virtual_server::can_create_sub_servers() ||
		     &virtual_server::can_create_master_servers()) && $dleft &&
		    $virtual_server::virtualmin_pro) {
			# Can create servers from batch file
			&print_category_link("virtual-server/mass_create_form.cgi", $text{'left_cmass'});
			}

		# Migration/import
		if (&virtual_server::can_import_servers()) {
			&print_category_link("virtual-server/import_form.cgi",
					     $text{'left_import'});
			}
		if (&virtual_server::can_migrate_servers()) {
			&print_category_link("virtual-server/migrate_form.cgi",
					     $text{'left_migrate'});
			}
    print "</div>\n";		
		}

 	# Backup/restore forms
  if (&virtual_server::can_backup_domains()) {
    &print_category_opener("backup", \@admincats, $text{'left_backup'});
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
	print "<div class='leftlink'><hr></div>\n";
	print "<div class='linkwithicon'><img src=images/mail-small.gif>\n";
	$fprog = $mconfig{'mail_system'} == 4 &&
		 &get_webmin_version() >= 1.227 ? "list_ifolders.cgi"
					        : "list_folders.cgi";
	print "<div class='aftericon'><a target=right href='mailbox/$fprog'>$text{'left_folders'}</a></div></div>\n";
	if (!$mconfig{'noprefs'}) {
		print "<div class='linkwithicon'><img src=images/usermin-small.gif>\n";
		print "<div class='aftericon'><a target=right href='uconfig.cgi?mailbox'>$text{'left_prefs'}</a></div></div>\n";
		}
	if (&foreign_available("changepass")) {
		print "<div class='linkwithicon'><img src=images/pass.gif>\n";
		print "<div class='aftericon'><a target=right href='changepass/'>$text{'left_pass'}</a></div></div>\n";
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
					     $minfo->{'desc'});
			}
		print "</div>\n";
		}
	print "<div class='leftlink'><hr></div>\n";
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

print "</form>\n" if ($doneform);
print <<EOF;
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
print "<a href=\"javascript:toggleview('$c','toggle$c')\" id='toggle$c'><img border='0' src='images/closedbg.gif' alt='[+]'></a>\n";
print "<div class='aftericon'><a href=\"javascript:toggleview('$c','toggle$c')\" id='toggle$c'><font size=+1 color=#000000 style='font-size:14px'>$label</font></a></div></div>\n";
}


sub print_category_link
{
local ($link, $label, $image, $noimage) = @_;
#if ($noimage) {
	print "<div class='linkindented'><a target=right href=$link><font size=-1>$label</font></a></div>\n";
#	}
# {
#	print "<div class='linkwithicon'>$image\n";
#	print "<div class='aftericon'><a target=right href=$link><font size=-1>$label</a></font></div></div>\n";
#	}
}

