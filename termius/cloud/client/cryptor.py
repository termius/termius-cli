# -*- coding: utf-8 -*-
"""Module with cryptor implementation."""
from __future__ import print_function

import os
import base64
import hashlib
import hmac as python_hmac
import binascii
import operator

from cached_property import cached_property
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from ...core.utils import bord, to_bytes, to_str
from ...core.exceptions import TermiusException


class CryptorException(TermiusException):
    """Raise cryptor face some problem with encrypting and decrypting."""


class CryptoSettings(object):
    """Store cryptor settings."""

    backend = default_backend()
    AES_BLOCK_SIZE = algorithms.AES.block_size
    SALT_SIZE = 8

    def __init__(self):
        """Construct new cryptor settings."""
        self._password = None
        self._encryption_salt = None
        self._hmac_salt = None

    @property
    def password(self):
        """Get password."""
        return self._password

    @password.setter
    def password(self, value):
        """Set password."""
        self._password = to_bytes(value)

    @property
    def encryption_salt(self):
        """Get salt for encryption key."""
        return self._encryption_salt

    @encryption_salt.setter
    def encryption_salt(self, value):
        """Set salt for encryption key."""
        self._encryption_salt = to_bytes(value)

    @property
    def hmac_salt(self):
        """Get salt for hmac key."""
        return self._hmac_salt

    @hmac_salt.setter
    def hmac_salt(self, value):
        """Set salt for hmac key."""
        self._hmac_salt = to_bytes(value)

    @property
    def initialization_vector(self):
        """Generate random bytes."""
        return os.urandom(int(self.AES_BLOCK_SIZE / 8))

    @cached_property
    def encryption_key(self):
        """Get encryption key."""
        return self.pbkdf2(self.password, self.encryption_salt)

    @cached_property
    def hmac_key(self):
        """Get hmac key."""
        return self.pbkdf2(self.password, self.hmac_salt)

    def pbkdf2(self, password, salt, iterations=10000, key_length=32):
        """Generate key."""
        key_generator = PBKDF2HMAC(
            algorithm=hashes.SHA1, length=key_length,
            salt=salt, iterations=iterations,
            backend=self.backend
        )
        return key_generator.derive(password)

    def get_cipher(self, initialization_vector):
        """Generate cipher for AES algorithm."""
        cipher = Cipher(
            algorithms.AES(self.encryption_key),
            modes.CBC(initialization_vector),
            backend=self.backend
        )
        return cipher


class RNCryptor(CryptoSettings):
    """RNCryptor is a symmetric-key encryption schema.

    NB. You must set encryption_salt, hmac_salt and password
    after creation of RNCryptor's instance.
    """

    encryptor = operator.methodcaller('encryptor')
    decryptor = operator.methodcaller('decryptor')

    bad_encrypted_exception = CryptorException

    def decrypt(self, data):
        """Decrypt data."""
        return self.unsafe_decrypt(data)

    def unsafe_decrypt(self, data):
        """Decrypt data."""
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
            raise CryptorException('Bad encryption salt or hmac salt!')

        hmac_key = self.hmac_key

        if self._hmac(hmac_key, data[:length - 32]) != hmac:
            raise CryptorException('Bad data!')

        decrypted_data = self._aes_decrypt(initialization_vector, cipher_text)

        return self.post_decrypt_data(decrypted_data)

    # pylint: disable=no-self-use
    def pre_decrypt_data(self, data):
        """Patch ciphertext."""
        try:
            data = to_bytes(data)
            return base64.b64decode(data)
        except (TypeError, binascii.Error):
            raise CryptorException('Can not decode cipher text!')

    # pylint: disable=no-self-use
    def post_decrypt_data(self, data):
        """Remove useless symbols.

        Its appear over padding for AES (PKCS#7).
        """
        data = data[:-bord(data[-1])]
        return to_str(data)

    def encrypt(self, data):
        """Encrypt data."""
        data = self.pre_encrypt_data(data)

        encryption_salt = self.encryption_salt

        hmac_salt = self.hmac_salt
        hmac_key = self.hmac_key

        initialization_vector = self.initialization_vector
        cipher_text = self._aes_encrypt(initialization_vector, data)

        version = b'\x03'
        options = b'\x01'

        new_data = b''.join([
            version, options,
            encryption_salt, hmac_salt,
            initialization_vector, cipher_text
        ])
        encrypted_data = new_data + self._hmac(hmac_key, new_data)

        return self.post_encrypt_data(encrypted_data)

    # pylint: disable=no-self-use
    def pre_encrypt_data(self, data):
        """Do padding for the data for AES (PKCS#7)."""
        data = to_bytes(data)

        padder = padding.PKCS7(self.AES_BLOCK_SIZE).padder()
        padded_data = padder.update(data) + padder.finalize()
        return padded_data

    # pylint: disable=no-self-use
    def post_encrypt_data(self, data):
        """Patch ciphertext."""
        data = base64.b64encode(data)
        return to_str(data)

    def _aes_encrypt(self, *args):
        return self._aes_process(self.encryptor, *args)

    def _aes_decrypt(self, *args):
        return self._aes_process(self.decryptor, *args)

    def _aes_process(self, get_operation, initialization_vector, data):
        operation = get_operation(self.get_cipher(initialization_vector))
        return operation.update(data) + operation.finalize()

    def _hmac(self, key, data):
        return python_hmac.new(key, data, hashlib.sha256).digest()
