# coding: utf-8

from __future__ import print_function

import base64
import hashlib
import hmac as python_hmac

from Crypto.Cipher import AES
from Crypto.Protocol import KDF
from Crypto import Random

from ..core.utils import bchr, bord, to_bytes, to_str


class CryptorException(Exception):
    pass


class RNCryptor(object):
    """RNCryptor is a symmetric-key encryption schema.

    NB. You must set encryption_salt, hmac_salt and password
    after creation of RNCryptor's instance.
    """

    AES_BLOCK_SIZE = AES.block_size
    AES_MODE = AES.MODE_CBC
    SALT_SIZE = 8

    def __init__(self):
        self._password = None
        self._encryption_salt = None
        self._hmac_salt = None
        self._encryption_key = None
        self._hmac_key = None

    # pylint: disable=no-self-use
    def pre_decrypt_data(self, data):
        data = to_bytes(data)
        return base64.decodestring(data)

    # pylint: disable=no-self-use
    def post_decrypt_data(self, data):
        """Remove useless symbols.

        Its appear over padding for AES (PKCS#7).
        """
        data = data[:-bord(data[-1])]
        return to_str(data)

    def decrypt(self, data):
        data = self.pre_decrypt_data(data)

        length = len(data)

        # version = data[0]
        # options = data[1]
        encryption_salt = data[2:10]
        hmac_salt = data[10:18]
        initialization_vector = data[18:34]
        cipher_text = data[34:length - 32]
        hmac = data[length - 32:]

        if ((encryption_salt != self.encryption_salt or
             hmac_salt != self.hmac_salt)):
            raise CryptorException("Bad encryption salt or hmac salt!")

        encryption_key = self.encryption_key
        hmac_key = self.hmac_key

        if self._hmac(hmac_key, data[:length - 32]) != hmac:
            raise CryptorException("Bad data!")

        decrypted_data = self._aes_decrypt(
            encryption_key, initialization_vector, cipher_text
        )

        return self.post_decrypt_data(decrypted_data)

    # pylint: disable=no-self-use
    def pre_encrypt_data(self, data):
        """Do padding for the data for AES (PKCS#7)."""
        data = to_bytes(data)
        rem = self.AES_BLOCK_SIZE - len(data) % self.AES_BLOCK_SIZE
        return data + bchr(rem) * rem

    # pylint: disable=no-self-use
    def post_encrypt_data(self, data):
        data = base64.encodestring(data)
        return to_str(data)

    def encrypt(self, data):
        data = self.pre_encrypt_data(data)

        encryption_salt = self.encryption_salt
        encryption_key = self.encryption_key

        hmac_salt = self.hmac_salt
        hmac_key = self.hmac_key

        initialization_vector = self.initialization_vector
        cipher_text = self._aes_encrypt(
            encryption_key, initialization_vector, data
        )

        version = b'\x02'
        options = b'\x01'

        new_data = b''.join([
            version, options,
            encryption_salt, hmac_salt,
            initialization_vector, cipher_text
        ])
        encrypted_data = new_data + self._hmac(hmac_key, new_data)

        return self.post_encrypt_data(encrypted_data)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = to_bytes(value)

    @property
    def encryption_salt(self):
        return self._encryption_salt

    @encryption_salt.setter
    def encryption_salt(self, value):
        self._encryption_salt = to_bytes(value)

    @property
    def hmac_salt(self):
        return self._hmac_salt

    @hmac_salt.setter
    def hmac_salt(self, value):
        self._hmac_salt = to_bytes(value)

    @property
    def initialization_vector(self):
        return Random.new().read(self.AES_BLOCK_SIZE)

    @property
    def encryption_key(self):
        if not getattr(self, '_encryption_key', None):
            self._encryption_key = self._pbkdf2(
                self.password, self.encryption_salt
            )
        return self._encryption_key

    @property
    def hmac_key(self):
        if not getattr(self, '_hmac_key', None):
            self._hmac_key = self._pbkdf2(self.password, self.hmac_salt)
        return self._hmac_key

    def _aes_encrypt(self, key, initialization_vector, text):
        return AES.new(key, self.AES_MODE, initialization_vector).encrypt(text)

    def _aes_decrypt(self, key, initialization_vector, text):
        return AES.new(key, self.AES_MODE, initialization_vector).decrypt(text)

    def _hmac(self, key, data):
        return python_hmac.new(key, data, hashlib.sha256).digest()

    def _pbkdf2(self, password, salt, iterations=10000, key_length=32):
        return KDF.PBKDF2(password, salt, dkLen=key_length, count=iterations,
                          prf=preudorandom)


def preudorandom(password, salt):
    return python_hmac.new(password, salt, hashlib.sha1).digest()
