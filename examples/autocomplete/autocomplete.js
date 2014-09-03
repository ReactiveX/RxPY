(function (global, $, undefined) {
    function main() {
        var $input = $('#textInput'),
            $results = $('#results');
        var ws = new WebSocket("ws://localhost:8080/ws");

        $input.keyup(function(ev) {
            msg = { term: ev.target.value };
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