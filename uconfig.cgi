#!/usr/local/bin/perl
# Display a form for editing the preferences in a Usermin module, one section
# at a time.

require './web-lib.pl';
require './config-lib.pl';
require './ui-lib.pl';
&init_config();
%text = &load_language($current_theme);
&ReadParse();
$m = $in{'module'} || $ARGV[0];
&foreign_available($m) || &error($text{'config_eaccess'});
&switch_to_remote_user();
&create_user_config_dirs();

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

# Read the config.info file to find sections
&read_file("$mdir/uconfig.info", \%info, \@info_order);
foreach $i (@info_order) {
	@p = split(/,/, $info{$i});
	if ($p[1] == 11) {
		push(@sections, [ $i, $p[0] ]);
		}
	}
if (@sections > 1 && &get_webmin_version() >= 1.225) {
	# We have some .. show a menu to select
	$in{'section'} ||= $sections[0]->[0];
	print &ui_form_start("uconfig.cgi");
	print &ui_hidden("module", $m),"\n";
	print $text{'config_section'},"\n";
	print &ui_select("section", $in{'section'}, \@sections,
			 1, 0, 0, 0, "onChange='form.submit()'");
	print &ui_submit($text{'config_change'});
	print &ui_form_end();
	($s) = grep { $_->[0] eq $in{'section'} } @sections;
	$sname = " ($s->[1])";
	}

print &ui_form_start("uconfig_save.cgi", "post");
print &ui_hidden("module", $m),"\n";
print &ui_hidden("section", $in{'section'}),"\n";
print &ui_table_start(&text('config_header', $module_info{'desc'}).$sname,
		      "width=100%", 2);
&read_file("$m/defaultuconfig", \%config);
&read_file("$config_directory/$m/uconfig", \%config);
&read_file("$user_config_directory/$m/config", \%config);
&read_file("$config_directory/$m/canconfig", \%canconfig);

if (-r "$mdir/uconfig_info.pl") {
	# Module has a custom config editor
	&foreign_require($m, "uconfig_info.pl");
	local $fn = "${m}::config_form";
	if (defined(&$fn)) {
		$func++;
		&foreign_call($m, "config_form", \%config, \%canconfig);
		}
	}
if (!$func) {
	# Use config.info to create config inputs
	&generate_config(\%config, "$mdir/uconfig.info", $m, undef,
			 %canconfig ? \%canconfig : undef, $in{'section'});
	}
print &ui_table_end();
print &ui_form_end([ [ "save", $text{'save'} ] ]);

&ui_print_footer("/$m", $text{'index'});

