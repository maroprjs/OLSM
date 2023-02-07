//defines:
var IO_SOCKET_SERVER_URL = 'http://0.0.0.0/';

var ios = require('socket.io-client');
var ioSocket = ios.connect(IO_SOCKET_SERVER_URL, {
    reconnection: true
});


//var gDemoState = "IDLE"; //INVENTORY, ASSEMBLY, CABLING, PROGRAMMING, INSPECTION, FINAL

ioSocket.on('connect', function () {
    console.log("Connected to " + IO_SOCKET_SERVER_URL );
    ioSocket.emit('adduser', "station");
});

ioSocket.on('disconnect', function () {
    console.log("Disconnected from " + IO_SOCKET_SERVER_URL );
});

ioSocket.on('selector', function (data) {
    console.log(data);
    //console.log(data.valueOf());
    var msg = data.split(',');
    var stationName = msg[0];
    var tagId = msg[1];
    var scenario = "";
    //var videopath = video_source[stationId, tagId]
    //if (gDemoState){}
    if (stationName == "station1"){
        //if (tagId == "00000000"){
        if (tagId == "8ad1aae"){ 
            scenario = "videos/inventory.mp4";
        //}else if(tagId == "00000000"){ 
        //        document.getElementById('video_source').src = "videos/Big_Buck_Bunny_1080_10s_1MB.mp4";  
        };
        if (tagId == "f82684d"){ 
            scenario = "videos/queue.mp4";
        };
    }
    if (stationName == "station2"){
        if (tagId == "f82684d"){ 
            scenario = "videos/assembly.mp4";
        };
    }
    if (stationName == "station3"){
        if (tagId == "f82684d"){ 
            console.log("cabling");
            scenario = "videos/cabling.mp4";
        };
    }
    if (stationName == "station4"){
        if (tagId == "f82684d"){ 
            scenario = "videos/programming.mp4";
        };
    }
    if (stationName == "station5"){
        if (tagId == "f82684d"){ 
            scenario = "videos/inspection.mp4";
        };
        if (tagId == "00000000"){ 
            scenario = "videos/Big_Buck_Bunny_1080_10s_1MB.mp4";
        };
    };
    if(ioSocket){
        ioSocket.emit('play_scenario', scenario);
     };

});

