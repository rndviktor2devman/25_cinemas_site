# -*- coding: utf-8 -*-
from flask import Flask, render_template
import requests
from afisha_interaction import movie_refs, parse_movie_data
from werkzeug.contrib.cache import SimpleCache

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
cache = SimpleCache()

AFISHA_URL = "http://www.afisha.ru/msk/schedule_cinema/"
TEMPLATE_URL = "films_list.html"
INDEX_URL = "/"
CACHE_TIMEOUT = 12 * 60 * 60    # 12 hours timeout
MAIN_PAGE_TIMEOUT = 60 * 30     # 30 minutes index timeout


def cached(url, timeout=CACHE_TIMEOUT):
    cached_page = cache.get(url)
    if cached_page:
        return cached_page.content
    cache.delete(url)
    page = requests.get(url)
    cache.add(url, page, timeout=timeout)
    return page.content


@app.route(INDEX_URL)
def films_list():
    base_page = cache.get(INDEX_URL)
    if base_page is not None:
        print('loaded from cache')
        return base_page
    else:
        cache.delete(INDEX_URL)
        print('build new page')
        afisha_page = cached(AFISHA_URL)
        refs = movie_refs(afisha_page)
        movies_data = []
        print('found %d movies' % len(refs))
        for ref in refs:
            movie_page = cached(ref)
            movies_data.append(parse_movie_data(movie_page))
        base_page = render_template(TEMPLATE_URL, movies=movies_data)
        cache.add(INDEX_URL, base_page, timeout=MAIN_PAGE_TIMEOUT)
        print('page cached')
        return base_page

if __name__ == "__main__":
    app.run()
