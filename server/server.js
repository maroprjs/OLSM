//defines:
var THIS_SERVER_IP = '0.0.0.0';
var THIS_SERVER_HTTP_PORT = 80; //same used for IO

var THIS_SERVER_UDP_PORT_1 = 5555; //to receice controllino status


//dependencies and global variables:
var express = require('express');
var app = express();
var http = require('http').createServer(app);
var ioSocket = require('socket.io')(http);
var dgram = require('dgram');
//var bodyParser = require("body-parser"); //for POST requests 
var udpdserver1 = dgram.createSocket('udp4'); //to receice controllino status

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
    console.log("connectio");
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
});

//------------------------ udp function ---------------------------------
// udp listener for stations:
udpdserver1.on('listening', function () {
    var address = udpdserver1.address();
    console.log('UDP Server listening on ' + address.address + ":" + address.port);
});

udpdserver1.on('message', function (message, remote) {
    var msg = message.toString();
    console.log(remote.address + ':' + remote.port + ' - ' + msg);
    var msgElementArray = msg.split(',');
    console.log(msgElementArray[0]); //station name
    console.log(msgElementArray[1]); //tag id
	if(ioSocket){
        //console.log("inside socket");
		ioSocket.emit('selector', msg);
	}
});

udpdserver1.bind(THIS_SERVER_UDP_PORT_1, THIS_SERVER_IP);

