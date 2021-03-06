=======
AFP-alppaca
=======

.. image:: https://travis-ci.org/ImmobilienScout24/afp-alppaca.png?branch=master
   :alt: Travis build status image
   :target: https://travis-ci.org/ImmobilienScout24/afp-alppaca

.. image:: https://coveralls.io/repos/ImmobilienScout24/afp-alppaca/badge.svg?branch=master
    :alt: Coverage status
    :target: https://coveralls.io/r/ImmobilienScout24/afp-alppaca?branch=master

.. image:: https://landscape.io/github/ImmobilienScout24/afp-alppaca/master/landscape.svg?style=flat
   :target: https://landscape.io/github/ImmobilienScout24/afp-alppaca/master
   :alt: Code Health


A(mazing) Local Prefetch Proxy for Amazon CredentiAls (using AFP)

About
=====

This prefetches and proxies AWS temporary credentials from the
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
part is alppaca, which pre-fetches the credentials for an application via the
IMS, caches them locally in memory and exposes them via a HTTP service
on the same server as the application. The main reason for pre-fetching
and caching is to ensure a response time below one second, which is the
AWS-SDK default timeout. The webservice listens on ``localhost:25772`` and an
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
alppaca's behaviour. You can also add more yaml files to the directory, they
are loaded and merged in alphabetical order by yamlreader.

.. code:: yaml

  ## Set Instance Metadata Service host, port and protocol for e.g. AFP
  ims_host: 'localhost'
  ims_port: 8080
  ims_protocol: 'http'

  ## Bind to the following address.
  bind_ip: 127.0.0.1
  bind_port: 25772
  ## Use these settings if no iptables is used:
  # bind_ip: 169.254.169.254
  # bind_port: 80

  ## Possible log levels are debug, info, warning (default), error
  log_level: warning

  ## Example for filelogging:
  log_format: '%(asctime)s [%(levelname)s] %(message)s'

  ## Import Python logging handler and configure.
  logging_handler:
    module: logging.handlers
    class: WatchedFileHandler
    args: [/var/log/alppaca.log]

  ## Allows to automatically switch to another role
  # assume_role: arn:aws:iam::123456789012:role/demoRole

  ## Proxy settings for assume_role call to aws
  # aws_proxy_host: my_proxy.local
  # aws_proxy_port: 3128
  ## Connect to specified region for assume_role call
  # aws_region: eu-central-1

  ## Drop privileges and run with this user and group
  # instead of user nobody you can use alpacca/alpacca
  user: nobody
  group: nobody

Full Source: ``src/main/python/resources/example_config.yaml``

iptables configuration
----------------------

When you can't bind your application on port 80 you can use this iptables rule snippet that ensures that all requests to IP
``169.254.169.254:80`` are redirected to ``localhost:25772``. You can use the
following statement in your iptables config::

    iptables -t nat -A OUTPUT -d 169.254.169.254/32 -p tcp -m addrtype --src-type LOCAL -j DNAT --to-destination 127.0.0.1:25772

alppaca as a service
--------------------

Find the init script in the ``/etc/init.d`` directory and start the alppaca
service with ``sudo service alppaca start``.

Usage of the init script: ``alppaca <start|restart|stop|status>``

set alppaca to assume a different role
--------------------------------------
You can configure alppaca to issue an assume_role API call using the configuration.
This can be useful when you want to assume the role of another account::

  assume_role: arn:aws:iam::123456789012:role/demoRole

In case a proxy is required in order to connect to AWS, use this config::

  aws_proxy_host: my_proxy.local
  aws_proxy_port: 3128


Quickstart - Playing around
===========================

If you do not want to install the dependencies system wide, use `virtualenv <http://virtualenv.readthedocs.org/en/latest/>`__ and `pybuilder <https://pybuilder.github.io/>`__.

Launch the mock IMS service in one terminal::

    $ PYTHONPATH=src/main/python python src/main/scripts/alppaca-server-mock

Launch ``alppaca`` in another::

    $ sudo PYTHONPATH=src/main/python python src/main/scripts/alppacad start -c src/main/python/resources/example_config.yaml

You need to be root (or use sudo) to start the alppaca as a deamon.

Use ``curl`` to perform some requests in a third one::

    $ curl localhost:25772/latest/meta-data/iam/security-credentials/
    test_role
    $ curl localhost:25772/latest/meta-data/iam/security-credentials/test_role
    '{"Code": "Success", "AccessKeyId": "ASIAI", "SecretAccessKey": "oieDhF", "Token": "6jmePdXNehjPVt7CZ1WMkKrqB6zDc34d2vpLej", "Expiration": "2015-04-17T13:40:18Z", "Type": "AWS-HMAC"}'

And watch the request logging in the other two terminals and in your syslog. Also, by default the
credentials are refreshed every minute, so you should see some logging
info about that.

Descriptive Haiku
=================

*Authentication*

*Local doesn't work for you*

*Al's now got your back*

See also
========

See Hologram_ for another solution that brings temporary AWS credentials onto Developer desktops. Metadataproxy_ is a solution to provide IAM credentials to docker containers.

.. _Hologram: https://github.com/AdRoll/hologram
.. _Metadataproxy: https://github.com/lyft/metadataproxy

License
=======

Copyright 2015 Immobilien Scout GmbH

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at::

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
