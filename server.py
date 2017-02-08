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
MAIN_PAGE_TIMEOUT = 60 * 30     # 30 minutes index timeout


def test_connect(data):
    print('call emit signal %s' % data)
    socketio.emit('movie_loaded', {'data': data})


cacher = Cacher(test_connect)


@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))


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
    main_page = cacher.get_cached_page('/')
    if main_page is not None:
        return main_page

    movies_data = cacher.get_movies_data()
    main_page = render_template(TEMPLATE_URL, movies=movies_data)
    if len(movies_data) == 0:
        print('start queue %s' % time.time())
        thread = Thread(target=cacher.cache_all_pages)
        thread.start()
        print('enqueued %s' % time.time())
    elif cacher.all_movies_cached():
        cacher.cache_page('/', main_page, MAIN_PAGE_TIMEOUT)
    return main_page

if __name__ == "__main__":
    socketio.run(app)
