class Video:
    def __init__(self, video_id=None, url=None, title=None):
        if (1 if video_id else 0) + (1 if url else 0) != 1:
            raise AssertionError('Need one of video_id and url')

        if url:
            self.video_id = url.split('/')[-1]
        if video_id:
            self.video_id = video_id
        self.title = title

    def __str__(self):
        return '{} {}'.format(self.title, self.video_id) if self.title else self.video_id

    @property
    def url(self):
        return 'http://www.nicovideo.jp/watch/' + self.video_id
