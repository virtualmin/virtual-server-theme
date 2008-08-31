#!/usr/local/bin/perl

do './web-lib.pl';
&init_config();
&load_theme_library();
%text = &load_language($current_theme);
&ReadParse();

# Work out which module to open by default
$hasvirt = &foreign_available("virtual-server");
$hasvm2 = &foreign_available("server-manager");
if ($in{'dom'} && $hasvirt) {
	# Caller has requested a specific domain ..
	&foreign_require("virtual-server", "virtual-server-lib.pl");
	$d = &virtual_server::get_domain($in{'dom'});
	if ($d) {
		$goto = &virtual_server::can_config_domain($d) ?
			"virtual-server/edit_domain.cgi?dom=$d->{'id'}" :
			"virtual-server/view_domain.cgi?dom=$d->{'id'}";
		$left = "left.cgi?dom=$d->{'id'}";
		}
	}
if (!$goto) {
	# Default is determined by Webmin config, defaults to system info page
	$minfo = &get_goto_module();
	$goto = $minfo && $minfo->{'dir'} ne 'virtual-server' ?
		"$minfo->{'dir'}/" :"right.cgi?open=system&auto=status&open=updates&open=common&open=owner&open=reseller";
	$left = "left.cgi";
	if ($minfo) {
		$left .= "?$minfo->{'category'}=1";
		}
	}

if ($gconfig{'os_version'} eq "*") {
	$ostr = $gconfig{'real_os_type'};
	}
else {
	$ostr = "$gconfig{'real_os_type'} $gconfig{'real_os_version'}";
	}
$host = &get_display_hostname();
if ($hasvirt) {
	# Show Virtualmin version
	%minfo = &get_module_info("virtual-server");
	$title = $gconfig{'nohostname'} ? $text{'vmain_title2'} :
		&text('vmain_title', $minfo{'version'}, $host, $ostr);
	}
elsif ($hasvm2) {
	# Show VM2 version
	%minfo = &get_module_info("server-manager");
	$title = $gconfig{'nohostname'} ? $text{'mmain_title2'} :
		&text('mmain_title', $minfo{'version'}, $host, $ostr);
	}
else {
	# Show Webmin version
	$title = $gconfig{'nohostname'} ? $text{'main_title2'} :
		&text('main_title', &get_webmin_version(), $host, $ostr);
	}
if ($gconfig{'showlogin'}) {
	$title = $remote_user." : ".$title;
	}

# Show frameset
&PrintHeader();
$sects = &get_right_frame_sections();
$cols = $sects->{'fsize'} ? $sects->{'fsize'} :
	&get_product_name() eq 'usermin' ? 180 :
	&foreign_available("server-manager") &&
	&foreign_available("virtual-server") ? 260 : 240;
$frame1 = "<frame name=left src='$left' scrolling=auto>";
$frame2 = "<frame name=right src='$goto' noresize>";
$fscols = "$cols,*";
if ($current_lang_info->{'rtl'} || $current_lang eq "ar") {
	($frame1, $frame2) = ($frame2, $frame1);
	$fscols = "*,$cols";
	}

print <<EOF;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head> <title>$title</title> </head>

<frameset cols='$fscols' border=0>
	$frame1
	$frame2
<noframes>
<body>

<p>This page uses frames, but your browser doesn't support them.</p>

</body>
</noframes>
</frameset>
</html>
EOF

