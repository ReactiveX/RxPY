$(function () {
    var result = $('#result');
    var ws = new WebSocket("wss://localhost/ws");

    $(document).keyup(function(ev) {
        console.log(ev.keyCode);
        msg = { key: ev.keyCode };
        ws.send(msg);
    });

    ws.onmessage = function(msg) {
        result.html('KONAMI!').fadeOut(2000);   // print the result
    };
});