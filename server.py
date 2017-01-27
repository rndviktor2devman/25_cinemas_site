from flask import Flask, render_template, json, Response
import requests
import afisha_interaction as ai
from werkzeug.contrib.cache import SimpleCache

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
cache = SimpleCache()

AFISHA_URL = "http://www.afisha.ru/msk/schedule_cinema/"
TEMPLATE_URL = "films_list.html"
API_TEMPLATE_URL = "api_desc.html"
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


@app.route('/api')
def api_about():
    return render_template(API_TEMPLATE_URL)


@app.route('/api/list', methods=['GET'])
def api_main():
    afisha_page = cached(AFISHA_URL)
    refs = ai.movie_refs(afisha_page)
    json_movies = []
    for ref in refs:
        movie_page = cached(ref)
        json_movies.append(ai.json_data(movie_page))
    return Response(json.dumps(json_movies, indent=2))


@app.route('/api/movie/<int:param>/', methods=['GET'])
def api_movie(param):
    url = 'http://www.afisha.ru/movie/{}'.format(param)
    movie_page = cached(url)
    return Response(json.dumps(ai.json_data(movie_page)))


@app.route("/")
def films_list():
    main_page = cache.get("/")
    if main_page is not None:
        return main_page
    cache.delete("/")
    afisha_page = cached(AFISHA_URL)
    refs = ai.movie_refs(afisha_page)
    movies_data = []
    print('found %d movies' % len(refs))
    for ref in refs:
        movie_page = cached(ref)
        movies_data.append(ai.parse_movie_data(movie_page))
    main_page = render_template(TEMPLATE_URL, movies=movies_data)
    cache.add("/", main_page, MAIN_PAGE_TIMEOUT)
    return main_page

if __name__ == "__main__":
    app.run()
