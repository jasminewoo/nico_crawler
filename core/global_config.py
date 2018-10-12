import json
import os


class Config(dict):
    def __init__(self, config_file_paths):
        dict.__init__(self)
        for config_file_path in config_file_paths:
            if os.path.exists(config_file_path):
                with open(config_file_path, 'r') as fp:
                    kvp = json.load(fp)
                    for key in kvp:
                        self[key] = kvp[key]


instance = Config(['config.json', 'config_secret.json'])
