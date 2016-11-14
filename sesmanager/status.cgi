#!/usr/bin/perl

use strict;
use warnings;

require './sesmanager-lib.pl';
our (%in, %text, %gconfig, %config,$module_name);
&ReadParse();

my $data = &Lgl::discover_getinventory();
my (@footer);

#show controller  status
if ($in{'controller'})
{
	my $key = $in{'controller'};
  print &ui_print_header(undef, $text{'status_controller_title'}." ".$in{'controller'}, "", undef, 1, 1);

#-- properties table --
  print &ui_hidden_table_start('Properties', "width=100%", 4,'controller_properties', 1);
  print &ui_controller_properties($key,\%$data);
  print &ui_hidden_table_end('controller_properties');
	
	push(@footer, "?mode=controllers", $text{'Controllers'}." list" );
}

#show enclosure status
elsif ($in{'enclosure'})
{
	my $key = $in{'enclosure'};
	&ui_print_header(undef, $text{'status_enclosure_title'}." ".$in{'enclosure'}, "", undef, 1, 1);

  #-- properties table --
  print &ui_hidden_table_start('Properties', "width=100%", 4,'enclosure_properties', 1);
  &ui_enclosure_properties($key,\%$data);
  print &ui_hidden_table_end('enclosure_properties');

  #-- devices    table --
  print &ui_hidden_table_start('Devices', "width=100%", 4,'enclosure_devices', 1);
  &ui_enclosure_devices($key,\%$data);
  print &ui_hidden_table_end('enclosure_devices');

  #-- slots      table --
  print &ui_hidden_table_start('Slots', "width=100%", 4,'enclosure_slots', 0);
  &ui_enclosure_slots($key,\%$data);
  print &ui_hidden_table_end('enclosure_slots');

  #-- status table --
  print &ui_hidden_table_start('Status', "width=100%", 1,'enclosure_status', 0);
  &ui_enclosure_status($key,\%$data);
  print &ui_hidden_table_end('enclosure_status');

	push(@footer, "?mode=enclosures", $text{'Enclosures'}." list" );
}

#show disk status
elsif ($in{'disk'})
{
	my $key = $in{'disk'};
  &ui_print_header(undef, $text{'status_disk_title'}." ".$in{'disk'}, "", undef, 1, 1);
  &ui_disk_properties($key,\%$data);	
  push(@footer, "?mode=disks", $text{'Disk'}." list" ) ;
}

#show path status
elsif ($in{'path'})
{
	my $key = $in{'path'};
  &ui_print_header(undef, $text{'status_path_title'}." ".$in{'path'}, "", undef, 1, 1);
	push(@footer, "?mode=paths", $text{'Path'}." list" );
}

else {
	  print &ui_print_header(undef, $text{'eno_unknown_error'}, "", undef, 1, 1);
	  push(@footer, "/", $text{'index_return'} );
}

&ui_print_footer(@footer[0], @footer[1]);
