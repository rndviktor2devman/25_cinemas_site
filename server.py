from flask import Flask, render_template
import requests
from afisha_interaction import movie_refs, parse_movie_data
from werkzeug.contrib.cache import SimpleCache

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
cache = SimpleCache()

AFISHA_URL = "http://www.afisha.ru/msk/schedule_cinema/"
TEMPLATE_URL = "films_list.html"
CACHE_TIMEOUT = 12 * 60 * 60


def cached(url, timeout=CACHE_TIMEOUT):
    cached_page = cache.get(url)
    if cached_page:
        return cached_page.content
    page = requests.get(url)
    cache.add(url, page, timeout=timeout)
    return page.content


@app.route('/')
def films_list():
    page = cached(AFISHA_URL)
    refs = movie_refs(page)
    movies_data = []
    print('found %d' % len(refs))
    for ref in refs:
        movie_page = cached(ref)
        movies_data.append(parse_movie_data(movie_page))
    return render_template(TEMPLATE_URL, movies=movies_data)

if __name__ == "__main__":
    app.run()
