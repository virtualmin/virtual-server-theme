#!/usr/local/bin/perl
# Update collected info

do './web-lib.pl';
&init_config();
&foreign_require("virtual-server", "virtual-server-lib.pl");
$info = &virtual_server::collect_system_info();
if ($info) {
	&virtual_server::save_collected_info($info);
	}
&redirect("right.cgi");

