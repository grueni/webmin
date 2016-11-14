#!/usr/bin/perl
# use strict;
# use warnings;

require './sesmanager-lib.pl';
&ReadParse();

my (@footer);

if ($in{'discover'})
{
  &ui_print_header(undef, "Discovering SES inventory", "", undef, 1, 1);
#  print "create.cgi ".Dumper(\%in);
	print &ui_form_start("cmd.cgi", "post");
	print &ui_hidden('discover', '1');
	print &ui_hidden('confirm', 'no');
	print &ui_hidden('cmd', $DISKMAP." discover" );
	print &ui_hidden('post_call_function', 'discover_getinventory' );
	print &ui_submit('Discover', 'submit');
	print &ui_form_end();
	push(@footer,"", $module_name );
} else {
	print &ui_print_header(undef, $text{'eno_unknown_error'}, "", undef, 1, 1);
	print "<pre>create.cgi in ".Dumper(\%in)."</pre>";
  push(@footer,"",$module_name );
}

&ui_print_footer(@footer[0], @footer[1]);
