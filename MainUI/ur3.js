//UR3 robot handling here: robot is activated when car is filled and at station 2 (fill levek noted ba tagId)

//defines:
var IO_SOCKET_SERVER_URL = 'http://0.0.0.0/';
var UR3_IP_ADDRESS = "10.200.21.120"
var UR3_TCP_PORT = 12345 //29999

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

ioSocket.on('selector', function (data) {
    console.log(data);
    //console.log(data.valueOf());
    var msg = data.split(',');
    var stationName = msg[0];
    var tagId = msg[1];
    if (stationName == "station2"){
        if (tagId == "8ad1aae"){ 
            //start Robot
            console.log("TODO: start UR3 robot and disable slector for time of processing"); 
            tcpClient.write(data);
        };
    }

});


// Send a connection request to the server.
tcpClient.connect({ port: UR3_TCP_PORT, host: UR3_IP_ADDRESS }, function() {
    // If there is no error, the server has accepted the request and created a new 
    // socket dedicated to us.
    console.log('TCP connection established with the server.');

    // The client can now send data to the server by writing to its socket.
    tcpClient.write('Hello, server.');
});

// The client can also receive data from the server by reading from its socket.
tcpClient.on('data', function(chunk) {
    console.log(`Data received from the server: ${chunk.toString()}.`);
    
    // Request an end to the connection after the data has been received.
    tcpClient.end();
});

tcpClient.on('end', function() {
    console.log('Requested an end to the TCP connection');
});