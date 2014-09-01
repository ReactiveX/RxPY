(function (global, $, undefined) {
    alert("got here");
    function main() {
        alert("Running main");
        var $input = $('#textInput'),
            $results = $('#results');
        var ws = new WebSocket("wss://localhost:8080/ws");

        $input.keyup(function(ev) {
            msg = { query: ev.target.value };
            ws.send(JSON.stringify(msg));
        });

        ws.onmessage = function(msg) {
            var data = msg.data;
            var res = data[1];

            // Append the results
            $results.empty();

            $.each(res, function (_, value) {
              $('<li>' + value + '</li>').appendTo($results);
            });
        }
    }
    main();
}(window, jQuery));