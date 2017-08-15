# -*- coding: utf-8 -*-
"""Module with SecureCRT parser."""
from os.path import expanduser


class SecureCRTConfigParser(object):
    """SecureCRT xml parser."""

    meta_sessions = ['Default']

    @classmethod
    def parse_hosts(cls, xml):
        """Parse SecureCRT Sessions."""
        sessions = cls.get_element_by_name(
            xml.getchildren(), 'Sessions'
        ).getchildren()

        parsed_hosts = []

        for session in sessions:
            if session.get('name') not in cls.meta_sessions:
                host = cls.make_host(session)
                if not host:
                    continue

                parsed_hosts.append(host)

        return parsed_hosts

    @classmethod
    def parse_identity(cls, xml):
        """Parse SecureCRT SSH2 raw key."""
        identity = cls.get_element_by_name(
            xml.getchildren(), 'SSH2'
        )
        if identity is None:
            return None

        identity_filename = cls.get_element_by_name(
            identity.getchildren(),
            'Identity Filename V2'
        )

        if identity_filename is None:
            return None

        path = identity_filename.text.split('/')
        public_key_name = path[-1].split('::')[0]
        private_key_name = public_key_name.split('.')[0]

        if path[0].startswith('$'):
            path.pop(0)
            path.insert(0, expanduser("~"))

        path[-1] = public_key_name
        public_key_path = '/'.join(path)
        path[-1] = private_key_name
        private_key_path = '/'.join(path)

        return private_key_path, public_key_path

    @classmethod
    def make_host(cls, session):
        """Adapt SecureCRT Session to Termius host."""
        session_attrs = session.getchildren()

        hostname = cls.get_element_by_name(session_attrs, 'Hostname')
        port = cls.get_element_by_name(session_attrs, '[SSH2] Port')
        username = cls.get_element_by_name(session_attrs, 'Username')

        if not cls.check_attribute(hostname):
            return None

        return {
            'label': session.get('name'),
            'hostname': hostname.text,
            'port': port.text if cls.check_attribute(port) else '22',
            'username': username.text
            if cls.check_attribute(username) else None
        }

    @classmethod
    def check_attribute(cls, attr):
        """Check an attribute."""
        return attr is not None and attr.text

    @classmethod
    def get_element_by_name(cls, elements, name):
        """Get SecureCRT config block."""
        for element in elements:
            if element.get('name') == name:
                return element

        return None
