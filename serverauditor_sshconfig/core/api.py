"""
Get connection /api/v1/terminal/connection/(int: server_id)/

{
  "color_scheme" : null,
  "created_at" : "2013-01-07T02:44:41",
  "hostname" : "U2FsdGVkX19sdEiVJfU/iyZJzyycrxWo97jexjksY+weYnqeIBCKJGd7B7AzQTmO",
  "id" : 1,
  "label" : "EC2 DB server",
  "port" : 22,
  "is_favorite" : false,
  "resource_uri" : "/api/v1/terminal/connection/1/",
  "ssh_key" : {
    "id" : 1,
    "resource_uri" : "/api/v1/ssh_key_crypt/1/"
  },
  "ssh_password" : "U2FsdGVkX1+T0TY8FmVHutXzn4ZfUq1n8kZlfS8IiEjbVqs/ZvxMqpBCv7C3lYfh",
  "ssh_username" : "U2FsdGVkX199ogQwDay6nktGUFuP2kvQF99YhXnsyatB8cBeNb4ebogjG5Tb7nMM",
  "updated_at" : "2013-01-07T02:48:25"
}

Create connection /api/v1/terminal/connection/

{
    "label": "EC2 Web server",
    "hostname": "U2FsdGVkX19LB5SpeL79/lEnWM+diX6kHGm0XtvkI1YbLt7iB6F9CWndyk3Ynv7O",
    "is_favorite" : true,
    "ssh_username": "U2FsdGVkX1+3wx7+L88SSr2AsfdOuLriPlwCJxsJHntrGZFkhZvXAoyL7JAwcqw0",
    "ssh_password": "U2FsdGVkX1/lNQma5CroJcu56HTB4ZDwqPAvY66EpXaR4adF8iXRPyahvwDCOw0T",
    "ssh_key" : 1,
    "port": 2222,
    "color_scheme": "pro"
}

HTTP/1.1 201 CREATED
Vary: Accept
Content-Type: application/json; charset=utf-8
Location: http://serverauditor/api/v1/terminal/connection/8/


########################################################################################

Get key /api/v1/terminal/ssh_key/(int: sshkey_id)/

{
  "created_at" : "2013-01-07T01:28:02",
  "id" : 2,
  "label" : "",
  "passphrase" : "nsu9nxYQwPfLyUWWhPO5lNHJtNZyRcwXJ+MSKwTQjqJijF/inY78RLY6Y7o+8npG",
  "resource_uri" : "/api/v1/terminal/ssh_key/2/",
  "updated_at" : "2013-01-07T01:28:02",
  "private_key" : "U2FsdGVkX1+hg6zEjkxi81xPXlNngPvwItnOB6127kBkukaMk9k9Hdps1AbSuQHS\r\ntrDFZFsX17HoTYNU0qrtu10mshUXwOD+exlgrbW+X0dnnEDIkSp5ZdBv9KWxw2GE\r\nXp1kIqh+/t8V1ocMxwYH5vRmUbXa6ubsSRXCZ97ka3xK2C2kX2RI8WBwa2Sks6Q4\r\nal7X9mVtDlJNls2teqT+HQnbYfZ9GL2a83stIYse/0xXEf0+G7iKzEcWVcuA9ORZ\r\nNLGiu43KOuaYsDNHDMOoRjRT4kWRfc8p6Vq4ahXR1xRWa1E9d4JxnbWaj0WT+2yd\r\nppyI4c+n2J+s+kJDwLPzhG/jefDieXvecbMhPAO5XZvB02sORd1bAtAzayajLDkc\r\nK8C/ls46YfRXumfswwnUpg5JWZNSzrql1yVCD35LCO0nCDqn+GEBrKtAEAg1adU1\r\nFJx9qFzZV3EdYpkS2aGmx/eYutTI9y8/zo3Ig+e4XG5EuQBLtJAJkco1ltRpwWYj",
  "public_key" : "U2FsdGVkX1+hg6zEjkxi81xPXlNngPvwItnOB6127kBkukaMk9k9Hdps1AbSuQHS\r\ntrDFZFsX17HoTYNU0qrtu10mshUXwOD+exlgrbW+X0dnnEDIkSp5ZdBv9KWxw2GE\r\nXp1kIqh+/t8V1ocMxwYH5vRmUbXa6ubsSRXCZ97ka3xK2C2kX2RI8WBwa2Sks6Q4\r\nal7X9mVtDlJNls2teqT+HQnbYfZ9GL2a83stIYse/0xXEf0+G7iKzEcWVcuA9ORZ\r\nNLGiu43KOuaYsDNHDMOoRjRT4kWRfc8p6Vq4ahXR1xRWa1E9d4JxnbWaj0WT+2yd\r\nppyI4c+n2J+s+kJDwLPzhG/jefDieXvecbMhPAO5XZvB02sORd1bAtAzayajLDkc\r\nK8C/ls46YfRXumfswwnUpg5JWZNSzrql1yVCD35LCO0nCDqn+GEBrKtAEAg1adU1\r\nFJx9qFzZV3EdYpkS2aGmx/eYutTI9y8/zo3Ig+e4XG5EuQBLtJAJkco1ltRpwWYj"
}

Create key /api/v1/terminal/ssh_key/

{
    "label": "my label",
    "passphrase": "U2FsdGVkX1/LKBolCxfEnITmjJZ2yF2iA0KndqjB104=",
    "private_key": "U2FsdGVkX1/2XFQFhBfJ8QPKCDlBK8urRyjYkDFr1LqQ7WCCHDHH6zSqxM2Fvevr
                   bsbpHHiNDaZwSSxpiW4S/C2vko4tFIJOTdF/r/McO8jZwnrVXzry5OLR16WHK3mN
                   nXkm6bSxBddH2tleqeGknyLad0hZx/sbG+z0MSiCJN2MO22pZbldTvyjqfwR//gl
                   ByYoJor7YOJUKwoLIymCo0V4a9rYyvietwiT646WujYxlhrAMu3nFH8xndJGqJRo
                   2RraXH0LXAOMgU/fdlNsWuo3vemRYtPkuleggszwbDlMzVqWU0GXHYRFeEURc7X5
                   pFwWXkzTYLKU5bPAN/NfUrqqvzk1dBU38WI9mdBgGhy9EOxQEUDjBj/LH+8Ss0dd
                   Lxr+A4+81abyg/ZItCIOBhfnCQQ6T+tJXl06vkEeW2T1BdNappydpCo/aT1olrjU
                   YB9q/AULVCdSJSOKZCHnacaF+/PBQlObvSzuOWT6uhIV+akaUFU4UCpKnyswwVEf",
    "public_key": "U2FsdGVkX1/2XFQFhBfJ8QPKCDlBK8urRyjYkDFr1LqQ7WCCHDHH6zSqxM2Fvevr
                  bsbpHHiNDaZwSSxpiW4S/C2vko4tFIJOTdF/r/McO8jZwnrVXzry5OLR16WHK3mN
                  nXkm6bSxBddH2tleqeGknyLad0hZx/sbG+z0MSiCJN2MO22pZbldTvyjqfwR//gl
                  ByYoJor7YOJUKwoLIymCo0V4a9rYyvietwiT646WujYxlhrAMu3nFH8xndJGqJRo
                  2RraXH0LXAOMgU/fdlNsWuo3vemRYtPkuleggszwbDlMzVqWU0GXHYRFeEURc7X5
                  pFwWXkzTYLKU5bPAN/NfUrqqvzk1dBU38WI9mdBgGhy9EOxQEUDjBj/LH+8Ss0dd
                  Lxr+A4+81abyg/ZItCIOBhfnCQQ6T+tJXl06vkEeW2T1BdNappydpCo/aT1olrjU
                  YB9q/AULVCdSJSOKZCHnacaF+/PBQlObvSzuOWT6uhIV+akaUFU4UCpKnyswwVEf"
}

HTTP/1.1 201 CREATED
Vary: Accept
Content-Type: application/json; charset=utf-8
Location: http://serverauditor/api/v1/terminal/ssh_key/3/

"""


import base64
import json
import urllib2


class API(object):

    API_URL = 'http://dev.serverauditor.com/api/v1/'

    def get_auth_key(self, username, password):
        """ Returns user's auth token. """

        request = urllib2.Request(self.API_URL + "token/auth/")
        auth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % auth)
        result = urllib2.urlopen(request)

        return json.load(result)['key']

    def get_keys_and_connections(self, username, auth_key):
        """ Gets current keys and connections.

        Sends request for getting keys and connections using username and auth_key.
        """

        auth_header = "ApiKey %s:%s" % (username, auth_key)

        request = urllib2.Request(self.API_URL + "terminal/ssh_key/?limit=100")
        request.add_header("Authorization", auth_header)
        request.add_header("Content-Type", "application/json")
        response = urllib2.urlopen(request)
        keys = json.loads(response.read())['objects']

        request = urllib2.Request(self.API_URL + "terminal/connection/?limit=100")
        request.add_header("Authorization", auth_header)
        request.add_header("Content-Type", "application/json")
        response = urllib2.urlopen(request)
        connections = json.loads(response.read())['objects']

        return keys, connections

    def create_keys_and_connections(self, hosts, username, auth_key):
        """ Creates keys and connections using hosts' configs.

        Sends request for creation keys and connections using username and key.
        """

        for host in hosts:
            auth_header = "ApiKey %s:%s" % (username, auth_key)

            # ssh_key = {
            #     'label': host['host'],
            #     'passphrase': ".",
            #     'value': host['identityfile'],
            #     'type': 'private'
            # }
            # request = urllib2.Request(self.API_URL + "terminal/ssh_key/")
            # request.add_header("Authorization", auth_header)
            # request.add_header("Content-Type", "application/json")
            # response = urllib2.urlopen(request, json.dumps(ssh_key))

            # key_number = int(response.headers['Location'].rstrip('/').rsplit('/', 1)[-1])
            connection = {
                "hostname": host['hostname'],
                "label": host['host'],
                "ssh_key": None,  # key_number,
                "ssh_password": host['password'],
                "ssh_username": host['user'],
            }
            request = urllib2.Request(self.API_URL + "terminal/connection/")
            request.add_header("Authorization", auth_header)
            request.add_header("Content-Type", "application/json")
            response = urllib2.urlopen(request, json.dumps(connection))

        return