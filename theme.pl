# Virtualmin Framed heme
# Icons copyright David Vignoni, all other theme elements copyright 2005-2007
# Virtualmin, Inc.

$main::vm2_no_create_links = 1;
$main::vm2_no_edit_buttons = 1;

$main::mailbox_no_addressbook_button = 1;
$main::mailbox_no_folder_button = 1;

# theme_ui_post_header([subtext])
# Returns HTML to appear directly after a standard header() call
sub theme_ui_post_header
{
local ($text) = @_;
local $rv;
$rv .= "<div class='ui_post_header'>$text</div>\n" if (defined($text));
$rv .= "<div class='section'>\n";
$rv .= "<p>" if (!defined($text));
return $rv;
}

# theme_ui_pre_footer()
# Returns HTML to appear directly before a standard footer() call
sub theme_ui_pre_footer
{
local $rv;
$rv .= "</div>\n";
return $rv;
}

# ui_print_footer(args...)
# Print HTML for a footer with the pre-footer line. Args are the same as those
# passed to footer()
sub theme_ui_print_footer
{
local @args = @_;
print &ui_pre_footer();
&footer(@args);
}

sub theme_icons_table
{
local ($i, $need_tr);
local $cols = $_[3] ? $_[3] : 4;
local $per = int(100.0 / $cols);
print "<table id='main' width=100% cellpadding=5>\n";
for($i=0; $i<@{$_[0]}; $i++) {
	if ($i%$cols == 0) { print "<tr>\n"; }
	print "<td width=$per% align=center valign=top>\n";
	&generate_icon($_[2]->[$i], $_[1]->[$i], $_[0]->[$i],
		       $_[4], $_[5], $_[6], $_[7]->[$i], $_[8]->[$i]);
	print "</td>\n";
        if ($i%$cols == $cols-1) { print "</tr>\n"; }
        }
while($i++%$cols) { print "<td width=$per%></td>\n"; $need_tr++; }
print "</tr>\n" if ($need_tr);
print "</table>\n";
}

sub theme_generate_icon
{
local $w = !defined($_[4]) ? "width=48" : $_[4] ? "width=$_[4]" : "";
local $h = !defined($_[5]) ? "height=48" : $_[5] ? "height=$_[5]" : "";
if ($tconfig{'noicons'}) {
	if ($_[2]) {
		print "$_[6]<a href=\"$_[2]\" $_[3]>$_[1]</a>$_[7]\n";
		}
	else {
		print "$_[6]$_[1]$_[7]\n";
		}
	}
elsif ($_[2]) {
	print "<table><tr><td width=48 height=48>\n",
	      "<a href=\"$_[2]\" $_[3]><img src=\"$_[0]\" alt=\"\" border=0 ",
	      "$w $h></a></td></tr></table>\n";
	print "$_[6]<a href=\"$_[2]\" $_[3]>$_[1]</a>$_[7]\n";
	}
else {
	print "<table><tr><td width=48 height=48>\n",
	      "<img src=\"$_[0]\" alt=\"\" border=0 $w $h>",
	      "</td></tr></table>\n$_[6]$_[1]$_[7]\n";
	}
}

# Called by Virtualmin after a domain is updated, to refresh the left menu
sub theme_post_save_domain
{
if (!$done_theme_post_save_domain++) {
	print "<script>\n";
	print "top.left.location = top.left.location;\n";
	print "</script>\n";
	}
}

# Called by VM2 after a server is updated, to refresh the left menu
sub theme_post_save_server
{
if (!$done_theme_post_save_server++) {
	print "<script>\n";
	print "top.left.location = top.left.location;\n";
	print "</script>\n";
	}
}

# theme_select_server(&server)
# Called by VM2 when a page for a server is displayed, to select it on the
# left menu.
sub theme_select_server
{
local ($server) = @_;
print <<EOF;
<script>
if (window.parent && window.parent.frames[0]) {
	var leftdoc = window.parent.frames[0].document;
	var leftform = leftdoc.forms[0];
	if (leftform) {
		var serversel = leftform['sid'];
		if (serversel && serversel.value != '$server->{'id'}') {
			// Need to change value
			serversel.value = '$server->{'id'}';
			window.parent.frames[0].location =
				'/left.cgi?mode=vm2&sid=$server->{'id'}';
			}
		}
	}
</script>
EOF
}

# theme_select_domain(&server)
# Called by Virtualmin when a page for a server is displayed, to select it on
# the left menu.
sub theme_select_domain
{
local ($server) = @_;
print <<EOF;
<script>
if (window.parent && window.parent.frames[0]) {
	var leftdoc = window.parent.frames[0].document;
	var leftform = leftdoc.forms[0];
	if (leftform) {
		var domsel = leftform['dom'];
		if (domsel && domsel.value != '$d->{'id'}') {
			// Need to change value
			domsel.value = '$d->{'id'}';
			window.parent.frames[0].location =
				'/left.cgi?mode=virtualmin&dom=$d->{'id'}';
			}
		}
	}
</script>
EOF
}

sub theme_prebody
{
if ($script_name =~ /session_login.cgi/) {
	# Generate CSS link
	print "<link rel='stylesheet' type='text/css' href='$gconfig{'webprefix'}/unauthenticated/style.css'>\n";
	}
if ($module_name eq "virtual-server") {
	# No need for Module Index link, as we have the left-side frame
	$tconfig{'nomoduleindex'} = 1;
	}
}

sub theme_postbody
{
# If we just came from a folder editing page, refresh the folder list
if ($module_name eq "mailbox" && $ENV{'HTTP_REFERER'} =~ /(edit|save)_(folder|comp|imap|pop3|virt)\.cgi|mail_search\.cgi|delete_folders\.cgi/) {
        print "<script>\n";
        print "top.frames[0].document.location = top.frames[0].document.location;\n";
        print "</script>\n";
        }
}

sub theme_prehead
{
print "<link rel='stylesheet' type='text/css' href='$gconfig{'webprefix'}/unauthenticated/style.css' />\n";
print "<script type='text/javascript' src='$gconfig{'webprefix'}/unauthenticated/toggleview.js'></script>\n";
print "<script>\n";
print "var rowsel = new Array();\n";
print "</script>\n";
print "<script type='text/javascript' src='$gconfig{'webprefix'}/unauthenticated/sorttable.js'></script>\n";
}

sub theme_popup_prehead
{
return &theme_prehead();
}

# theme_ui_columns_start(&headings, [width-percent], [noborder], [&tdtags], [heading])
# Returns HTML for a multi-column table, with the given headings
sub theme_ui_columns_start
{
local ($heads, $width, $noborder, $tdtags, $heading) = @_;
local ($href) = grep { $_ =~ /<a\s+href/i } @$heads;
local $rv;
$theme_ui_columns_row_toggle = 0;
local @classes;
push(@classes, "ui_table") if (!$noborder);
push(@classes, "sortable") if (!$href);
$rv .= "<table".(@classes ? " class='".join(" ", @classes)."'" : "").
    (defined($width) ? " width=$width%" : "").">\n";
if ($heading) {
  $rv .= "<thead> <tr $tb><td colspan=".scalar(@$heads).
         "><b>$heading</b></td></tr> </thead> <tbody>\n";
  }
$rv .= "<thead> <tr $tb>\n";
local $i;
for($i=0; $i<@$heads; $i++) {
  $rv .= "<td ".$tdtags->[$i]."><b>".
         ($heads->[$i] eq "" ? "<br>" : $heads->[$i])."</b></td>\n";
  }
$rv .= "</tr></thead> <tbody>\n";
$theme_ui_columns_count++;
return $rv;
}

# theme_ui_columns_row(&columns, &tdtags)
# Returns HTML for a row in a multi-column table
sub theme_ui_columns_row
{
$theme_ui_columns_row_toggle = $theme_ui_columns_row_toggle ? '0' : '1';
local ($cols, $tdtags) = @_;
local $rv;
$rv .= "<tr class='ui_columns row$theme_ui_columns_row_toggle' onMouseOver=\"this.className='mainhigh'\" onMouseOut=\"this.className='mainbody row$theme_ui_columns_row_toggle'\">\n";
local $i;
for($i=0; $i<@$cols; $i++) {
	$rv .= "<td ".$tdtags->[$i].">".
	       ($cols->[$i] !~ /\S/ ? "<br>" : $cols->[$i])."</td>\n";
	}
$rv .= "</tr>\n";
return $rv;
}

# theme_ui_columns_end()
# Returns HTML to end a table started by ui_columns_start
sub theme_ui_columns_end
{
return "</tbody> </table>\n";
}

# theme_select_all_link(field, form, text)
# Adds support for row highlighting to the normal select all
sub theme_select_all_link
{
local ($field, $form, $text) = @_;
$form = int($form);
$text ||= $text{'ui_selall'};
return "<a href='#' onClick='f = document.forms[$form]; ff = f.$field; ff.checked = true; r = document.getElementById(\"row_\"+ff.id); if (r) { r.className = \"mainsel\" }; for(i=0; i<f.$field.length; i++) { ff = f.${field}[i]; ff.checked = true; r = document.getElementById(\"row_\"+ff.id); if (r) { r.className = \"mainsel\" } } return false'>$text</a>";
}

# theme_select_invert_link(field, form, text)
# Adds support for row highlighting to the normal invert selection
sub theme_select_invert_link
{
local ($field, $form, $text) = @_;
$form = int($form);
$text ||= $text{'ui_selinv'};
return "<a href='#' onClick='f = document.forms[$form]; ff = f.$field; ff.checked = !f.$field.checked; r = document.getElementById(\"row_\"+ff.id); if (r) { r.className = ff.checked ? \"mainsel\" : \"mainbody\" }; for(i=0; i<f.$field.length; i++) { ff = f.${field}[i]; ff.checked = !ff.checked; r = document.getElementById(\"row_\"+ff.id); if (r) { r.className = ff.checked ? \"mainsel\" : \"mainbody\" } } return false'>$text</a>";
}

sub theme_ui_checked_columns_row
{
$theme_ui_columns_row_toggle = $theme_ui_columns_row_toggle ? '0' : '1';
local ($cols, $tdtags, $checkname, $checkvalue, $checked) = @_;
local $rv;
local $cbid = &quote_escape(quotemeta("${checkname}_${checkvalue}"));
local $rid = &quote_escape(quotemeta("row_${checkname}_${checkvalue}"));
local $ridtr = &quote_escape("row_${checkname}_${checkvalue}");
local $mycb = $cb;
if ($checked) {
	$mycb =~ s/mainbody/mainsel/g;
	}
$mycb =~ s/class='/class='row$theme_ui_columns_row_toggle /;
$rv .= "<tr id=\"$ridtr\" $mycb onMouseOver=\"this.className = document.getElementById('$cbid').checked ? 'mainhighsel' : 'mainhigh'\" onMouseOut=\"this.className = document.getElementById('$cbid').checked ? 'mainsel' : 'mainbody row$theme_ui_columns_row_toggle'\">\n";
$rv .= "<td ".$tdtags->[0].">".
       &ui_checkbox($checkname, $checkvalue, undef, $checked, "onClick=\"document.getElementById('$rid').className = this.checked ? 'mainhighsel' : 'mainhigh';\"").
       "</td>\n";
local $i;
for($i=0; $i<@$cols; $i++) {
	$rv .= "<td ".$tdtags->[$i+1].">";
	if ($cols->[$i] !~ /<a\s+href|<input|<select|<textarea/) {
		$rv .= "<label for=\"".
			&quote_escape("${checkname}_${checkvalue}")."\">";
		}
	$rv .= ($cols->[$i] !~ /\S/ ? "<br>" : $cols->[$i]);
	if ($cols->[$i] !~ /<a\s+href|<input|<select|<textarea/) {
		$rv .= "</label>";
		}
	$rv .= "</td>\n";
	}
$rv .= "</tr>\n";
return $rv;
}

sub theme_ui_radio_columns_row
{
local ($cols, $tdtags, $checkname, $checkvalue, $checked) = @_;
local $rv;
local $cbid = &quote_escape(quotemeta("${checkname}_${checkvalue}"));
local $rid = &quote_escape(quotemeta("row_${checkname}_${checkvalue}"));
local $ridtr = &quote_escape("row_${checkname}_${checkvalue}");
local $mycb = $cb;
if ($checked) {
	$mycb =~ s/mainbody/mainsel/g;
	}

$rv .= "<tr $mycb id=\"$ridtr\" onMouseOver=\"this.className = document.getElementById('$cbid').checked ? 'mainhighsel' : 'mainhigh'\" onMouseOut=\"this.className = document.getElementById('$cbid').checked ? 'mainsel' : 'mainbody'\">\n";
$rv .= "<td ".$tdtags->[0].">".
       &ui_oneradio($checkname, $checkvalue, undef, $checked, "onClick=\"for(i=0; i<form.$checkname.length; i++) { ff = form.${checkname}[i]; r = document.getElementById('row_'+ff.id); if (r) { r.className = 'mainbody' } } document.getElementById('$rid').className = this.checked ? 'mainhighsel' : 'mainhigh';\"").
       "</td>\n";
local $i;
for($i=0; $i<@$cols; $i++) {
	$rv .= "<td ".$tdtags->[$i+1].">";
	if ($cols->[$i] !~ /<a\s+href|<input|<select|<textarea/) {
		$rv .= "<label for=\"".
			&quote_escape("${checkname}_${checkvalue}")."\">";
		}
	$rv .= ($cols->[$i] !~ /\S/ ? "<br>" : $cols->[$i]);
	if ($cols->[$i] !~ /<a\s+href|<input|<select|<textarea/) {
		$rv .= "</label>";
		}
	$rv .= "</td>\n";
	}
$rv .= "</tr>\n";
return $rv;
}

# theme_footer([page, name]+, [noendbody])
# Output a footer for returning to some page
sub theme_footer
{
local $i;
local $count = 0;
for($i=0; $i+1<@_; $i+=2) {
	local $url = $_[$i];
	if ($url ne '/' || !$tconfig{'noindex'}) {
		if ($url eq '/') {
			$url = "/?cat=$module_info{'category'}";
			}
		elsif ($url eq '' && $module_name eq 'virtual-server' ||
		       $url eq '/virtual-server/') {
			# Don't bother with virtualmin menu
			next;
			}
		elsif ($url eq '' && $module_name eq 'server-manager' ||
		       $url eq '/server-manager/') {
			# Don't bother with vm2 menu
			next;
			}
		elsif ($url =~ /(view|edit)_domain.cgi/ &&
		       $module_name eq 'virtual-server' ||
		       $url =~ /^\/virtual-server\/(view|edit)_domain.cgi/) {
			# Don't bother with link to domain details
			next;
			}
		elsif ($url =~ /edit_serv.cgi/ &&
		       $module_name eq 'server-manager' ||
		       $url =~ /^\/virtual-server\/edit_serv.cgi/) {
			# Don't bother with link to system details
			next;
			}
		elsif ($url eq '' && $module_name) {
			$url = "/$module_name/$module_info{'index_link'}";
			}
		elsif ($url =~ /^\?/ && $module_name) {
			$url = "/$module_name/$url";
			}
		$url = "$gconfig{'webprefix'}$url" if ($url =~ /^\//);
		if ($count++ == 0) {
			print "<a href=\"$url\"><img alt=\"<-\" align=middle border=0 src=\"$gconfig{'webprefix'}/images/left.gif\"></a>\n";
			}
		else {
			print "&nbsp;|\n";
			}
		print "&nbsp;<a href=\"$url\">",&text('main_return', $_[$i+1]),"</a>\n";
		}
	}
print "<br>\n";
if (!$_[$i]) {
	&theme_postbody(@_);
	print "</body></html>\n";
	}
}

$right_frame_sections_file = "$config_directory/$current_theme/sections";
@right_frame_sections = ( 'system', 'status', 'virtualmin', 'quotas', 'ips',
			  'sysinfo', 'vm2servers' );

# get_right_frame_sections()
# Returns a hash containg details of visible right-frame sections
sub get_right_frame_sections
{
local %sects;
&read_file($right_frame_sections_file, \%sects);
if ($sects{'global'}) {
	# Force use of global settings
	return \%sects;
	}
else {
	# Can try personal settings, but fall back to global
	local %usersects;
	if (&read_file($right_frame_sections_file.".".$remote_user,
		       \%usersects)) {
		return \%usersects;
		}
	else {
		return \%sects;
		}
	}
}

# save_right_frame_sections(&sects)
sub save_right_frame_sections
{
local ($sects) = @_;
&make_dir("$config_directory/$current_theme", 0700);
if ($sects->{'global'}) {
	# Update global settings, for all users
	&write_file($right_frame_sections_file, $sects);
	}
else {
	# Save own, and turn off global flag (if this is the master admin)
	&foreign_require("virtual-server", "virtual-server-lib.pl");
	if (&virtual_server::master_admin()) {
		local %globalsect;
		&read_file($right_frame_sections_file, \%globalsect);
		$globalsect{'global'} = 0;
		&write_file($right_frame_sections_file, \%globalsect);
		}
	&write_file($right_frame_sections_file.".".$remote_user, $sects);
	}
}

# list_right_frame_sections()
# Returns a list of possible sections for the current user
sub list_right_frame_sections
{
local ($hasvirt, $level, $hasvm2) = &get_virtualmin_user_level();
if ($level == 0) {
	local @rv = ( 'system' );
	if ($hasvirt) {
		push(@rv, 'updates', 'status', 'virtualmin', 'quotas',
			  'ips', 'sysinfo');
		}
	if ($hasvm2) {
		push(@rv, 'vm2servers');
		}
	return @rv;
	}
elsif ($level == 1) {
	return ( 'virtualmin' );
	}
elsif ($level == 2) {
	return ( 'system', 'quotas', 'bw' );
	}
else {
	return ( 'system' );
	}
}

# get_virtualmin_user_level()
# Returns three numbers - the first being a flag if virtualmin is installed,
# the second a user type (3=usermin, 2=domain, 1=reseller, 0=master), the
# third a flag for VM2
sub get_virtualmin_user_level
{
local ($hasvirt, $hasvm2, $level);
if (&foreign_available("server-manager")) {
	&foreign_require("server-manager", "server-manager-lib.pl");
	$hasvm2 = 1;
	}
if (&foreign_available("virtual-server")) {
	&foreign_require("virtual-server", "virtual-server-lib.pl");
	$hasvirt = 1;
	$level = &virtual_server::master_admin() ? 0 :
		 &virtual_server::reseller_admin() ? 1 : 2;
	}
elsif (&get_product_name() eq "usermin") {
	$level = 3;
	}
else {
	$level = 0;
	}
return ($hasvirt, $level, $hasvm2);
}

# Don't show virtualmin menu
sub theme_redirect
{
local ($orig, $url) = @_;
if ($module_name eq "virtual-server" && $orig eq "" &&
    $url =~ /^((http|https):\/\/([^\/]+))\//) {
	$url = "$1/right.cgi";
	}
print "Location: $url\n\n";
}

