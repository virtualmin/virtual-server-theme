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

# Work out if we have a top frame
if ($hasvirt) {
	%vconfig = &foreign_config("virtual-server");
	}
$upperframe = $vconfig{'theme_topframe'} ||
	      $gconfig{'theme_topframe'};
$upperrows = $vconfig{'theme_toprows'} ||
	     $gconfig{'theme_toprows'} || 200;
if ($upperframe =~ /\$LEVEL|\$\{LEVEL/) {
	# Sub in user level
	$levelnum = &get_virtualmin_user_level();
	$level = $levelnum == 0 ? "master" :
		 $levelnum == 1 ? "reseller" :
		 $levelnum == 2 ? "domain" :
		 $levelnum == 3 ? "usermin" :
		 $levelnum == 4 ? "owner" : "unknown";
	$upperframe = &substitute_template($upperframe, { 'level' => $level });
	}

# Show frameset
&PrintHeader();
$cols = &get_left_frame_width();
$frame1 = "<frame name=left src='$left' scrolling=auto>";
$frame2 = "<frame name=right src='$goto' noresize scrolling=auto>";
$fscols = "$cols,*";
if ($current_lang_info->{'rtl'} || $current_lang eq "ar") {
	($frame1, $frame2) = ($frame2, $frame1);
	$fscols = "*,$cols";
	}

# Page header
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">\n";
print "<html>\n";
print "<head> <title>$title</title> </head>\n";

# Upper custom frame
if ($upperframe) {
	print "<frameset rows='$upperrows,*' border=0>\n";
	if ($upperframe =~ /^\//) {
		# Local file to serve
		print "<frame name=top src='top.cgi' scrolling=auto>\n";
		}
	else {
		# Absolute URL
		print "<frame name=top src='$upperframe' scrolling=auto>\n";
		}
	}

# Left and right frames
print "<frameset cols='$fscols' border=0>\n";
print $frame1,"\n";
print $frame2,"\n";

# What if no frames?
print "<noframes>\n";
print "<body>\n";
print "<p>This page uses frames, but your browser doesn't support them.</p>\n";
print "</body>\n";
print "</noframes>\n";

# End of the frames and page
if ($upperframe) {
	print "</frameset>\n";
	}
print "</frameset>\n";
print "</html>\n";

