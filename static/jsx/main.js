var socket = io.connect('http://' + document.domain + ':' + location.port);
var MoviesList = React.createClass({
    getInitialState() {
        return {
            movies: [],
            showSpinner: false,
            allMovies: 0,
        };
    },

    componentDidMount(){
        socket.on('connect', this._initialize);
        socket.on('movie_loaded', this._load_movie);
        socket.on('finish_loading', this._finish_loading);
        socket.on('clean_movies', this._clean_movies);
        socket.on('startup_cache', this._load_movies);
    },

    _clean_movies(){
        var movies = [];
        this.setState({movies, showSpinner: true});
    },

    _initialize(){
        socket.emit('on_startup')
    },

    _load_movies(movies_data){
        var movies = movies_data.movies;
        var loading = movies_data.loading;
        var count = movies_data.count;
        this.setState({movies, showSpinner: loading, allMovies: count});
    },

    _load_movie(movie){
        var movies = this.state.movies;
        var moviesCount = movie.count;
        movies.push(movie.data);
        this.setState({movies, showSpinner: true, allMovies: moviesCount});
    },

    _finish_loading(){
        var movies = this.state.movies;
        this.setState({movies, showSpinner: false});
    },

    handleClick(){
        console.log('click');
        socket.emit('trigger_clean_movies');
    },

    render() {
        var movies = this.state.movies;
        var showSpinner = this.state.showSpinner;
        var allMovies = this.state.allMovies;
        return(
            <div>
                <div className="state_panel col-md-12 row">
                    <div className="col-md-4">
                        <i className={showSpinner ? 'fa fa-refresh fa-spin fa-3x fa-fw' : 'fa fa-refresh fa-3x fa-fw'} onClick={this.handleClick}>
                        </i>
                    </div>
                    <div className="col-md-7">
                        <h4>Загружено {movies.length}/{allMovies} описаний</h4>
                    </div>
                </div>
                <ul className="list-unstyled">
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