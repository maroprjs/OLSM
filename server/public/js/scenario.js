var gDemoState = "IDLE"; //INVENTORY, ASSEMBLY, CABLING, PROGRAMMING, INSPECTION, FINAL

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
		//console.log(data);
		//console.log(data.valueOf());
        var msg = data.split(',');
        var stationName = msg[0];
        var tagId = msg[1];
        //var videopath = video_source[stationId, tagId]
        //if (gDemoState){}
        if (stationName == "station1"){
            //if (tagId == "00000000"){
            if (tagId == "8ad1aae"){ 
                document.getElementById('video_source').src = "videos/inventory.mp4";
            //}else if(tagId == "00000000"){ 
            //        document.getElementById('video_source').src = "videos/Big_Buck_Bunny_1080_10s_1MB.mp4";  
            };
            if (tagId == "f82684d"){ 
                document.getElementById('video_source').src = "videos/queue.mp4";
            };
        }
        if (stationName == "station2"){
            if (tagId == "f82684d"){ 
                document.getElementById('video_source').src = "videos/assembly.mp4";
            };
        }
        if (stationName == "station3"){
            if (tagId == "f82684d"){ 
                console.log("cabling");
                document.getElementById('video_source').src = "videos/cabling.mp4";
            };
        }
        if (stationName == "station4"){
            if (tagId == "f82684d"){ 
                document.getElementById('video_source').src = "videos/programming.mp4";
            };
        }
        if (stationName == "station5"){
            if (tagId == "f82684d"){ 
                document.getElementById('video_source').src = "videos/inspection.mp4";
            };
            if (tagId == "00000000"){ 
                document.getElementById('video_source').src = "videos/Big_Buck_Bunny_1080_10s_1MB.mp4";
            };
        }
    
	});
    //var _video_src = document.getElementById('video_source').src = "videos/inspection.mp4";
});