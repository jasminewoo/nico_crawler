import json


class Config(dict):
    def __init__(self, config_file_path):
        dict.__init__(self)
        with open(config_file_path, 'r') as fp:
            kvp = json.load(fp)
            for key in kvp:
                self[key] = kvp[key]


instance = Config('config.json')
