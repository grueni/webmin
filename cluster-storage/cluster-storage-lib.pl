# cluster-shell-lib.pl
# Doesn't really contain anything ..

BEGIN { push(@INC, ".."); };
use WebminCore;
use Lgl;

our (%in, %text, %gconfig, %config);
&init_config();

&foreign_require("servers", "servers-lib.pl");
&foreign_require("sesmanager", "sesmanager-lib.pl");

our $commands_file = "$module_config_directory/commands";
our $tempfileInventories = eval { &tempname($main::session_id.".get_Inventories") };

sub ui_enclosure_list
{
  my $action = shift;
  my $data = shift;
  print &ui_table_start($text{'Enclosures'}, undef);
  my @leftlinks = ();
  my @rightlinks = ();
  push(@leftlinks, &ui_link("create.cgi?discover=1",'Discover configuration') );
#  push(@rightlinks, &ui_link("test.cgi",'Test') );
  my @grid = ( &ui_links_row(\@leftlinks), &ui_links_row(\@rightlinks) );
  print &ui_grid_table(\@grid, 2, 100, [ "align=left", "align=right" ]);
#  print "<pre>".Dumper(\%$data)."</pre>";
  my $i = 0;
  foreach my $key (sort( keys (%{$data}))) {
    my $v = \%{$data->{$key}};
    my $hash = \%{$v->{Enclosures}};
#   print "<pre>server=$key v=$v</pre>";
#   print "<pre>".Dumper(\%$hash)."</pre>";
    $i += 1;
    print &ui_hidden_table_start("Server: ".$key, "width=100%", 7,$i.'_enclosure', 1);
    &sesmanager::print_enclosures('status.cgi?enclosure=',\%$hash);
    print &ui_hidden_table_end($i.'_enclosure');
  }
  print &ui_table_end();
}

1;

