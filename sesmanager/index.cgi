#!/usr/bin/perl
use strict;
use warnings;
use Data::Dumper;

require './sesmanager-lib.pl';
our (%in, %text, %gconfig, %config,$module_name);
&ReadParse();

#my $json;
#{
#  local $/; #Enable 'slurp' mode
#  my $output = qx($DISKMAP getInventory);
#  my $i = index($output,'{');
#  $json = $i > 0 ? substr $output,$i : $output;
#}
# my $hash = decode_json($json);

&ui_print_header(undef, $text{'index_title'}, '', undef, 1, 1, 0, &help_search_link('ses', 'sg3_utils', 'sasinfo', 'doc', 'google'), undef, undef, $text{'index_version'} );

#print "<pre>module_name=".$module_name."</pre>";
#print "<pre>".Dumper(\%config)."</pre>";
#print "<pre>".Dumper(\%gconfig)."</pre>";

my $data = &Lgl::discover_getinventory();

# define tabs
my @tabs = (
    [ 'enclosures',  $text{'Enclosures'},  'index.cgi?mode=enclosures' ],
		[ 'controllers', $text{'Controllers'}, 'index.cgi?mode=controllers' ],
		[ 'disks',       $text{'Disks'},       'index.cgi?mode=disks' ],
		[ 'paths',       $text{'Paths'},       'index.cgi?mode=paths' ],
);

# start tabes
# $in{'mode'} ||= 'pools';
# print "<pre>".Dumper(\%gconfig)."</pre>";
print &ui_tabs_start(\@tabs, "mode", $in{'mode'} || $tabs[0]->[0], 1);

# start enclosures tab
print &ui_tabs_start_tab('mode', 'enclosures');
&ui_enclosure_list(undef,\%$data);
print &ui_tabs_end_tab('mode', 'enclosures');

# start controllers
print &ui_tabs_start_tab('mode', 'controllers');
&ui_controller_list(undef,\%$data);
print &ui_tabs_end_tab('mode', 'controllers');

# start disks tab
print &ui_tabs_start_tab('mode', 'disks');
&ui_disk_list(undef,\%$data);
print &ui_tabs_end_tab('mode', 'disks');

# start paths tab
print &ui_tabs_start_tab('mode', 'paths');
&ui_path_list(undef,\%$data);
print &ui_tabs_end_tab('mode', 'paths'); 

# end tabs
print &ui_tabs_end(1);

&ui_print_footer("/", $text{'index_return'});
