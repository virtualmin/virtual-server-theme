#!/usr/bin/perl
# Update visible right-frame sections

do './web-lib.pl';
&init_config();
do 'ui-lib.pl';
&ReadParse();
%text = &load_language($current_theme);
&error_setup($text{'edright_err'});
&load_theme_library();
($hasvirt, $level, $hasvm2) = &get_virtualmin_user_level();
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
if ($hasvirt) {
	$sect->{'dom'} = $in{'dom'};
	}
if ($hasvirt && &virtual_server::master_admin()) {
	$sect->{'global'} = $in{'global'};
	}

# Save config
&save_right_frame_sections($sect);
&redirect("right.cgi");

