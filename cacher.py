import requests
import afisha_interaction as ai
from werkzeug.contrib.cache import SimpleCache

AFISHA_URL = "http://www.afisha.ru/msk/schedule_cinema/"
CACHE_TIMEOUT = 12 * 60 * 60  # 12 hours timeout


class Cacher():
    def __init__(self, callback, finish_callback):
        self.cache = SimpleCache()
        self.callback = callback
        self.finish = finish_callback
        self.count_refs = -1
        self.caching_pending = False

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
        self.count_refs = len(refs)
        for ref in refs:
            movie_page = self.cached(ref)
            movie_data = ai.parse_movie_data(movie_page)
            movies_data.append(movie_data)
            self.callback(movie_data)
            self.cache.delete('movies_data')
            self.cache.set('movies_data', movies_data)
        self.caching_pending = False
        self.finish()
        print('cached found %d movies' % len(refs))

    def get_movies_data(self):
        data = []
        if self.cache.get('movies_data') is not None:
            data = self.cache.get('movies_data')
        return data

    def all_movies_cached(self):
        return self.count_refs == len(self.get_movies_data())

    def get_cached_page(self, url):
        return self.cache.get(url)
