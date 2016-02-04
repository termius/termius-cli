# -*- coding: utf-8 -*-
from os import urandom
from base64 import b64decode
from nose.tools import eq_, ok_, raises
from itertools import product

from serverauditor_sshconfig.cloud.client.cryptor import RNCryptor


def test_dual_encrypt_and_decrypt():
    configs = [
        config_factory(i)
        for i in ('password', 'pass', 'psswrd', 'pa$$word')
    ]
    texts = [
        'test', 'text', '',
    ]
    for config, text in product(configs, texts):
        cryptor = generate_cryptor(**config)
        yield dual_encrypt_decrypt_text, cryptor, text


def dual_encrypt_decrypt_text(cryptor, original_text):
    ciphertext = cryptor.encrypt(original_text)
    text = cryptor.decrypt(ciphertext)
    eq_(text, original_text)


def test_encrypt_and_decrypt():
    cryptor = generate_cryptor(
        '1', b64decode('wenOgffhaJ8='), b64decode('8VbldsORPa4=')
    )
    text__ciphertexts = [
        ('localhost',
         'AgHB6c6B9+Fon/FW5XbDkT2ub25WJP3rVv1e4yHAljHPbH1xn9IIqw24in73DmAihe0'
         'fEvUCObqsbPwOaD3kaj6L7W+uK03ayY6+mveto9yQqg=='),
        ('localhost',
         'AgHB6c6B9+Fon/FW5XbDkT2uMjUIJNPPUSbx++sR7leHVb0ys8vOP6s1BNCuCaf2FFm'
         'skP2XVvHAR9xolNtfWwUDLQqgO1q5hiH3bukiCLJ1cw=='),
        ('localhost',
         'AgHB6c6B9+Fon/FW5XbDkT2ub25WJP3rVv1e4yHAljHPbH1xn9IIqw24in73Dm'
         'Aihe0fEvUCObqsbPwOaD3kaj6L7W+uK03ayY6+mveto9yQqg=='),
    ]
    for text, ciphertext in text__ciphertexts:
        yield encrypt_decrypt_text, cryptor, text, ciphertext


def encrypt_decrypt_text(cryptor, original_text, original_ciphertext):
    text = cryptor.decrypt(original_ciphertext)
    ciphertext = cryptor.encrypt(text)
    eq_(text, original_text)
    ok_(ciphertext != original_ciphertext)


@raises(TypeError)
def test_encrypt_none():
    cryptor = generate_cryptor(**config_factory('pass'))
    cryptor.encrypt(None)


@raises(TypeError)
def test_decrypt_none():
    cryptor = generate_cryptor(**config_factory('pa$$'))
    cryptor.decrypt(None)


def generate_cryptor(password, encryption_salt, hmac_salt):
    cryptor = RNCryptor()
    cryptor.password = password
    cryptor.encryption_salt = encryption_salt
    cryptor.hmac_salt = hmac_salt
    return cryptor


def config_factory(password):
    return {
        'password': password,
        'encryption_salt': urandom(8),
        'hmac_salt': urandom(8),
    }
