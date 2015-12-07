=======
alppaca
=======

.. image:: https://travis-ci.org/ImmobilienScout24/alppaca.png?branch=master
   :alt: Travis build status image
   :target: https://travis-ci.org/ImmobilienScout24/alppaca

.. image:: https://coveralls.io/repos/ImmobilienScout24/alppaca/badge.png?branch=master
    :alt: Coverage status
    :target: https://coveralls.io/r/ImmobilienScout24/alppaca?branch=master

A(mazing) Local Prefetch Proxy for Amazon CredentiAls

About
=====

This prefeteches and proxies AWS temporary credentials from the
`AWS Federation Proxy
(AFP) <https://github.com/ImmobilienScout24/afp-core>`__.

On any Amazon EC2 instance there is a special webserver that listens on
a link-local address and provides so-called `Instance
Metadata <http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html>`__.
When running applications on servers inside a private cloud that should
authenticate against AWS, this metadata server isn't available. Hence,
we have to build a bridge into AWS to provide temporary credentials for
that application, so that it believes it is being executed in the cloud
even though it is not. The first part of that bridge is the
aforementioned IMS which connects the private cloud to AWS. The second
part is alppaca, pre-fetches the credentials for an application via the
IMS, caches them locally in memory and exposes them via a HTTP service
on the same server as the application. The main reason for pre-fetching
and caching is to ensure a response time below one second, which is the
AWS-SDK default. The webservice listens on ``localhost:25772`` and an
iptables rule is used to have it serve requests on
``169.254.169.254:80``. It is up to the IMS to decide which account and
role to use in order to obtain temporary credentials for the
application/server.

Schematic
=========

.. figure:: schematic.png
   :alt: Schematic

   schematic

Integration
===========

Configuration
-------------

You can change the following values in ``/etc/alppaca/config.yaml`` to modify
alppacas behaviour. You can also add more yaml files to the directory, they
are loaded and merged in alphabetical order by yamlreader.

.. code:: yaml

  # Set Instance Metadata Service host, port and protocol for e.g. AFP
  ims_host: 'localhost'
  ims_port: 8080
  ims_protocol: 'https'

  # Bind to the following address.
  # Use these settings if no iptables is used:
  # bind_ip: 169.254.169.254
  # bind_port: 80
  bind_ip: 127.0.0.1
  bind_port: 25772
  
  # Possible log levels are debug, info, warning (default), error
  log_level: warning 
  # Import Python logging handler and configure.
  # Uses syslog by default.
  logging_handler:
    'module': 'logging.handlers'
    'class': 'SysLogHandler'
    'args': []
    'kwargs':
      'address': '/dev/log'

Source: ``src/main/python/resources/example_config.yaml``

iptables configuration
----------------------

When you can't bind your application on port 80 you can use this iptables rule snippet that ensures that all requests to IP
``169.254.169.254:80`` are redirected to ``localhost:25772``. You can use the
following statement in your iptables config:

::

    iptables -t nat -A OUTPUT -d 169.254.169.254/32 -p tcp -m addrtype --src-type LOCAL -j DNAT --to-destination 127.0.0.1:25772

alppaca as a service
--------------------

Find the init script in the ``/etc/init.d`` directory and start the alppaca
service with ``sudo service alppaca start``.

Usage of the init script: ``alppaca <start|restart|stop|status>``

Playing around
==============

Start ``tmux``.

Launch the mock IMS service in one tmux window:

::

    $ PYTHONPATH=src/main/python python src/main/scripts/alppaca-server-mock

Launch ``alppaca`` in another:

::

    $ PYTHONPATH=src/main/python python src/main/scripts/alppacad -c src/main/python/resources/example_config.yaml

Use ``curl`` to perform some requests in a third one:

::

    $ curl localhost:25772/latest/meta-data/iam/security-credentials/
    test_role
    $ curl localhost:25772/latest/meta-data/iam/security-credentials/test_role
    '{"Code": "Success", "AccessKeyId": "ASIAI", "SecretAccessKey": "oieDhF", "Token": "6jmePdXNehjPVt7CZ1WMkKrqB6zDc34d2vpLej", "Expiration": "2015-04-17T13:40:18Z", "Type": "AWS-HMAC"}'

And watch the logging info in the other two. Also, by default the
credentials are refreshed every minute, so you should see some logging
info about that.

Descriptive Haiku
=================

*Authentication*

*Local doesn't work for you*

*Al's now got your back*

See also
========

See Hologram_ for another solution that brings temporary AWS credentials onto Developer desktops.

.. _Hologram: https://github.com/AdRoll/hologram

License
=======

Copyright 2015 Immobilienscout24 GmbH

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

::

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
