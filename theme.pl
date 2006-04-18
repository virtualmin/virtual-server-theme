
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
	print "<link rel='stylesheet' type='text/css' href='$gconfig{'webprefix'}/unauthenticated/style.css'>\n";
	}
}

sub theme_prehead
{
print "<link rel='stylesheet' type='text/css' href='$gconfig{'webprefix'}/unauthenticated/style.css' />\n";
print "<script type='text/javascript' src='$gconfig{'webprefix'}/unauthenticated/toggleview.js'></script>\n";
print "<!--[if gte IE 5.5000]>\n";
print "<script type='text/javascript' src='$gconfig{'webprefix'}/unauthenticated/pngfix.js'></script>\n";
print "<![endif]-->\n";
}

