#!/usr/local/bin/perl
# Show the left-side menu of Virtualmin domains, plus modules

$trust_unknown_referers = 1;
require "virtual-server-theme/virtual-server-theme-lib.pl";
&ReadParse();
@admincats = ( "tmpl", "create", "backup" );
%gaccess = &get_module_acl(undef, "");

&popup_header("Virtualmin");
print "<script type='text/javascript' src='$gconfig{'webprefix'}/unauthenticated/toggleview.js'></script>\n";

# Find all left-side items from Webmin
@leftitems = &list_combined_webmin_menu();
($lefttitle) = grep { $_->{'type'} eq 'title' } @leftitems;

# Default left-side mode
$mode = $in{'mode'} ? $in{'mode'} :
	$sects->{'tab'} =~ /vm2|virtualmin|mail/ ? "items" :
	@leftitems ? "items" : "modules";

# Show mode selector
@has = ( );
if (@leftitems) {
	push(@has, { 'id' => 'items',
		     'desc' => $lefttitle->{'desc'},
		     'icon' => $lefttitle->{'icon'} });
	}
if ($sects->{'nowebmin'} == 0 ||
    $sects->{'nowebmin'} == 2 && $is_master) {
	$p = &get_product_name();
	push(@has, { 'id' => 'modules',
		     'desc' => $text{'has_'.$p},
		     'icon' => '/images/'.$p.'-small.png' });
	}
if (&indexof($mode, (map { $_->{'id'} } @has)) < 0) {
	$mode = $has[0]->{'id'};
	}
if (@has > 1) {
	print "<div class='mode'>";
	foreach $m (@has) {
		if ($m->{'id'} ne $mode) {
			print "<a href='newleft.cgi?mode=$m->{'id'}&dom=$did'>";
			}
		else {
			print "<b>";
			}
		if ($m->{'icon'}) {
			print "<img src='$m->{'icon'}' alt='$m->{'id'}'> ";
			}
		print $m->{'desc'};
		if ($m ne $mode) {
			print "</a>\n";
			}
		else {
			print "</b>\n";
			}
		}
	print "</div>";
	}

print "<div class='wrapper'>\n";
print "<table id='main' width='100%'><tbody><tr><td>\n";
if (($mode eq "webmin" || $mode eq "usermin") && $cansearch) {
	# Left form is for searching Webmin
	print "<form action=webmin_search.cgi target=right style='display:inline'>\n";
	$doneform = 1;
	}
elsif ($hasvirt || $hasvm2) {
	# Left form is for changing domain / server
	print "<form action=left.cgi style='display:inline'>\n";
	$doneform = 1;
	}
elsif ($mode eq "mail") {
	# Left form is for searching a mail folder
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
	print "            if (nv[1] != '1' && url.indexOf('view_mail.cgi') <= 0) {\n";
	print "                document.forms[0].id.value = unescape(nv[1]);\n";
	print "                }\n";
	print "            }\n";
	print "        else if (nv[0] == 'folder') {\n";
	print "            document.forms[0].folder.value = nv[1];\n";
	print "            }\n";
	print "        }\n";
	print "    }\n";
	print "}\n";
	print "</script>\n";
	print "<form action=mailbox/mail_search.cgi target=right onSubmit='GetMailFolder()' style='display:inline'>\n";
	print &ui_hidden("simple", 1);
	print &ui_hidden("folder", $dfolder->{'index'});
	print &ui_hidden("id", undef);
	$doneform = 1;
	}

$selwidth = (&get_left_frame_width() - 70)."px";
if ($mode eq "items") {
	# Show left menu items recursively
	&show_menu_items_list(\@leftitems, 0);
	}
elsif ($mode eq "modules") {
	# Work out what modules and categories we have
	@cats = &get_visible_modules_categories();
	@catnames = map { $_->{'code'} } @cats;

	if ($gconfig{"notabs_${base_remote_user}"} == 2 ||
	    $gconfig{"notabs_${base_remote_user}"} == 0 && $gconfig{'notabs'}) {
		# Show modules in one list
		foreach $minfo (map { @{$_->{'modules'}} } @cats) {
			&print_category_link("$minfo->{'dir'}/",
				     $minfo->{'desc'},
				     undef,
				     undef,
				     $minfo->{'noframe'} ? "_top" : "", 1);
			}
		}
	else {
		# Show all modules under categories
		foreach $c (@cats) {
			# Show category opener, plus modules under it
			&print_category_opener($c->{'code'}, \@catnames,
				$c->{'unused'} ?
				"<font color=#888888>$c->{'desc'}</font>" :
				$c->{'desc'});
			print "<div class='itemhidden' id='$c->{'code'}'>";
			foreach $minfo (@{$c->{'modules'}}) {
				&print_category_link("$minfo->{'dir'}/",
					     $minfo->{'desc'},
					     undef,
					     undef,
					     $minfo->{'noframe'} ? "_top" : "");
				}
			print "</div>\n";
			}
		}

	print "<hr>\n";
	}

# Show system information link
print "<div class='linkwithicon'><img src='images/gohome.png' alt=''>\n";
if ($mode eq "vm2") {
	$sparam = $server ? "&$server->{'id'}" : "";
	print "<div class='aftericon'><a target=right href='right.cgi?open=system&open=vm2servers&open=vm2limits&open=vm2usage&open=updates&open=owner$sparam'>$text{'left_home3'}</a></div></div>\n";
	}
elsif (&get_product_name() eq 'usermin') {
	print "<div class='aftericon'><a target=right href='right.cgi?open=system&open=common'>$text{'left_home2'}</a></div></div>\n";
	}
else {
	$dparam = $d ? "&amp;dom=$d->{'id'}" : "";
	print "<div class='aftericon'><a target=right href='right.cgi?open=system&auto=status&open=updates&open=reseller$dparam'>$text{'left_home'}</a></div></div>\n";
	}

# Show refresh modules link
if ($mode eq "webmin" && &foreign_available("webmin")) {
        print "<div class='linkwithicon'><img src='images/reload.png' alt=''>\n";
        print "<div class='aftericon'><a target=right href='webmin/refresh_modules.cgi'>$text{'main_refreshmods'}</a></div></div>\n";
	}

# Show logout link
&get_miniserv_config(\%miniserv);
if ($miniserv{'logout'} && !$ENV{'SSL_USER'} && !$ENV{'LOCAL_USER'} &&
    $ENV{'HTTP_USER_AGENT'} !~ /webmin/i) {
	print "<div class='linkwithicon'><img src='images/stock_quit.png' alt=''>\n";
	if ($main::session_id) {
		print "<div class='aftericon'><a target=_top href='session_login.cgi?logout=1'>$text{'main_logout'}</a></div>";
		}
	else {
		print "<div class='aftericon'><a target=_top href='switch_user.cgi'>$text{'main_switch'}</a></div>";
		}
	print "</div>\n";
	}

print "</td></tr></tbody></table>\n";
print "</div>\n";
&popup_footer();

# print_category_opener(name, &allcats, label)
# Prints out an open/close twistie for some category
sub print_category_opener
{
local ($c, $cats, $label) = @_;
local @others = grep { $_ ne $c } @$cats;
local $others = join("&", map { $_."=".$in{$_} } @others);
$others = "&$others" if ($others);
$others .= "&amp;dom=$did";
$others .= "&amp;mode=$mode";
$label = $c eq "others" ? $text{'left_others'} : $label;

# Show link to close or open catgory
print "<div class='linkwithicon'>";
print "<a href=\"javascript:toggleview('$c','toggle$c')\" id='toggle$c'><img border='0' src='images/closed.gif' alt='[+]'></a>\n";
print "<div class='aftericon'><a href=\"javascript:toggleview('$c','toggle$c')\" id='toggletext$c'><font color='#000000'>$label</font></a></div></div>\n";
}


sub print_category_link
{
print &category_link(@_);
}

sub category_link
{
local ($link, $label, $image, $noimage, $target, $noindent) = @_;
$target ||= "right";
return ($noindent ? "<div class='leftlink'>"
		  : "<div class='linkindented'>").
       "<a target='$target' href='$link'>$label</a></div>\n";
}

sub print_virtualmin_link
{
local ($l, $cls, $icon) = @_;
local $t = $l->{'target'} || "right";
if ($icon) {
	print "<div class='linkwithicon'><img src='images/$l->{'icon'}.png' alt=''>\n";
	}
print "<div class='$cls'>";
print "<b>" if ($l->{'icon'} eq 'index');
print "<a href='$l->{'url'}' target=$t>$l->{'title'}</a>";
print "</b>" if ($l->{'icon'} eq 'index');
print "</div>";
if ($icon) {
	print "</div>";
	}
print "\n";
}

# show_menu_items_list(&list, indent)
# Actually prints the HTML for menu items
sub show_menu_items_list
{
my ($items, $indent) = @_;
foreach my $item (@$items) {
	if ($item->{'type'} eq 'item') {
		# Link to some page
		if ($item->{'icon'}) {
			print "<div class='linkwithicon'>".
			      "<img src='$item->{'icon'}' alt=''>\n";
			}
		my $cls = $item->{'icon'} ? 'aftericon' :
		          $indent ? 'linkindented' : 'leftlink';
		print "<div class='$cls'>";
		print "<a href='$item->{'link'}' target=right>".
		      "$item->{'desc'}</a>";
		print "</div>";
		if ($item->{'icon'}) {
			print "</div>";
			}
		print "\n";
		}
	elsif ($item->{'type'} eq 'cat') {
		# Start of a new category
		my $c = $item->{'id'};
		print "<div class='linkwithicon'>";
		print "<a href=\"javascript:toggleview('$c','toggle$c')\" ".
		      "id='toggle$c'><img border='0' src='images/closed.gif' ".
		      "alt='[+]'></a>\n";
		print "<div class='aftericon'>".
		      "<a href=\"javascript:toggleview('$c','toggle$c')\" ".
		      "id='toggletext$c'>".
		      "<font color='#000000'>$item->{'desc'}</font></a></div>";
		print "</div>\n";
		print "<div class='itemhidden' id='cat_$c'>\n";
		&show_menu_items_list($item->{'members'}, $indent+1);
		print "</div>\n";
		}
	elsif ($item->{'type'} eq 'html') {
		# Some HTML block
		print $item->{'html'};
		}
	elsif ($item->{'type'} eq 'text') {
		# A line of text
		print &html_escape($item->{'desc'}),"<br>\n";
		}
	elsif ($item->{'type'} eq 'hr') {
		# Separator line
		print "<hr>\n";
		}
	elsif ($item->{'type'} eq 'menu' || $item->{'type'} eq 'input') {
		# For with an input of some kind
		print "<form action='$item->{'cgi'}'>\n";
		foreach my $h (@{$item->{'hidden'}}) {
			print &ui_hidden(@$h);
			}
		print $item->{'desc'},"\n";
		if ($item->{'type'} eq 'menu') {
			print &ui_select($item->{'name'}, $item->{'value'},
					 $item->{'menu'});
			}
		elsif ($item->{'type'} eq 'input') {
			print &ui_textbox($item->{'name'}, $item->{'value'},
					  $item->{'size'});
			}
		if ($item->{'icon'}) {
			print "<input type=image src='$item->{'icon'}' border=0>\n";
			}
		print "</form>\n";
		}
	elsif ($item->{'type'} eq 'title') {
		# Nothing to print here, as it is used for the tab title
		}
	}
}

