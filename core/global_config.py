import json
import os

from core import path_utils


class Config(dict):
    def __init__(self, config_file_paths):
        dict.__init__(self)
        prefix = path_utils.get_root_prefix()
        for config_file_path in config_file_paths:
            path = prefix + config_file_path
            if os.path.exists(path):
                with open(path, 'r') as fp:
                    kvp = json.load(fp)
                    for key in kvp:
                        self[key] = kvp[key]


instance = Config(['config.json', 'config_secret.json'])
