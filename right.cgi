#!/usr/local/bin/perl
# Show server or domain information

do './web-lib.pl';
&init_config();
do 'ui-lib.pl';
&ReadParse();
&load_theme_library();

# Work out system capabilities. Level 3 = usermin, 2 = domain owner,
# 1 = reseller, 0 = master
($hasvirt, $level) = &get_virtualmin_user_level();
%text = &load_language($current_theme);
$bar_width = 100;
foreach $o (split(/\0/, $in{'open'})) {
	push(@open, $o);
	$open{$o} = 1;
	}

&popup_header(undef, &capture_function_output(\&theme_prehead));

if ($hasvirt) {
	# Show link for editing what appears
	$sects = &get_right_frame_sections();
	if (!$sects->{'global'} || &virtual_server::master_admin()) {
		print "<div align=right>";
		@links = ( "<a href='edit_right.cgi'>$text{'right_edit'}</a>" );
		if (&virtual_server::master_admin()) {
			push(@links, "<a href='recollect.cgi'>".
				     "$text{'right_recollect'}</a>");
			}
		print &ui_links_row(\@links);
		print "</div>\n";
		$shown_config_link = 1;
		}
	}

# Check for custom URL
if ($sects->{'alt'}) {
	$url = $sects->{'alt'};
	if ($shown_config_link) {
		# Show in iframe, so that the config link is visible
		print "<iframe src='$url' width=100% height=95% frameborder=0 ",
		      "marginwidth=0 marginheight=0>\n";
		}
	else {
		# Redirect whole frame
		print "<script>\n";
		print "document.location = '$url';\n";
		print "</script>\n";
		}
	&popup_footer();
	exit;
	}

if ($hasvirt) {
	# Check licence
	print &virtual_server::licence_warning_message();

	# See if module config needs to be checked
	if (&virtual_server::need_config_check() &&
	    &virtual_server::can_check_config()) {
		print "<table width=100%><tr bgcolor=#ffee00><td align=center>";
		print &ui_form_start("virtual-server/check.cgi");
		print "<b>$virtual_server::text{'index_needcheck'}</b><p>\n";
		print &ui_submit($virtual_server::text{'index_srefresh'});
		print &ui_form_end();
		print "</td></tr></table>\n";
		}
	}

# Check if OS according to Webmin is out of date
if ($level == 0 && &foreign_available("webmin") &&
    &get_webmin_version() >= 1.326) {
	&foreign_require("webmin", "webmin-lib.pl");
	%realos = &webmin::detect_operating_system(undef, 1);
	if ($realos{'os_version'} ne $gconfig{'os_version'} ||
	    $realos{'os_type'} ne $gconfig{'os_type'}) {
		print "<table width=100%><tr bgcolor=#ffee00><td align=center>";
		print &ui_form_start("webmin/fix_os.cgi");
		print "<b>",&webmin::text('os_incorrect',
                        $realos{'real_os_type'},
                        $realos{'real_os_version'}),"</b><p>\n";
		print &ui_submit($webmin::text{'os_fix'});
		print &ui_form_end();
		print "</td></tr></table>\n";
		}
	}

if ($level == 0) {		# Master admin
	# Show Virtualmin master admin info
	if ($hasvirt) {
		$info = &virtual_server::get_collected_info();
		}

	if (!$sects->{'nosystem'}) {
		# Show general system information
		&show_toggleview("system", "toggler1", 1,
				 $text{'right_systemheader'});

		print "<table>\n";

		# Host and login info
		print "<tr> <td><b>$text{'right_host'}</b></td>\n";
		print "<td>",&get_system_hostname(),"</td> </tr>\n";

		print "<tr> <td><b>$text{'right_os'}</b></td>\n";
		if ($gconfig{'os_version'} eq '*') {
			print "<td>$gconfig{'real_os_type'}</td> </tr>\n";
			}
		else {
			print "<td>$gconfig{'real_os_type'} $gconfig{'real_os_version'}</td> </tr>\n";
			}

		if (&get_product_name() eq 'webmin') {
			print "<tr> <td><b>$text{'right_webmin'}</b></td>\n";
			print "<td>",&get_webmin_version(),"</td> </tr>\n";

			print "<tr> <td><b>$text{'right_virtualmin'}</b></td>\n";
			if ($hasvirt) {
				print "<td>",$virtual_server::module_info{'version'},"</td> </tr>\n";
				}
			else {
				print "<td>",$text{'right_not'},"</td> </tr>\n";
				}
			}
		else {
			print "<tr> <td><b>$text{'right_usermin'}</b></td>\n";
			print "<td>",&get_webmin_version(),"</td> </tr>\n";
			}

		# System time
		$tm = localtime(time());
		print "<tr> <td><b>$text{'right_time'}</b></td>\n";
		print "<td>$tm</td> </tr>\n";

		# Load and memory info
		if ($info->{'load'}) {
			@c = @{$info->{'load'}};
			print "<tr> <td><b>$text{'right_cpu'}</b></td>\n";
			print "<td>",&text('right_load', @c),"</td> </tr>\n";
			}

		# Running processes
		if ($info->{'procs'}) {
			print "<tr> <td><b>$text{'right_procs'}</b></td>\n";
			print "<td>$info->{'procs'}</td> </tr>\n";
			}

		# Memory used
		if ($info->{'mem'}) {
			@m = @{$info->{'mem'}};
			if (@m && $m[0]) {
				print "<tr> <td><b>$text{'right_real'}</b></td>\n";
				print "<td>",&nice_size($m[0]*1024)." total, ".
					    &nice_size(($m[0]-$m[1])*1024)." used</td> </tr>\n";
				print "<tr> <td></td>\n";
				print "<td>",&bar_chart($m[0], $m[0]-$m[1], 1),
				      "</td> </tr>\n";
				}

			if (@m && $m[2]) {
				print "<tr> <td><b>$text{'right_virt'}</b></td>\n";
				print "<td>",&nice_size($m[2]*1024)." total, ".
					    &nice_size(($m[2]-$m[3])*1024)." used</td> </tr>\n";
				print "<tr> <td></td>\n";
				print "<td>",&bar_chart($m[2], $m[2]-$m[3], 1),
				      "</td> </tr>\n";
				}
			}

		# Disk space on local drives
		if ($info->{'disk_total'}) {
			print "<tr> <td><b>$text{'right_disk'}</b></td>\n";
			print "<td>",&text('right_used',
			   &nice_size($info->{'disk_total'}),
			   &nice_size($info->{'disk_total'}-
				      $info->{'disk_free'})),"</td> </tr>\n";
			print "<tr> <td></td>\n";
			print "<td>",&bar_chart($info->{'disk_total'},
						$info->{'disk_total'}-
						 $info->{'disk_free'}, 1),
			      "</td> </tr>\n";
			}

		print "</table>\n";
		print "</div></p>\n";
		}

	# Check for package updates
	if (!$sects->{'noupdates'} && $info->{'poss'} &&
	    (@poss = @{$info->{'poss'}})) {
		# Show updates section
		&show_toggleview("updates", "toggler7", 1,
				 $text{'right_updatesheader'});
		print &ui_form_start("security-updates/update.cgi");
		print &text(
			@poss > 1 ? 'right_upcount' : 'right_upcount1',
			scalar(@poss),
			'security-updates/'),"<p>\n";
		print &ui_columns_start([ $text{'right_upname'},
					  $text{'right_updesc'},
					  $text{'right_upver'} ]);
		foreach $p (@poss) {
			print &ui_columns_row([
			 $p->{'name'}, $p->{'desc'}, $p->{'version'} ]);
			print &ui_hidden("u", $p->{'name'});
			}
		print &ui_columns_end();
		print &ui_form_end([ [ undef, $text{'right_upok'} ] ]);
		print "</div>\n";
		}

	if ($hasvirt && !$sects->{'nostatus'} && $info->{'startstop'} &&
	    &virtual_server::can_stop_servers()) {
		# Show Virtualmin feature statuses
		&show_toggleview("status", "toggler2", 1,
				 $text{'right_statusheader'});
		@ss = @{$info->{'startstop'}};
		print "<table>\n";
		foreach $status (@ss) {
			print &ui_form_start("virtual-server/".
			   ($status->{'status'} ? "stop_feature.cgi" :
						 "start_feature.cgi"));
			print &ui_hidden("feature", $status->{'feature'});
			print &ui_hidden("redirect", "/right.cgi");
			print "<tr>\n";
			print "<td><b>",$status->{'name'},"</b></td>\n";
			print "<td>",(!$status->{'status'} ?
			    "<font color=#ff0000>$text{'right_down'}</font>" :
			    "<font color=#00aa00>$text{'right_up'}</font>"),
			    "</td>\n";
			print "<td>",&ui_submit($status->{'desc'}),"</td>\n";
			print &ui_form_end();

			if ($status->{'status'}) {
				# Show restart button too
				print &ui_form_start(
					"virtual-server/restart_feature.cgi");
				print &ui_hidden("feature",
						 $status->{'feature'});
				print &ui_hidden("redirect", "/right.cgi");
				print "<td>",&ui_submit($status->{'restartdesc'} || &text('right_restart', $status->{'name'})),"</td>\n";
				print &ui_form_end();
				}
			print "</tr>\n";
			}
		print "</table><p>\n";
		print "</div>\n";
		}

	if ($hasvirt && !$sects->{'novirtualmin'} && $info->{'fcount'}) {
		# Show Virtualmin information
		&show_toggleview("virtualmin", "toggler3", 0,
				 $text{'right_virtheader'});
		print "<table>\n";
		my $i = 0;
		foreach my $f (@{$info->{'ftypes'}}) {
			local $cur = int($info->{'fcount'}->{$f});
			local $extra = $info->{'fextra'}->{$f};
			local $max = $info->{'fmax'}->{$f};
			local $hide = $info->{'fhide'}->{$f};
			print "<tr>\n" if ($i%2 == 0);
			print "<td width=25%>",$text{'right_f'.$f},"</td>\n";
			if ($extra < 0 || $hide) {
				print "<td width=25%>",$cur,"</td>\n";
				}
			else {
				print "<td width=25%>",&text('right_out', $cur, $max),"</td>\n";
				}
			print "</tr>\n" if ($i%2 == 1);
			$i++;
			}
		print "</table>\n";
		print "</div>\n";
		}

	if ($hasvirt && !$sects->{'noquotas'} && $info->{'quota'} &&
	    @{$info->{'quota'}}) {
		# Show quota graphs
		&show_toggleview("quotas", "toggler4", 0,
				 $text{'right_quotasheader'});
		&show_quotas_info($info->{'quota'}, $info->{'maxquota'});
		print "</div><p>\n";
		}

	if ($hasvirt && !$sects->{'noips'} && $info->{'ips'}) {
		# Show virtual IPs used
		&show_toggleview("ips", "toggler5", 0,
				 $text{'right_ipsheader'});
		print "<table>\n";
		foreach my $ipi (@{$info->{'ips'}}) {
			print "<tr>\n";
			print "<td width=30%>$ipi->[0]</td>\n";
			print "<td>",$ipi->[1] eq 'def' ? $text{'right_defip'} :
				     $ipi->[1] eq 'reseller' ?
					&text('right_reselip', $ipi->[2]) :
				     $ipi->[1] eq 'shared' ?
					$text{'right_sharedip'} :
					$text{'right_ip'},"</td>\n";
			if ($ipi->[3] == 1) {
				print "<td><tt>$ipi->[4]</tt></td>\n";
				}
			else {
				print "<td>",&text('right_ips', $ipi->[3]),	
				      "</td>\n";
				}
			print "</tr>\n";
			}
		print "</table>\n";
		print "</div><p>\n";
		}

	# Show system information section
	if ($hasvirt && !$sects->{'nosysinfo'} && $info->{'progs'} &&
	    &virtual_server::can_view_sysinfo()) {
		&show_toggleview("sysinfo", "toggler6", 0,
				 $text{'right_sysinfoheader'});
		print "<table>\n";
		@info = @{$info->{'progs'}};
		for($i=0; $i<@info; $i++) {
			print "<tr>\n" if ($i%2 == 0);
			print "<td><b>$info[$i]->[0]</b></td>\n";
			print "<td>$info[$i]->[1]</td>\n";
			print "</tr>\n" if ($i%2 == 1);
			}
		print "</table>\n";
		print "</div><p>\n";
		}
	}
elsif ($level == 1) {		# Reseller
	# Show a reseller info about his domains
	if (!$sects->{'novirtualmin'}) {
		print "<h3>$text{'right_header2'}</h3>\n";
		@doms = grep { $_->{'reseller'} eq $base_remote_user }
			     &virtual_server::list_domains();
		&show_domains_info(\@doms);
		}
	}
elsif ($level == 2) {		# Domain owner
	# Show a server owner info about one domain
	print "<h3>$text{'right_header3'}</h3>\n";
	$ex = &virtual_server::extra_admin();
	if ($ex) {
		$d = &virtual_server::get_domain($ex);
		}
	else {
		$d = &virtual_server::get_domain_by(
			"user", $remote_user, "parent", "");
		}

	print "<table>\n";

	print "<tr> <td><b>$text{'right_login'}</b></td>\n";
	print "<td>",$remote_user,"</td> </tr>\n";

	print "<tr> <td><b>$text{'right_from'}</b></td>\n";
	print "<td>",$ENV{'REMOTE_HOST'},"</td> </tr>\n";

	print "<tr> <td><b>$text{'right_virtualmin'}</b></td>\n";
	if ($hasvirt) {
		print "<td>",$virtual_server::module_info{'version'},
		      "</td> </tr>\n";
		}
	else {
		print "<td>",$text{'right_not'},"</td> </tr>\n";
		}

	print "<tr> <td><b>$text{'right_dom'}</b></td>\n";
	print "<td><tt>$d->{'dom'}</tt></td> </tr>\n";

	@subs = ( $d, &virtual_server::get_domain_by("parent", $d->{'id'}) );
	($sleft, $sreason, $stotal, $shide) = &virtual_server::count_domains();
	print "<tr> <td><b>$text{'right_subs'}</b></td>\n";
	if ($sleft < 0 || $shide) {
		print "<td>",scalar(@subs),"</td> </tr>\n";
		}
	else {
		print "<td>",&text('right_of',
				   scalar(@subs), $stotal),"</td> </tr>\n";
		}

	# Users and aliases info
	@users = &virtual_server::list_domain_users($d, 0, 1, 1, 1);
	($uleft, $ureason, $utotal, $uhide) =
		&virtual_server::count_feature("mailboxes");
	print "<tr> <td><b>$text{'right_fusers'}</b></td>\n";
	if ($uleft < 0 || $uhide) {
		print "<td>",scalar(@users),"</td> </tr>\n";
		}
	else {
		print "<td>",&text('right_of',
				   scalar(@users), $utotal),"</td> </tr>\n";
		}

	@aliases = &virtual_server::list_domain_aliases($d, 1);
	($aleft, $areason, $atotal, $ahide) =
		&virtual_server::count_feature("aliases");
	print "<tr> <td><b>$text{'right_faliases'}</b></td>\n";
	if ($aleft < 0 || $ahide) {
		print "<td>",scalar(@aliases),"</td> </tr>\n";
		}
	else {
		print "<td>",&text('right_of',
				   scalar(@aliases), $atotal),"</td> </tr>\n";
		}

	# Databases
	@dbs = &virtual_server::domain_databases($d);
	($dleft, $dreason, $dtotal, $dhide) =
		&virtual_server::count_feature("dbs");
	print "<tr> <td><b>$text{'right_fdbs'}</b></td>\n";
	if ($dleft < 0 || $dhide) {
		print "<td>",scalar(@dbs),"</td> </tr>\n";
		}
	else {
		print "<td>",&text('right_of',
				   scalar(@dbs), $dtotal),"</td> </tr>\n";
		}

	if (!$sects->{'noquotas'} &&
	    &virtual_server::has_home_quotas()) {
		# Disk usage for all owned domains
		$homesize = &virtual_server::quota_bsize("home");
		$mailsize = &virtual_server::quota_bsize("mail");
		($home, $mail, $db) = &virtual_server::get_domain_quota($d, 1);
		$usage = $home*$homesize + $mail*$mailsize + $db;
		$limit = $d->{'quota'}*$homesize;
		print "<tr> <td><b>$text{'right_quota'}</b></td>\n";
		if ($limit) {
			print "<td>",&text('right_of', &nice_size($usage), &nice_size($limit)),"</td> </tr>\n";
			print "<tr> <td></td>\n";
			print "<td>",&bar_chart_three($limit, $usage-$db, $db,
						      $limit-$usage),
			      "</td> </tr>\n";
			}
		else {
			print "<td>",&nice_size($usage),"</td> </tr>\n";
			}
		}

	if (!$sects->{'nobw'} &&
	    $virtual_server::config{'bw_active'} && $d->{'bw_limit'}) {
		# Bandwidth usage and limit
		print "<tr> <td><b>$text{'right_bw'}</b></td>\n";
		print "<td>",
		   &text('right_of', &nice_size($d->{'bw_usage'}),
			&virtual_server::text(
			'edit_bwpast_'.$virtual_server::config{'bw_past'},
			&nice_size($d->{'bw_limit'}),
			$virtual_server::config{'bw_period'})),
		      "</td> </tr>\n";
		print "<tr> <td></td>\n";
		print "<td>",&bar_chart($d->{'bw_limit'}, $d->{'bw_usage'}, 1),
		      "</td> </tr>\n";
		}

	print "</table>\n";
	}
elsif ($level == 3) {		# Usermin
	# Show user's information
	print "<h3>$text{'right_header5'}</h3>\n";
	print "<table>\n";

	# Host and login info
	print "<tr> <td><b>$text{'right_host'}</b></td>\n";
	print "<td>",&get_system_hostname(),"</td> </tr>\n";

	print "<tr> <td><b>$text{'right_os'}</b></td>\n";
	if ($gconfig{'os_version'} eq '*') {
		print "<td>$gconfig{'real_os_type'}</td> </tr>\n";
		}
	else {
		print "<td>$gconfig{'real_os_type'} $gconfig{'real_os_version'}</td> </tr>\n";
		}

	print "<tr> <td><b>$text{'right_usermin'}</b></td>\n";
	print "<td>",&get_webmin_version(),"</td> </tr>\n";

	# Disk quotas
	if (&foreign_installed("quota")) {
		&foreign_require("quota", "quota-lib.pl");
		$n = &quota::user_filesystems($remote_user);
		$usage = 0;
		$quota = 0;
		for($i=0; $i<$n; $i++) {
			if ($quota::filesys{$i,'hblocks'}) {
				$quota += $quota::filesys{$i,'hblocks'};
				$usage += $quota::filesys{$i,'ublocks'};
				}
			elsif ($quota::filesys{$i,'sblocks'}) {
				$quota += $quota::filesys{$i,'sblocks'};
				$usage += $quota::filesys{$i,'ublocks'};
				}
			}
		if ($quota) {
			$bsize = $quota::config{'block_size'};
			print "<tr> <td><b>$text{'right_uquota'}</b></td>\n";
			print "<td>",&text('right_out',
				&nice_size($usage*$bsize),
				&nice_size($quota*$bsize)),"</td> </tr>\n";
			print "<tr> <td></td>\n";
			print "<td>",&bar_chart($quota, $usage, 1),
			      "</td> </tr>\n";
			}
		}
	}

&popup_footer();

# bar_chart(total, used, blue-rest)
# Returns HTML for a bar chart of a single value
sub bar_chart
{
local ($total, $used, $blue) = @_;
local $rv;
$rv .= sprintf "<div class='barchart'><img src=images/red.gif width=%s%% height=12px>",
  int($bar_width*$used/$total)+1;
if ($blue) {
  $rv .= sprintf "<img src=images/blue.gif width=%s%% height=12px></div>",
    $bar_width - int($bar_width*$used/$total)-1;
  }
else {
  $rv .= sprintf "<img src=images/white.gif width=%s%% height=12px></div>",
    $bar_width - int($bar_width*$used/$total)-1;
  }
return $rv;
}

# bar_chart_three(total, used1, used2, used3)
# Returns HTML for a bar chart of three values, stacked
sub bar_chart_three
{
local ($total, $used1, $used2, $used3) = @_;
local $rv;
local $w1 = int($bar_width*$used1/$total)+1;
local $w2 = int($bar_width*$used2/$total);
local $w3 = int($bar_width*$used3/$total);
local $w4 = int($bar_width - $w1 - $w2 - $w3);
$rv .= "<div class='barchart'>";
if ($w1) {$rv .= sprintf "<img src=images/red.gif width=%s%% height=12px>", $w1;}
if ($w2) {$rv .= sprintf "<img src=images/purple.gif width=%s%% height=12px>", $w2;}
if ($w3) {$rv .= sprintf "<img src=images/blue.gif width=%s%% height=12px>", $w3;}
if ($w4) {$rv .= sprintf "<img src=images/grey.gif width=%s%% height=12px>", $w4;}
$rv .= "</div>";
return $rv;
}

# show_domains_info(&domains)
# Given a list of domains, show summaries of feature usage
sub show_domains_info
{
# Count features for specified domains
local @doms = @{$_[0]};
local %fcount = map { $_, 0 } @virtual_server::features;
$fcount{'doms'} = 0;
foreach my $d (@doms) {
	$fcount{'doms'}++;
	foreach my $f (@virtual_server::features) {
		$fcount{$f}++ if ($d->{$f});
		}
	my @dbs = &virtual_server::domain_databases($d);
	$fcount{'dbs'} += scalar(@dbs);
	my @users = &virtual_server::list_domain_users($d, 0, 1, 1, 1);
	$fcount{'users'} += scalar(@users);
	my @aliases = &virtual_server::list_domain_aliases($d, 1);
	$fcount{'aliases'} += scalar(@aliases);
	}

# Show counts for features, including maxes
print "<table>\n";
my $i = 0;
foreach my $f ("doms", "dns", "web", "ssl", "mail",
	       "dbs", "users", "aliases") {
	local $cur = int($fcount{$f});
	local ($extra, $reason, $max, $hide) =
		&virtual_server::count_feature($f);
	print "<tr>\n" if ($i%2 == 0);
	print "<td width=25%>",$text{'right_f'.$f},"</td>\n";
	if ($extra < 0 || $hide) {
		print "<td width=25%>",$cur,"</td>\n";
		}
	else {
		print "<td width=25%>",&text('right_out', $cur, $max),"</td>\n";
		}
	print "</tr>\n" if ($i%2 == 1);
	$i++;
	}
print "</table>\n";
}

# show_quotas_info(&quotas, maxquota)
sub show_quotas_info
{
local ($quota, $maxquota) = @_;
local @quota = @$quota;
if (@quota) {
	# Show disk usage by various domains
	@quota = sort { $b->[1] <=> $a->[1] } @quota;
	print "<table>\n";
	if (@quota > 10) {
		@quota = @quota[0..9];
		print "<tr> <td colspan=2>$text{'right_quota10'}</td> </tr>\n";
		}
	foreach my $q (@quota) {
		print "<tr>\n";
		my $ed = &virtual_server::can_config_domain($q->[0]) ?
			"edit_domain.cgi" : "view_domain.cgi";
		print "<td width=30%><a href='virtual-server/$ed?",
		      "dom=$q->[0]->{'id'}'>$q->[0]->{'dom'}</a></td>\n";
		print "<td width=50%>",&bar_chart_three(
				$maxquota,		# Highest quota
				$q->[1],		# Domain's disk usage
				$q->[3],		# DB usage
				$q->[2] ? $q->[2]-$q->[1]-$q->[3] : 0,	# Leftover
				),"</td>\n";
		if ($q->[2]) {
			print "<td>",&text('right_out',
				&nice_size($q->[1]+$q->[3]),
				&nice_size($q->[2])),"</td>\n";
			}
		else {
			print "<td>",&nice_size($q->[1]+$q->[3]),"</td>\n";
			}
		print "</tr>\n";
		}
	print "</table>\n";
	}
}

# collapsed_header(text, name)
sub collapsed_header
{
local ($text, $name) = @_;
print "<br><font style='font-size:16px'>";
local $others = join("&", map { "open=$_" } grep { $_ ne $name } @open);
$others = "&$others" if ($others);
if ($open{$name}) {
	print "<img src=images/open.gif border=0>\n";
	print "<a href='right.cgi?$others'>$text</a>";
	}
else {
	print "<img src=images/closed.gif border=0>\n";
	print "<a href='right.cgi?open=$name$others'>$text</a>";
	}
print "</font><br>\n";
return $open{$name};
}

# show_toggleview(name, id, status, header)
# Prints HTML for an open/close toggler
sub show_toggleview
{
local ($name, $id, $status, $header) = @_;
local $img = $status ? "open" : "closed";
local $cls = $status ? "itemshown" : "itemhidden";
print "<a href=\"javascript:toggleview('$name','$id')\" id='$id'><img border='0' src='images/$img.gif' alt='[&ndash;]'></a>";
print "<a href=\"javascript:toggleview('$name','$id')\" id='$id'><b> $header</b></a><p>";
print "<div class='$cls' id='$name'>";
}

