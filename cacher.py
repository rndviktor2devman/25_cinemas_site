import requests
import afisha_interaction as ai
from werkzeug.contrib.cache import SimpleCache

AFISHA_URL = "http://www.afisha.ru/msk/schedule_cinema/"
CACHE_TIMEOUT = 12 * 60 * 60  # 12 hours timeout
MOVIES_SET_TIMEOUT = 30  # 30 secs timeout
MOVIES_SET = 'movies_data'


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
        self.caching_pending = True
        afisha_page = self.cached(AFISHA_URL)
        refs = ai.movie_refs(afisha_page)
        movies_data = []
        self.count_refs = len(refs)
        print('found %d movies' % self.count_refs)
        for ref in refs:
            movie_page = self.cached(ref)
            movie_data = ai.parse_movie_data(movie_page)
            movies_data.append(movie_data)
            self.callback(movie_data, self.count_refs)
            self.cache.delete(MOVIES_SET)
            self.cache.set(MOVIES_SET, movies_data, MOVIES_SET_TIMEOUT)
        self.caching_pending = False
        self.finish()
        print('cached found %d movies' % len(refs))

    def get_movies_data(self):
        data = []
        if self.cache.get(MOVIES_SET) is not None:
            data = self.cache.get(MOVIES_SET)
        return data

    def clean_cache(self):
        self.cache.delete(AFISHA_URL)

    def needs_cache(self):
        cached_movies = self.cache.get(MOVIES_SET)
        print(cached_movies)
        return cached_movies is None and not self.caching_pending

    def cache_is_clean(self):
        return self.count_refs == 0

    def all_movies_cached(self):
        return self.count_refs == len(self.get_movies_data())

    def get_cached_page(self, url):
        return self.cache.get(url)
