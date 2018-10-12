from core.mylist import MyList
from core.ranking import Ranking
from core.search import Search
from core.video import Video


class NicoObjectFactory:
    def __init__(self, url):
        self.nico_object = None
        if 'mylist' in url:
            self.nico_object = MyList(url=url)
        elif 'search' in url:
            self.nico_object = Search(url=url)
        elif 'ranking' in url:
            self.nico_object = Ranking(url=url)
        else:
            self.nico_object = Video(url=url)

    def get_videos(self, min_mylist=0):
        vids = self.nico_object.videos if type(self.nico_object) is not Video else [self.nico_object]

        if min_mylist == 0:
            return vids

        to_return = []
        for vid in vids:
            if vid.mylist >= min_mylist:
                to_return.append(vid)
        return to_return
