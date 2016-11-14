=head1 sesmanager-lib.pl

Functions for managing storage hardware with SES-2 commands.

=cut

BEGIN { push(@INC, ".."); };
use strict;
use warnings;
use WebminCore;
use Lgl;
#require 'lgl-lib.pl';
our (%in, %text, %gconfig, %config);
&init_config();
&foreign_require("cluster_storage", "cluster-storage-lib.pl");

my $smartctl="smartctl";

my %access = &get_module_acl();

# $in{'text'} = "vor discover";
# &webmin_log("_load_", undef, undef, \%in);
# $in{'text'} = "nach discover ".Dumper(\%$data);
# &webmin_log("_load_", undef, undef, \%in);

sub ui_controller_list
{
	my $action = shift;
  my $data = shift;
  print &ui_table_start($text{'Controllers'}, undef);
  my @leftlinks = ();
  my @rightlinks = ();
  push(@leftlinks, &ui_link("create.cgi?discover=1",'Discover configuration') );
  my @grid = ( &ui_links_row(\@leftlinks), &ui_links_row(\@rightlinks) );
  print &ui_grid_table(\@grid, 2, 100, [ "align=left", "align=right" ]);
  my $hash = $data->{Controllers};
#	print Dumper(\%$hash);
  &print_controllers('status.cgi?controller=',\%$hash);
#	print "<pre>tempfileInventories=".$cluster_storage::tempfileInventories."</pre>";
  print &ui_table_end();
}

sub ui_enclosure_list
{
	my $action = shift;
	my $data = shift;
  print &ui_table_start($text{'Enclosures'}, undef);
  my @leftlinks = ();
  my @rightlinks = ();
  push(@leftlinks, &ui_link("create.cgi?discover=1",'Discover configuration') );
	push(@rightlinks, &ui_link("test.cgi",'Test') );
  my @grid = ( &ui_links_row(\@leftlinks), &ui_links_row(\@rightlinks) );
  print &ui_grid_table(\@grid, 2, 100, [ "align=left", "align=right" ]);
  my $hash = $data->{Enclosures};
#  print Dumper(\%$hash);	
  &print_enclosures('status.cgi?enclosure=',\%$hash);
  print &ui_table_end();
}

sub ui_disk_list
{
	my $action = shift;	
	my $data = shift;
  print &ui_table_start($text{'Disks'}, undef);
  my @leftlinks = ();
  my @rightlinks = ();
  push(@leftlinks, &ui_link("create.cgi?discover=1",'Discover configuration') );
  my @grid = ( &ui_links_row(\@leftlinks), &ui_links_row(\@rightlinks) );
  print &ui_grid_table(\@grid, 2, 100, [ "align=left", "align=right" ]);
  my $hash = $data->{Disks};
#  print Dumper(\%$hash);
  &print_disks('status.cgi?disk=',\%$hash);
  print &ui_table_end();
}

sub ui_disk_properties
{
	my $key = shift;
  my @result = (`$smartctl -x $key 2>&1`);
	my $rc = ${^CHILD_ERROR_NATIVE};
	print "<pre>".join("",@result)."</pre>";
}

sub ui_controller_properties
  {
	my $key = shift;
	my $data = shift;
	my ($col, @table1, @table2);

	my $v = \%{$data->{Controllers}->{$key}};
	print &ui_table_row("Manufacurer", $v->{manufacturer});
	print &ui_table_row("Model", $v->{model});
	print &ui_table_row("Firmware", $v->{firmwareversion});
	print &ui_table_row("Logical Identifier", $v->{id});
	print &ui_table_row("Serial number", $v->{serial});
	print &ui_table_row("Drivername", $v->{drivername});

	print &ui_hr();
	push(@table1, "Ports" );
	push(@table2,  
			[ "Address" ],
			[ "attached to" ],
			[ "State" ],
			[ "Phys" ]  
		);
	$col = 0;	
	foreach my $port (keys %{$v->{ports}}) {
		$col += 1;
		my $p = \%{$v->{ports}->{$port}};
		my $e = \%{$data->{Addresses}->{$p->{"attached to"}}};
		@table1[$col] = $port;
		$table2[0][$col]= $p->{address} ;
		$table2[1][$col]= &ui_link("status.cgi?enclosure=$e->{enclosure}","$p->{'attached to'}");
		$table2[2][$col]= $p->{state} ;
		$table2[3][$col]= $p->{phys} ;
		};      
	&ui_columns_table(
		\@table1,
		100,
		\@table2,
		undef,
		0,
		"Ports",
		$text{"eno_data_available"},
		);
}

sub ui_enclosure_status
{
  my $key = shift;
  print "key=$key";
	
}

sub ui_enclosure_properties
	{
		my $key = shift;
	  my $data = shift;
		my ( @table1,$x, $s );
	  my $v = \%{$data->{Enclosures}->{$key}};

	  print &ui_table_row("Manufacurer", $v->{vendor});
		print &ui_table_row("Model", $v->{model});
		print &ui_table_row("Firmware", $v->{firmware});
		print &ui_table_row("Index", $v->{enclosureindex});

		push(@table1, "Type","Text","possible Elements");
		print &ui_table_start("Element types",undef,3); 
		print &ui_columns_start(\@table1, 100, 1);
    foreach my $et (sort keys %{$v->{"Element types"}}) {
			my $vv = \%{$v->{"Element types"}->{$et}};
			print &ui_columns_row([ $et,$vv->{"text"},$vv->{"possible elements"} ]);
		}
		print &ui_columns_end();
		print &ui_table_end();

}

sub ui_enclosure_devices
  {
    my $key = shift;
		my $data = shift;
    my $v = \%{$data->{Enclosures}->{$key}};
		my @table1;
    push(@table1, "Type","Device","Address","Type","Device","Address",);
    print &ui_columns_start(\@table1, 100, 1);
    foreach my $device (@{$v->{"devices"}}) {
			next if (index($device, "/dev/es/") == -1); 
      my $vv = \%{$data->{EnclosureDevices}->{$device}};
      my $sesaddress = $vv->{"address"};
      $vv = \%{$data->{Addresses}->{$sesaddress}};
      my $seset = $vv->{"Element type"};
			$vv = \%{$data->{EnclosureDevices}->{$device}};
			my (@smpet,@smpdevice,@smpaddress);
			foreach my $smpdevice (@{$vv->{"smp"}}) {
				push(@smpdevice, $smpdevice);
				$vv = \%{$data->{EnclosureDevices}->{$smpdevice}};
			  push(@smpaddress, $vv->{"address"});
				$vv = \%{$data->{Addresses}->{$vv->{"address"}}};
				push(@smpet, $vv->{"Element type"});
			}
      print &ui_columns_row([ $seset,$device,$sesaddress,
         join('<br/>',@smpet),join('<br/>',@smpdevice),join('<br/>',@smpaddress) ]);
    }
    print &ui_columns_end();
	}

sub ui_enclosure_slots
  {
    my $key = shift;
		my $data = shift;
		my ($v, $vv, $slots, @expanders, $disk, %ea );
		$v = \%{$data->{Enclosures}->{$key}};
	  $vv = \%{$v->{"Element types"}->{"Array device slot"}};
		$slots = $vv->{"possible elements"};
		@expanders = grep {&Lgl::start_with($_,"/dev/smp/expd") } @{$v->{"devices"}};
	  for (my $slot=0; $slot <= $slots-1; $slot++) {
			$ea{$slot} = {};
			foreach my $expander (@expanders) {
				$vv = \%{$data->{EnclosureDevices}->{$expander}};
			  my $a = $vv->{address};
				$ea{$slot}{$a} = {}; 
				$vv = \%{$data->{Addresses}->{$a}};
				$ea{$slot}{$a}{'es'} = $vv->{es};
			}
		}
		$vv = \%{$data->{Addresses}};
		foreach (%{$data->{Disks}}) {
		  $disk = \%{$data->{Disks}->{$_}};
			next if ($disk->{"enclosure"} ne $key);
			foreach my $port (@{$disk->{"ports"}}) {
				my $slot = $disk->{slot};
				my $asa = $vv->{$port}->{'attached to'}; 
				$ea{$slot}{$asa}{address} = $port;
				$ea{$slot}{$asa}{device} = $disk->{device};
			}
	  }
	
		my $i=0;	
		print &ui_columns_start([ "Slot","SES","Expander","SAS Address","Disk","SAS Address","Expander","SES", ],100,1);
		foreach my $slot (sort {$a <=> $b} (keys(%ea))) {
			my @trow;
			push(@trow, $slot );
			$i=0;
			$v = $ea{$slot};
			foreach my $asa (sort (keys %{$v})) {
				$vv = $ea{$slot}->{$asa};
				if (exists $vv->{'device'}) {
					my $str = $vv->{'device'};
					$str =~ s/\/dev\/rdsk\///ig;
					if ($i == 0) {
						push(@trow, $vv->{'es'},$asa, $vv->{'address'}, $str);
					} else {
						push(@trow, $vv->{'address'}, $asa, $vv->{'es'} );
						}
					$i += 1;
				}
			}
			print &ui_columns_row(\@trow);
		}
		print &ui_columns_end();
  }


sub print_controllers {
  my $action = shift;
  my $hash = shift;
	my @tds = [ 'width=5' ];
  print &ui_columns_start([ $text{'Controller'}, "Manufacturer", "Model", "Firmware", "SerialNo", "Ports", "Driver", "Id"],100,1);
  foreach my $key (sort(keys %{$hash})) {  
		my $v = \%{$hash->{$key}};
		print &ui_columns_row(["<a href='$action$key'>$key</a>", $v->{manufacturer}, $v->{model}, $v->{firmwareversion}, $v->{serial}, $v->{hbaports}, $v->{drivername}, $v->{id},  ],
					\@tds);
#	print &ui_checked_columns_row(\@cols, \@tds, "d", $i->{'id'});
	}
  print &ui_columns_end();
}

sub print_enclosures {
  my $action = shift;
  my $hash = shift;
	my @tds = ["align=right","align=right","align=right","align=right","align=right","align=right","align=right",];
	my %sums;
#	print Dumper(\%$hash);
	$sums{count} = 0;
	$sums{slots} = 0;
	$sums{disks} = 0;
	$sums{capacity} = 0;

  print &ui_columns_start([ $text{'Enclosure'}, "Manufacturer", "Model", "Firmware", "Slots/Disks", "SES", "Capacity"],100,1,\@tds);
  foreach my $key (sort(keys %{$hash})) {
    my $v = \%{$hash->{$key}};
	  my $sesp = $v->{"Element types"}->{"Enclosure services device"}->{"possible elements"};
		my $sesf = grep {&Lgl::start_with($_,"/dev/es/") } @{$v->{"devices"}};
		my $vv =  \%{$hash->{$key}->{stats}};
    print &ui_columns_row(["<a href='$action$key'>$key</a>", $v->{vendor}, $v->{model}, $v->{firmware}, 
				$vv->{slots}.'/'.$vv->{disks}, ($sesp ? $sesp : "-")."/".$sesf, &nice_size($vv->{capacity}*1024*1024)  ],\@tds);
		$sums{count} += 1;
		$sums{slots} += $vv->{slots};
		$sums{disks} += $vv->{disks};
		$sums{capacity} += $vv->{capacity};
  }
  print &ui_columns_row(["Total", "", "", "", 
      $sums{slots}.'/'.$sums{disks}, "", &nice_size($sums{capacity}*1024*1024)  ],@tds);
  print &ui_columns_end();
}

sub print_disks {
  my $action = shift;
  my $hash = shift;
	my $typ = 1;
	if ($typ == 1) { 
		print &ui_columns_start([ $text{'Disk'}, "Manufacturer", "Model", "SerialNo", "Capacity", ],100,1);
	} else {
		print &ui_columns_start([ $text{'Disk'}, "Manufacturer", "Model", "Firmware", "SerialNo", "Id", "Capacity", "Slot"],100,1);
	}
  foreach my $key (sort(keys %{$hash})) {
    my $v = \%{$hash->{$key}};
    my $str = $key; 
    if (index($str, "/dev/rdsk/") != -1) {
    	$str =~ s/\/dev\/rdsk\///ig;
		}
	  if ($typ == 1) {	
	    print &ui_columns_row(["<a href='$action$key'>$str</a>", $v->{vendor}, $v->{model},$v->{serial}, &nice_size($v->{sizemb}*1024*1024),  ]);
	  } else {
		  print &ui_columns_row(["<a href='$action$key'>$str</a>", $v->{vendor}, $v->{model},"???", $v->{serial}, $v->{device}, &nice_size($v->{sizemb}*1024*1024), $v->{slot},  ]);
	  }
  }
  print &ui_columns_end();
}

sub ui_path_list {
	my $html=<<'END_HTML';
  <div id="cy"></div>
<script id="javascript" type="text/javascript">
$('#cy').cytoscape({
  style: cytoscape.stylesheet()
    .selector('node')
      .css({
        'content': 'data(name)',
        'text-valign': 'center',
        'color': 'white',
        'text-outline-width': 2,
        'text-outline-color': '#888'
      })
    .selector('edge')
      .css({
        'target-arrow-shape': 'triangle'
      })
    .selector(':selected')
      .css({
        'background-color': 'black',
        'line-color': 'black',
        'target-arrow-color': 'black',
        'source-arrow-color': 'black'
      })
    .selector('.faded')
      .css({
        'opacity': 0.25,
        'text-opacity': 0
      }),
  
  elements: {
    nodes: [
      { data: { id: 'j', name: 'Jerry' } },
      { data: { id: 'e', name: 'Elaine' } },
      { data: { id: 'k', name: 'Kramer' } },
      { data: { id: 'g', name: 'George' } }
    ],
    edges: [
      { data: { source: 'j', target: 'e' } },
      { data: { source: 'j', target: 'k' } },
      { data: { source: 'j', target: 'g' } },
      { data: { source: 'e', target: 'j' } },
      { data: { source: 'e', target: 'k' } },
      { data: { source: 'k', target: 'j' } },
      { data: { source: 'k', target: 'e' } },
      { data: { source: 'k', target: 'g' } },
      { data: { source: 'g', target: 'j' } }
    ]
  },
  
  ready: function(){
    window.cy = this;
    
    // giddy up...
    
    cy.elements().unselectify();
    
    cy.on('tap', 'node', function(e){
      var node = e.cyTarget; 
      var neighborhood = node.neighborhood().add(node);
      
      cy.elements().addClass('faded');
      neighborhood.removeClass('faded');
    });
    
    cy.on('tap', function(e){
      if( e.cyTarget === cy ){
        cy.elements().removeClass('faded');
      }
    });
  }
});

</script>
END_HTML
	print $html;
}


1;
