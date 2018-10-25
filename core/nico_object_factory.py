from core.mylist import MyList
from core.ranking import Ranking
from core.search import Search
from core.video import Video


class NicoObjectFactory:
    def __init__(self, url, logger):
        self.nico_object = None
        self.logger = logger
        if 'mylist' in url:
            self.nico_object = MyList(url=url, logger=logger)
        elif 'search' in url:
            self.nico_object = Search(url=url)
        elif 'ranking' in url:
            self.nico_object = Ranking(url=url)
        else:
            self.nico_object = Video(url=url)

    def get_videos(self, min_mylist=0):
        is_video = type(self.nico_object) is Video
        if not is_video:
            self.logger.debug('Getting videos for {}'.format(self.nico_object))
        vids = self.nico_object.videos if not is_video else [self.nico_object]
        if not is_video:
            self.logger.debug('len(vids) = {}'.format(len(vids)))

        if min_mylist == 0:
            return vids

        to_return = []
        for vid in vids:
            self.logger.debug('{}.mylist_count={}'.format(vid, vid.mylist_count))
            if vid.mylist_count >= min_mylist:
                to_return.append(vid)
        return to_return
