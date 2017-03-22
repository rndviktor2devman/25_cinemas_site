from flask import Flask, render_template, json, Response
from cacher import Cacher
import afisha_interaction as ai
from threading import Thread


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

AFISHA_URL = "http://www.afisha.ru/msk/schedule_cinema/"
TEMPLATE_URL = "films_list.html"
API_TEMPLATE_URL = "api_description.html"


@app.route('/ping', methods=['GET'])
def ping_by_timeout():
    if cacher.afisha_timed_out():
        thread = Thread(target=cacher.renew_cache)
        thread.start()
    data = {
        'count': cacher.count_refs
    }
    return json.dumps({'status': 'ok', 'data': data})


@app.route('/get_movies', methods=['GET'])
def get_movies_from_cache():
    movies = cacher.get_movies_data()

    data = {
        'movies': movies
    }
    return json.dumps({'status': 'ok', 'data': data})


@app.route('/renew_cache', methods=['POST'])
def clean_cache():
    if cacher.caching_available():
        cacher.clean_cache()
        start_queue()
        return json.dumps({'status': 'ok', 'data': 'dropped'})
    else:
        return json.dumps({'status': 'ok', 'data': 'forbid'})


def start_queue():
    if cacher.caching_available():
        thread = Thread(target=cacher.cache_all_pages)
        thread.start()


cacher = Cacher()


@app.route('/api')
def api_about():
    return render_template(API_TEMPLATE_URL)


@app.route('/api/list', methods=['GET'])
def api_main():
    afisha_page = cacher.cached(AFISHA_URL)
    refs = ai.movie_refs(afisha_page)
    json_movies = []
    for ref in refs:
        movie_page = cacher.cached(ref)
        json_movies.append(ai.json_data(movie_page))
    return Response(json.dumps(json_movies, indent=2))


@app.route('/api/movie/<int:param>/', methods=['GET'])
def api_movie(param):
    url = 'http://www.afisha.ru/movie/{}'.format(param)
    movie_page = cacher.cached(url)
    return Response(json.dumps(ai.json_data(movie_page)))


@app.route("/")
def films_list():
    main_page = render_template(TEMPLATE_URL)
    start_queue()
    return main_page

if __name__ == "__main__":
    app.run()
