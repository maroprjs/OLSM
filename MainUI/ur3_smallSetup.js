//UR3 robot handling here: robot is activated when car is filled and at station 2 (fill levek noted ba tagId)

//defines:
var IO_SOCKET_SERVER_URL = 'http://0.0.0.0/';
var UR3_IP_ADDRESS = "10.200.20.162"
var UR3_TCP_PORT = 29999 //12345
var UR3_PROGRAMM = "flex_manu_01.urp"
var UR3_PROGRAMM2 = "flex_manu_02.urp"
var FAILED_TO_PLAY = false;
var robotEnabled = true;
var robotEnabledTimer = 20000;
var stationRoleValid = false;

const net = require('net');
const tcpClient = new net.Socket(); //https://plainenglish.io/blog/how-to-set-up-your-tcp-client-server-application-with-nodejs-from-scratch-5d218a1300f2

var ios = require('socket.io-client');


var ioSocket = ios.connect(IO_SOCKET_SERVER_URL, {
    reconnection: true
});

ioSocket.on('connect', function () {
    console.log("Connected to " + IO_SOCKET_SERVER_URL );
    ioSocket.emit('adduser', "station");
});

ioSocket.on('disconnect', function () {
    console.log("Disconnected from " + IO_SOCKET_SERVER_URL );
});

//requires that presenter publishes the mapping info prior plaving agv on station(via streamdeck/companion)!!
ioSocket.on('station_mapping_info', function (data) { //requires that presenter publishes the mapping info prior plaving agv on station(via streamdeck/companion)
    console.log(data);
    var msg = data.split(',');
    var stationName = msg[0]; //not needed
    var stationRole = msg[1];
    if (stationRole == "ASSEMBLY\n"){
       stationRoleValid = true;
       if(robotEnabled){ //disable any other request for a few seconds
          robotEnabled = false;
          console.log("loading UR3_PROGRAMM");
          tcpClient.connect({ port: UR3_TCP_PORT, host: UR3_IP_ADDRESS }, function() {
             tcpClient.write("load  " + UR3_PROGRAMM + "\n");
          });
          setTimeout(function(){
             robotEnabled = true;
             console.log("robotenabled")
          },3000);
       };
    };
    if (stationRole == "INSPECTION\n"){
       stationRoleValid = true;
       if(robotEnabled){ //disable any other request for a few seconds
          robotEnabled = false;
          console.log("loading UR3_PROGRAMM2");
          tcpClient.connect({ port: UR3_TCP_PORT, host: UR3_IP_ADDRESS }, function() {
             tcpClient.write("load  " + UR3_PROGRAMM2 + "\n");
          });
          setTimeout(function(){
             robotEnabled = true;
          },3000);
       };
    };
});

ioSocket.on('station_state_info', function (data) {
    console.log(data);
    //console.log(data.valueOf());
    var msg = data.split(',');
    var stationName = msg[0];
    var tagId = msg[1];
    var timerRobot = 2000; //15000
    
       if ((stationName == "station2")&&(stationRoleValid == true)){
          //if ((tagId == "EQUIPPED_ELECTRIC_PART2") || (tagId == "EQUIPPED_HYBRID_PART2") || (tagId == "EQUIPPED_ELECTRIC_PART1") || (tagId == "EQUIPPED_HYBRID_PART1") || (tagId == "UNEQUIPPED_ELECTRIC") || (tagId == "UNEQUIPPED_HYBRID")){ 
          if ((tagId == "EQUIPPED_ELECTRIC_PART2") || (tagId == "EQUIPPED_HYBRID_PART2")){ //|| (tagId == "EQUIPPED_ELECTRIC_PART1") || (tagId == "EQUIPPED_HYBRID_PART1")){
             if(robotEnabled){
                robotEnabled = false;
                //start Robot
                setTimeout(function(){
                   setTimeout( function(){
                     tcpClient.connect({ port: UR3_TCP_PORT, host: UR3_IP_ADDRESS }, function() {
                        console.log('TCP connection established with the server.');
                        // The client can now send data to the server by writing to its socket.
                        tcpClient.write('play\n');
                        setTimeout(function(){
                             robotEnabled = true;
                        },robotEnabledTimer);
                     });
                   },timerRobot);
                },2000);
             };
          }
          if (tagId == "00000000"){
             if (FAILED_TO_PLAY == true){
                tcpClient.connect({ port: UR3_TCP_PORT, host: UR3_IP_ADDRESS }, function() {
                   tcpClient.write("load  " + UR3_PROGRAMM + "\n");
               });
               FAILED_TO_PLAY = false;
             };
          };
      };
      if ((stationName == "station5")&&(stationRoleValid == true)){
          if ( (tagId == "UNEQUIPPED_ELECTRIC") || (tagId == "UNEQUIPPED_HYBRID")){
              //start Robot
              if(robotEnabled){
                robotEnabled = false;
                setTimeout(function(){
                  setTimeout( function(){
                       tcpClient.connect({ port: UR3_TCP_PORT, host: UR3_IP_ADDRESS }, function() {
                          // If there is no error, the server has accepted the request and create>
                          // socket dedicated to us.
                          console.log('TCP connection established with the server.');
                          // The client can now send data to the server by writing to its socket.
                          tcpClient.write('play\n');
                          setTimeout(function(){
                               robotEnabled = true;
                          },robotEnabledTimer);

                       });
                    },timerRobot);
                },2000);
             }; 
          };
          if (tagId == "00000000"){
             if (FAILED_TO_PLAY == true){
                tcpClient.connect({ port: UR3_TCP_PORT, host: UR3_IP_ADDRESS }, function() {
                   tcpClient.write("load  " + UR3_PROGRAMM2 + "\n");
               });
               FAILED_TO_PLAY = false;
             };
          };
      };
});


// Send a connection request to the server.
//tcpClient.connect({ port: UR3_TCP_PORT, host: UR3_IP_ADDRESS }, function() {
    // If there is no error, the server has accepted the request and created a new 
    // socket dedicated to us.
//    console.log('TCP connection established with the server.');

    // The client can now send data to the server by writing to its socket.
//    tcpClient.write('Hello, server.');
//});

// The client can also receive data from the server by reading from its socket.
tcpClient.on('data', function(chunk) {
    console.log(`Data received from the server: ${chunk.toString()}.`);
    if (chunk.toString().includes("Failed to execute: play") == true){
        console.log("failed to play");
        FAILED_TO_PLAY = true;
        //tcpClient.write("play\n");
    }; 
    if (chunk.toString().includes("File not found:") == true){
        console.log("File not found! Check Programms on Robot");
        FAILED_TO_PLAY = true;
    };
    // Request an end to the connection after the data has been received.
    tcpClient.end();
});

tcpClient.on('end', function() {
    console.log('Requested an end to the TCP connection');
    robotEnabled = true;
});

tcpClient.on('error', function(err) {
    //console.error('Connection error: ' + err);
    //console.error(new Error().stack);
    console.log("connection error detected");
    robotEnabled = true;
    tcpClient.end();
    //tcpClient.destroy();
});
