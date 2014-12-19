#!/usr/local/bin/perl
# Show the left-side menu of Virtualmin domains, plus modules
use warnings;
use strict;

# Globals
our %gconfig;
our %in;
our %text;
our $base_remote_user;
our %miniserv;
our %gaccess;
our $session_id;

our $trust_unknown_referers = 1;
require "virtual-server-theme/virtual-server-theme-lib.pl";
require "virtual-server-theme/theme.pl";
ReadParse();

popup_header("Virtualmin");
print "<script type='text/javascript' src='$gconfig{'webprefix'}/unauthenticated/toggleview.js'></script>\n";

my $is_master;
# Is this user root?
if (foreign_available("virtual-server")) {
	foreign_require("virtual-server");
	$is_master = virtual_server::master_admin();
	}
elsif (foreign_available("server-manager")) {
	foreign_require("server-manager");
	$is_master = server_manager::can_action(undef, "global");
	}

# Find all left-side items from Webmin
my $sects = get_right_frame_sections();
my @leftitems = list_combined_webmin_menu($sects, \%in);
my ($lefttitle) = grep { $_->{'type'} eq 'title' } @leftitems;

# Default left-side mode
my $mode = $in{'mode'} ? $in{'mode'} :
	$sects->{'tab'} =~ /vm2|virtualmin|mail/ ? "items" :
	@leftitems ? "items" : "modules";

# Show mode selector
my @has = ( );
if (@leftitems) {
	push(@has, { 'id' => 'items',
		     'desc' => $lefttitle->{'desc'},
		     'icon' => $lefttitle->{'icon'} });
	}
if ($sects->{'nowebmin'} == 0 ||
    $sects->{'nowebmin'} == 2 && $is_master) {
	my $p = get_product_name();
	push(@has, { 'id' => 'modules',
		     'desc' => $text{'has_'.$p},
		     'icon' => '/images/'.$p.'-small.png' });
	}
if (indexof($mode, (map { $_->{'id'} } @has)) < 0) {
	$mode = $has[0]->{'id'};
	}
if (@has > 1) {
	print "<div class='mode'>";
	foreach my $m (@has) {
		print "<b>";
		if ($m->{'id'} ne $mode) {
			print "<a href='newleft.cgi?mode=$m->{'id'}'>";
			}
		if ($m->{'icon'}) {
			my $icon = add_webprefix($m->{'icon'});
			print "<img src='$icon' alt='$m->{'id'}'> ";
			}
		print $m->{'desc'};
		if ($m->{'id'} ne $mode) {
			print "</a>\n";
			}
		print "</b>\n";
		}
	print "</div>";
	}

print "<div class='wrapper'>\n";
print "<table id='main' width='100%'><tbody><tr><td>\n";

my $selwidth = (get_left_frame_width() - 70)."px";
if ($mode eq "modules") {
	# Work out what modules and categories we have
	# XXX call list_modules_webmin_menu once Webmin 1.730 is out
	my @cats = get_visible_modules_categories();
	my @catnames = map { $_->{'code'} } @cats;

	if ($gconfig{"notabs_${base_remote_user}"} == 2 ||
	    $gconfig{"notabs_${base_remote_user}"} == 0 && $gconfig{'notabs'}) {
		# Show modules in one list
		@leftitems = map { module_to_menu_item($_) }
				 (map { @{$_->{'modules'}} } @cats);
		}
	else {
		# Show all modules under categories
		@leftitems = ( );
		foreach my $c (@cats) {
			my $citem = { 'type' => 'cat',
				      'id' => $c->{'code'},
				      'desc' => $c->{'desc'},
				      'members' => [ ] };
			foreach my $minfo (@{$c->{'modules'}}) {
				push(@{$citem->{'members'}},
				     module_to_menu_item($minfo));
				}
			push(@leftitems, $citem);
			}
		}
	push(@leftitems, { 'type' => 'hr' });
	}

# Show system information link
push(@leftitems, { 'type' => 'item',
		   'id' => 'home',
		   'desc' => $text{'left_home'},
		   'link' => '/'.&right_page_cgi(),
		   'icon' => '/images/gohome.png' });

# Show refresh modules link
if ($mode eq "modules" && foreign_available("webmin")) {
	push(@leftitems, { 'type' => 'item',
			   'id' => 'refresh',
			   'desc' => $text{'main_refreshmods'},
			   'link' => '/webmin/refresh_modules.cgi',
			   'icon' => '/images/reload.png' });
	}

# Show logout link
get_miniserv_config(\%miniserv);
if ($miniserv{'logout'} && !$ENV{'SSL_USER'} && !$ENV{'LOCAL_USER'} &&
    $ENV{'HTTP_USER_AGENT'} !~ /webmin/i) {
	my $logout = { 'type' => 'item',
		       'id' => 'logout',
		       'icon' => '/images/stock_quit.png' };
	if ($main::session_id) {
		$logout->{'desc'} = $text{'main_logout'};
		$logout->{'link'} = '/session_login.cgi?logout=1';
		}
	else {
		$logout->{'desc'} = $text{'main_switch'};
		$logout->{'link'} = '/switch_user.cgi';
		}
	push(@leftitems, $logout);
	}

# Show Webmin search form
my $cansearch = $gaccess{'webminsearch'} ne '0' && !$sects->{'nosearch'};
if ($mode eq "modules" && $cansearch) {
	push(@leftitems, { 'type' => 'input',
			   'desc' => $text{'left_search'},
			   'name' => 'search',
			   'cgi' => '/webmin_search.cgi', });
	}

show_menu_items_list(\@leftitems, 0);

print "</td></tr></tbody></table>\n";
print "</div>\n";
popup_footer();

# show_menu_items_list(&list, indent)
# Actually prints the HTML for menu items
sub show_menu_items_list
{
my ($items, $indent) = @_;
foreach my $item (@$items) {
	if ($item->{'type'} eq 'item') {
		# Link to some page
		my $t = $item->{'target'} eq 'new' ? '_blank' :
			$item->{'target'} eq 'window' ? '_top' : 'right';
		if ($item->{'icon'}) {
			my $icon = add_webprefix($item->{'icon'});
			print "<div class='linkwithicon'>".
			      "<img src='$icon' alt=''>\n";
			}
		my $cls = $item->{'icon'} ? 'aftericon' :
		          $indent ? 'linkindented' : 'leftlink';
		print "<div class='$cls'>";
		my $link = add_webprefix($item->{'link'});
		print "<a href='$link' target=$t>".
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
		print "<a href=\"javascript:toggleview('cat$c','toggle$c')\" ".
		      "id='toggle$c'><img border='0' src='images/closed.gif' ".
		      "alt='[+]'></a>\n";
		print "<div class='aftericon'>".
		      "<a href=\"javascript:toggleview('cat$c','toggle$c')\" ".
		      "id='toggletext$c'>".
		      "<font color='#000000'>$item->{'desc'}</font></a></div>";
		print "</div>\n";
		print "<div class='itemhidden' id='cat$c'>\n";
		show_menu_items_list($item->{'members'}, $indent+1);
		print "</div>\n";
		}
	elsif ($item->{'type'} eq 'html') {
		# Some HTML block
		print "<div class='leftlink'>",$item->{'html'},"</div>\n";
		}
	elsif ($item->{'type'} eq 'text') {
		# A line of text
		print "<div class='leftlink'>",
		      html_escape($item->{'desc'}),"</div>\n";
		}
	elsif ($item->{'type'} eq 'hr') {
		# Separator line
		print "<hr>\n";
		}
	elsif ($item->{'type'} eq 'menu' || $item->{'type'} eq 'input') {
		# For with an input of some kind
		if ($item->{'cgi'}) {
			print "<form action='$item->{'cgi'}' target=right>\n";
			}
		else {
			print "<form>\n";
			}
		foreach my $h (@{$item->{'hidden'}}) {
			print ui_hidden(@$h);
			}
		print "<div class='leftlink'>";
		print $item->{'desc'},"\n";
		if ($item->{'type'} eq 'menu') {
			my $sel = "";
			if ($item->{'onchange'}) {
				$sel = "window.parent.frames[1].location = ".
				       "\"$item->{'onchange'}\" + this.value";
				}
			print ui_select($item->{'name'}, $item->{'value'},
					 $item->{'menu'}, 1, 0, 0, 0,
					 "onChange='form.submit(); $sel' ".
					 "style='width:$selwidth'");
			}
		elsif ($item->{'type'} eq 'input') {
			print ui_textbox($item->{'name'}, $item->{'value'},
					  $item->{'size'});
			}
		if ($item->{'icon'}) {
			my $icon = add_webprefix($item->{'icon'});
			print "<input type=image src='$icon' ".
			      "border=0 class=goArrow>\n";
			}
		print "</div>";
		print "</form>\n";
		}
	elsif ($item->{'type'} eq 'title') {
		# Nothing to print here, as it is used for the tab title
		}
	}
}

# module_to_menu_item(&module)
# Converts a module to the hash ref format expected by show_menu_items_list
sub module_to_menu_item
{
my ($minfo) = @_;
return { 'type' => 'item',
	 'id' => $minfo->{'dir'},
	 'desc' => $minfo->{'desc'},
	 'link' => '/'.$minfo->{'dir'}.'/' };
}

# add_webprefix(link)
# If a URL starts with a / , add webprefix
sub add_webprefix
{
my ($link) = @_;
return $link =~ /^\// ? $gconfig{'webprefix'}.$link : $link;
}
