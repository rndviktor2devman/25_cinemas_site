from flask import Flask, render_template, json, Response
from cacher import Cacher
import afisha_interaction as ai
import time
from threading import Thread
from flask_socketio import SocketIO, emit


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

AFISHA_URL = "http://www.afisha.ru/msk/schedule_cinema/"
TEMPLATE_URL = "films_list.html"
API_TEMPLATE_URL = "api_description.html"


def load_movie_callback(data, count):
    socketio.emit('movie_loaded', {'data': data, 'count': count})


def loading_finish():
    socketio.emit('finish_loading')


@socketio.on('ping_action')
def ping_by_timeout():
    if cacher.afisha_timed_out():
        print('renew cache')
        thread = Thread(target=cacher.renew_cache)
        thread.start()


@socketio.on('on_startup')
def get_cached_movies():
    movies = cacher.get_movies_data()
    loading = cacher.caching_pending
    count = cacher.count_refs
    socketio.emit('startup_cache', {'movies': movies, 'loading': loading, 'count': count})


@socketio.on('trigger_clean_movies')
def clean_cache():
    socketio.emit('clean_movies')
    print('clean cache')
    cacher.clean_cache()
    start_queue()


def start_queue():
    if cacher.caching_available():
        thread = Thread(target=cacher.cache_all_pages)
        thread.start()


cacher = Cacher(load_movie_callback, loading_finish)


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
    socketio.run(app)
