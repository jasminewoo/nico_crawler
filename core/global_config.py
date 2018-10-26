import json
import os


class Config(dict):
    def __init__(self, config_file_paths):
        dict.__init__(self)
        prefix = ''
        cwd = os.getcwd().split('/')
        while cwd[-1] != 'nico_crawler':
            cwd.remove(cwd[-1])
            prefix += '../'
        for config_file_path in config_file_paths:
            path = prefix + config_file_path
            if os.path.exists(path):
                with open(path, 'r') as fp:
                    kvp = json.load(fp)
                    for key in kvp:
                        self[key] = kvp[key]


instance = Config(['config.json', 'config_secret.json'])
