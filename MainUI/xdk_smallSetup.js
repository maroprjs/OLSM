//XDK cam emulation handling here: led is activated when car is filled and at station 5 (fill levek noted ba tagId)

//defines:
var IO_SOCKET_SERVER_URL = 'http://0.0.0.0/';
var XDK_IP_ADDRESS = 'coap://10.200.20.181/';
var xdkEnabled = true;
var xdkEnabledTimer = 30000;

const net = require('net');
const tcpClient = new net.Socket(); //https://plainenglish.io/blog/how-to-set-up-your-tcp-client-server-application-with-nodejs-from-scratch-5d218a1300f2

var ios = require('socket.io-client');

const coap = require('coap');
var creq = coap.request( XDK_IP_ADDRESS );

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
    
      if (stationName == "station5"){
          if ( (tagId == "UNEQUIPPED_ELECTRIC") || (tagId == "UNEQUIPPED_HYBRID")){
             if (xdkEnabled){
               xdkEnabled = false;
               console.log("writing O");
               creq = coap.request( XDK_IP_ADDRESS );
               creq.write("O");
               creq.end();
               setTimeout( function(){
                 creq = coap.request( XDK_IP_ADDRESS );
                 console.log("writing o");
                 creq.write("o");
                 creq.end();
                 setTimeout( function(){
                   creq = coap.request( XDK_IP_ADDRESS );
                   console.log("writing O");
                   creq.write("O");
                   creq.end();
                   setTimeout( function(){
                     creq = coap.request( XDK_IP_ADDRESS );
                     console.log("writing o");
                     creq.write("o");
                     creq.end();
                     setTimeout( function(){
                       creq = coap.request( XDK_IP_ADDRESS );
                       console.log("writing O");
                       creq.write("O");
                       creq.end();
                       setTimeout( function(){
                         creq = coap.request( XDK_IP_ADDRESS );
                         console.log("writing o");
                         creq.write("o");
                         creq.end();
                       },3000);
                     },3000);
                   },3000);
                 },3000);

               },3000);
               setTimeout(function(){
                 xdkEnabled = true;
               },xdkEnabledTimer);
             };

       };
    };
});


