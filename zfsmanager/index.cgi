#!/usr/bin/perl

require './zfsmanager-lib.pl';
&ReadParse();

my %conf = get_zfsmanager_config();

&ui_print_header(undef, $text{'index_title'}, '', undef, 1, 1, 0, &help_search_link('zfs, zpool', 'man', 'doc', 'google'), undef, undef, $text{'index_version'} );

# define tabs
@tabs = (
    [ 'pool', 'ZFS Pools', 'index.cgi?mode=pools' ],
    [ 'zfs', 'ZFS File Systems', 'index.cgi?mode=zfs' ],
  );
if ($conf{'list_snap'}) { push(@tabs, [ 'snapshot', 'Snapshots', 'index.cgi?mode=snapshot' ]); }
push(@tabs, [ 'ses', 'SES', 'index.cgi?mode=ses' ]);

# start tabes
# $in{'mode'} ||= 'pools';
print &ui_tabs_start(\@tabs, "mode", $in{'mode'} || $tabs[0]->[0], 1);

# start pools tab
print &ui_tabs_start_tab('mode', 'pool');
&ui_zpools_list();
#alerts
print '<h3>Alerts: </h3>', get_alerts(), "";
print &ui_tabs_end_tab('mode', 'pool');

# start zfs tab
print &ui_tabs_start_tab('mode', 'zfs');
&ui_zfs_list();
print &ui_tabs_end_tab('mode', 'zfs');

# start snapshots tab
if ($conf{'list_snap'}) {
  print &ui_tabs_start_tab('mode', 'snapshot');
  &ui_snapshot_list();
  print &ui_tabs_end_tab('mode', 'snapshot');
}

# start disks tab
print &ui_tabs_start_tab('mode', 'ses');
&ui_ses_list();
print &ui_tabs_end_tab('mode', 'ses');

# end tabs
print &ui_tabs_end(1);

&ui_print_footer('/', $text{'index'});
