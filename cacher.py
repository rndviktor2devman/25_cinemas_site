import requests
import datetime
import afisha_interaction as ai
from werkzeug.contrib.cache import FileSystemCache

AFISHA_URL = "http://www.afisha.ru/msk/schedule_cinema/"
CACHE_TIMEOUT = 12 * 60 * 60  # 12 hours timeout
AFISHA_TIMEOUT = 20 * 60  # 20 min timeout
MOVIES_SET = 'movies_data'
COUNT_REFS = 'count_refs'
CACHING_AVAILABLE = 'caching_available'
UPDATE_TIME = 'update_time'


class Cacher():
    def __init__(self):
        self.cache = FileSystemCache('cache_dir')
        self.cache.set(COUNT_REFS, 0)
        self.cache.set(CACHING_AVAILABLE, True)
        self.cache.set(UPDATE_TIME, '')

    def cached(self, url, timeout=CACHE_TIMEOUT):
        cached_page = self.cache.get(url)
        if cached_page:
            return cached_page.content
        self.cache.delete(url)
        page = requests.get(url)
        self.cache.add(url, page, timeout=timeout)
        return page.content

    def cache_all_pages(self):
        self.cache.set(CACHING_AVAILABLE, False)
        afisha_page = self.cached(AFISHA_URL, AFISHA_TIMEOUT)
        refs = ai.movie_refs(afisha_page)
        movies_data = []
        self.cache.set(COUNT_REFS, len(refs))
        for ref in refs:
            if 'http:https:' in ref:
                ref = ref.replace('http:', '')
            movie_page = self.cached(ref)
            movie_data = ai.parse_movie_data(movie_page)
            movies_data.append(movie_data)
            self.cache.delete(MOVIES_SET)
            self.cache.set(MOVIES_SET, movies_data, CACHE_TIMEOUT)
        self.cache.set(CACHING_AVAILABLE, True)

    def renew_cache(self):
        self.cache_all_pages()

    def afisha_timed_out(self):
        afisha = self.cache.get(AFISHA_URL)
        return afisha is None and self.caching_available()

    def get_movies_data(self):
        movies = []
        if self.cache.get(MOVIES_SET) is not None:
            movies = self.cache.get(MOVIES_SET)
        return movies

    def get_non_shown_movies(self, shown_movies):
        output_movies = []
        if self.cache.get(MOVIES_SET) is not None:
            cached_movies = self.cache.get(MOVIES_SET)
            for movie in cached_movies:
                if movie['url'] not in shown_movies:
                    output_movies.append(movie)
        return output_movies

    def clean_cache(self):
        self.cache.set(UPDATE_TIME, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.cache.delete(AFISHA_URL)

    def count_refs(self):
        return self.cache.get(COUNT_REFS)

    def update_time(self):
        return self.cache.get(UPDATE_TIME)

    def caching_available(self):
        return self.cache.get(CACHING_AVAILABLE)
