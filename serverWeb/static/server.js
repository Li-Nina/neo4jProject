var http = require('http');

var server = http.createServer();
server.on('request',function(req,res){
    console.log(1)
    res.writeHead(200,{
        'Content-Type':'text/plain',
        'Access-Control-Allow-Origin':'*',
        "Access-Control-Allow-Headers":"Content-Type,Content-Length, Authorization, Accept,X-Requested-With",
        "Access-Control-Allow-Methods":"PUT,POST,GET,DELETE,OPTIONS",
        //"Access-Control-Allow-Credentials":"true"

    });
    res.end('Hello World\n');
})
server.listen(12020);
console.log('server runing at 3000')