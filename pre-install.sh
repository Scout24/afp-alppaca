#!/bin/bash
user=alppaca
logdir=/var/log/alppaca
confdir=/etc/alppaca

# add service user and group
groupadd $user 2> /dev/null || :
useradd -c "Alppaca - a local prefetch proxy for amazon credentials" -s /sbin/nologin -r -d /tmp -g $user $user 2> /dev/null || :

# Add log directory
if [ ! -d $logdir ]; then
  mkdir -p $logdir
fi

# change ownership of directory to $user
chown -R $user: $logdir

# Add the conf directory
if [ ! -d $confdir ]; then
  mkdir -p $confdir
fi

# change ownership of directory to $user
chown -R $user: $confdir