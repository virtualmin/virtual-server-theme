#!/usr/bin/perl
# Show a form for configuring what gets dislayed on the right frame

do './web-lib.pl';
&init_config();
do 'ui-lib.pl';
&foreign_require("virtual-server", "virtual-server-lib.pl");
%text = &load_language($current_theme);
&load_theme_library();
$sects = &get_right_frame_sections();
!$sects->{'global'} || &virtual_server::master_admin() ||
	&error($text{'edright_ecannot'});

&ui_print_header(undef, $text{'edright_title'}, "", undef, 0, 1, 1);

print &ui_form_start("save_right.cgi", "post");
print &ui_table_start($text{'edright_header'}, undef ,2);

# Visible sections
print &ui_table_row($text{'edright_sects'},
    join("<br>\n", map { &ui_checkbox($_, 1, $text{'right_'.$_.'header'},
			!$sects->{'no'.$_}) } &list_right_frame_sections()));
# Alternate page
print &ui_table_row($text{'edright_alt'},
    &ui_opt_textbox("alt", $sects->{'alt'}, 40, $text{'edright_altdef'}."<br>",
		    $text{'edright_alturl'}));

# Default domain
print &ui_table_row($text{'edright_dom'},
    &ui_select("dom", $sects->{'dom'},
	       [ [ "", $text{'edright_first'} ],
		 map { [ $_->{'id'}, $_->{'dom'} ] }
		     grep { &virtual_server::can_edit_domain($_) }
			  sort { $a->{'dom'} cmp $b->{'dom'} }
			       &virtual_server::list_domains() ]));

# Allow changing
if (&virtual_server::master_admin()) {
	print &ui_table_row($text{'edright_global'},
		&ui_yesno_radio("global", int($sects->{'global'})));
	}

print &ui_table_end();
print &ui_form_end([ [ "save", $text{'save'} ] ]);

&ui_print_footer("right.cgi", $text{'right_return'});

