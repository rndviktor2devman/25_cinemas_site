import requests
import afisha_interaction as ai
from werkzeug.contrib.cache import SimpleCache

AFISHA_URL = "http://www.afisha.ru/msk/schedule_cinema/"
CACHE_TIMEOUT = 12 * 60 * 60  # 12 hours timeout


class Cacher():
    def __init__(self, callback):
        self.cache = SimpleCache()
        self.callback = callback

    def cached(self, url, timeout=CACHE_TIMEOUT):
        cached_page = self.cache.get(url)
        if cached_page:
            return cached_page.content
        self.cache.delete(url)
        page = requests.get(url)
        self.cache.add(url, page, timeout=timeout)
        return page.content

    def cache_all_pages(self):
        afisha_page = self.cached(AFISHA_URL)
        refs = ai.movie_refs(afisha_page)
        movies_data = []
        print('found %d movies' % len(refs))
        for ref in refs:
            movie_page = self.cached(ref)
            self.callback(ref)
            movies_data.append(ai.parse_movie_data(movie_page))
        print('cached found %d movies' % len(refs))
        self.cache.delete('refs')
        self.cache.set('refs', refs)

    def get_refs(self):
        return self.cache.get('refs')
