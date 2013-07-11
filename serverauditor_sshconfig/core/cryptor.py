#!/usr/bin/env python
# coding: utf-8

"""
Copyright (c) 2013 Crystalnix.
License BSD, see LICENSE for more details.
"""

from __future__ import print_function

import base64
import hashlib
import hmac

from Crypto import Hash
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Protocol import KDF

from .utils import bchr, bord, to_bytes, to_str


class CryptorException(Exception):
    pass


class RNCryptor(object):

    AES_BLOCK_SIZE = AES.block_size
    AES_MODE = AES.MODE_CBC
    SALT_SIZE = 8

    def pre_decrypt_data(self, data):
        data = to_bytes(data)
        return base64.decodestring(data)

    def post_decrypt_data(self, data):
        """ Removes useless symbols which appear over padding for AES (PKCS#7). """

        data = data[:-bord(data[-1])]
        return to_str(data)

    def decrypt(self, data, password):
        data = self.pre_decrypt_data(data)
        password = to_bytes(password)

        n = len(data)

        version = data[0]
        options = data[1]
        encryption_salt = data[2:10]
        hmac_salt = data[10:18]
        iv = data[18:34]
        cipher_text = data[34:n - 32]
        hmac = data[n - 32:]

        encryption_key = self._pbkdf2(password, encryption_salt)
        hmac_key = self._pbkdf2(password, hmac_salt)

        if self._hmac(hmac_key, data[:n - 32]) != hmac:
            raise CryptorException("Bad data")

        decrypted_data = self._aes_decrypt(encryption_key, iv, cipher_text)

        return self.post_decrypt_data(decrypted_data)

    def pre_encrypt_data(self, data):
        """ Does padding for the data for AES (PKCS#7). """

        data = to_bytes(data)
        rem = self.AES_BLOCK_SIZE - len(data) % self.AES_BLOCK_SIZE
        return data + bchr(rem) * rem

    def post_encrypt_data(self, data):
        data = base64.encodestring(data)
        return to_str(data)

    def encrypt(self, data, password):
        data = self.pre_encrypt_data(data)
        password = to_bytes(password)

        encryption_salt = self.encryption_salt
        encryption_key = self._pbkdf2(password, encryption_salt)

        hmac_salt = self.hmac_salt
        hmac_key = self._pbkdf2(password, hmac_salt)

        iv = self.iv
        cipher_text = self._aes_encrypt(encryption_key, iv, data)

        version = b'\x02'
        options = b'\x01'

        new_data = b''.join([version, options, encryption_salt, hmac_salt, iv, cipher_text])
        encrypted_data = new_data + self._hmac(hmac_key, new_data)

        return self.post_encrypt_data(encrypted_data)

    @property
    def encryption_salt(self):
        return self._encryption_salt

    @encryption_salt.setter
    def encryption_salt(self, value):
        self._encryption_salt = value

    @property
    def hmac_salt(self):
        Random.atfork()
        return Random.new().read(self.SALT_SIZE)

    @hmac_salt.setter
    def hmac_salt(self, value):
        raise NotImplementedError()

    @property
    def iv(self):
        return self._iv

    @iv.setter
    def iv(self, value):
        self._iv = value

    def _aes_encrypt(self, key, iv, text):
        return AES.new(key, self.AES_MODE, iv).encrypt(text)

    def _aes_decrypt(self, key, iv, text):
        return AES.new(key, self.AES_MODE, iv).decrypt(text)

    def _hmac(self, key, data):
        return Hash.HMAC.new(key, data, Hash.SHA256).digest()

    def _pbkdf2(self, password, salt, iterations=10000, key_length=32):
        return KDF.PBKDF2(password, salt, dkLen=key_length, count=iterations,
                          prf=lambda p, s: hmac.new(p, s, hashlib.sha1).digest())

        ## django 1.5 version -- faster than crypto version
        # import hashlib
        # from django.utils.crypto import pbkdf2
        # return pbkdf2(password, salt, iterations, dklen=key_length, digest=hashlib.sha1)

        ## passlib version -- the fastest version
        # from passlib.utils.pbkdf2 import pbkdf2
        # return pbkdf2(password, salt, iterations, key_length)


def main():
    from time import time

    cryptor = RNCryptor()
    cryptor.encryption_salt = b'1' * 8
    cryptor.iv = b'2' * 16

    passwords = 'p@s$VV0Rd', 'пароль'
    texts = 'www.crystalnix.com', 'текст', '', '1' * 16, '2' * 15, '3' * 17

    for password in passwords:
        for text in texts:
            print('text: "{}"'.format(text))

            s = time()
            encrypted_data = cryptor.encrypt(text, password)
            print('encrypted {}: "{}"'.format(time() - s, encrypted_data))

            s = time()
            decrypted_data = cryptor.decrypt(encrypted_data, password)
            print('decrypted {}: "{}"\n'.format(time() - s, decrypted_data))

            assert text == decrypted_data


if __name__ == '__main__':

    main()