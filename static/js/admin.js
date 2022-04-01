/**
 * Created by Sylvain on 14.09.2016.
 */

/**
 * Log messages from the server
 */

var ws = new WebSocket('ws://' + document.domain + '/ws/wstest')
var pingTime = 0;

function encode_message(header, body) {
    var obj = {
        'header': header,
        'body': body
    };
    return JSON.stringify(obj);
}

ws.onopen = function () {
    console.log("Connected !");
    ping();
};

ws.onerror = function (error) {
    console.log('WebSocket Error ' + error);
};

ws.onmessage = function (m) {
    var data = JSON.parse(m.data);

    switch (data.header) {

        case 'users-online':
            $('#span-users-online').text("Total users online : " + data.body);
            break;

        case 'pong':
            pong();
            break;

        default:
            console.log(data);
            break;
    }
};

function ping() {
    pingTime = new Date().getTime();
    ws.send(encode_message('ping', ""));
    setTimeout(ping, 2000);
}

function pong() {
    var pongTime = new Date().getTime();
    $('#span-ping').text("Ping : " + (pongTime - pingTime) + " ms");
}

$('#button-start').click(function () {
    ws.send(encode_message('start', ""));
});

$('#button-start-10').click(function () {
    ws.send(encode_message('start-10', ""));

    var timer = 10;
    (function () {

        if (timer > 0) {
            $('#span-timeout').text(timer);
            timer --;
        } else {
            $('#span-timeout').text("START");
        }

        setTimeout(arguments.callee, 1000);
    })();
});
