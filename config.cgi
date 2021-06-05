#!/usr/local/bin/perl
# Display a form for editing the configuration of a module, one section at
# a time.

require "virtual-server-theme/virtual-server-theme-lib.pl";
require './config-lib.pl';
&ReadParse();

$m = $in{'module'} || $ARGV[0];
&foreign_available($m) || &error($text{'config_eaccess'});
%access = &get_module_acl(undef, $m);
$access{'noconfig'} &&
	&error($text{'config_ecannot'});
%module_info = &get_module_info($m);
if (-r &help_file($m, "config_intro")) {
	$help = [ "config_intro", $m ];
	}
else {
	$help = undef;
	}
&ui_print_header(&text('config_dir', $module_info{'desc'}),
		 $text{'config_title'}, "", $help, 0, 1);
$mdir = &module_root_directory($m);
my $mdir_conf_file = "$mdir/config.info";
if ($current_lang && $default_lang &&
    $current_lang ne $default_lang &&
    -r "$mdir_conf_file.$current_lang")
{
    $mdir_conf_file .= ".$current_lang";
}

# Read the config.info file to find sections
&read_file($mdir_conf_file, \%info, \@info_order);
foreach $i (@info_order) {
	@p = split(/,/, $info{$i});
	if ($p[1] == 11) {
		push(@sections, [ $i, $p[0] ]);
		}
	}
if (@sections > 1) {
	# Work out template section to edit
	$in{'section'} ||= $sections[0]->[0];
	$idx = &indexof($in{'section'}, map { $_->[0] } @sections);
	if ($in{'nprev'}) {
		$idx--;
		$idx = @sections-1 if ($idx < 0);
		}
	elsif ($in{'nnext'}) {
		$idx++;
		$idx = 0 if ($idx >= @sections);
		}
	$in{'section'} = $sections[$idx]->[0];

	# We have some sections .. show a menu to select
	print &ui_form_start("config.cgi");
	print &ui_hidden("module", $m),"\n";
	print $text{'config_section'},"\n";
	print &ui_select("section", $in{'section'}, \@sections,
			 1, 0, 0, 0, "onChange='form.submit()'");
	print &ui_submit($text{'config_change'});
	print "&nbsp;&nbsp;\n";
	print &ui_submit($text{'config_nprev'}, "nprev");
	print &ui_submit($text{'config_nnext'}, "nnext");
	print &ui_form_end();
	($s) = grep { $_->[0] eq $in{'section'} } @sections;
	$sname = $s->[1];
	}

print &ui_form_start("config_save.cgi", "post");
print &ui_hidden("module", $m),"\n";
print &ui_hidden("section", $in{'section'}),"\n";
if ($s) {
	# Find next section
	$idx = &indexof($s, @sections);
	if ($idx == @sections-1) {
		print &ui_hidden("section_next", $sections[0]->[0]);
		}
	else {
		print &ui_hidden("section_next", $sections[$idx+1]->[0]);
		}
	}
print &ui_table_start($sname, "width=100%", 2);
&read_file("$config_directory/$m/config", \%newconfig);
&load_module_preferences($m, \%newconfig);

if (-r "$mdir/config_info.pl") {
	# Module has a custom config editor
	&foreign_require($m, "config_info.pl");
	local $fn = "${m}::config_form";
	if (defined(&$fn)) {
		$func++;
		&foreign_call($m, "config_form", \%newconfig);
		}
	}
if (!$func) {
	# Use config.info to create config inputs
	&generate_config(\%newconfig, $mdir_conf_file, $m, undef, undef,
			 $in{'section'});
	}
print &ui_table_end();
print &ui_form_end([ [ "save", $text{'save'} ],
		     $s ? ( [ "save_next", $text{'config_next'} ] ) : ( ) ]);

if ($m eq "virtual-server") {
	&ui_print_footer("/right.cgi", $text{'config_return'});
	}
else {
	&ui_print_footer("/$m", $text{'index'});
	}

