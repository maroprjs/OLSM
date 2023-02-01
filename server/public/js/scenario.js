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
        ioSocket.emit('adduser', "GUI");
    });
    ioSocket.on('selector', function (data) {
		console.log(data);
		//var test = String(data);
		console.log(data.valueOf());
        var stationId = data[0];
        var tagId = data[1];
        var videopath = video_source[stationId, tagId]
        document.getElementById('video_source').src = "videos/inspection.mp4";

	});
    //var _video_src = document.getElementById('video_source').src = "videos/inspection.mp4";
});