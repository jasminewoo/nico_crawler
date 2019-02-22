from core.config import Config
from tests.custom_test_case import CustomTestCase


class ConfigUtilsTest(CustomTestCase):
    def test_no_creds(self):
        config_json = {}
        c = Config(dict=config_json)
        self.assertFalse(c.has_nico_creds())

    def test_zero_creds(self):
        config_json = {"nico_creds": []}
        c = Config(dict=config_json)
        self.assertFalse(c.has_nico_creds())

    def test_incorrect_keys_for_creds(self):
        config_json = {"nico_creds": [{"email": "e@mail.com", "pass": "pass!"}]}
        c = Config(dict=config_json)
        self.assertFalse(c.has_nico_creds())

    def test_nico_creds_positive(self):
        config_json = {"nico_creds": [{"username": "myUsername", "password": "myPassword"}]}
        c = Config(dict=config_json)
        self.assertTrue(c.has_nico_creds())
        ncs = c.get_all_nico_creds()
        self.assertEqual(1, len(ncs))
        self.assertEqual('myUsername', ncs[0].username)
        self.assertEqual('myPassword', ncs[0].password)

    def test_nico_creds_multiple_kvps(self):
        config_json = {"nico_creds": [{"username": "myUsername1", "password": "myPassword1"},
                                      {"username": "myUsername2", "password": "myPassword2"}]}
        c = Config(dict=config_json)
        self.assertTrue(c.has_nico_creds())
        ncs = c.get_all_nico_creds()
        self.assertEqual(2, len(ncs))
        self.assertEqual('myUsername1', ncs[0].username)
        self.assertEqual('myPassword1', ncs[0].password)
        self.assertEqual('myUsername2', ncs[1].username)
        self.assertEqual('myPassword2', ncs[1].password)

    def test_nico_creds_shuffle(self):
        nico_creds = [{"username": "myUsername1", "password": "myPassword1"},
                      {"username": "myUsername2", "password": "myPassword2"},
                      {"username": "myUsername3", "password": "myPassword3"},
                      {"username": "myUsername4", "password": "myPassword4"}]
        c = Config(dict={"nico_creds": nico_creds})
        username_set = set()
        for i in range(len(nico_creds) * 50):
            nc = c.get_random_nico_creds()
            username_set.add(nc.username)
        self.assertEqual(len(nico_creds), len(username_set))
