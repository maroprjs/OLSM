//defines:
var THIS_SERVER_IP = '0.0.0.0';
var THIS_SERVER_HTTP_PORT = 80; //same used for IO
var THIS_SERVER_UDP_PORT_1 = 5555; //to receice  status


//dependencies and global variables:
var express = require('express');
var app = express();
var http = require('http').createServer(app);
var ioSocket = require('socket.io')(http);
var dgram = require('dgram');
//var bodyParser = require("body-parser"); //for POST requests 
var udpdserver1 = dgram.createSocket('udp4'); //to receice controllino status

//var gStation1State = "FREE"; //"FREE", "OCCUPIED", "STATE_CHECK"
//var gStation2State = "FREE"; //"FREE", "OCCUPIED", "STATE_CHECK"
//var gStation3State = "FREE"; //"FREE", "OCCUPIED", "STATE_CHECK"
//var gStation4State = "FREE"; //"FREE", "OCCUPIED", "STATE_CHECK"
//var gStation5State = "FREE"; //"FREE", "OCCUPIED", "STATE_CHECK"

//------------------ app: -------------------------------------------
// Webserver
http.listen(THIS_SERVER_HTTP_PORT, () => {
 console.log("Http Get Server running on port " + THIS_SERVER_HTTP_PORT );
});

// use static data
app.use(express.static(__dirname + '/public'));
// call path 
app.get('/', function (req, res) {
    // open the file
    res.sendfile(__dirname + '/public/index.html');
});


//----------------- IO Socket ----------------------------------------
ioSocket.sockets.on('connection', function (socket) {
    console.log("connection");
    socket.on('adduser', function () {
        socket.room = 'user';
        socket.join('user');
        console.log('User ' + socket.id + ' connected.');
    });
    // when the user log out.. perform this
    socket.on('logout', function () {
        // echo globally that this client has left
        socket.leave(socket.room);
        console.log('User ' + socket.id + ' left.');
    });
    // when the user disconnects.. perform this
    socket.on('disconnect', function () {
        socket.leave(socket.room);
        console.log('User ' + socket.id + ' disconnected.');
    });
    socket.on('send-clients', function (data) {});
    socket.on('command', function (data) {
        console.log(data.toString());
        var umsg = Buffer.from( data );
        //var udp_client = dgram.createSocket('udp4');
        //udp_client.send(umsg, 0, umsg.length, CONVEYOR_UDP_PORT, CONVEYOR_IP, function(error) {
        //  if(error){
        //    udp_client.close();
            //sendUdpMsg( );
        //  }else{
        //    udp_client.close();
        //    console.log('sent UDP: ' + umsg);
        //  }
        //});

    });

    //socket.on('selector', function (data) { //which station sequence
        //console.log("selector received");
    //    ioSocket.emit('selector', data);


    //});
    socket.on('play_main_scenario', function (data) { //emit provided by view.js, forwarded to browser
        //console.log("selector received");
        ioSocket.emit('play_main_scenario', data);


    });
    socket.on('play_agv_scenario', function (data) { ////emit provided by view.js, forwarded to browser
        //console.log("selector received");
        ioSocket.emit('play_agv_scenario', data);


    })

    socket.on('omron_pic', function (data) { ////emit provided by view.js, forwarded to browser
        console.log(data);
        ioSocket.emit('omron_pic', data);


    })

});

//------------------------ udp function---------------------------------
// udp listener for stations:
udpdserver1.on('listening', function () {
    var address = udpdserver1.address();
    console.log('UDP Server listening on ' + address.address + ":" + address.port);
});

udpdserver1.on('message', function (message, remote) {
    var msg = message.toString();
    //if(ioSocket){
        //console.log("inside socket");
    //    ioSocket.emit('udp1_msg', msg);
    //};   
    console.log(remote.address + ':' + remote.port + ' - ' + msg);
    //filterUdpFromStation(msg);
    if(ioSocket){
        //console.log("inside socket");
        //console.log(msg);
        ioSocket.emit('station_state_info', msg); //this is received by view.js, to chose appropriate video
     };
});

udpdserver1.bind(THIS_SERVER_UDP_PORT_1, THIS_SERVER_IP);


/*
*
*   TODO: THIS IS OBSOLETE: delete this!
*
*/
//just filter out when agv is placed on station and removed from station:
function filterUdpFromStation(msg){
    var msgElementArray = msg.split(',');
    //console.log(msgElementArray[0]); //station name
    //console.log(msgElementArray[1]); //tag id
    var stationName = msgElementArray[0];
    if (stationName == "station1"){
        
        if (gStation1State == "FREE"){
            if(ioSocket){
                //console.log("inside socket");
                //console.log(msg);
                ioSocket.emit('selector', msg);
             };
             gStation1State = "OCCUPIED";
             armStation1StatusCheck();
        };
        if (gStation1State == "STATE_CHECK"){
            gStation1State = "OCCUPIED";
        };
    };
    if (stationName == "station2"){
        
        if (gStation2State == "FREE"){
            if(ioSocket){
                //console.log("inside socket");
                ioSocket.emit('selector', msg);
             };
             gStation2State = "OCCUPIED";
             armStation2StatusCheck();
        };
        if (gStation2State == "STATE_CHECK"){
            gStation2State = "OCCUPIED";
        };
    };
    if (stationName == "station3"){
        
        if (gStation3State == "FREE"){
            if(ioSocket){
                //console.log("inside socket");
                ioSocket.emit('selector', msg);
             };
             gStation3State = "OCCUPIED";
             armStation3StatusCheck();
        };
        if (gStation3State == "STATE_CHECK"){
            gStation3State = "OCCUPIED";
        };
    };
    if (stationName == "station4"){
        
        if (gStation4State == "FREE"){
            if(ioSocket){
                //console.log("inside socket");
                ioSocket.emit('selector', msg);
             };
             gStation4State = "OCCUPIED";
             armStation4StatusCheck();
        };
        if (gStation4State == "STATE_CHECK"){
            gStation4State = "OCCUPIED";
        };
    };
    if (stationName == "station5"){
        
        if (gStation5State == "FREE"){
            if(ioSocket){
                //console.log("inside socket");
                ioSocket.emit('selector', msg);
             };
             gStation5State = "OCCUPIED";
             armStation5StatusCheck();
        };
        if (gStation5State == "STATE_CHECK"){
            gStation5State = "OCCUPIED";
        };
    };

};

//------------------------ check station state ---------------------------------

function armStation1StatusCheck() {
  setTimeout(function() { 
    if (gStation1State == "STATE_CHECK"){   //if station is still in state check, it means that no udp message has arrived in given time frame
                                            //and most likely no AGV on Station 
        if(ioSocket){
            ioSocket.emit('selector', 'station1,00000000'); //00000000 means reset ()
         };
         gStation1State = "FREE";
    }; 
    if (gStation1State == "OCCUPIED"){
        gStation1State = "STATE_CHECK";
        armStation1StatusCheck();   //incomming station message sets state always back to occupied as long as agv is present
                                    //this function needs to call itself to check if station sent a message
                                    //otherwise, just emit that station is free again 
    };

  }, 1500) //TODO: check if 2 seconds is appropriate
};  

function armStation2StatusCheck() {
    setTimeout(function() { 
      if (gStation2State == "STATE_CHECK"){   //if station is still in state check, it means that no udp message has arrived in given time frame
                                              //and most likely no AGV on Station 
          if(ioSocket){
              ioSocket.emit('selector', 'station2,00000000'); //00000000 means reset ()
           };
           gStation2State = "FREE";
      }; 
      if (gStation2State == "OCCUPIED"){
          gStation2State = "STATE_CHECK";
          armStation2StatusCheck();   //incomming station message sets state always back to occupied as long as agv is present
                                      //this function needs to call itself to check if station sent a message
                                      //otherwise, just emit that station is free again 
      };
  
    }, 1500) //TODO: check if 2 seconds is appropriate  
};

function armStation3StatusCheck() {
    setTimeout(function() { 
      if (gStation3State == "STATE_CHECK"){   //if station is still in state check, it means that no udp message has arrived in given time frame
                                              //and most likely no AGV on Station 
          if(ioSocket){
              ioSocket.emit('selector', 'station3,00000000'); //00000000 means reset ()
           };
           gStation3State = "FREE";
      }; 
      if (gStation3State == "OCCUPIED"){
          gStation3State = "STATE_CHECK";
          armStation3StatusCheck();   //incomming station message sets state always back to occupied as long as agv is present
                                      //this function needs to call itself to check if station sent a message
                                      //otherwise, just emit that station is free again 
      };
  
    }, 1500) //TODO: check if 2 seconds is appropriate
  };  

  function armStation4StatusCheck() {
    setTimeout(function() { 
      if (gStation4State == "STATE_CHECK"){   //if station is still in state check, it means that no udp message has arrived in given time frame
                                              //and most likely no AGV on Station 
          if(ioSocket){
              ioSocket.emit('selector', 'station4,00000000'); //00000000 means reset ()
           };
           gStation4State = "FREE";
      }; 
      if (gStation4State == "OCCUPIED"){
          gStation4State = "STATE_CHECK";
          armStation4StatusCheck();   //incomming station message sets state always back to occupied as long as agv is present
                                      //this function needs to call itself to check if station sent a message
                                      //otherwise, just emit that station is free again 
      };
  
    }, 1500) //TODO: check if 2 seconds is appropriate
  };  

  function armStation5StatusCheck() {
    setTimeout(function() { 
      if (gStation5State == "STATE_CHECK"){   //if station is still in state check, it means that no udp message has arrived in given time frame
                                              //and most likely no AGV on Station 
          if(ioSocket){
              ioSocket.emit('selector', 'station5,00000000'); //00000000 means reset ()
           };
           gStation5State = "FREE";
      }; 
      if (gStation5State == "OCCUPIED"){
          gStation5State = "STATE_CHECK";
          armStation5StatusCheck();   //incomming station message sets state always back to occupied as long as agv is present
                                      //this function needs to call itself to check if station sent a message
                                      //otherwise, just emit that station is free again 
      };
  
    }, 1500) //TODO: check if 2 seconds is appropriate
  };  

  
  
  
