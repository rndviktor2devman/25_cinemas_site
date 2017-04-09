from flask import Flask, render_template, json, request, jsonify
from cacher import Cacher
import afisha_interaction as ai
from threading import Thread


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


@app.route('/ping', methods=['GET'])
def ping_by_timeout():
    if cacher.afisha_timed_out():
        thread = Thread(target=cacher.renew_cache)
        thread.start()
    data = {
        'count': cacher.count_refs(),
        'updateDateTime': cacher.update_time()
    }
    return jsonify(data)


@app.route('/get_movies', methods=['POST'])
def get_movies_from_cache():
    shown_movies = request.json

    movies = cacher.get_non_shown_movies(shown_movies)
    return jsonify(movies)


@app.route('/renew_cache', methods=['POST'])
def clean_cache():
    if start_queue():
        return jsonify()
    else:
        return forbidden_access()


def start_queue():
    if cacher.caching_available():
        thread = Thread(target=cacher.cache_all_pages)
        thread.start()
        return True
    else:
        return False


cacher = Cacher()


@app.route('/api')
def api_about():
    return render_template(API_TEMPLATE_URL)


@app.route('/api/list', methods=['GET'])
def api_main():
    return app.response_class(
        response=json.dumps(cacher.get_movies_data(), ensure_ascii=False),
        status=200,
        content_type="application/json; charset=utf-8"
    )


@app.route('/api/movie/<int:param>/', methods=['GET'])
def api_movie(param):
    url = 'http://www.afisha.ru/movie/{}'.format(param)
    movie_page = cacher.cached(url)
    return app.response_class(
        response=json.dumps(ai.json_data(movie_page), ensure_ascii=False),
        status=200,
        content_type="application/json; charset=utf-8"
    )


@app.route("/")
def films_list():
    main_page = render_template(TEMPLATE_URL)
    start_queue()
    return main_page

if __name__ == "__main__":
    app.run()
