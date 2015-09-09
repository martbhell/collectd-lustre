#!/usr/bin/python

#Brock Palen
# brockp@umich.edu
#
#Modified by johan.guldmyr@csc.fi to output in collectd format.
#
# Dependencies:
# * python
# * python-simplejson
# * The json-stats-wrapper-collectd.sh which only runs:
# python json-stats-wrapper-collectd.py /proc/fs/lustre/obdfilter/*/stats
# 
# Instead of going through /proc one should use lctl get_param - future proof.
#
# Expected output:
# PUTVAL "hostname_domain_tld/lustre.fsname.OST0009.reconnect/gauge" interval=60 N:26
#
# collectd configuration:
# LoadPlugin exec
#<Plugin exec>
#        Exec "nagios" "/usr/local/bin/json-stats-wrapper-collectd.sh"
#</Plugin>


'''
Takes data in the form of:

metric         number

snapshot_time             1396141904.951010 secs.usecs
open                      28540765918 samples [reqs]
close                     10256936166 samples [reqs]
mknod                     30061 samples [reqs]

and creates a json version:
metric: number
'''

import sys
try:   #rhel5 doesn't have json
   import json
except ImportError:
   import simplejson as json

import socket
hostname = socket.gethostname().replace('.','_')

# Collectd Types: https://collectd.org/wiki/index.php/Data_source
#
# Gauge = as is
# Counter = Change (never decreasing, if so assume wrap)
#
# bytes (gauge)
bytes_list = [ "read_bytes", "write_bytes" ]
# pages (counter)
pages_list = [ "cache_miss", "cache_access", "lustrecache_hit" ]
# mdt (counter)
mdt_list = [ "open", "getattr", "close", "unlink", "setattr", "getxattr" ]
# everything else is gauge 

def dictify(filename):
    try:
        f = open(filename, 'r')
    except:
        sys.stderr.write("failed to open"+filename+"\n")
        sys.exit(-1)

    data = {'source':f.name}
    #read the strcture line at a time and build a dict out of it:
    for line in f:
      words = line.split()
      #OST's use formats where the last number is the one you want
      #read_bytes                100121201 samples [bytes] 0 1048576 54023523712987
      # Get the OST name - used in metric name
      source = data["source"].split('-')
      fspath = source[0].split('/')
      fs = fspath[5]
      s1 = source[1].split('/')
      OST = s1[0]

      metric = "PUTVAL " + '"' + hostname + "/lustre." + fs + "." + OST + "." + words[0]
      if(words[-1].isdigit()):
           data[metric] = words[-1]
      else:
           data[metric] = words[1]
    f.close()
    #print json.JSONEncoder().encode(data)
    # make it output one line at a time, and add interval= and EPOCH:value
    # PUTVAL "hostname_domain_tld/lustre.fsname.OST0009.reconnect/gauge" interval=60 N:26
    for key in data:
      if key is not "source":
        metrick = key.split('.')
        if metrick[3] in bytes_list or metrick[3] in pages_list:
          print key + "/bytes" + '" ' + "interval=60 " + "N:" + data[key]
          print key + "/counter" + '" ' + "interval=60 " + "N:" + data[key]
	elif metrick[3] in mdt_list and "MDT" in metrick[2]:
          print key + "/counter" + '" ' + "interval=60 " + "N:" + data[key]
          print key + "/gauge" + '" ' + "interval=60 " + "N:" + data[key]
	else:
          print key + "/gauge" + '" ' + "interval=60 " + "N:" + data[key]


for x in range(1, len(sys.argv)):
   filename = sys.argv[x]
   dictify(filename)
