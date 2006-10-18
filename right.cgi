#!/usr/bin/perl
# Show server or domain information

do './web-lib.pl';
&init_config();
do './ui-lib.pl';
&ReadParse();
if (&foreign_available("virtual-server")) {
	&foreign_require("virtual-server", "virtual-server-lib.pl");
	if ($virtual_server::module_info{'version'} >= 2.99) {
		$hasvirt = 1;
		$level = &virtual_server::master_admin() ? 0 :
			 &virtual_server::reseller_admin() ? 1 : 2;
		}
	else {
		$level = 0;
		}
	}
elsif (&get_product_name() eq "usermin") {
	$level = 3;
	}
else {
	$level = 0;
	}
%text = &load_language($current_theme);
$bar_width = 300;
foreach $o (split(/\0/, $in{'open'})) {
	push(@open, $o);
	$open{$o} = 1;
	}

&popup_header();
print "<center>\n";

if ($hasvirt) {
	# Check licence
	print &virtual_server::licence_warning_message();

	# See if module config needs to be checked
	if (&virtual_server::need_config_check() &&
	    &virtual_server::can_check_config()) {
		print "<table width=100%><tr bgcolor=#ffee00><td align=center>";
		print &ui_form_start("../virtual-server/check.cgi");
		print "<b>$virtual_server::text{'index_needcheck'}</b><p>\n";
		print &ui_submit($virtual_server::text{'index_srefresh'});
		print &ui_form_end();
		print "</td></tr></table>\n";
		}
	}

if ($level == 0) {
	# Show general system information
	print "<a href=\"javascript:toggleview('system','toggler1')\" id='toggler1'><img border='0' src='images/openbg.gif' alt='[&ndash;]'></a>";
	print "<a href=\"javascript:toggleview('system','toggler1')\" id='toggler1'><b> $text{'right_systemheader'}</b></a><p>";
	print "<div class='itemshown' id='system'>";

	print "<table width=70%>\n";

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
	if (&foreign_check("proc")) {
		&foreign_require("proc", "proc-lib.pl");
		if (defined(&proc::get_cpu_info)) {
			@c = &proc::get_cpu_info();
			print "<tr> <td><b>$text{'right_cpu'}</b></td>\n";
			print "<td>",&text('right_load', @c),"</td> </tr>\n";
			}
		if (defined(&proc::get_memory_info)) {
			@m = &proc::get_memory_info();
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

		#@procs = &proc::list_processes();
		#print "<tr> <td><b>$text{'right_procs'}</b></td>\n";
		#print "<td>",scalar(@procs),"</td> </tr>\n";
		}

	# Disk space on local drives
	if (&foreign_check("mount")) {
		&foreign_require("mount", "mount-lib.pl");
		@mounted = &mount::list_mounted();
		$total = 0;
		$free = 0;
		foreach $m (@mounted) {
			if ($m->[2] eq "ext2" || $m->[2] eq "ext3" ||
			    $m->[2] eq "reiserfs" || $m->[2] eq "ufs") {
				($t, $f) = &mount::disk_space($m->[2], $m->[0]);
				$total += $t*1024;
				$free += $f*1024;
				}
			}
		if ($total) {
			print "<tr> <td><b>$text{'right_disk'}</b></td>\n";
			print "<td>",&text('right_used',
				   &nice_size($total),
				   &nice_size($total-$free)),"</td> </tr>\n";
			print "<tr> <td></td>\n";
			print "<td>",&bar_chart($total, $total-$free, 1),
			      "</td> </tr>\n";
			}
		}

	print "</table>\n";
	print "</div></p>\n";

	if ($hasvirt) {
		# Show Virtualmin feature statuses
		if (&virtual_server::can_stop_servers()) {
			print "<a href=\"javascript:toggleview('status','toggler2')\" id='toggler2'><img border='0' src='images/openbg.gif' alt='[&ndash;]'></a>";
			print "<a href=\"javascript:toggleview('status','toggler2')\" id='toggler2'><b> $text{'right_statusheader'}</b></a><p>";
	  	print "<div class='itemshown' id='status'>";	
			@ss = &virtual_server::get_startstop_links();
			print "<table>\n";
			foreach $status (@ss) {
				print &ui_form_start("virtual-server/".
				   ($status->{'status'} ? "stop_feature.cgi" :
							 "start_feature.cgi"));
				print &ui_hidden("feature", $status->{'feature'});
				print "<tr>\n";
				print "<td><b>",$status->{'name'},"</b></td>\n";
				print "<td>",(!$status->{'status'} ?
				 "<font color=#ff0000>$text{'right_down'}</font>" :
				 "<font color=#00aa00>$text{'right_up'}</font>"),"</td>\n";
				print "<td>",&ui_submit($status->{'desc'}),"</td>\n";
				print &ui_form_end();

				if ($status->{'status'}) {
					# Show restart button too
					print &ui_form_start("virtual-server/restart_feature.cgi");
					print &ui_hidden("feature", $status->{'feature'});
					print "<td>",&ui_submit($status->{'restartdesc'} || &text('right_restart', $status->{'name'})),"</td>\n";
					print &ui_form_end();
					}
				print "</tr>\n";
				}
			print "</table><p>\n";
			print "</div>\n";
			}

		# Show Virtualmin information
		@doms = &virtual_server::list_domains();
		print "<a href=\"javascript:toggleview('virtualmin','toggler3')\" id='toggler3'><img border='0' src='images/closedbg.gif' alt='[+]'></a>";
		print "<a href=\"javascript:toggleview('virtualmin','toggler3')\"><b> $text{'right_virtheader'}</b></a><p>";
		print "<div class='itemhidden' id='virtualmin'>";
		&show_domains_info(\@doms);
		print "</div>\n";

		if (&virtual_server::has_home_quotas()) {
			print "<a href=\"javascript:toggleview('quotas','toggler4')\" id='toggler4'><img border='0' src='images/closedbg.gif' alt='[+]'></a>";
		        print "<a href=\"javascript:toggleview('quotas','toggler4')\"><b> $text{'right_quotasheader'}</b></a><p>";
			print "<div class='itemhidden' id='quotas'>";
			&show_quotas_info(\@doms);
			print "</div><p>\n";
			}

		# Show virtual IPs used
		local (%ipcount, %ipdom);
		foreach my $d (@doms) {
			next if ($d->{'alias'});
			$ipcount{$d->{'ip'}}++;
			$ipdom{$d->{'ip'}} ||= $d;
			}
		if (keys %ipdom > 1) {
			print "<a href=\"javascript:toggleview('ips','toggler5')\" id='toggler5'><img border='0' src='images/closedbg.gif' alt='[+]'></a>";
		        print "<a href=\"javascript:toggleview('ips','toggler5')\"><b> $text{'right_ipheader'}</b></a><p>";
			print "<div class='itemhidden' id='ips'>";
			print "<table>\n";
			$defip = &virtual_server::get_default_ip();
			foreach $ip ($defip,
				     (grep { $_ ne $defip } 
					   sort { $a cmp $b } keys %ipcount)) {
				print "<tr>\n";
				print "<td width=30%>$ip</td>\n";
				print "<td>",$ip eq $defip ?
					      $text{'right_defip'} :
					      $text{'right_ip'},"</td>\n";
				if ($ipcount{$ip} == 1) {
					print "<td><tt>".$ipdom{$ip}->{'dom'}."</tt></td>\n";
					}
				else {
					print "<td>",&text('right_ips', $ipcount{$ip}),"</td>\n";
					}
				print "</tr>\n";
				}
			print "</table>\n";
			print "</div><p>\n";
			}
		}
	}
elsif ($level == 1) {
	# Show a reseller info about his domains
	print "<h3>$text{'right_header2'}</h3>\n";
	@doms = grep { $_->{'reseller'} eq $base_remote_user }
		     &virtual_server::list_domains();
	&show_domains_info(\@doms);
	}
elsif ($level == 2) {
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

	print "<table width=70%>\n";

	print "<tr> <td><b>$text{'right_login'}</b></td>\n";
	print "<td>",$remote_user,"</td> </tr>\n";

	print "<tr> <td><b>$text{'right_from'}</b></td>\n";
	print "<td>",$ENV{'REMOTE_HOST'},"</td> </tr>\n";

	print "<tr> <td><b>$text{'right_virtualmin'}</b></td>\n";
	if ($hasvirt) {
		print "<td>",$virtual_server::module_info{'version'},"</td> </tr>\n";
		}
	else {
		print "<td>",$text{'right_not'},"</td> </tr>\n";
		}

	print "<tr> <td><b>$text{'right_dom'}</b></td>\n";
	print "<td><tt>$d->{'dom'}</tt></td> </tr>\n";

	@subs = ( $d, &virtual_server::get_domain_by("parent", $d->{'id'}) );
	($sleft, $sreason, $stotal) = &virtual_server::count_domains();
	print "<tr> <td><b>$text{'right_subs'}</b></td>\n";
	if ($sleft < 0) {
		print "<td>",scalar(@subs),"</td> </tr>\n";
		}
	else {
		print "<td>",&text('right_of',
				   scalar(@subs), $stotal),"</td> </tr>\n";
		}

	# Users and aliases info
	@users = &virtual_server::list_domain_users($d, 0, 1, 1, 1);
	($uleft, $ureason, $utotal) = &virtual_server::count_feature("mailboxes");
	print "<tr> <td><b>$text{'right_fusers'}</b></td>\n";
	if ($uleft < 0) {
		print "<td>",scalar(@users),"</td> </tr>\n";
		}
	else {
		print "<td>",&text('right_of',
				   scalar(@users), $utotal),"</td> </tr>\n";
		}

	@aliases = &virtual_server::list_domain_aliases($d, 1);
	($aleft, $areason, $atotal) = &virtual_server::count_feature("aliases");
	print "<tr> <td><b>$text{'right_faliases'}</b></td>\n";
	if ($aleft < 0) {
		print "<td>",scalar(@aliases),"</td> </tr>\n";
		}
	else {
		print "<td>",&text('right_of',
				   scalar(@aliases), $atotal),"</td> </tr>\n";
		}

	# Databases
	@dbs = &virtual_server::domain_databases($d);
	($dleft, $dreason, $dtotal) = &virtual_server::count_feature("dbs");
	print "<tr> <td><b>$text{'right_fdbs'}</b></td>\n";
	if ($dleft < 0) {
		print "<td>",scalar(@dbs),"</td> </tr>\n";
		}
	else {
		print "<td>",&text('right_of',
				   scalar(@dbs), $dtotal),"</td> </tr>\n";
		}

	if (&virtual_server::has_home_quotas()) {
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

	if ($virtual_server::config{'bw_active'} && $d->{'bw_limit'}) {
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
elsif ($level == 3) {
	# Show user's information
	print "<h3>$text{'right_header5'}</h3>\n";
	print "<table width=70%>\n";

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

print "</center>\n";
&popup_footer();

# bar_chart(total, used, blue-rest)
# Returns HTML for a bar chart of a single value
sub bar_chart
{
local ($total, $used, $blue) = @_;
local $rv;
$rv .= sprintf "<img src=images/red.gif width=%s height=10>",
	int($bar_width*$used/$total)+1;
if ($blue) {
	$rv .= sprintf "<img src=images/blue.gif width=%s height=10>",
		$bar_width - int($bar_width*$used/$total)-1;
	}
else {
	$rv .= sprintf "<img src=images/white.gif width=%s height=10>",
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
$rv .= sprintf "<img src=images/red.gif width=%s height=10>", $w1;
$rv .= sprintf "<img src=images/purple.gif width=%s height=10>", $w2;
$rv .= sprintf "<img src=images/blue.gif width=%s height=10>", $w3;
$rv .= sprintf "<img src=images/grey.gif width=%s height=10>",
	$bar_width - $w1 - $w2 - $w3;
return $rv;
}

# show_domains_info(&domains)
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
print "<table width=70%>\n";
my $i = 0;
foreach my $f ("doms", "dns", "web", "ssl", "mail",
	       "dbs", "users", "aliases") {
	local $cur = int($fcount{$f});
	local ($extra, $reason, $max) = &virtual_server::count_feature($f);
	print "<tr>\n" if ($i%2 == 0);
	print "<td width=25%>",$text{'right_f'.$f},"</td>\n";
	if ($extra < 0) {
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

# show_quotas_info(&domains)
sub show_quotas_info
{
local @doms = @{$_[0]};
local @quota;
local $homesize = &virtual_server::quota_bsize("home");
local $mailsize = &virtual_server::quota_bsize("mail");
local $maxquota = 0;

# Work out quotas
foreach my $d (@doms) {
	# If this is a parent domain, sum up quotas
	if (!$d->{'parent'} && &virtual_server::has_home_quotas()) {
		local ($home, $mail, $dbusage) =
			&virtual_server::get_domain_quota($d, 1);
		local $usage = $home*$homesize +
			       $mail*$mailsize;
		$maxquota = $usage if ($usage > $maxquota);
		local $limit = $d->{'quota'}*$homesize;
		$maxquota = $limit if ($limit > $maxquota);
		push(@quota, [ $d, $usage, $limit, $dbusage ]);
		}
	}

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
		print "<td>",&bar_chart_three(
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

# Show bandwidth usage by domains
# XXX
}

# collapsed_header(text, name)
sub collapsed_header
{
local ($text, $name) = @_;
print "<br><font style='font-size:16px'>";
local $others = join("&", map { "open=$_" } grep { $_ ne $name } @open);
$others = "&$others" if ($others);
if ($open{$name}) {
	print "<img src=images/openbg.gif border=0>\n";
	print "<a href='right.cgi?$others'>$text</a>";
	}
else {
	print "<img src=images/closed.gif border=0>\n";
	print "<a href='right.cgi?open=$name$others'>$text</a>";
	}
print "</font><br>\n";
return $open{$name};
}

