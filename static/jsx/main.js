var MoviesList = React.createClass({
    getInitialState() {
        return {
            movies: [],
            showSpinner: false,
            allMovies: 0,
        };
    },

    componentDidMount(){
        setInterval(this._ping_server, 5000);
        setInterval(this._check_movies_list, 1000);
    },

    _clean_movies(){
        var movies = [];
        this.setState({movies, showSpinner: true});
    },

    _ping_server(){
        var sendUrl = document.URL + 'ping';
        $.ajax({
          url: sendUrl,
          dataType: 'json',
          cache: false,
          success: function(data) {
              var movies_count = this.state.movies.length;
              var server_movies = data.data.count;
              if(server_movies < movies_count){
                  this._clean_movies();
              }
              this.setState({showSpinner:(movies_count < server_movies), allMovies: server_movies});
          }.bind(this),
          error: function(xhr, status, err) {
            console.error(this.props.url, status, err.toString());
          }.bind(this)
        });
    },

    _check_movies_list(){
        var movies = this.state.movies;
        if(movies.length < this.state.allMovies)
        {
            var sendUrl = document.URL + 'get_movies';
            var urls = movies.map(function(movie) {
                return movie.url;
            });
            $.ajax({
              url: sendUrl,
              type: 'POST',
              data: JSON.stringify(urls),
              contentType: 'application/json;charset=UTF-8',
              success: function(data) {
                  var json = $.parseJSON(data);
                  this.setState({
                      movies: json.data.movies,
                  });
              }.bind(this),
              error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
              }.bind(this)
            });
        }
    },

    handleClick(){
        var sendUrl = document.URL + 'renew_cache';
        $.ajax({
          url: sendUrl,
          type: 'POST',
          data: JSON.stringify(this.state),
          contentType: 'application/json;charset=UTF-8',
          success: function(data) {
              var json = $.parseJSON(data);
              if(json.data==='dropped') {
                  this._clean_movies();
              } else {
                  console.log('forbidden dropping cache');
              }
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
            <div>
                <div className="state_panel col-md-12 row">
                    <div className="col-xs-4">
                        <i className={showSpinner ? 'fa fa-refresh fa-spin fa-3x fa-fw' : 'fa fa-refresh fa-3x fa-fw'} onClick={this.handleClick}>
                        </i>
                    </div>
                    <div className="col-xs-7">
                        <h4>Загружено {movies.length}/{allMovies} описаний</h4>
                    </div>
                </div>
                <ul className="list-unstyled">
                    { movies.map(function (movie) {
                        return <li>
                            <div className="movie_class col-md-12 row">
                                <div className="col-xs-4">
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
                                <div className="col-xs-7">
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