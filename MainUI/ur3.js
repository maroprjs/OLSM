//UR3 robot handling here: robot is activated when car is filled and at station 2 (fill levek noted ba tagId)

//defines:
var IO_SOCKET_SERVER_URL = 'http://0.0.0.0/';
var UR3_IP_ADDRESS = "10.200.20.53"
var UR3_TCP_PORT = 29999 //12345
var UR3_PROGRAMM = "mwc23_01.urp"
var FAILED_TO_PLAY = false;
var robotEnabled = true;
var robotEnabledTimer = 60000;

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

ioSocket.on('station_state_info', function (data) {
    console.log(data);
    //console.log(data.valueOf());
    var msg = data.split(',');
    var stationName = msg[0];
    var tagId = msg[1];
    var timerRobot = 2000; //15000
    if(robotEnabled == true){
      robotEnabled = false;
       if (stationName == "station2"){
          if ((tagId == "EQUIPPED_ELECTRIC_PART2") || (tagId == "EQUIPPED_HYBRID_PART2")){ 
              //start Robot
              console.log("TODO: start UR3 robot and disable slector for time of processing"); 
              //tcpClient.write(data);
              // Send a connection request to the server.
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
          };
          if (tagId == "00000000"){
             if (FAILED_TO_PLAY == true){
                tcpClient.connect({ port: UR3_TCP_PORT, host: UR3_IP_ADDRESS }, function() {
                   tcpClient.write("load  " + UR3_PROGRAMM + "\n");
               });
               FAILED_TO_PLAY = false;
             };
          };
      }
    }
   

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
});

tcpClient.on('error', function(err) {
    //console.error('Connection error: ' + err);
    //console.error(new Error().stack);
    console.log("connection error detected");
    tcpClient.end();
});
