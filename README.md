# collectd-lustre
Script that outputs Lustre performance metrics in collectd format

 - the wrapper.sh script has a conditional that makes it grab the MDS metrics only if the server's hostname starts with mds*

# collectd configuration:

<pre>
LoadPlugin exec
<Plugin exec>
        Exec "nagios" "/usr/local/bin/json-stats-wrapper-collectd.sh"
</Plugin>
</pre>
