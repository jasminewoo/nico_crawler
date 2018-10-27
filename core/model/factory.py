from core.model.mylist import MyList
from core.model.ranking import Ranking
from core.model.search import Search
from core.model.video import Video


class Factory:
    k_VIDEO = 'video'
    k_MYLIST = 'mylist'
    k_SEARCH = 'search'
    k_RANKING = 'ranking'

    k_TYPE_MAP = {
        k_MYLIST: MyList,
        k_SEARCH: Search,
        k_RANKING: Ranking
    }

    def __init__(self, url, logger):
        self.logger = logger
        self.nico_object = Video(url=url)
        self.type = self.k_VIDEO
        for nico_object_type, obj in self.k_TYPE_MAP.items():
            if nico_object_type in url:
                self.nico_object = obj(url=url)
                self.type = nico_object_type
                break

    def get_videos(self, min_mylist=0):
        vids = [self.nico_object] if type(self.nico_object) is Video else self.nico_object.videos

        if min_mylist == 0:
            return vids

        to_return = []
        for vid in vids:
            self.logger.debug('{}.mylist_count={}'.format(vid, vid.mylist_count))
            if vid.mylist_count >= min_mylist:
                to_return.append(vid)
        return to_return
