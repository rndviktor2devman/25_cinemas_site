import requests
import afisha_interaction as ai
from werkzeug.contrib.cache import SimpleCache

AFISHA_URL = "http://www.afisha.ru/msk/schedule_cinema/"
CACHE_TIMEOUT = 12 * 60 * 60  # 12 hours timeout
AFISHA_TIMEOUT = 60 * 60  # 1 hour timeout
MOVIES_SET = 'movies_data'


class Cacher():
    def __init__(self, callback, finish_callback):
        self.cache = SimpleCache()
        self.callback = callback
        self.finish = finish_callback
        self.count_refs = 0
        self.caching_pending = False

    def cached(self, url, timeout=CACHE_TIMEOUT):
        cached_page = self.cache.get(url)
        if cached_page:
            return cached_page.content
        self.cache.delete(url)
        page = requests.get(url)
        self.cache.add(url, page, timeout=timeout)
        return page.content

    def cache_all_pages(self, old_cache=[]):
        self.caching_pending = True
        afisha_page = self.cached(AFISHA_URL, AFISHA_TIMEOUT)
        refs = ai.movie_refs(afisha_page)
        movies_data = []
        self.count_refs = len(refs)
        for ref in refs:
            if 'http:https:' in ref:
                ref = ref.replace('http:', '')
            movie_page = self.cached(ref)
            movie_data = ai.parse_movie_data(movie_page)
            movies_data.append(movie_data)
            if old_cache is None or movie_data not in old_cache:
                self.callback(movie_data, self.count_refs)
            self.cache.delete(MOVIES_SET)
            self.cache.set(MOVIES_SET, movies_data, CACHE_TIMEOUT)
        self.caching_pending = False
        self.finish()

    def renew_cache(self):
        old_cache = self.cache.get(MOVIES_SET)
        self.cache_all_pages(old_cache)

    def afisha_timed_out(self):
        afisha = self.cache.get(AFISHA_URL)
        return afisha is None

    def get_movies_data(self):
        data = []
        if self.cache.get(MOVIES_SET) is not None:
            data = self.cache.get(MOVIES_SET)
        return data

    def clean_cache(self):
        self.cache.delete(AFISHA_URL)

    def caching_available(self):
        return not self.caching_pending
