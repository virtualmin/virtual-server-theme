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
	}

if ($level == 0) {
	# Show general system information
	if (&collapsed_header($text{'right_header0'}, "system")) {
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
		}

	if ($hasvirt) {
		# Show Virtualmin feature statuses
		if (&virtual_server::can_stop_servers() &&
		    &collapsed_header($text{'right_header6'}, "status")) {
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
			print "</table>\n";
			}

		# Show Virtualmin information
		@doms = &virtual_server::list_domains();
		if (&collapsed_header($text{'right_header1'}, "virtualmin")) {
			&show_domains_info(\@doms);
			}
		if (&virtual_server::has_home_quotas() &&
		    &collapsed_header($text{'right_header4'}, "quotas")) {
			&show_quotas_info(\@doms);
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
		# Disk usage
		local $homesize = &virtual_server::quota_bsize("home");
		local $mailsize = &virtual_server::quota_bsize("mail");
		local @qinfo = &virtual_server::get_domain_user_quotas($d);
		$usage = $qinfo[0]*$homesize + $qinfo[1]*$mailsize +
			 $qinfo[2]->{'uquota'}*$homesize + $qinfo[3];
		$limit = $d->{'quota'}*$homesize;
		print "<tr> <td><b>$text{'right_quota'}</b></td>\n";
		if ($limit) {
			print "<td>",&text('right_of', &nice_size($usage), &nice_size($limit)),"</td> </tr>\n";
			print "<tr> <td></td>\n";
			print "<td>",&bar_chart($limit, $usage, 1),
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

# bar_chart_two(total, used1, used2)
# Returns HTML for a bar chart of two values
sub bar_chart_two
{
local ($total, $used1, $used2) = @_;
local $rv;
local $w1 = int($bar_width*$used1/$total)+1;
local $w2 = int($bar_width*$used2/$total);
$rv .= sprintf "<img src=images/red.gif width=%s height=10>", $w1;
$rv .= sprintf "<img src=images/blue.gif width=%s height=10>", $w2;
$rv .= sprintf "<img src=images/grey.gif width=%s height=10>",
	$bar_width - $w1 - $w2;
return $rv;
}

# show_domains_info(&domains)
sub show_domains_info
{
# Count features for specified domains
local @doms = @{$_[0]};
local %fcount = map { $_, 0 } @virtual_server::features;
$fcount{'virtualmin'} = 0;
foreach my $d (@doms) {
	$fcount{'virtualmin'}++;
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

# Show features
print "<table width=70%>\n";
my $i = 0;
foreach my $f ("virtualmin", "dns", "web", "ssl", "mail",
	    "dbs", "users", "aliases") {
	print "<tr>\n" if ($i%2 == 0);
	print "<td width=25%>",$text{'right_f'.$f},"</td>\n";
	print "<td width=25%>",$fcount{$f},"</td>\n";
	print "</tr>\n" if ($i%2 == 1);
	$i++;
	}
print "</table>\n";
}

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
		local @sdoms = ( $d, &virtual_server::get_domain_by("parent", $d->{'id'}) );
		local @qinfo = &virtual_server::get_domain_user_quotas(@sdoms);
		local $usage = $qinfo[0]*$homesize + $qinfo[1]*$mailsize +
			       $qinfo[2]->{'uquota'}*$homesize + $qinfo[3];
		$maxquota = $usage if ($usage > $maxquota);
		local $limit = $d->{'quota'}*$homesize;
		$maxquota = $limit if ($limit > $maxquota);
		push(@quota, [ $d, @qinfo, $usage, $limit ]);
		}
	}

if (@quota) {
	# Show disk usage by various domains
	@quota = sort { $b->[5] <=> $a->[5] } @quota;
	print "<table>\n";
	if (@quota > 10) {
		@quota = @quota[0..9];
		print "<tr> <td colspan=2>$text{'right_quota10'}</td> </tr>\n";
		}
	foreach my $q (@quota) {
		print "<tr>\n";
		print "<td width=30%>$q->[0]->{'dom'}</td>\n";
		print "<td>",&bar_chart_two($maxquota, $q->[5], $q->[6] ? $q->[6]-$q->[5] : 0, 1),"</td>\n";
		if ($q->[6]) {
			print "<td>",&text('right_out',
				&nice_size($q->[5]), &nice_size($q->[6])),"</td>\n";
			}
		else {
			print "<td>",&nice_size($q->[5]),"</td>\n";
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

