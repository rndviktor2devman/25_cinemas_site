(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
var socket = io.connect('https://' + document.domain + ':' + location.port);
var MoviesList = React.createClass({displayName: "MoviesList",
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
        setTimeout(this._start_with_pause, 5000);
        setInterval(this._ping_server, 60000);
    },

    _clean_movies(){
        var movies = [];
        this.setState({movies, showSpinner: true});
    },

    _initialize(){
        this.setState({showSpinner: true});
    },

    _start_with_pause(){
        var sendUrl = document.URL + 'on_startup';
        $.ajax({
          url: sendUrl,
          type: 'POST',
          data: JSON.stringify(this.state),
          contentType: 'application/json;charset=UTF-8',
          success: function(data) {
              var json = $.parseJSON(data);
              this.setState({
                  movies: json.data.movies,
                  allMovies: json.data.count,
                  showSpinner: json.data.loading,
              });
          }.bind(this),
          error: function(xhr, status, err) {
            console.error(this.props.url, status, err.toString());
          }.bind(this)
        });
    },

    _ping_server(){
        socket.emit('ping_action')
    },

    _load_movie(movie){
        var movies = this.state.movies;
        var moviesCount = movie.count;
        movies.push(movie.data);
        this.setState({movies, showSpinner: true, allMovies: moviesCount});
    },

    _finish_loading(){
        this.setState({showSpinner: false});
    },

    handleClick(){
        var sendUrl = document.URL + 'renew_cache';
        $.ajax({
          url: sendUrl,
          type: 'POST',
          data: JSON.stringify(this.state),
          contentType: 'application/json;charset=UTF-8',
          success: function(data) {
              this.setState({showSpinner: true});
          }.bind(this),
          error: function(xhr, status, err) {
            console.error(this.props.url, status, err.toString());
          }.bind(this)
        });
    },

    render() {
        var movies = this.state.movies;
        var showSpinner = this.state.showSpinner;
        var allMovies = this.state.allMovies;
        return(
            React.createElement("div", null, 
                React.createElement("div", {className: "state_panel col-md-12 row"}, 
                    React.createElement("div", {className: "col-xs-4"}, 
                        React.createElement("i", {className: showSpinner ? 'fa fa-refresh fa-spin fa-3x fa-fw' : 'fa fa-refresh fa-3x fa-fw', onClick: this.handleClick}
                        )
                    ), 
                    React.createElement("div", {className: "col-xs-7"}, 
                        React.createElement("h4", null, "Загружено ", movies.length, "/", allMovies, " описаний")
                    )
                ), 
                React.createElement("ul", {className: "list-unstyled"}, 
                     movies.map(function (movie) {
                        return React.createElement("li", null, 
                            React.createElement("div", {className: "movie_class col-md-12 row"}, 
                                React.createElement("div", {className: "col-xs-4"}, 
                                    React.createElement("div", {className: "moviediv"}, 
                                        React.createElement("a", {href:  movie.url}, 
                                            React.createElement("img", {src:  movie.image, className: "img-rounded movie_image", alt:  movie.title})
                                        )
                                    ), 
                                    React.createElement("ul", null, 
                                        React.createElement("li", null, React.createElement("b", null, "Режиссер: "),  movie.director), 
                                        React.createElement("li", null, React.createElement("b", null, "Продолжительность: "),  movie.duration), 
                                        React.createElement("li", null, React.createElement("b", null, "Дата релиза: "),  movie.release)
                                    )
                                ), 
                                React.createElement("div", {className: "col-xs-7"}, 
                                    React.createElement("div", {className: "row"}, 
                                        React.createElement("h2", null, React.createElement("a", {href:  movie.url},  movie.name))
                                    ), 
                                    React.createElement("div", {className: "row"}, 
                                      React.createElement("ul", null, 
                                        React.createElement("li", null, React.createElement("b", null, "Жанр: "),  movie.genre), 
                                        React.createElement("li", null, React.createElement("b", null, "Оценка/Голосовало: "),  movie.rating, React.createElement("b", null, "/"),  movie.voted)
                                      )
                                    ), 
                                    React.createElement("h3", null, React.createElement("a", {href:  movie.url},  movie.title)), 
                                    React.createElement("p", null,  movie.description), 
                                    React.createElement("p", null, React.createElement("b", null, "Описание:")), 
                                    React.createElement("p", null,  movie.text)
                                )
                            )
                        )
                    }) 
                )
            )
        )
    }
});

var movies = [];

ReactDOM.render(
    React.createElement(MoviesList, {items: movies}), document.getElementById("main_list")
);

},{}]},{},[1]);
