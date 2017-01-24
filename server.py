from flask import Flask, render_template
import requests
from afisha_interaction import fetch_afisha_page, movie_refs, parse_movie_data
from werkzeug.contrib.cache import SimpleCache

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
cache = SimpleCache()


def retrieve_cached(url, timeout=43200):
    cached_page = cache.get(url)
    if cached_page:
        return cached_page
    page = requests.get(url)
    cache.add(url, page, timeout=timeout)
    return page


@app.route('/')
def films_list():
    page = fetch_afisha_page()
    refs = movie_refs(page)
    movies_data = []
    print('found %d' % len(refs))
    for ref in refs:
        movies_data.append(parse_movie_data(requests.get(ref).content))
    return render_template('films_list.html', movies=movies_data)

if __name__ == "__main__":
    app.run()
