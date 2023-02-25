//OMRON TM5-700 robot handling here: robot is activated when car is filled and at station 5 (fill levek noted ba tagId)

//defines:
var IO_SOCKET_SERVER_URL = 'http://0.0.0.0/';
var TM5_IP_ADDRESS = "10.200.20.61"
var TCP_PORT = 12345 //29999

const net = require('net');
//const tcpServer = net.createServer(onClientConnection); //https://www.yld.io/blog/building-a-tcp-service-using-node-js/
var server = net.createServer();    
var tcpConnection;

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
    if (stationName == "station5"){
        if ((tagId == "UNEQUIPPED_ELECTRIC")||(tagId == "UNEQUIPPED_HYBRID")){ 
            //start Robot
            console.log("TODO: start disable slector for time of processing"); 
            //tcpClient.write(data);
            if (tcpConnection != undefined){
               tcpConnection.write("true\r\n");
            }else{
              console.log("No TCP client!!");
            };
        };
    }

});

server.on('connection', handleConnection);

server.listen(TCP_PORT, function() {    
    console.log('server listening to %j', server.address());  
  });

function handleConnection(conn) {
    var remoteAddress = conn.remoteAddress + ':' + conn.remotePort;  
    console.log('new client connection from %s', remoteAddress);
    conn.setEncoding('utf8');
    conn.on('data', onConnData);  
    conn.once('close', onConnClose);  
    conn.on('error', onConnError);
    tcpConnection = conn;
    function onConnData(d) {  
        console.log('connection data from %s: %j', remoteAddress, d);  
        //conn.write(d);  
        //inspection_pic_01
        if(ioSocket){
            //console.log("inside socket");
           //console.log(d);
           ioSocket.emit('omron_pic', d); //this is received by view.js, to chose appropriate video
        };

    }
    function onConnClose() {  
        console.log('connection from %s closed', remoteAddress);  
    }
    function onConnError(err) {  
        console.log('Connection %s error: %s', remoteAddress, err.message);  
    }  
}
