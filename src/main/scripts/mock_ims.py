from bottle import route, run

""" Super simple IMS mock.

Just listens on localhost:8080 for the appropriate url, returns a test role and
a dummy json response.

"""

json_response = '\'{"Code": "Success", ' \
                '"AccessKeyId": "ASIAI", ' \
                '"SecretAccessKey": "oieDhF", ' \
                '"Token": "6jmePdXNehjPVt7CZ1WMkKrqB6zDc34d2vpLej", ' \
                '"Expiration": "2015-04-17T13:40:18Z", ' \
                '"Type": "AWS-HMAC"}\''

path = '/latest/meta-data/iam/security-credentials/'


@route(path)
def get_roles():
    return 'test_role'


@route(path+'<role>')
def get_credentials(role):
        return json_response if role == 'test_role' else ''


run(host='localhost', port=8080)
