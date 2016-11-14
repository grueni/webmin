#!/usr/bin/perl
# index.cgi
# Shows a form for running a command, allowing the selection of a server or
# group of servers to run it on.
use strict;
use warnings;

require './cluster-storage-lib.pl';
our (%in, %text, %gconfig, %config);
our ($tempfileInventories);

&ui_print_header(undef, $text{'index_title'}, "", "intro", 0, 1);

my $inventories = &Lgl::discover_getinventories($tempfileInventories);

# define tabs
my @tabs = (
    [ 'storages',   $text{'Storages'},    'index.cgi?mode=storages' ],
    [ 'enclosures', $text{'Enclosures'},  'index.cgi?mode=enclosures' ],
);

# start tabs
print &ui_tabs_start(\@tabs, "mode", $in{'mode'} || $tabs[0]->[0], 1);

# start storages  tab
print &ui_tabs_start_tab('mode', 'storages');
#&ui_enclosure_list(undef,\%$data);
print &ui_tabs_end_tab('mode', 'storages');

# start enclosures tab
print &ui_tabs_start_tab('mode', 'enclosures');
&ui_enclosure_list(undef,\%$inventories);
print &ui_tabs_end_tab('mode', 'enclosures');

# end tabs
print &ui_tabs_end(1);
 
&ui_print_footer("/", $text{'index'});

