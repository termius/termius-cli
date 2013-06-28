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

        auth_header = "ApiKey %s:%s" % (username, auth_key)

        for host in hosts:

            key_numbers = []
            for ssh_key in host['ssh_key']:
                request = urllib2.Request(self.API_URL + "terminal/ssh_key/")
                request.add_header("Authorization", auth_header)
                request.add_header("Content-Type", "application/json")
                response = urllib2.urlopen(request, json.dumps(ssh_key))
                key_numbers.append(int(response.headers['Location'].rstrip('/').rsplit('/', 1)[-1]))

            key = None
            if key_numbers:
                key = key_numbers[0]

            connection = {
                "hostname": host['hostname'],
                "label": host['host'],
                "ssh_key": key,
                "ssh_password": host['password'],
                "ssh_username": host['user'],
            }
            request = urllib2.Request(self.API_URL + "terminal/connection/")
            request.add_header("Authorization", auth_header)
            request.add_header("Content-Type", "application/json")
            response = urllib2.urlopen(request, json.dumps(connection))

        return