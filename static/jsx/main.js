var socket = io.connect('http://' + document.domain + ':' + location.port);
var MoviesList = React.createClass({
    getInitialState() {
        return {
            movies: [],
            showSpinner: false
        };
    },

    componentDidMount(){
        socket.on('init', this._initialize);
        socket.on('movie_loaded', this._load_movie);
    },

    _initialize(data){
        var {movies, show} = data;
        this.setState({movies, showSpinner: show});
    },

    _load_movie(movie){
        var movies = this.state.movies;
        movies.push(movie.data);
        this.setState({movies, showSpinner: true});
    },

    render() {
        var movies = this.state.movies;
        var showSpinner = this.state.showSpinner;
        return(
            <div>
                <div className="row">
                    <div className={showSpinner ? 'loader' : 'loader hidden'}></div>
                </div>
                <ul>
                    { movies.map(function (movie) {
                        return <li>
                            <div className="movie_class col-md-12 row">
                                <div className="col-md-4">
                                    <div className="moviediv">
                                        <a href={ movie.url }>
                                            <img src={ movie.image } className="img-rounded movie_image" alt={ movie.title }/>
                                        </a>
                                    </div>
                                    <ul>
                                        <li><b>Режиссер: </b>{ movie.director }</li>
                                        <li><b>Продолжительность: </b>{ movie.duration }</li>
                                        <li><b>Дата релиза: </b>{ movie.release }</li>
                                    </ul>
                                </div>
                                <div className="col-md-7">
                                    <div className="row">
                                        <h2><a href={ movie.url }>{ movie.name }</a></h2>
                                    </div>
                                    <div className="row">
                                      <ul>
                                        <li><b>Жанр: </b>{ movie.genre }</li>
                                        <li><b>Оценка/Голосовало: </b>{ movie.rating }<b>/</b>{ movie.voted }</li>
                                      </ul>
                                    </div>
                                    <h3><a href={ movie.url }>{ movie.title }</a></h3>
                                    <p>{ movie.description }</p>
                                    <p><b>Описание:</b></p>
                                    <p>{ movie.text }</p>
                                </div>
                            </div>
                        </li>
                    }) }
                </ul>
            </div>
        )
    }
});

var movies = [];

ReactDOM.render(
    <MoviesList items={movies}/>, document.getElementById("main_list")
);