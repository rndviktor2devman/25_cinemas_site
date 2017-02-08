var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connect', function() {
        socket.emit('my event', {data: 'I\'m connected!'});
    });
    socket.on('movie_loaded', function (movie) {
        console.log(movie);
        var d = document.getElementById('movies_row');
        var stub = document.getElementById('stub');
        if(stub){
            d.removeChild(stub);
        }
    });
