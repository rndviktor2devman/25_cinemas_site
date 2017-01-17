from flask import Flask, render_template
import requests
from afisha_interaction import fetch_afisha_page
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
    return render_template('films_list.html')

if __name__ == "__main__":
    raw_data = fetch_afisha_page()
    app.run()
