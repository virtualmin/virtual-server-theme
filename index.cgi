#!/usr/bin/perl

do './web-lib.pl';
&init_config();
%text = &load_language($current_theme);

$minfo = &get_goto_module();
$goto = $minfo && $minfo->{'dir'} ne 'virtual-server' ?
	"/$minfo->{'dir'}/" : "/right.cgi?open=system&open=status";
if ($minfo) {
	$cat = "?$minfo->{'category'}=1";
	}
if (&foreign_available("virtual-server")) {
	%minfo = &get_module_info("virtual-server");
	$ver = "Virtualmin $minfo{'version'}";
	}
else {
	$ver = ucfirst(&get_product_name())." ".&get_webmin_version();
	}
if ($gconfig{'os_version'} eq "*") {
	$ostr = $gconfig{'real_os_type'};
	}
else {
	$ostr = "$gconfig{'real_os_type'} $gconfig{'real_os_version'}";
	}
$host = &get_display_hostname();

# Work out the page title
if ($gconfig{'os_version'} eq "*") {
	$ostr = $gconfig{'real_os_type'};
	}
else {
	$ostr = "$gconfig{'real_os_type'} $gconfig{'real_os_version'}";
	}
$title = $gconfig{'nohostname'} ? $text{'main_title2'}
			        : &text('main_title', $ver, $hostname, $ostr);

# Show frameset
&PrintHeader();
print <<EOF;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">

<html>
<head> <title>$title</title> </head>

<frameset cols="230,*">
	<frame name="left" src="left.cgi$cat" scrolling="auto">
	<frame name="right" src="$goto" noresize>
<noframes>
<body>

<p>This page uses frames, but your browser doesn't support them.</p>

</body>
</noframes>
</frameset>
</html>
EOF

