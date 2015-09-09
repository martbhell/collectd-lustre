#!/bin/bash
# This only runs the python script because execplugins, collectd and arguments.
if [[ $HOSTNAME == mds* ]];  then
  python /usr/local/bin/lustre-stats-wrapper-collectd.py /proc/fs/lustre/mdt/*-MDT0000/md_stats
else
  python /usr/local/bin/lustre-stats-wrapper-collectd.py /proc/fs/lustre/obdfilter/*/stats
fi
