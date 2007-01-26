
# Swell-Nuvola theme
# Icons copyright David Vignoni, all other theme elements copyright Joe Cooper.

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

sub theme_post_save_domain
{
print "<script>\n";
print "top.left.location = top.left.location;\n";
print "</script>\n";
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
print "<!--[if gte IE 5.5000]>\n";
print "<script type='text/javascript' src='$gconfig{'webprefix'}/unauthenticated/pngfix.js'></script>\n";
print "<![endif]-->\n";
print "<script>\n";
print "var rowsel = new Array();\n";
print "</script>\n";
print "<script type='text/javascript' src='$gconfig{'webprefix'}/unauthenticated/sorttable.js'></script>\n";
}

# theme_ui_columns_start(&headings, [width-percent], [noborder], [&tdtags], [heading])
# Returns HTML for a multi-column table, with the given headings
sub theme_ui_columns_start
{
local ($heads, $width, $noborder, $tdtags, $heading) = @_;
local ($href) = grep { $_ =~ /<a\s+href/i } @$heads;
local $rv;
$rv .= "<table".($noborder ? "" : " border").
    (defined($width) ? " width=$width%" : "").
    ($href ? "" : " class='sortable'").">\n";
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
local ($cols, $tdtags) = @_;
local $rv;
$rv .= "<tr $cb onMouseOver=\"this.className='mainhigh'\" onMouseOut=\"this.className='mainbody'\">\n";
local $i;
for($i=0; $i<@$cols; $i++) {
	$rv .= "<td ".$tdtags->[$i].">".
	       ($cols->[$i] eq "" ? "<br>" : $cols->[$i])."</td>\n";
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
local ($cols, $tdtags, $checkname, $checkvalue, $checked) = @_;
local $rv;
local $cbid = &quote_escape(quotemeta("${checkname}_${checkvalue}"));
local $rid = &quote_escape(quotemeta("row_${checkname}_${checkvalue}"));
local $ridtr = &quote_escape("row_${checkname}_${checkvalue}");
local $mycb = $cb;
if ($checked) {
	$mycb =~ s/mainbody/mainsel/g;
	}
$rv .= "<tr $mycb id=\"$ridtr\" class=\"$cclass\" onMouseOver=\"this.className = document.getElementById('$cbid').checked ? 'mainhighsel' : 'mainhigh'\" onMouseOut=\"this.className = document.getElementById('$cbid').checked ? 'mainsel' : 'mainbody'\">\n";
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
	$rv .= ($cols->[$i] eq "" ? "<br>" : $cols->[$i]);
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
local ($cols, $tdtags, $checkname, $checkvalue) = @_;
local $rv;
local $cbid = &quote_escape(quotemeta("${checkname}_${checkvalue}"));
local $rid = &quote_escape(quotemeta("row_${checkname}_${checkvalue}"));
local $ridtr = &quote_escape("row_${checkname}_${checkvalue}");

$rv .= "<tr $cb id=\"$ridtr\" onMouseOver=\"this.className = document.getElementById('$cbid').checked ? 'mainhighsel' : 'mainhigh'\" onMouseOut=\"this.className = document.getElementById('$cbid').checked ? 'mainsel' : 'mainbody'\">\n";
$rv .= "<td ".$tdtags->[0].">".
       &ui_oneradio($checkname, $checkvalue, undef, 0, "onClick=\"for(i=0; i<form.$checkname.length; i++) { ff = form.${checkname}[i]; r = document.getElementById('row_'+ff.id); if (r) { r.className = 'mainbody' } } document.getElementById('$rid').className = this.checked ? 'mainhighsel' : 'mainhigh';\"").
       "</td>\n";
local $i;
for($i=0; $i<@$cols; $i++) {
	$rv .= "<td ".$tdtags->[$i+1].">";
	if ($cols->[$i] !~ /<a\s+href|<input|<select|<textarea/) {
		$rv .= "<label for=\"".
			&quote_escape("${checkname}_${checkvalue}")."\">";
		}
	$rv .= ($cols->[$i] eq "" ? "<br>" : $cols->[$i]);
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
for($i=0; $i+1<@_; $i+=2) {
	local $url = $_[$i];
	if ($url ne '/' || !$tconfig{'noindex'}) {
		if ($url eq '/') {
			$url = "/?cat=$module_info{'category'}";
			}
		elsif ($url eq '' && $module_name eq 'virtual-server') {
			# Don't bother with virtualmin menu
			next;
			}
		elsif ($url eq '' && $module_name) {
			$url = "/$module_name/$module_info{'index_link'}";
			}
		elsif ($url =~ /^\?/ && $module_name) {
			$url = "/$module_name/$url";
			}
		$url = "$gconfig{'webprefix'}$url" if ($url =~ /^\//);
		if ($i == 0) {
			print "<a href=\"$url\"><img alt=\"<-\" align=middle border=0 src=$gconfig{'webprefix'}/images/left.gif></a>\n";
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
			  'sysinfo' );

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
local ($hasvirt, $level) = &get_virtualmin_user_level();
if (!$hasvirt) {
	return ( 'system' );
	}
elsif ($level == 0) {
	return ( 'system', 'status', 'virtualmin', 'quotas', 'ips', 'sysinfo' );
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
# Returns two numbers - the first being a flag if virtualmin is installed,
# the second a user type (3=usermin, 2=domain, 1=reseller, 0=master)
sub get_virtualmin_user_level
{
local ($hasvirt, $level);
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
return ($hasvirt, $level);
}

