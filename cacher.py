import datetime
import requests
import afisha_interaction as ai
from werkzeug.contrib.cache import SimpleCache

AFISHA_URL = "http://www.afisha.ru/msk/schedule_cinema/"
CACHE_TIMEOUT = 12 * 60 * 60  # 12 hours timeout
AFISHA_TIMEOUT = 60 * 60  # 1 hour timeout
MOVIES_SET = 'movies_data'


class Cacher():
    def __init__(self):
        self.cache = SimpleCache()
        self.count_refs = 0
        self.cached_refs = 0
        self.update_time = ''

    def cached(self, url, timeout=CACHE_TIMEOUT):
        cached_page = self.cache.get(url)
        if cached_page:
            return cached_page.content
        self.cache.delete(url)
        page = requests.get(url)
        self.cache.add(url, page, timeout=timeout)
        return page.content

    def cache_all_pages(self):
        self.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        afisha_page = self.cached(AFISHA_URL, AFISHA_TIMEOUT)
        refs = ai.movie_refs(afisha_page)
        movies_data = []
        self.count_refs = len(refs)
        self.cached_refs = 0
        for ref in refs:
            if 'http:https:' in ref:
                ref = ref.replace('http:', '')
            movie_page = self.cached(ref)
            movie_data = ai.parse_movie_data(movie_page)
            movies_data.append(movie_data)
            self.cache.delete(MOVIES_SET)
            self.cache.set(MOVIES_SET, movies_data, CACHE_TIMEOUT)
            self.cached_refs += 1

    def renew_cache(self):
        self.cache_all_pages()

    def afisha_timed_out(self):
        afisha = self.cache.get(AFISHA_URL)
        return afisha is None

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
        self.cache.delete(AFISHA_URL)

    def caching_available(self):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        return self.cached_refs == self.count_refs and \
               current_time != self.update_time
