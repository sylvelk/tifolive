/**
 * Created by Sylvain on 28.07.2016.
 */

screen.keepAwake = true;


var partition = [];
var tempo = 0;
var ws = new WebSocket('ws://' + document.domain + '/ws/wstest')
var pingTime = 0;
var timeOffset = 0;

function get_partition() {
    $.ajax(
        {
            type: "GET",
            url: "/ajax/tifodata",
            dataType: 'json',
            data: {
                'stadium_short': location.pathname.split('/')[1],
                'sector_short': location.pathname.split('/')[3],
                'row_short': location.pathname.split('/')[4],
                'seat_short': location.pathname.split('/')[5],
            },
            success: function (response) {

                console.log("Ajax received");

                if (response.status == "200") {
                    partition = response.data.colors;
                    tempo = response.data.tempo;
                }
                else if (response.status == "400") {
                    console.log("No tifo found !");
                }
                else {
                    console.log(response);
                }
            },
            error: function (ts) {
                console.log("Ajax error : " + ts.responseText);
            }
        }
    );
}

function encode_message(header, body) {
    var obj = {
        'header': header,
        'body': body
    };
    return JSON.stringify(obj);
}

ws.onopen = function () {
    console.log("Connected !");
    ping_time();
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

        case 'pong-time':
            pong_time(data.body);
            break;

        case 'start-time':
            start_time(data.body);
            break;

        default:
            console.log(data);
            break;
    }
};

function ping_time() {
    ws.send(encode_message('ping-time', ""));
    pingTime = new Date().getTime();
}

function pong_time(data) {
    var pongTime = new Date().getTime();
    $('#span-ping').text("Ping : " + (pongTime - pingTime) + " ms");
    var averageTime = (pingTime + pongTime) / 2;
    timeOffset = Math.floor(data - averageTime);
    console.log("Time offset : " + timeOffset);
    get_partition();
}

function start_time(data) {
    console.log("Data : " + data);
    var startTime = data - timeOffset;
    console.log("Compensated data : " + startTime);
    var currentTime = new Date().getTime();
    console.log("Current time : " + currentTime);
    console.log("Delay : " + (startTime - currentTime));

    start_time.timer = setInterval(function () {
        console.log("TIFO START");
        console.log(startTime - new Date().getTime());
        start_tifo();
    }, startTime - currentTime);
}

function setIntervalAndExecute(fn, t) {
    fn();
    return (setInterval(fn, t));
}

function start_tifo() {
    clearInterval(start_time.timer);
    start_tifo.counter = 0;

    var i = setIntervalAndExecute(
        function () {
            $('html').css('background-color', partition[start_tifo.counter]);
            start_tifo.counter++;
            if (start_tifo.counter > partition.length) {
                clearInterval(i);
            }
        }, tempo);
}

$('#button-fullscreen').click(function () {
        if (screenfull.enabled) {
            screenfull.request();
        }
    }
);

