#!/usr/bin/perl
# Show the left-side menu of Virtualmin domains, plus modules
# XXX show all possible domain action buttons?

do './web-lib.pl';
do './ui-lib.pl';
&init_config();
&ReadParse();
%text = &load_language($current_theme);
@admincats = ( "tmpl", "create", "backup" );

# Work out what categories we have
@modules = &get_visible_module_infos();
&read_file("$config_directory/webmin.catnames", \%catnames);
foreach $m (@modules) {
	$c = $m->{'category'};
	$cname = $c || "others";
	next if ($cats{$cname});
	if (defined($catnames{$c})) {
		$cats{$cname} = $catnames{$c};
		}
	elsif ($text{"category_$c"}) {
		$cats{$cname} = $text{"category_$c"};
		}
	else {
		# try to get category name from module ..
		local %mtext = &load_language($m->{'dir'});
		if ($mtext{"category_$c"}) {
			$cats{$cname} = $mtext{"category_$c"};
			}
		else {
			$cats{$cname} = $c;
			}
		}
	}
@cats = sort { ($b eq "others" ? "" : $b) cmp ($a eq "others" ? "" : $a) } keys %cats;

&PrintHeader();
print <<EOF;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
$tconfig{'headhtml'}
<script type='text/javascript' src='/toggleview.js'></script>
<!--[if gte IE 5.5000]>
  <script type='text/javascript' src='/pngfix.js'></script>
<![endif]-->
</head>
<body bgcolor=#e8e8ea>
<table width=100%>
EOF

# Find editable domains
$hasvirt = &foreign_available("virtual-server");
if ($hasvirt) {
	%minfo = &get_module_info("virtual-server");
	$hasvirt = 0 if ($minfo{'version'} < 2.99);
	}
$mode = $in{'mode'} ? $in{'mode'} : $hasvirt ? "virtualmin" : "webmin";
if ($mode eq "virtualmin" && $hasvirt) {
	&foreign_require("virtual-server", "virtual-server-lib.pl");
	@alldoms = &virtual_server::list_domains();
	@doms = grep { &virtual_server::can_edit_domain($_) } @alldoms;
	@doms = sort { lc($a->{'dom'}) cmp lc($b->{'dom'}) } @doms;
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

# Show virtualmin / webmin mode selector
if ($hasvirt) {
	print "<tr> <td colspan=2 nowrap>";
	foreach $m ("virtualmin", "webmin") {
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
	print "</td> </tr>\n";
	}

# Show login and Virtualmin access level
print "<tr> <td colspan=2>\n";
print &text('left_login', $remote_user);
if (@doms) {
	$level = &virtual_server::master_admin() ? $text{'left_master'} :
		 &virtual_server::reseller_admin() ? $text{'left_reseller'} :
		 &virtual_server::extra_admin() ? $text{'left_extra'} :
		 $virtual_server::single_domain_mode ? $text{'left_single'} :
						       $text{'left_user'};
	print " ($level)";
	}
print "</td><tr>\n";

if ($mode eq "virtualmin" && @doms) {
	# Show Virtualmin servers this user can edit, plus links for various
	# functions within each
	print "<form action=left.cgi>\n";
	print "<tr> <td colspan=2 nowrap>";
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
	print "</form>\n";
	if (!$d) {
		if ($in{'dname'}) {
			print "<tr> <td colspan=2>$text{'left_nosuch'}</td> </tr>\n";
			}
		goto nodomain;
		}

	# Users and aliases links
	if (&virtual_server::can_domain_have_users($d) &&
	    &virtual_server::can_edit_users()) {
		print "<tr> <td colspan=2><a href='virtual-server/list_users.cgi?dom=$d->{'id'}' target=right>$text{'left_users'}</a></td> </tr>\n";
		}
	if ($d->{'mail'} && &virtual_server::can_edit_aliases()) {
		print "<tr> <td colspan=2><a href='virtual-server/list_aliases.cgi?dom=$d->{'id'}' target=right>$text{'left_aliases'}</a></td> </tr>\n";
		}

	# Editing options
	$canconfig = &virtual_server::can_config_domain($d);
	if (&virtual_server::database_feature($d) &&
	    &virtual_server::can_edit_databases()) {
		print "<tr> <td colspan=2><a href='virtual-server/list_databases.cgi?dom=$d->{'id'}' target=right>$text{'left_databases'}</a></td> </tr>\n";
		}
	if (!$d->{'parent'} && &virtual_server::can_edit_admins()) {
		print "<tr> <td colspan=2><a href='virtual-server/list_admins.cgi?dom=$d->{'id'}' target=right>$text{'left_admins'}</a></td> </tr>\n";
		}
	if ($d->{'web'} && &virtual_server::can_edit_scripts() &&
	    !$d->{'subdom'}) {
		print "<tr> <td colspan=2><a href='virtual-server/list_scripts.cgi?dom=$d->{'id'}' target=right>$text{'left_scripts'}</a></td> </tr>\n";
		}
	if ($canconfig) {
		print "<tr> <td colspan=2><a href='virtual-server/edit_domain.cgi?dom=$d->{'id'}' target=right>$text{'left_edit'}</a></td> </tr>\n";
		}
	else {
		print "<tr> <td colspan=2><a href='virtual-server/view_domain.cgi?dom=$d->{'id'}' target=right>$text{'left_view'}</a></td> </tr>\n";
		}
	if ($d->{'unix'} && &virtual_server::can_edit_limits($d) && !$d->{'alias'}) {
		print "<tr> <td colspan=2><a href='virtual-server/edit_limits.cgi?dom=$d->{'id'}' target=right>$text{'left_limits'}</a></td> </tr>\n";
		}
	if ($virtual_server::config{'bw_active'} && !$d->{'parent'} &&
	    &virtual_server::can_monitor_bandwidth($d)) {
		print "<tr> <td colspan=2><a href='virtual-server/bwgraph.cgi?dom=$d->{'id'}&mode=2' target=right>$text{'left_bw'}</a></td> </tr>\n";
		}
	if (&virtual_server::can_delete_domain($d)) {
		print "<tr> <td colspan=2><a href='virtual-server/delete_domain.cgi?dom=$d->{'id'}' target=right>$text{'left_delete'}</a></td> </tr>\n";
		}

	# Feature and plugin links
	@links = &virtual_server::feature_links($d);
	@flinks = grep { !$_->{'plugin'} && !$_->{'other'} } @links;
	@plinks = grep { $_->{'plugin'} } @links;
	@olinks = grep { $_->{'other'} } @links;
	foreach $lt (\@flinks, \@plinks, \@olinks) {
		if (@$lt) {
			if ($lt eq \@flinks || $lt eq \@olinks) {
				print "<tr> <td colspan=2><hr></td> </tr>\n";
				}
			foreach $l (@$lt) {
				print "<tr> <td colspan=2><a href='$l->{'mod'}/$l->{'page'}' target=right>$l->{'desc'}</a></td> </tr>\n";
				}
			}
		}

	print "<tr> <td colspan=2><hr></td> </tr>\n";
	nodomain:
	}
elsif ($mode eq "virtualmin") {
	# No domains
	print "<tr> <td colspan=2>";
	if (@alldoms) {
		print $text{'left_noaccess'};
		}
	else {
		print $text{'left_nodoms'};
		}
	print "</td> </tr>\n";
	}

print "</table>\n";

if ($mode eq "virtualmin") {
	if (&virtual_server::can_edit_templates()) {
		# Show collapsible section for template links
		&print_category_opener("tmpl", \@admincats,
					   $text{'left_tmpl'});
		print "<div class='itemhidden' id='tmpl'>\n";
		print "<table width=100%>\n";
		($tlinks, $ttitles) = &virtual_server::get_template_pages();
		for($i=0; $i<@$tlinks; $i++) {
			&print_category_link(
				"/virtual-server/$tlinks->[$i]",
				$ttitles->[$i]);
			}
		&print_category_link(
			"/config.cgi?virtual-server",
			$text{'header_config'});
		&print_category_link(
			"/virtual-server/check.cgi",
			$text{'left_check'});
		print "</table>\n";
		print "</div><br>\n";
		}

	# Creation/migration forms
	if (&virtual_server::can_create_master_servers() ||
	    &virtual_server::can_create_sub_servers()) {
	   &print_category_opener("create", \@admincats,
				   $text{'left_create'});
    print "<div class='itemhidden' id='create'>";
    print "<table width=100%>\n";
		($dleft, $dreason, $dmax) = &virtual_server::count_domains(
						"realdoms");
		($aleft, $areason, $amax) = &virtual_server::count_domains(
						"aliasdoms");
		if ($dleft == 0) {
			# Cannot add
			print "<tr> <td></td> <td>",&virtual_server::text('index_noadd'.$dreason, $dmax),"</td> </tr>\n";
			}
		elsif (!&virtual_server::can_create_master_servers() &&
		       &virtual_server::can_create_sub_servers()) {
			# Can just add sub-server
			&print_category_link("/virtual-server/domain_form.cgi", $text{'left_addsub'});
			}
		elsif (&virtual_server::can_create_master_servers()) {
			# Can add master or sub-server
			&print_category_link("/virtual-server/domain_form.cgi",
					     $text{'left_add'});
			&print_category_link("/virtual-server/domain_form.cgi?parentuser1=$d->{'user'}&add1=1", $text{'left_addsub'});
			}
		if (&virtual_server::can_create_sub_servers() &&
		    !$d->{'alias'} && !$d->{'subdom'} && $dleft) {
			# Can add sub-domain
			&print_category_link("/virtual-server/domain_form.cgi?parentuser1=$d->{'user'}&add1=1&subdom=$d->{'id'}", $text{'left_addsubdom'});
			}
		if (&virtual_server::can_create_sub_servers() &&
		    !$d->{'alias'} && $aleft) {
			# Can add alias domain
			&print_category_link("/virtual-server/domain_form.cgi?to=$d->{'id'}", $text{'left_addalias'});
			}

		# Migration/import
		if (&virtual_server::can_import_servers()) {
			&print_category_link("/virtual-server/import_form.cgi",
					     $text{'left_import'});
			}
		if (&virtual_server::can_migrate_servers()) {
			&print_category_link("/virtual-server/migrate_form.cgi",
					     $text{'left_migrate'});
			}
	  print "</table>\n";
    print "</div><br>\n";		
		}

 	# Backup/restore forms
  if (&virtual_server::can_backup_domains()) {
    &print_category_opener("backup", \@admincats, $text{'left_backup'});
    print "<div class='itemhidden' id='backup'>";
		print "<table width=100%>\n";
		&print_category_link("/virtual-server/backup_form.cgi",
				     $virtual_server::text{'index_backup'});
		&print_category_link("/virtual-server/backup_form.cgi?sched=1",
				     $virtual_server::text{'index_sched'});
		&print_category_link("/virtual-server/restore_form.cgi",
				     $virtual_server::text{'index_restore'});
		print "</table>\n";
		print "</div><br>\n";
		}

	# Normal Virtualmin menu
  print "<table width=100%>\n";
	print "<tr> <td><img src=images/virtualmin-small.gif></td> <td><b><a href='virtual-server/index.cgi' target=right>$text{'left_virtualmin'}</a></b></td> </tr>\n";
	}

if ($mode eq "webmin") {
	# Show all modules under categories
	foreach $c (@cats) {
		# Show category opener, plus modules under it
		&print_category_opener($c, \@cats, $cats{$c});
  	print "<div class='itemhidden' id='$c'>";
		print "<table width=100%>\n";
		$creal = $c eq "others" ? "" : $c;
		@inmodules = grep { $_->{'category'} eq $creal } @modules;
		foreach $minfo (@inmodules) {
			&print_category_link("/$minfo->{'dir'}/",
					     $minfo->{'desc'});
			}
		print "</table>\n";
		print "</div><br>\n";
		}
	print "<tr> <td colspan=2><hr></td> </tr>\n";
	}

# Show info link
print "<tr>\n";
print "<td width=5%><img src=/images/gohome.gif></td>\n";
print "<td><a target=right href='/right.cgi?open=system&open=status'>$text{'left_home'}</a></td>\n";
print "</tr>\n";

# Show logout link
&get_miniserv_config(\%miniserv);
if ($miniserv{'logout'} && !$ENV{'SSL_USER'} && !$ENV{'LOCAL_USER'} &&
    $ENV{'HTTP_USER_AGENT'} !~ /webmin/i) {
	print "<tr>\n";
	print "<td width=5%><img src=/images/stock_quit.png></td>\n";
	if ($main::session_id) {
		print "<td><a target=_top href='/session_login.cgi?logout=1'>$text{'main_logout'}</a></td>\n";
		}
	else {
		print "<td><a target=_top href='/switch_user.cgi'>$text{'main_switch'}</a></td>\n";
		}
	print "</tr>\n";
	}

print <<EOF;
</table>
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

# Show link to close or open catgory
print "<tr>\n";
print "<td width=5%>";
print "<a href=\"javascript:toggleview('$c','toggle$c')\" id='toggle$c'><img border='0' src='/images/closed.gif' alt='[+]'></a>\n";
print "</td>\n";
print "<td><font size=+1 color=#000000 style='font-size:14px'>$label</font></a></td>\n";
print "</tr>\n";
}


sub print_category_link
{
local ($link, $label, $image, $noimage) = @_;
print "<tr>\n";
if ($noimage) {
	print "<td colspan=2><a target=right href=$link><font size=-1>$label</a></td>\n";
	}
else {
	print "<td width=5%>$image</td>\n";
	print "<td><a target=right href=$link><font size=-1>$label</a></td>\n";
	}
print "</tr>\n";
}

