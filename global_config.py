class Config:
    def __init__(self, config_file_path):
        self._path = config_file_path
        self._dict = None

    @property
    def dict(self):
        if not self._dict:
            with open('config.json', 'r') as fp:
                import json
                self._dict = json.load(fp)
        return self._dict


instance = Config('config.json')
