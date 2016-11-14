#!/usr/bin/perl

require './zfsmanager-lib.pl';
ReadParse();
use Data::Dumper;
%conf = get_zfsmanager_config();

#show pool status
if ($in{'pool'})
{
  ui_print_header(undef, $text{'status_title'}." ".$in{'pool'}, "", undef, 1, 1);

  my %status = zpool_status($in{'pool'});
  my $root = (sort keys %status)[0];

  #-- status table --
  print ui_hidden_table_start('Status', "width=100%", 1,'zpool_status', 1);
  print ui_table_row("Scan:", $status{$root}{scan});
  print ui_table_row("Errors:", $status{$root}{errors});
  ui_zpool_status($in{'pool'});

  if (exists $status{$root}{status} || exists $status{$root}{action} || exists $status{$root}{see}) {
  #  print ui_table_start("Attention", "width=100%", "1");
    print '<h3>Attention</h3>';
    if (exists $status{$root}{status}) { print ui_table_row("Status:", $status{$root}{status}); }
    if (exists $status{$root}{action}) { print ui_table_row("Action:", $status{$root}{action}); }
    if (exists $status{$root}{see})    { print ui_table_row("See:",    $status{$root}{see}); }
  #  print ui_table_end();
  }
  print '<h4>Alerts: </h4>', get_alerts($in{'pool'}), "";
  print ui_hidden_table_end('zpool_status');

  #-- properties table --
  print ui_hidden_table_start('Properties', "width=100%", 4,'zpool_properties', 1);
  ui_zpool_properties($in{'pool'});
  print ui_hidden_table_end('zpool_properties');

  #-- tasks table --
  print ui_hidden_table_start('Tasks', 'width=100%', 1,'zpool_tasks',1, ['align=left'] );
  if ($conf{'zfs_properties'}) {
    print ui_table_row("New file system: ", "<a href='create.cgi?create=zfs&parent=$in{pool}'>Create file system</a>");
    #print ui_table_row('Export ',  "<a href='cmd.cgi?cmd=export&pool=$in{pool}'>Export pool</a>");
  }
  if ($conf{'pool_properties'}) {
    if ($status{$root}{scan} =~ /scrub in progress/) { print ui_table_row('Scrub ',"<a href='cmd.cgi?cmd=scrub&stop=y&pool=$in{pool}'>Stop scrub</a>"); }
    else { print ui_table_row('Scrub ', "<a href='cmd.cgi?cmd=scrub&pool=$in{pool}'>Scrub pool</a>");}
    print ui_table_row('Upgrade ', "<a href='cmd.cgi?cmd=upgrade&pool=$in{pool}'>Upgrade pool</a>");
    print ui_table_row('Export ',  "<a href='cmd.cgi?cmd=export&pool=$in{pool}'>Export pool</a>");
  }
  if ($conf{'pool_destroy'}) { print ui_table_row("Destroy ", "<a href='cmd.cgi?cmd=pooldestroy&pool=$in{pool}'>Destroy this pool</a>"); }
  print ui_hidden_table_end('zpool_tasks');

  #-- zfs table --
  print ui_hidden_table_start('ZFS File Systems and Datasets', "width=100%", 1,'zpool_zfs', 1);
  %zfs = list_zfs("-r ".$in{'pool'});
  print_zfs("status.cgi?zfs=",\%zfs);
  print ui_hidden_table_end('zpool_zfs');

  #-- vdev table--
  print ui_hidden_table_start('Virtual Devices', 'width=100%', 5,'zpool_vdevs',0 );
  print ui_columns_header([ "Virtual Device", "State", "Read", "Write", "Cksum" ]);
  foreach $key (sort keys %status)
  {
    if ($key eq $root) {
      print ui_columns_row([$status{$key}{name}, $status{$key}{state}, $status{$key}{read}, $status{$key}{write}, $status{$key}{cksum}]);
    } elsif ($status{$key}{parent} =~ /pool/ && $key ne $root) {
      print ui_columns_row(["<a href='config-vdev.cgi?pool=".$in{'pool'}.'&dev='.$key."'>_".$status{$key}{name}."</a>", 
					$status{$key}{state}, $status{$key}{read}, $status{$key}{write}, $status{$key}{cksum}]);
    } else {
      print ui_columns_row(["<a href='config-vdev.cgi?pool=".$in{'pool'}.'&dev='.$key."'>__".$status{$key}{name}."</a>", 
					$status{$key}{state}, $status{$key}{read}, $status{$key}{write}, $status{$key}{cksum}]);
    }
  }
  print ui_columns_end();
  print ui_hidden_table_end('zpool_vdevs');
  ui_print_footer('', $text{'index_return'});
  return; 
}

#show filesystem status
if ($in{'zfs'})
{
  ui_print_header(undef, "ZFS File System"." ".$in{'zfs'}, "", undef, 1, 1);

  #-- properties table --
  print ui_hidden_table_start('Properties', "width=100%", 4,'zfs_properties', 1);
  ui_zfs_properties($in{'zfs'});
  print ui_hidden_table_end('zfs_properties');

  #-- tasks table --
  print ui_hidden_table_start('Tasks', 'width=100%', 1,'zfs_tasks',1, ['align=left'] );
  if ($conf{'snap_properties'}) { print ui_table_row("Snapshot: ", ui_snapshot_create($in{'zfs'})); }
  if ($conf{'zfs_properties'}) {
    #print ui_table_row("New file system: ", ui_popup_link('Create child file system', "create.cgi?create=zfs&parent=$in{'zfs'}"));
    print ui_table_row("New file system: ", "<a href='create.cgi?create=zfs&parent=".$in{'zfs'}."'>Create child file system</a>");
    if (index($in{'zfs'}, '/') != -1) { print ui_table_row("Rename: ", "<a href='create.cgi?rename=".$in{'zfs'}."'>Rename ".$in{'zfs'}."</a>"); }
    if ($hash{$in{'zfs'}}{origin}) { print ui_table_row("Promote: ", "This file system is a clone, <a href='cmd.cgi?cmd=promote&zfs=$in{zfs}'>promote $in{zfs}</a>"); }
  }
  if ($conf{'zfs_destroy'}) { print ui_table_row("Destroy: ", "<a href='cmd.cgi?cmd=zfsdestroy&zfs=$in{zfs}'>Destroy this file system</a>"); }
  print ui_hidden_table_end('zfs_tasks');

  #-- snapshot table --
  print ui_hidden_table_start('Snapshots & Clones', "width=100%", 1,'zfs_snapshot', 0);
  #show list of snapshots based on filesystem
  ui_snapshot_list('-rd1 '.$in{'zfs'});
  print ui_hidden_table_end('zfs_snapshot');

  ui_print_footer('index.cgi?mode=zfs', $text{'zfs_return'});
  return;
}

#show snapshot status
#show status of current snapshot
if ($in{'snap'})
{
  ui_print_header(undef, $text{'snapshot_title'}, "", undef, 1, 1);

# TODO: depends on the other TODOs
  my $zfs = $in{'snap'};
  $zfs =~ s/\@.*//;

  #-- properties table --
  print ui_hidden_table_start('Properties', "width=100%", 4,'zfs_properties', 1);
  ui_zfs_properties($in{'snap'});
  print ui_hidden_table_end('zfs_properties');

  #-- tasks table --
  print ui_hidden_table_start('Tasks', 'width=100%', 1,'zfs_snap_tasks',1, ['align=left'] );
  print ui_table_row('Differences', "<a href='diff.cgi?snap=$in{snap}'>Show differences in $in{'snap'}</a>");
  if ($conf{'snap_properties'}) {
# TODO: check usability
    print ui_table_row("Snapshot: ", ui_snapshot_create($zfs));
    print ui_table_row("Rename: ", "<a href='create.cgi?rename=".$in{'snap'}."'>Rename ".$in{'snap'}."</a>");
  }
  if ($conf{'zfs_properties'}) {
    print ui_table_row('Clone:', "<a href='create.cgi?clone=$in{snap}'>Clone $in{'snap'} to new file system</a>");
  }
  if ($conf{'snap_properties'} && $conf{'zfs_properties'}) {
# TODO: $zfs and $in{'snap') is the same snapshot 
    print ui_table_row('Rollback:', "Rollback $zfs to $in{'snap'}");
  }
  if ($conf{'snap_destroy'}) { print ui_table_row('Destroy:',"<a href='cmd.cgi?cmd=snpdestroy&snapshot=$in{snap}'>Destroy snapshot</a>", ); }
  print ui_hidden_table_end('zfs_snap_tasks');

  #-- snapshot table --
  print ui_hidden_table_start('Snapshots & Clones', "width=100%", 1,'zfs_snap_snapshot', 0);
  #show list of snapshots based on filesystem
  ui_snapshot_list('-rd1 '.$in{'snap'});
  print ui_hidden_table_end('zfs_snap_shanpshot');

  if ($conf{'list_snap'}) { 
    ui_print_footer('index.cgi?mode=snapshot', $text{'snapshot_return'}); } else { ui_print_footer('index.cgi?mode=zfs', $text{'zfs_return'}); 
  }
  return;
}

