import json
import os

from core.utils import path_utils


class Config(dict):
    def __init__(self, config_file_paths):
        dict.__init__(self)
        prefix = path_utils.get_root_prefix()
        for config_file_path in config_file_paths:
            path = prefix + config_file_path
            if os.path.exists(path):
                with open(path, 'r') as fp:
                    kvps = json.load(fp)
                    for key in kvps:
                        self[key] = kvps[key]


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


global_instance = Config(['config.json', 'config_secret.json'])
