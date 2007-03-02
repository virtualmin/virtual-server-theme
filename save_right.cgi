#!/usr/bin/perl
# Update visible right-frame sections

do './web-lib.pl';
&init_config();
do 'ui-lib.pl';
&ReadParse();
&foreign_require("virtual-server", "virtual-server-lib.pl");
%text = &load_language($current_theme);
&error_setup($text{'edright_err'});
&load_theme_library();
$sects = &get_right_frame_sections();
!$sects->{'global'} || &virtual_server::master_admin() ||
	&error($text{'edright_ecannot'});

# Validate and store
foreach $s (&list_right_frame_sections()) {
	$sect->{'no'.$s} = !$in{$s};
	}
if ($in{'alt_def'}) {
	delete($sect->{'alt'});
	}
else {
	$in{'alt'} =~ /^(http|https|\/)/ || &error($text{'edright_ealt'});
	$sect->{'alt'} = $in{'alt'};
	}
$sect->{'dom'} = $in{'dom'};
if (&virtual_server::master_admin()) {
	$sect->{'global'} = $in{'global'};
	}

# Save config
&save_right_frame_sections($sect);
&redirect("right.cgi");

