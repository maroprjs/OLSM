
import mainViewConfigFile from './../config/MainViewConfig.json' assert { type: 'json' };
import agvViewConfigFile from './../config/AgvViewConfig.json' assert { type: 'json' };
var currentMainVideo = 0;
var videos = ""; //main
var currentAgvVideo = 0;
var agvVideos = ""; //


//fetch('./config/MainViewConfig.json')
//    .then((response) => response.json())
//    .then((json) => console.log(json));

var ready = (callback) => {
    if (document.readyState != "loading") callback();
    else document.addEventListener("DOMContentLoaded", callback);
}

ready(() => {
    var ioSocket;
    ioSocket = io();
    console.log("ready called");
    var mainViewConfig = JSON.stringify(mainViewConfigFile);
    var agvViewConfig = JSON.stringify(agvViewConfigFile);
    mainViewConfig = JSON.parse(mainViewConfig);
    agvViewConfig = JSON.parse(agvViewConfig);
    //console.log(mainViewConfig);
    //console.log(agvViewConfig);

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
                                            //https://stackoverflow.com/questions/21471116/html5-video-waiting-for-video-end-waiting-for-video-ready
      function playAgvSequence(stationName) { //https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/ended_event
        var videosrc = document.getElementById( stationName + '_video'); //https://www.experts-exchange.com/questions/28664145/play-multiple-videos-in-a-loop-using-HTML5-and-JavaScript.html
        videosrc.removeEventListener('ended', playAgvSequence);
        //console.log(currentAgvVideo);
        //console.log(agvVideos);
        //console.log(videos[currentAgvVideo]);
        if ((agvVideos[currentAgvVideo] != 'none') && (agvVideos[currentAgvVideo] != 'home')) {
            videosrc.src = agvVideos[currentAgvVideo];
        };
        currentAgvVideo = (currentAgvVideo + 1);
        if (currentAgvVideo < agvVideos.length ){
            videosrc.addEventListener('ended', playAgvSequence(stationName) ,false);
        }else{
            currentAgvVideo = 0;
        }
      };


      ioSocket.on('station_state_info', function (data) {
        console.log(data);
        //console.log(data.valueOf());
        var msg = data.split(',');
        var stationName = msg[0];
        var stationState = msg[1]; //FREE, UNEQUIPPED_ELECTRIC, UNEQUIPPED_HYBRID, EQUIPPED_ELECTRIC, EQUIPPED_HYBIRD, TEST_1, TEST_2
        var scenario = "";
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
        if ( (agvViewConfig[stationName].hasOwnProperty(stationState) ) == true ) {
            //ioSocket.emit('play_agv_scenario', agvViewConfigFile[stationName][stationState]); //this is received by browser to load appropriate video
            //ioSocket.emit('play_agv_scenario', agvViewConfig); //this is received by browser to load appropriate video
            
            var data = agvViewConfigFile[stationName][stationState];
            if (data["src"] != 'none'){
                agvVideos = data["src"];
                currentAgvVideo = 0;
                playAgvSequence(stationName);
            };
        }else{
            console.log("error: agvViewConfigFile TAG NOT DEFINED");
        };    
    });

    ioSocket.on('omron_pic', function (data) { //data = video source
        console.log(data); //= inspection_pic_01 inspection_pic_02 inspection_pic_03 inspection_pic_04
        
    });

    ioSocket.on('_play_main_scenario', function (data) { //data = video source
        //console.log(data);
        //console.log(data["src"]);
        if (data["src"] != 'none'){
            videos = data["src"];
            currentMainVideo = 0;
            playSequence();
        };

    });
    
    ioSocket.on('_play_agv_scenario', function (data) { //data = video source
        //console.log(data);
        var msg = data.split(',');
        var stationName = msg[0];
        var stationState = msg[1]; //FREE, UNEQUIPPED_ELECTRIC, UNEQUIPPED_HYBRID, EQUIPPED_ELECTRIC, EQUIPPED_HYBIRD, TEST_1, TEST_2
        console.log( "agv scenario: " + data["src"]);
        if (data["src"] != 'none'){
            agvVideos = data["src"];
            currentAgvVideo = 0;
            playAgvSequence();
        };

    });

	//});
    //var _video_src = document.getElementById('video_source').src = "videos/inspection.mp4";
});
