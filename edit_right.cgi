#!/usr/bin/perl
# Show a form for configuring what gets dislayed on the right frame

do './web-lib.pl';
&init_config();
do 'ui-lib.pl';
%text = &load_language($current_theme);
&load_theme_library();
($hasvirt, $level, $hasvm2) = &get_virtualmin_user_level();
$sects = &get_right_frame_sections();
!$sects->{'global'} || &virtual_server::master_admin() ||
	&error($text{'edright_ecannot'});

&ui_print_header(undef, $text{'edright_title'}, "", undef, 0, 1, 1);

print &ui_form_start("save_right.cgi", "post");
print &ui_table_start($text{'edright_header'}, undef ,2);

# Visible sections
print &ui_table_row($text{'edright_sects'},
    join("<br>\n", map { &ui_checkbox($_->{'name'}, 1, $_->{'title'},
			!$sects->{'no'.$_->{'name'}}) }
		       &list_right_frame_sections()));
# Alternate page
print &ui_table_row($text{'edright_alt'},
    &ui_opt_textbox("alt", $sects->{'alt'}, 40, $text{'edright_altdef'}."<br>",
		    $text{'edright_alturl'}));

# Default tab
print &ui_table_row($text{'edright_deftab'},
    &ui_select("tab", $sects->{'tab'},
       [ [ "", $text{'edright_tab1'} ],
	 $hasvirt ? ( [ "virtualmin", $text{'edright_virtualmin'} ] ) : ( ),
	 $hasvm2 ? ( [ "vm2", $text{'edright_vm2'} ] ) : ( ),
	 [ "webmin", $text{'edright_webmin'} ] ]));

if ($hasvirt) {
	# Default domain
	print &ui_table_row($text{'edright_dom'},
	    &ui_select("dom", $sects->{'dom'},
		       [ [ "", $text{'edright_first'} ],
			 map { [ $_->{'id'}, $_->{'dom'} ] }
			     grep { &virtual_server::can_edit_domain($_) }
				  sort { $a->{'dom'} cmp $b->{'dom'} }
				       &virtual_server::list_domains() ]));

	# Sort quotas by
	print &ui_table_row($text{'edright_qsort'},
	    &ui_radio("qsort", int($sects->{'qsort'}),
		      [ [ 1, $text{'edright_qsort1'} ],
		 	[ 0, $text{'edright_qsort0'} ] ]));

	# Number of servers to show
	print &ui_table_row($text{'edright_max'},
	    &ui_opt_textbox("max", $sects->{'max'}, 5,
			    $text{'default'}." ($default_domains_to_show)"));
	}

if ($hasvm2) {
	# Default VM2 server
	print &ui_table_row($text{'edright_server'},
	    &ui_select("server", $sects->{'server'},
		       [ [ "", $text{'edright_first'} ],
			 map { [ $_->{'id'}, $_->{'host'} ] }
			     sort { $a->{'host'} cmp $b->{'host'} }
				  &server_manager::list_managed_servers() ]));
	}

# Allow changing
if ($hasvirt && &virtual_server::master_admin()) {
	print &ui_table_row($text{'edright_global'},
		&ui_yesno_radio("global", int($sects->{'global'})));
	}

print &ui_table_end();
print &ui_form_end([ [ "save", $text{'save'} ] ]);

&ui_print_footer("right.cgi", $text{'right_return'});

