import json
import logging
import os
from random import shuffle

from core.utils import path_utils

log = logging.getLogger(__name__)


class Config(dict):
    def __init__(self, config_file_paths=None, dict=None):
        dict.__init__(self)
        prefix = path_utils.get_root_prefix() + 'config/'
        if config_file_paths:
            for config_file_path in config_file_paths:
                path = prefix + config_file_path
                if os.path.exists(path):
                    log.info('Reading config: ' + path)
                    with open(path, 'r') as fp:
                        kvps = json.load(fp)
                        for key, value in kvps.items():
                            self[key] = value
        if dict:
            for key, value in dict.items():
                self[key] = value

    def has_nico_creds(self):
        ncs = self.get_all_nico_creds()
        return len(ncs) > 0

    def get_all_nico_creds(self):
        ncs = []
        if 'nico_creds' in self:
            for d in self['nico_creds']:
                if 'username' in d and 'password' in d:
                    ncs.append(NicoCreds(d['username'], d['password']))
        return ncs

    def get_random_nico_creds(self):
        ncs = self.get_all_nico_creds()
        if len(ncs) > 0:
            shuffle(ncs)
            return ncs[0]
        else:
            return None


def save(filename, kvps):
    path = path_utils.get_root_prefix() + '/' + filename
    if os.path.exists(filename):
        with open(path, 'r') as fp:
            org_kvps = json.load(fp)
            for key, value in kvps.items():
                org_kvps[key] = value
            kvps = org_kvps
    with open(path, 'w') as fp:
        json.dump(kvps, fp)


class NicoCreds:
    def __init__(self, username, password):
        self.username = username
        self.password = password


global_instance = Config(config_file_paths=['default.json', 'user.json'])
