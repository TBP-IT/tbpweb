/*jshint unused:false*/
function loadVideo(path) {
    var player = document.getElementById('player');
    var videoSource = document.getElementById('video');

    videoSource.setAttribute('src', path);
    player.load();
    player.play();
  }
