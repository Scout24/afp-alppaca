# alppaca
A(mazing) Local Prefetch Proxy for Amazon CredentiAls

# About

This prefeteches and proxies AWS temporary credentials from the [Instance
Metadata Server
(IMS)](https://github.com/ImmobilienScout24/aws-instance-metadata-server).

# The how the internal redirect works

An iptables rule snippet redirect ensures that all requests to IP 169.254.169.254:80 are redirected to localhost:5000.
This setup is not yet generic since the /etc/iptables.d/nat.d directory is specific to IS24.
To manually add the iptables rule, insert the following statement into your iptables config: 

```
-A OUTPUT -p tcp -i lo -d 169.254.169.254 --dport 80 -j DNAT --to 127.0.0.1:5000
```

# alppaca as a service
Upstart is our weapon of choice to initialize alppaca during the boot phase as to ensure that credentials are cached before the application starts up.


# Playing around

Start ``tmux``.

Launch the mock IMS service in one tmux window:

```
$ PYTHONPATH=src/main/python python src/main/scripts/mock_ims.py
```

Launch ``alppaca`` in another:

```
$ PYTHONPATH=src/main/python python src/main/python/alppaca/main.py
```

Use ``curl`` to perform some requests in a third one:

```
$ curl localhost:8080/latest/meta-data/iam/security-credentials/
test_role
$ curl localhost:8080/latest/meta-data/iam/security-credentials/test_role
'{"Code": "Success", "AccessKeyId": "ASIAI", "SecretAccessKey": "oieDhF", "Token": "6jmePdXNehjPVt7CZ1WMkKrqB6zDc34d2vpLej", "Expiration": "2015-04-17T13:40:18Z", "Type": "AWS-HMAC"}'
```

And watch the logging info in the other two. Also, by default the credentials
are refreshed every minute, so you should see some logging info about that.

# Descriptive Haiku
_Authentication_

_Local doesn't work for you_

_Al's now got your back_

# Schematic

![schematic](schematic.png "Schematic")
