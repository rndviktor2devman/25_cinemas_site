from flask import Flask, render_template, json, request
from cacher import Cacher
import afisha_interaction as ai
from threading import Thread
import datetime


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

AFISHA_URL = "http://www.afisha.ru/msk/schedule_cinema/"
TEMPLATE_URL = "films_list.html"
API_TEMPLATE_URL = "api_description.html"


def forbidden_access():
    message = {
        'status': 403,
        'message': 'Forbidden:' + request.url
    }
    return app.response_class(
        response=json.dumps(message),
        status=403,
        mimetype='application/json'
    )


def correct_response(data=None):
    return app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )


@app.route('/ping', methods=['GET'])
def ping_by_timeout():
    if cacher.afisha_timed_out():
        thread = Thread(target=cacher.renew_cache)
        thread.start()
    data = {
        'count': cacher.count_refs,
        'updateDateTime': cacher.update_time
    }
    return correct_response(data)


@app.route('/get_movies', methods=['POST'])
def get_movies_from_cache():
    shown_movies = request.json

    movies = cacher.get_non_shown_movies(shown_movies)

    data = {
        'movies': movies
    }
    return correct_response(movies)


@app.route('/renew_cache', methods=['POST'])
def clean_cache():
    if cacher.caching_available():
        cacher.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        cacher.clean_cache()
        start_queue()
        return correct_response()
    else:
        return forbidden_access()


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
    return correct_response(cacher.get_movies_data())


@app.route('/api/movie/<int:param>/', methods=['GET'])
def api_movie(param):
    url = 'http://www.afisha.ru/movie/{}'.format(param)
    movie_page = cacher.cached(url)
    return correct_response(ai.json_data(movie_page))


@app.route("/")
def films_list():
    main_page = render_template(TEMPLATE_URL)
    start_queue()
    return main_page

if __name__ == "__main__":
    app.run()
