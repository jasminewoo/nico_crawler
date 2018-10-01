class Video:
    def __init__(self, js):
        self._js = js
        self.video_id = js['video_id']
        self.title = js['title']
        self.is_deleted = js['deleted'] != '0'