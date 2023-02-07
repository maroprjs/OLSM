

var ready = (callback) => {
    if (document.readyState != "loading") callback();
    else document.addEventListener("DOMContentLoaded", callback);
}

ready(() => {
    var ioSocket;
    ioSocket = io();
    console.log("ready called");
    ioSocket.on('connect', function () {
        //call the server-side function 'adduser' and send one parameter (value of prompt)
        console.log("socket connected");
        ioSocket.emit('adduser', "GUIscenario");
    });

    ioSocket.on('play_scenario', function (data) { //data = video source
        if (data != "") document.getElementById('video_source').src = data;
    });
    
	//});
    //var _video_src = document.getElementById('video_source').src = "videos/inspection.mp4";
});