# -*- coding: utf-8 -*-
"""
pbkdf2
~~~~~~

This module implements pbkdf2 for Python. It also has some basic
tests that ensure that it works. The implementation is straightforward
and uses stdlib only stuff and can be easily be copy/pasted into
your favourite application.

Use this as replacement for bcrypt that does not need a c implementation
of a modified blowfish crypto algo.

Example usage:

>>> pbkdf2_hex('what i want to hash', 'the random salt')
'fa7cc8a2b0a932f8e6ea42f9787e9d36e592e0c222ada6a9'

How to use this:

1. Use a constant time string compare function to compare the stored hash
with the one you're generating::

def safe_str_cmp(a, b):
if len(a) != len(b):
return False
rv = 0
for x, y in izip(a, b):
rv |= ord(x) ^ ord(y)
return rv == 0

2. Use `os.urandom` to generate a proper salt of at least 8 byte.
Use a unique salt per hashed password.

3. Store ``algorithm$salt:costfactor$hash`` in the database so that
you can upgrade later easily to a different algorithm if you need
one. For instance ``PBKDF2-256$thesalt:10000$deadbeef...``.


:copyright: (c) Copyright 2011 by Armin Ronacher.
:license: BSD, see LICENSE for more details.
"""
import hmac
import hashlib
from struct import Struct
from operator import xor
from itertools import izip, starmap


_pack_int = Struct('>I').pack


def pbkdf2_hex(data, salt, iterations=1000, keylen=24, hashfunc=None):
    """Like :func:`pbkdf2_bin` but returns a hex encoded string."""
    return pbkdf2_bin(data, salt, iterations, keylen, hashfunc).encode('hex')


def pbkdf2_bin(data, salt, iterations=1000, keylen=24, hashfunc=None):
    """Returns a binary digest for the PBKDF2 hash algorithm of `data`
with the given `salt`. It iterates `iterations` time and produces a
key of `keylen` bytes. By default SHA-1 is used as hash function,
a different hashlib `hashfunc` can be provided.
"""
    hashfunc = hashfunc or hashlib.sha1
    mac = hmac.new(data, None, hashfunc)
    def _pseudorandom(x, mac=mac):
        h = mac.copy()
        h.update(x)
        return map(ord, h.digest())
    buf = []
    for block in xrange(1, -(-keylen // mac.digest_size) + 1):
        rv = u = _pseudorandom(salt + _pack_int(block))
        for i in xrange(iterations - 1):
            u = _pseudorandom(''.join(map(chr, u)))
            rv = starmap(xor, izip(rv, u))
        buf.extend(rv)
    return ''.join(map(chr, buf))[:keylen]