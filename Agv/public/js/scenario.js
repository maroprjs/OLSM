
import mainViewConfigFile from './../config/AgvViewConfig.json' assert { type: 'json' };
var currentMainVideo = 0;
var videos = ""; //main
var currentAgvVideo = 0;


var ready = (callback) => {
    if (document.readyState != "loading") callback();
    else document.addEventListener("DOMContentLoaded", callback);
}

ready(() => {
    var ioSocket;
    ioSocket = io();
    console.log("ready called");
    var mainViewConfig = JSON.stringify(mainViewConfigFile);
    mainViewConfig = JSON.parse(mainViewConfig);
    //console.log(mainViewConfig);

    ioSocket.on('connect', function () {
        //call the server-side function 'adduser' and send one parameter (value of prompt)
        console.log("socket connected");
        ioSocket.emit('adduser', "GUIscenario");
    });

                                            //https://stackoverflow.com/questions/21471116/html5-video-waiting-for-video-end-waiting-for-video-ready
    function playMainSequence(stationName) { //Main //https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/ended_event 

        var videosrc = document.getElementById('video_source'); //https://www.experts-exchange.com/questions/28664145/play-multiple-videos-in-a-loop-using-HTML5-and-JavaScript.html
        videosrc.removeEventListener('ended', playMainSequence);
        //console.log(currentMainVideo);
        //console.log(videos);
        console.log(stationName);
        console.log(videos[currentMainVideo]);
        if (videos[currentMainVideo] != 'none') {
            videosrc.src = videos[currentMainVideo];
        };
        currentMainVideo = (currentMainVideo + 1);
        if (currentMainVideo < videos.length ){
            videosrc.addEventListener('ended', playMainSequence(stationName) ,false);
        }else{
            currentMainVideo = 0;
        }
      };

      ioSocket.on('agv_state_info', function (data) {
        console.log(data);
        //console.log(data.valueOf());
        var msg = data.split(',');
        var stationName = msg[0];
        var stationState = msg[1]; //FREE, UNEQUIPPED_ELECTRIC, UNEQUIPPED_HYBRID, EQUIPPED_ELECTRIC, EQUIPPED_HYBIRD, TEST_1, TEST_2
        var scenario = "";
        if (stationName != "UNDEFINED"){
                if ( (mainViewConfig[stationName].hasOwnProperty(stationState) ) == true ) {
                    var data = mainViewConfigFile[stationName][stationState];
                    if (data["src"] != 'none'){
                        videos = data["src"];
                        currentMainVideo = 0;
                        playMainSequence(stationName);
                    };
                }else{
                    console.log("error: mainViewConfigFile TAG NOT DEFINED!!!!!!!!!!");
                };   
        }
    });

});