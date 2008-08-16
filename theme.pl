# Virtualmin Framed heme
# Icons copyright David Vignoni, all other theme elements copyright 2005-2007
# Virtualmin, Inc.

$main::vm2_no_create_links = 1;
$main::vm2_no_edit_buttons = 1;
$main::vm2_no_global_links = 1;

$main::mailbox_no_addressbook_button = 1;
$main::mailbox_no_folder_button = 1;

$main::basic_virtualmin_menu = 1;
$main::nocreate_virtualmin_menu = 1;
$main::nosingledomain_virtualmin_mode = 1;

$default_domains_to_show = 10;

# Global state for wrapper
# if 0, wrapper isn't on, add one and open it, if 1 close it, if 2+, subtract
# but don't close
$WRAPPER_OPEN = 0;

# theme_ui_post_header([subtext])
# Returns HTML to appear directly after a standard header() call
sub theme_ui_post_header
{
local ($text) = @_;
my $rv;
$rv .= "<div class='ui_post_header'>$text</div>\n" if (defined($text));
#$rv .= "<div class='section'>\n";
$rv .= "<p>" if (!defined($text));
return $rv;
}

# theme_ui_pre_footer()
# Returns HTML to appear directly before a standard footer() call
sub theme_ui_pre_footer
{
my $rv;
$rv .= "</div><p>\n";
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
my ($i, $need_tr);
my $cols = $_[3] ? $_[3] : 4;
my $per = int(100.0 / $cols);
print "<div class='wrapper'>\n";
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
print "</div>\n";
}

sub theme_generate_icon
{
my $w = !defined($_[4]) ? "width=48" : $_[4] ? "width=$_[4]" : "";
my $h = !defined($_[5]) ? "height=48" : $_[5] ? "height=$_[5]" : "";
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

# theme_post_save_domain(&domain, action)
# Called by Virtualmin after a domain is updated, to refresh the left menu
sub theme_post_save_domain
{
local ($d, $action) = @_;
# Refresh left side, in case options have changed
print "<script>\n";
if ($action eq 'create') {
	# Select the new domain
	print "top.left.location = '$gconfig{'webprefix'}/left.cgi?dom=$d->{'id'}';\n";
	}
else {
	# Just refresh left
	print "top.left.location = top.left.location;\n";
	}
print "</script>\n";
}

# theme_post_save_domains([domain, action]+)
# Called after multiple domains are updated, to refresh the left menu
sub theme_post_save_domains
{
print "<script>\n";
print "top.left.location = top.left.location;\n";
print "</script>\n";
}

# Called by VM2 after a server is updated, to refresh the left menu
sub theme_post_save_server
{
local ($s, $action) = @_;
if ($action eq 'create' || $action eq 'delete' ||
    !$done_theme_post_save_server++) {
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
				'$gconfig{'webprefix'}/left.cgi?mode=vm2&sid=$server->{'id'}';
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
				'$gconfig{'webprefix'}/left.cgi?mode=virtualmin&dom=$d->{'id'}';
			}
		}
	}
</script>
EOF
}

# theme_post_save_folder(&folder, action)
# Called after some folder is changed, to refresh the left frame. The action
# may be 'create', 'delete', 'modify' or 'read'
sub theme_post_save_folder
{
local ($folder, $action) = @_;
my $ref;
if ($action eq 'create' || $action eq 'delete' || $action eq 'modify') {
	# Always refresh
	$ref = 1;
	}
else {
	# Only refesh if showing unread count
	if (defined(&should_show_unread) && &should_show_unread($folder)) {
		$ref = 1;
		}
	}
if ($ref) {
	print "<script>\n";
	print "top.frames[0].document.location = top.frames[0].document.location;\n";
	print "</script>\n";
	}
}

sub theme_post_change_modules
{
print <<EOF;
<script>
var url = '' + top.left.location;
if (url.indexOf('mode=webmin') > 0) {
    top.left.location = url;
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

# ui_table_start(heading, [tabletags], [cols], [&default-tds])
# A table with a heading and table inside
sub theme_ui_table_start
{
my ($heading, $tabletags, $cols, $tds) = @_;
if (defined($main::ui_table_cols)) {
  # Push on stack, for nested call
  push(@main::ui_table_cols_stack, $main::ui_table_cols);
  push(@main::ui_table_pos_stack, $main::ui_table_pos);
  push(@main::ui_table_default_tds_stack, $main::ui_table_default_tds);
  }
my $rv;

if (!$WRAPPER_OPEN) {
	#my ($width) = $tabletags =~ m/width=(\d+\%)/;
	#$rv .= "<div class='shrinkwrapper'>\n";
	#$rv .= "<span>\n"; # for IE
	$rv .= "<table class='shrinkwrapper' $tabletags>\n";
	$rv .= "<tr><td>\n";
	}
$WRAPPER_OPEN++;
$rv .= "<table class='ui_table' $tabletags>\n";
$rv .= "<thead> <tr> <td><b>$heading</b></td> </tr> </thead>\n" if (defined($heading));
$rv .= "<tbody> <tr> <td><table width=100%>\n";
$main::ui_table_cols = $cols || 4;
$main::ui_table_pos = 0;
$main::ui_table_default_tds = $tds;
return $rv;
}

# ui_table_end()
# The end of a table started by ui_table_start
sub theme_ui_table_end
{
my $rv;
if ($main::ui_table_cols == 4 && $main::ui_table_pos) {
  # Add an empty block to balance the table
  $rv .= &ui_table_row(" ", " ");
  }
if (@main::ui_table_cols_stack) {
  $main::ui_table_cols = pop(@main::ui_table_cols_stack);
  $main::ui_table_pos = pop(@main::ui_table_pos_stack);
  $main::ui_table_default_tds = pop(@main::ui_table_default_tds_stack);
  }
else {
  $main::ui_table_cols = undef;
  $main::ui_table_pos = undef;
  $main::ui_table_default_tds = undef;
  }
$rv .= "</tbody></table></td></tr></table>\n";
if ($WRAPPER_OPEN==1) {
	#$rv .= "</div>\n";
	$rv .= "</td></tr>\n";
	$rv .= "</table>\n";
	}
$WRAPPER_OPEN--;
return $rv;
}

# theme_ui_tabs_start(&tabs, name, selected, show-border)
# Render a row of tabs from which one can be selected. Each tab is an array
# ref containing a name, title and link.
sub theme_ui_tabs_start
{
my ($tabs, $name, $sel, $border) = @_;
my $rv;
if (!$main::ui_hidden_start_donejs++) {
  $rv .= &ui_hidden_javascript();
  }

# Build list of tab titles and names
my $tabnames = "[".join(",", map { "\"".&html_escape($_->[0])."\"" } @$tabs)."]";
my $tabtitles = "[".join(",", map { "\"".&html_escape($_->[1])."\"" } @$tabs)."]";
$rv .= "<script>\n";
$rv .= "document.${name}_tabnames = $tabnames;\n";
$rv .= "document.${name}_tabtitles = $tabtitles;\n";
$rv .= "</script>\n";

# Output the tabs
my $imgdir = "$gconfig{'webprefix'}/images";
$rv .= &ui_hidden($name, $sel)."\n";
$rv .= "<table border=0 cellpadding=0 cellspacing=0>\n";
$rv .= "<tr><td bgcolor=#ffffff colspan=".(scalar(@$tabs)*2+1).">";
if ($ENV{'HTTP_USER_AGENT'} !~ /msie/i) {
	# For some reason, the 1-pixel space above the tabs appears huge on IE!
	$rv .= "<img src=$imgdir/1x1.gif>";
	}
$rv .= "</td></tr>\n";
$rv .= "<tr>\n";
$rv .= "<td bgcolor=#ffffff width=1><img src=$imgdir/1x1.gif></td>\n";
foreach my $t (@$tabs) {
	if ($t ne $tabs[0]) {
		# Spacer
		$rv .= "<td width=2 bgcolor=#ffffff>".
		       "<img src=$imgdir/1x1.gif></td>\n";
		}
	my $tabid = "tab_".$t->[0];
	$rv .= "<td id=${tabid}>";
	$rv .= "<table cellpadding=0 cellspacing=0 border=0><tr>";
	if ($t->[0] eq $sel) {
		# Selected tab
		$rv .= "<td valign=top class='selectedtab'>".
		       "<img src=$imgdir/lc2.gif alt=\"\"></td>";
		$rv .= "<td class='selectedtab' nowrap>".
		       "&nbsp;<b>$t->[1]</b>&nbsp;</td>";
		$rv .= "<td valign=top class='selectedtab'>".
		       "<img src=$imgdir/rc2.gif alt=\"\"></td>";
		}
	else {
		# Other tab (which has a link)
		$rv .= "<td valign=top $tb>".
		       "<img src=$imgdir/lc1.gif alt=\"\"></td>";
		$rv .= "<td $tb nowrap>".
		       "&nbsp;<a href='$t->[2]' ".
		       "onClick='return select_tab(\"$name\", \"$t->[0]\")'>".
		       "$t->[1]</a>&nbsp;</td>";
		$rv .= "<td valign=top $tb>".
		       "<img src=$imgdir/rc1.gif ".
		       "alt=\"\"></td>";
		$rv .= "</td>\n";
		}
	$rv .= "</tr></table>";
	$rv .= "</td>\n";
	}
$rv .= "<td bgcolor=#ffffff width=1><img src=$imgdir/1x1.gif></td>\n";
$rv .= "</table>\n";

if ($border) {
	# All tabs are within a grey box
	$rv .= "<table width=100% cellpadding=0 cellspacing=0 border=0>\n";
	$rv .= "<tr> <td bgcolor=#ffffff rowspan=3 width=1><img src=$imgdir/1x1.gif></td>\n";
	$rv .= "<td class='selectedtab' colspan=3 height=2><img src=$imgdir/1x1.gif></td> </tr>\n";
	$rv .= "<tr> <td class='selectedtab' width=2><img src=$imgdir/1x1.gif></td>\n";
	$rv .= "<td valign=top>";
	}
$main::ui_tabs_selected = $sel;
return $rv;
}

# theme_ui_columns_start(&headings, [width-percent], [noborder], [&tdtags], [heading])
# Returns HTML for a multi-column table, with the given headings
sub theme_ui_columns_start
{
local ($heads, $width, $noborder, $tdtags, $heading) = @_;
local ($href) = grep { $_ =~ /<a\s+href/i } @$heads;
my $rv;
$theme_ui_columns_row_toggle = 0;
if (!$noborder && !$WRAPPER_OPEN) {
	$rv .= "<table class='wrapper' width=$width%>\n";
	$rv .= "<tr><td>\n";
	}
$WRAPPER_OPEN++;
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
my $i;
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
my $rv;
$rv .= "<tr class='ui_columns row$theme_ui_columns_row_toggle' onMouseOver=\"this.className='mainhigh'\" onMouseOut=\"this.className='mainbody row$theme_ui_columns_row_toggle'\">\n";
my $i;
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
my $rv;
$rv = "</tbody> </table>\n";
if ($WRAPPER_OPEN == 1) { # Last wrapper
	$rv .= "</td> </tr> </table>\n";
	}
$WRAPPER_OPEN--;
return $rv;
}

# theme_ui_grid_table(&elements, columns, [width-percent], [tds], [tabletags],
#   [title])
# Given a list of HTML elements, formats them into a table with the given
# number of columns. However, themes are free to override this to use fewer
# columns where space is limited.
sub theme_ui_grid_table
{
my ($elements, $cols, $width, $tds, $tabletags, $title) = @_;
return "" if (!@$elements);
	
my $rv = "<table class='wrapper' " 
       . ($width ? " width=$width%" : "")
       . ($tabletags ? " ".$tabletags : "")
       . "><tr><td>\n";
$rv .= "<table class='ui_table'"
     . ($width ? " width=$width%" : "")
     . ($tabletags ? " ".$tabletags : "")
     . ">\n";
if ($title) {
	$rv .= "<thead><tr $tb> <td colspan=$cols><b>$title</b></td> </tr></thead>\n";
	}
$rv .= "<tbody>\n";
my $i;
for($i=0; $i<@$elements; $i++) {
  $rv .= "<tr>" if ($i%$cols == 0);
  $rv .= "<td ".$tds->[$i%$cols]." valign=top>".$elements->[$i]."</td>\n";
  $rv .= "</tr>" if ($i%$cols == $cols-1);
  }
if ($i%$cols) {
  while($i%$cols) {
    $rv .= "<td ".$tds->[$i%$cols]."><br></td>\n";
    $i++;
    }
  $rv .= "</tr>\n";
  }
$rv .= "</table>\n";
$rv .= "</tbody>\n";
$rv .= "</td></tr></table>\n"; # wrapper
return $rv;
}

# theme_ui_hidden_table_start(heading, [tabletags], [cols], name, status,
#     [&default-tds])
# A table with a heading and table inside, and which is collapsible
sub theme_ui_hidden_table_start
{
my ($heading, $tabletags, $cols, $name, $status, $tds) = @_;
my $rv;
if (!$main::ui_hidden_start_donejs++) {
  $rv .= &ui_hidden_javascript();
  }
my $divid = "hiddendiv_$name";
my $openerid = "hiddenopener_$name";
my $defimg = $status ? "open.gif" : "closed.gif";
my $defclass = $status ? 'opener_shown' : 'opener_hidden';
my $text = defined($tconfig{'cs_text'}) ? $tconfig{'cs_text'} :
        defined($gconfig{'cs_text'}) ? $gconfig{'cs_text'} : "000000";
if (!$WRAPPER_OPEN) { # If we're not already inside of a wrapper, wrap it
	#$rv .= "<div class='wrapper'>\n";
	$rv .= "<table class='wrapper' $tabletags>\n";
	$rv .= "<tr><td>\n";
	}
$WRAPPER_OPEN++;
$rv .= "<table class='ui_table' border $tabletags class='ui_table'>\n";
$rv .= "<thead> <tr> <td><a href=\"javascript:hidden_opener('$divid', '$openerid')\" id='$openerid'><img border=0 src='$gconfig{'webprefix'}/images/$defimg'></a> <a href=\"javascript:hidden_opener('$divid', '$openerid')\"><b><font color=#$text>$heading</font></b></a></td> </tr> </thead>\n" if (defined($heading));
$rv .= "<tbody><tr> <td><div class='$defclass' id='$divid'><table width=100%>\n";
$main::ui_table_cols = $cols || 4;
$main::ui_table_pos = 0;
$main::ui_table_default_tds = $tds;
return $rv;
}

# ui_hidden_table_end(name)
# Returns HTML for the end of table with hiding, as started by
# ui_hidden_table_start
sub theme_ui_hidden_table_end
{
my ($name) = @_;
$rv .= "</table></div></td></tr></tbody></table>\n";
if ( $WRAPPER_OPEN == 1 ) {
	$WRAPPER_OPEN--;
	#$rv .= "</div>\n";
	$rv .= "</td></tr></table>\n";
	}
elsif ($WRAPPER_OPEN) { $WRAPPER_OPEN--; }
return $rv;
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
return "<a href='#' onClick='f = document.forms[$form]; ff = f.$field; ff.checked = !f.$field.checked; r = document.getElementById(\"row_\"+ff.id); if (r) { r.className = ff.checked ? \"mainsel\" : \"mainbody\" }; for(i=0; i<f.$field.length; i++) { ff = f.${field}[i]; ff.checked = !ff.checked; r = document.getElementById(\"row_\"+ff.id); if (r) { r.className = ff.checked ? \"mainsel\" : \"mainbody row\"+((i+1)%2) } } return false'>$text</a>";
}

# theme_select_status_link(name, form, &folder, &mails, start, end, status, label)
# Adds support for row highlighting to read mail module selector
sub theme_select_status_link
{
local ($name, $formno, $folder, $mail, $start, $end, $status, $label) = @_;
$formno = int($formno);
local @sel;
for(my $i=$start; $i<=$end; $i++) {
	local $read = &get_mail_read($folder, $mail->[$i]);
	if ($status == 0) {
		push(@sel, ($read&1) ? 0 : 1);
		}
	elsif ($status == 1) {
		push(@sel, ($read&1) ? 1 : 0);
		}
	elsif ($status == 2) {
		push(@sel, ($read&2) ? 1 : 0);
		}
	}
my $js = "var sel = [ ".join(",", @sel)." ]; ";
$js .= "var f = document.forms[$formno]; ";
$js .= "for(var i=0; i<sel.length; i++) { document.forms[$formno].${name}[i].checked = sel[i]; var ff = f.${name}[i]; var r = document.getElementById(\"row_\"+ff.id); if (r) { r.className = ff.checked ? \"mainsel\" : \"mainbody row\"+((i+1)%2) } }";
$js .= "return false;";
return "<a href='#' onClick='$js'>$label</a>";
}

sub theme_select_rows_link
{
local ($field, $form, $text, $rows) = @_;
$form = int($form);
my $js = "var sel = { ".join(",", map { "\"".&quote_escape($_)."\":1" } @$rows)." }; ";
$js .= "for(var i=0; i<document.forms[$form].${field}.length; i++) { var ff = document.forms[$form].${field}[i]; var r = document.getElementById(\"row_\"+ff.id); ff.checked = sel[ff.value]; if (r) { r.className = ff.checked ? \"mainsel\" : \"mainbody row\"+((i+1)%2) } } ";
$js .= "return false;";
return "<a href='#' onClick='$js'>$text</a>";
}

sub theme_ui_checked_columns_row
{
$theme_ui_columns_row_toggle = $theme_ui_columns_row_toggle ? '0' : '1';
local ($cols, $tdtags, $checkname, $checkvalue, $checked, $disabled) = @_;
my $rv;
my $cbid = &quote_escape(quotemeta("${checkname}_${checkvalue}"));
my $rid = &quote_escape(quotemeta("row_${checkname}_${checkvalue}"));
my $ridtr = &quote_escape("row_${checkname}_${checkvalue}");
my $mycb = $cb;
if ($checked) {
	$mycb =~ s/mainbody/mainsel/g;
	}
$mycb =~ s/class='/class='row$theme_ui_columns_row_toggle /;
$rv .= "<tr id=\"$ridtr\" $mycb onMouseOver=\"this.className = document.getElementById('$cbid').checked ? 'mainhighsel' : 'mainhigh'\" onMouseOut=\"this.className = document.getElementById('$cbid').checked ? 'mainsel' : 'mainbody row$theme_ui_columns_row_toggle'\">\n";
$rv .= "<td ".$tdtags->[0].">".
       &ui_checkbox($checkname, $checkvalue, undef, $checked, "onClick=\"document.getElementById('$rid').className = this.checked ? 'mainhighsel' : 'mainhigh';\"", $disabled).
       "</td>\n";
my $i;
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
my $rv;
my $cbid = &quote_escape(quotemeta("${checkname}_${checkvalue}"));
my $rid = &quote_escape(quotemeta("row_${checkname}_${checkvalue}"));
my $ridtr = &quote_escape("row_${checkname}_${checkvalue}");
my $mycb = $cb;
if ($checked) {
	$mycb =~ s/mainbody/mainsel/g;
	}

$rv .= "<tr $mycb id=\"$ridtr\" onMouseOver=\"this.className = document.getElementById('$cbid').checked ? 'mainhighsel' : 'mainhigh'\" onMouseOut=\"this.className = document.getElementById('$cbid').checked ? 'mainsel' : 'mainbody'\">\n";
$rv .= "<td ".$tdtags->[0].">".
       &ui_oneradio($checkname, $checkvalue, undef, $checked, "onClick=\"for(i=0; i<form.$checkname.length; i++) { ff = form.${checkname}[i]; r = document.getElementById('row_'+ff.id); if (r) { r.className = 'mainbody' } } document.getElementById('$rid').className = this.checked ? 'mainhighsel' : 'mainhigh';\"").
       "</td>\n";
my $i;
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
my $i;
my $count = 0;
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
	print "</body></html>\n";
	}
}

$right_frame_sections_file = "$config_directory/$current_theme/sections";

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
	if (&foreign_check("virtual-server")) {
		&foreign_require("virtual-server", "virtual-server-lib.pl");
		if (&virtual_server::master_admin()) {
			local %globalsect;
			&read_file($right_frame_sections_file, \%globalsect);
			$globalsect{'global'} = 0;
			&write_file($right_frame_sections_file, \%globalsect);
			}
		}
	&write_file($right_frame_sections_file.".".$remote_user, $sects);
	}
}

# list_right_frame_sections()
# Returns a list of possible sections for the current user, as hash refs
sub list_right_frame_sections
{
local ($hasvirt, $level, $hasvm2) = &get_virtualmin_user_level();
local @rv;
if ($level == 0) {
	# Master admin
	@rv = ( 'system' );
	if ($hasvirt) {
		push(@rv, 'updates', 'status', 'newfeatures', 'virtualmin',
			  'quotas', 'bw', 'ips', 'sysinfo');
		}
	if ($hasvm2) {
		push(@rv, 'vm2servers');
		}
	}
elsif ($level == 1) {
	# Domain owner
	push(@rv, 'virtualmin');
	}
elsif ($level == 2) {
	# Reseller
	push(@rv, 'system', 'quotas', 'bw');
	}
elsif ($level == 4) {
	# VM2 system owner
	push(@rv, 'owner', 'vm2servers');
	}
else {
	# Usermin
	push(@rv, 'system');
	}
@rv = map { { 'name' => $_, 'title' => $text{'right_'.$_.'header'} } } @rv;
# Add plugin-defined sections
if (($level == 0 || $level == 1 || $level == 2) && $hasvirt &&
    defined(&virtual_server::list_plugin_sections)) {
	push(@rv, &virtual_server::list_plugin_sections($level));
	}
return @rv;
}

# get_virtualmin_user_level()
# Returns three numbers - the first being a flag if virtualmin is installed,
# the second a user type (3=usermin, 2=domain, 1=reseller, 0=master, 4=system
# owner), the third a flag for VM2
sub get_virtualmin_user_level
{
local ($hasvirt, $hasvm2, $level);
$hasvm2 = &foreign_available("server-manager");
$hasvirt = &foreign_available("virtual-server");
if ($hasvm2) {
	&foreign_require("server-manager", "server-manager-lib.pl");
	}
if ($hasvirt) {
	&foreign_require("virtual-server", "virtual-server-lib.pl");
	}
if ($hasvm2) {
	$level = $server_manager::access{'owner'} ? 4 : 0;
	}
elsif ($hasvirt) {
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

sub get_virtualmin_docs
{
local ($level) = @_;
return $level == 0 ? "http://www.virtualmin.com/documentation/id,virtualmin_administrators_guide/" :
       $level == 1 ? "http://www.virtualmin.com/documentation/id,virtualmin_resellers_guide/" :
       $level == 2 ? "http://www.virtualmin.com/documentation/id,virtualmin_virtual_server_owners_guide/" :
		     "http://www.virtualmin.com/documentation/";
}

sub get_vm2_docs
{
local ($level) = @_;
return "http://www.virtualmin.com/documentation/id,vm2_manual/";
}

sub ie_wrapper_fix
{
return <<"END_WRAPPER_FIX";
<!--[if IE]>
div.shrinkwrapper {
/* reset for IE */
display:block;
padding:0;
border: none;
background-color: #fff;
}
div.shrinkwrapper span {
display:inline-block;
text-align:left;
border: 1px solid #D9D9D9;
background: #F5F5F5;
zoom:1;
}
<![endif]-->
END_WRAPPER_FIX
}

1;

