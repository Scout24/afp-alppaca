#!/bin/bash

# add alpacca to chkconfig
/sbin/chkconfig --add alppaca

# set alppaca to autostart
/sbin/chkconfig alppaca on

# Move old pid file to new place. This can be removed later on
if [ -f /tmp/alppaca.pid ] && kill -0 $(cat /tmp/alppaca.pid); then
  mv /tmp/alppaca.pid /var/run/alppacad/alppacad.pid
fi

# Restart Service if running
if service alppaca status; then
  service alppaca restart
fi
