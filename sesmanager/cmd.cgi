#!/usr/bin/perl
# use strict;
# use warnings;

require './sesmanager-lib.pl';
&ReadParse();

if ($in{'discover'})
{
	print &ui_print_header(undef, "Discovering SES inventory", "", undef, 1, 1);
	print &Lgl::ui_cmd("Discovering SES inventory ...",$Lgl::DISKMAP." discover",\%in);
} else {
  print &ui_print_header(undef, $text{'eno_unknown_error'}, "", undef, 1, 1);
  print "<pre>cmd.cgi in ".Dumper(\%in)."</pre>";
  push(@footer,"",$module_name );
}

&ui_print_footer("", $module_name);
