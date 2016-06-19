# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from os import urandom
from base64 import b64decode
from nose.tools import eq_, ok_, raises
from itertools import product
from unittest import TestCase

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


class CryptorV2Test(TestCase):

    def setUp(self):
        self.encryption_salt = b64decode('2ddhjTxwLmw=')
        self.hmac_salt = b64decode('Yx6z87fkXzo=')

    def test_decrypt_empty_value(self):
        password = 'a'
        decrypted_value = ''
        encrypted_by_ios_value = 'AgHZ12GNPHAubGMes/O35F86ZRB4uTy4AyCGVEax8dUXBQZe50jMkRckoUGrHFjkjc5jnfR2bg5aN6LWHKaXNmxJOHKi1Ok8PVEIrFEDKFKm2Q=='
        encrypted_by_web_value = 'AgHZ12GNPHAubGMes/O35F86rVUPKkH9SmPuMrcVfkrNEgwgvIIX2Q0btG44er8AphIff/2VkXYIHCsi7FiQyucMqNyzFzIJKPu8iJciQPsq/g=='
        self.perform_encryption_actions(encrypted_by_ios_value, encrypted_by_web_value, password, decrypted_value, False)

    def test_decrypt_one_byte_value(self):
        password = 'thepassword'
        decrypted_value = '01'
        encrypted_by_ios_value = 'AgHZ12GNPHAubGMes/O35F860Y1ckCCuUSW5N1AmA6pyFsItkh4l5ikyZUdcjhjeR1T/xMqD7dbzJPuzyQTzaWrpa5x42HF9DHY5dQkE0ldUxw=='
        encrypted_by_web_value = 'AgHZ12GNPHAubGMes/O35F86EcZGN9JuNHHt0/+4k6X8JEu0ppx2gq65S3Fg+ekpoR7nYSB2Rux/mV+8phnSyaoaecorZplWt+djj5VV1C0Eeg=='
        self.perform_encryption_actions(encrypted_by_ios_value, encrypted_by_web_value, password, decrypted_value, False)

    def test_decrypt_value(self):
        password = 'thepassword'
        decrypted_value = '0123456789abcdef'
        encrypted_by_ios_value = 'AgHZ12GNPHAubGMes/O35F86s0oM0Q2GPKMIq/pAgXT1qFFcjJ6JBQEnHFjTsofC9zNSdv+iBuJgXYV3V66zBHPgNtaxv1qfpip68dWVOKjJ9roPlvwtRi8m+4uhyp00Jew='
        encrypted_by_web_value = 'AgHZ12GNPHAubGMes/O35F86S7NBmtS8Ctdv0kr2jFYfN9+fMOui7s1iuZ1ErmdfXjXSxH/D4Rw3TWKVJKQDaVOMXDn/L2TbrmLt61mZSjoc2LPewVqfVNCQu3BoOA52iQc='
        self.perform_encryption_actions(encrypted_by_ios_value, encrypted_by_web_value, password, decrypted_value, False)

    def test_decrypt_value_with_space(self):
        password = 'thepassword'
        decrypted_value = '0123456789abcdef 01234567'
        encrypted_by_ios_value = 'AgHZ12GNPHAubGMes/O35F86Jrimi5HAzmODZkuLzR1veMlAqoZF6ptWYC+keaJBOi8z9ektY+0m+uSb6DiRBdbkmr6QNp9usLaokrf3roSrLpOufF6Fb4lHc8Y65jZ/8Q0='
        encrypted_by_web_value = 'AgHZ12GNPHAubGMes/O35F86gwICP/QMhS310NA/LWZiWg3ZlNPreaNMLK4P4IYF3SUqCBT6L0Dy6xAhyqdWkR2qrLUBQ4BY44OxgIkL0s2EbbjNyvufXWvxs3yBvJ9ynGk='
        self.perform_encryption_actions(encrypted_by_ios_value, encrypted_by_web_value, password, decrypted_value, False)

    def test_fail_to_decrypt_value_with_space_by_multi_byte_password(self):
        password = '中文密码'
        decrypted_value = '23456789abcdef 0123456701'
        encrypted_by_ios_value = 'AgHZ12GNPHAubGMes/O35F86KSMM0xuVMS3b/RQI/FeOFjpBQHxEKPfA+T2AIJ3QU15cbJcRC9mXagSQ0jdKh+HnUkalis3c6+WT/lPvjFLz0fQoWi6m4FSIe/rdtzvoknQ='
        encrypted_by_web_value = 'AgHZ12GNPHAubGMes/O35F86MNtvS3Wg6QPegGSBZbDac2CFPpGG48x29zQgX6fukIe+MBtI1lxqaL4fPal2crmOXpGLBCnqPyOFeJKzwhyFriyK8gZ71hPlLaOO4XvONAc='
        self.perform_encryption_actions(encrypted_by_ios_value, encrypted_by_web_value, password, decrypted_value, True)

    def test_decrypt_long_value_with_space_by_long_password(self):
        password = 'It was the best of times, it was the worst of times; it was the age of wisdom, it was the age of foolishness;'
        decrypted_value = '69 74 20 77 61 73 20 74 68 65 20 65 70 6f 63 68 20 6f 66 20 62 65 6c 69 65 66 2c 20 69 74 20 77 61 73 20 74 68 65 20 65 70 6f 63 68 20 6f 66 20 69 6e 63 72 65 64 75 6c 69 74 79 3b 20 69 74 20 77 61 73 20 74 68 65 20 73 65 61 73 6f 6e 20 6f 66 20 4c 69 67 68 74 2c 20 69 74 20 77 61 73 20 74 68 65 20 73 65 61 73 6f 6e 20 6f 66 20 44 61 72 6b 6e 65 73 73 3b 20 69 74 20 77 61 73 20 74 68 65 20 73 70 72 69 6e 67 20 6f 66 20 68 6f 70 65 2c 20 69 74 20 77 61 73 20 74 68 65 20 77 69 6e 74 65 72 20 6f 66 20 64 65 73 70 61 69 72 3b 20 77 65 20 68 61 64 20 65 76 65 72 79 74 68 69 6e 67 20 62 65 66 6f 72 65 20 75 73 2c 20 77 65 20 68 61 64 20 6e 6f 74 68 69 6e 67 20 62 65 66 6f 72 65 20 75 73 3b 20 77 65 20 77 65 72 65 20 61 6c 6c 20 67 6f 69 6e 67 20 64 69 72 65 63 74 6c 79 20 74 6f 20 48 65 61 76 65 6e 2c 20 77 65 20 77 65 72 65 20 61 6c 6c 20 67 6f 69 6e 67 20 74 68 65 20 6f 74 68 65 72 20 77 61 79 2e 0a 0a'
        encrypted_by_ios_value = 'AgHZ12GNPHAubGMes/O35F86Q5jcarOXsQZZwy/28W6cpPWrxNLZgUfc2YvmJLukJp7OuFwru3ZYSOB6VelK7nBYA0abhEhzanfSgmhTDfkJwV8D/HRVmhCL3k2NQ94wDAeX+VteyLfhlkC4XRu4UhLBvap3lbp7XXrKdMAJ5iFOU/1+Vm+D2A/xOjvmXRqOQ+xc7C21gnLQzV7cLosIh0wPcMhaJ3KvUAntn/Iqy8rquXj6Et8Resb6W9zFrHLYQh8uqRqcijlpsNeS+qRNHL6768l7vzRjzQPOQIV1RwqpmWWcaiAqTX859Nwd7aAFjZei+CfMOFdVRtQ2mHp96XKT4gcFzvJSRNpjcLMWag5yBbvwEs3MDv3erykBrd0q8wZSGODg9k6J2PQcMCPYOiCamcTRtM3f7dsj2euPMBJkM6RexH5hLrkMLrO+fdxG1zyAjcyZfUcowdmZinXsgDfWKipdw52GjirjEtf15nVMK6t2cdtQR6+BZ/ZcNA/hhJ4PsQB2ieBeFv0mv29exlTI1IvhEG4uMwpwSTgaFZOeYDRu3N8ksAN8MsglyTfzUO086kGFNiavtXJEFSQIp+EbHcg20ZE6BczGORvl3/p5eAZ5iYbOPDQm3buFwxFlPLeGGfbAwuOLCHaY76Wq9febnoMe1a0C9M0I8ueuzoeBSHiZDxlW6gqGYJo/PuRrNCI4DBAwexCTzvA8t6Ad1zyE1qP0l+lUEQw8ijXoDAZxQN423XVq1gZG+UDJtKyPRaZy/KTrURXY2t7admOfjxR+TZplGC9S1tu7ST5RmsTsnx4K7wtn3ePsUxLT3Bf0ViHJtHIAy92FrTtyEAUckzD+a30UWW/WVgZlQkeHSGvuo79fWEDM4YnbtEOj6F0jYomLhMp6aqG8hdtnDfV2gihO7s9p0cAc5OLbgfPUMRVuvphAfV62jEEiMXpaUubb+nY6ys2MTOF4LTKP0y0//jBh8XKEYnqfr9b0Ro//WAVZFsVAd81hnrlvHPFTpGeZeqJLXifAVUHoFkSZKIIZjKw63hHDs578ama/0Y77HKP8xGcv0GK/EJREB4WxyAXGtSS99HTzGtIQiBY41X+0yFjNZS2l+yxhLrfDf1QuxxkzAdoVpPiD4WVkSqko1Yi5DaK/2utyDqDUVD2a9WE8mSFNYBE6z74AunmqO/BV6pOOPdvnN9ezfuevg8bH9fMDAdpy1f79OA0v6D/91gcEbdvZO9k2vPt9V6kvRu2rzm49UuYK49vC1P6Tx5oHDhK1iexMiUBk5ypzCCtzcQqDHOJF'
        encrypted_by_web_value = 'AgHZ12GNPHAubGMes/O35F86pNYoOFuyYJKate7YvxWmbjMEEGwehb+WQzJWplBurq++hkV/lPrsl/dYRL7ekKrvG7k8EwgMXlMZ77pJv5E+B4GDVGg7Qvr9ut7wTb5w44my9+jBM6yuvT836aoz0q3vM/2xSv7tlhngsx5ka+KvqqOiTMPlKs4bMxB8CZW2fjdM8DaHyapKoK6BlMcFtQ2yqvhp5PzOpAU5gFWX+GELIgS9M/WDogzipfbJNGc6PS7TL+WZNX+FEMAJce62QDHLKpPpg2UnN/POQtUMJsO/GLzbSruclswy3NMHlS9z/6LA7i/XlSKvoqvGJWo95vp8zyibPCwcbRh14Gqfrxr7qNxTp7Is7v2/5A3STJFB6tDVwJXtahYrpKD0MxTLHe5b2hdDwB+NbNrEBibJihl98j0u+iSnNAuFcNnnRC/MQR25U1xUJw3HEGNFGs7K9Ly7WWwKnKEqOCrfAVbcg8YE8ORDAg/EQna9CqgaqcZcC6dFsa2/vW3E9jvAUy+k6eOHJabNTT4RiOeLqFIJ1CYu9dVMDrITjyRoi27J4QFMjJ2LsleLCue5rYHhY66oW36iJaQzz5OFUzReOXUp4BEVN7e3i9v1cHX7lzB2EMxNpkV1DeMzGOxWYOSpBpXV0zkMYusBGjoGTWP9tZXu8KnCGkKtu/T+pX+ixEZY7q5cAsgd8d2kNaLp1qPvOFzXOduAtk/sron4iLseIXFQbf9zvDUTm6Q/TQfgCrQ/Rn967COhlrf+60A6+QpRK+V9c5HOVgryDTjdpCEjgnu7PDUfjSlj9oUytXBC6isw/rFt8UmJf46qhm8kFtpvQsIL8InjR3Dmdmne0ge6Dv9WLssIvVf9obQIvp8xS8EJRsbH+AYx1ytLyQbKjz4JEuS2piWC7GDvP76ep0v0hORwfQv0PjkerKFyQmWEVEpW6cThxibK82Ge6GU0mtXu9GE1VSVGePb+3KYY6udlHwZLC4+vHutmqiF+utGfrge9xallyVokIBRL35ykIb34O3ANFt/U0725bHMTh6IC0Gk5C6beSfWIqMVI0bw1wDVas6cmgvW9xXZEpiW1huwzDy9LzDxby6R5wE4bzwsblhYPncgwe5mKd6i0J9iYXbKhr+fBA7GHic57vIxcEWwANQZNSmjruRBllisZJafrQzgQkMsJ9VTUcyA7WFwIQhAxHIId3QDz5ZnV9qehf5FRKll7RYMhRnexk/x+FMQ5srhudvTz2/qN+3q5gxY53in2tjldJPgZoJtjRTkDO3XIzrqLKV3I'
        self.perform_encryption_actions(encrypted_by_ios_value, encrypted_by_web_value, password, decrypted_value, False)

    def perform_encryption_actions(self, encrypted_by_ios_value, encrypted_by_web_value, password,
                                   expected_result, should_faild):

        cryptor = self.generate_cryptor(password)

        val = cryptor.encrypt(expected_result)

        res_web = cryptor.decrypt(encrypted_by_web_value)
        self.assertEquals(expected_result, res_web)

        resIos = cryptor.decrypt(encrypted_by_ios_value)
        if should_faild:
            self.assertNotEquals(expected_result, resIos)
        else:
            self.assertEquals(expected_result, resIos)

    def generate_cryptor(self, password):
        return generate_cryptor(password, self.encryption_salt, self.hmac_salt)


class CryptorV3Test(TestCase):

    def setUp(self):
        self.encryption_salt = b64decode('2ddhjTxwLmw=')
        self.hmac_salt = b64decode('Yx6z87fkXzo=')

    def test_decrypt_empty_value(self):
        password = 'a'
        decrypted_value = ''
        encrypted_value = 'AwHZ12GNPHAubGMes/O35F86hel8B6ZuqC9Lc1ZDsbnEHdPIcyBemqzKXSLX5lVlEW7x2ZiuQe0zZCZKXLCFEIxSLNy/uD0F1/z/5C0vBXO9Ew=='
        self.perform_encryption_actions(encrypted_value, password, decrypted_value)

    def test_decrypt_one_byte_value(self):
        password = 'thepassword'
        decrypted_value = '01'
        encrypted_value = 'AwHZ12GNPHAubGMes/O35F868RaU+TIu27SpZPSBlTwmge+mSMGmnRGvjyGQq1gUt6h7enTKa8b60t0rpr6Idf9STg8pZ9uJTHjHPM+jj98qcA=='
        self.perform_encryption_actions(encrypted_value, password, decrypted_value)

    def test_decrypt_value(self):
        password = 'thepassword'
        decrypted_value = '0123456789abcdef'
        encrypted_value = 'AwHZ12GNPHAubGMes/O35F86hkKw6Eq9Hz9sA47z/bZq+4RwmZfSBhc0B8Z5pTNZwG/EBn9naVesVUzl//QW+ORJQDLsNl3ztzrrioXM2uK7Br38hO4I47eJI8yk+T4lAbI='
        self.perform_encryption_actions(encrypted_value, password, decrypted_value)

    def test_decrypt_value_with_space(self):
        password = 'thepassword'
        decrypted_value = '0123456789abcdef 01234567'
        encrypted_value = 'AwHZ12GNPHAubGMes/O35F86HmETN6HKkm0+M0eIy44/2ypeX9OSZW35cXBZ5mg2ytvZ7EuxnEcrGTjafiY0BJodtWQf9Qlif4s4W+oUKp2+PWY4hIZsy8NUseICkxJojF0='
        self.perform_encryption_actions(encrypted_value, password, decrypted_value)

    def test_decrypt_value_with_space_by_multi_byte_password(self):
        password = '中文密码'
        decrypted_value = '23456789abcdef 0123456701'
        encrypted_value = 'AwHZ12GNPHAubGMes/O35F86lk3GRUdecB2k/+NSHiEohixwgt0bIuABoW8RfrRBHff1HhlLNpmpQ0JjiVqeUh9jTAUZcv3H//6WnSgYp1Nbhl6L5gIxr/CysRXAMI26HeI='
        self.perform_encryption_actions(encrypted_value, password, decrypted_value)

    def test_decrypt_long_value_with_space_by_long_password(self):
        password = 'It was the best of times, it was the worst of times; it was the age of wisdom, it was the age of foolishness;'
        decrypted_value = '69 74 20 77 61 73 20 74 68 65 20 65 70 6f 63 68 20 6f 66 20 62 65 6c 69 65 66 2c 20 69 74 20 77 61 73 20 74 68 65 20 65 70 6f 63 68 20 6f 66 20 69 6e 63 72 65 64 75 6c 69 74 79 3b 20 69 74 20 77 61 73 20 74 68 65 20 73 65 61 73 6f 6e 20 6f 66 20 4c 69 67 68 74 2c 20 69 74 20 77 61 73 20 74 68 65 20 73 65 61 73 6f 6e 20 6f 66 20 44 61 72 6b 6e 65 73 73 3b 20 69 74 20 77 61 73 20 74 68 65 20 73 70 72 69 6e 67 20 6f 66 20 68 6f 70 65 2c 20 69 74 20 77 61 73 20 74 68 65 20 77 69 6e 74 65 72 20 6f 66 20 64 65 73 70 61 69 72 3b 20 77 65 20 68 61 64 20 65 76 65 72 79 74 68 69 6e 67 20 62 65 66 6f 72 65 20 75 73 2c 20 77 65 20 68 61 64 20 6e 6f 74 68 69 6e 67 20 62 65 66 6f 72 65 20 75 73 3b 20 77 65 20 77 65 72 65 20 61 6c 6c 20 67 6f 69 6e 67 20 64 69 72 65 63 74 6c 79 20 74 6f 20 48 65 61 76 65 6e 2c 20 77 65 20 77 65 72 65 20 61 6c 6c 20 67 6f 69 6e 67 20 74 68 65 20 6f 74 68 65 72 20 77 61 79 2e 0a 0a'
        encrypted_value = 'AwHZ12GNPHAubGMes/O35F86s90AhqVv6vDYGXLrRODTmc7NuFZVpJPHZSsI3V6cXoad8uqADuzvG46WPXmPn7rcDY8S1wWciJHXZTywGXRtAhEy/d6K7gfBViwhCD0j9hR5T7YD1z3gaQNtLB9s/kDUJJRyn4oSZQYtfbVm8DESGKJHeOyesrhEsG/5SlMOPcnrbPCkJ8dWRq3XREIj5WaPHM5VHD+iOSTeJliL6/NSI2Bl+bNF6/H9a9RQyQAlipvN/nc/htJ0r8mTtvKaQkVniHcrbjVAA8VDY+W5G5lPfNJ4f9fL23FJvo6/9gVQPG/BfDvIlBKX58NNew7t7PeEQoOfTAr96uPP13B3/0MM9fmjYc+KlSAaKKnQoSdVNibtq+7y3j+s0BaL4DBEHEiflNgPQ5gOf8KQd1zGOlR64j6yPwiP4srLVjBj1ERwrEEzw/DJfshvsE1MWsJ4tp9kSl2ydQEJ/hc6PVtX5sjIypJD5EFEFPI6SCCOD3WvJ6N9Cm1xl55yoIyPcoJPS6GOvQJY9PfDSLQpjpsBnjxKdMYgTBR6VEJXJYkG3inqCaVl06iDMz/O7MZzlJfvy6AfbMufwSj2O6PIFeHdQ9JT39uujTDDM/XI0UjksenBRwke/6IFzOppPkwvDQjrOQjPbM2uVANKOUWJNy+x5AlpGtcKd7dpcZgmNdgo3/rbFpHTAw0wmNlXeG8naP3jR2FLO3x7GIfgueGofOrO+HGEyJvVV/TAINo9FF5bW2oudTpPQo+VVs6WQ2WttrrkVJc5WtorCylBYNGIAG9PR9N130WVI9sx2Ka7OnoYcESxme06y8eZMX0j7/i00lpKywTIF7XSehUesvJEFVBYODYsw41qx4uODlXFKu1VLXLTDA2L89qlD5gXRXJWII2bIuwejP8G/3sl/Z9MjVRuDGP2efLt9Hb3opJgLMng+U/9RjpThBniZtSANX5Ksre3p4kvEF7BU2Epnz5N9nNcX+k1V4uBL/6+7SWN0KR0qxTyF3gDpubd/lCzEm4LjR3kWJ7GMYhxGXNyQGZO5Oh5CYS3nXbm1Pip2SvnHVCTZ83FrkRzL+p1/D+szzvmYXGYOpmlp28FTCpOxTkFg2mNb9kgbYaUcIsXRtmrcMUX6sY6VXny08ZZGW0a3WtKYwTTuQ2Zixdup8Rpew3mhx5AvRIOD9K3bD50Hxhr6fdJjhijMJk/aeDg1FIn9f4LojqAflswlwAe0IcjslOlbUlJf4rf+hOO2FdRaPd5/oFnysjB46JX8EVh7hao8dhV16JFRmpy'
        self.perform_encryption_actions(encrypted_value, password, decrypted_value)

    def perform_encryption_actions(self, encrypted_value, password, expected_result):
        cryptor = self.generate_cryptor(password)

        val = cryptor.encrypt(expected_result)

        res = cryptor.decrypt(encrypted_value)
        self.assertEquals(expected_result, res)

    def generate_cryptor(self, password):
        return generate_cryptor(password, self.encryption_salt, self.hmac_salt)
