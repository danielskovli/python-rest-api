import unittest
import random
from simple_rest_api import constants, utils



class TestUtilsCryptography(unittest.TestCase):

    def test_generate_key(self):
        # NOTE: The `base64` nature of the `token_urlsafe` implementation
        # makes this test a bit weak. We can't exactly anticipate the length
        # of the returned key.

        key = utils.cryptography.generate_api_key('', 10)
        self.assertTrue(isinstance(key, str)) # type: ignore
        self.assertGreater(len(key), 10)

        key = utils.cryptography.generate_api_key('x_', 32)
        self.assertGreater(len(key), 32 + 2)

    def test_hash_key1(self):
        straight_alphanum_key = 'abcdefghijklmnopqrstuvwxyz0123456789'

        for method in constants.HashingMethod:
            self.assertEqual(
                utils.cryptography.hash_api_key(straight_alphanum_key, method.value),
                utils.cryptography.hash_api_key(straight_alphanum_key, method.value),
            )

    def test_hash_key2(self):
        random_keys = [
            utils.cryptography.generate_api_key(length=random.randint(1, 50)) for _ in range(10)
        ]

        for method in constants.HashingMethod:
            for key in random_keys:
                self.assertEqual(
                    utils.cryptography.hash_api_key(key, method.value),
                    utils.cryptography.hash_api_key(key, method.value),
                )