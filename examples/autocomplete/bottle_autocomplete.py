"""
The automcomplete example rewritten for bottle / gevent.
- Requires besides bottle and gevent also the geventwebsocket pip package
- Instead of a future we create the inner stream for flat_map_latest manually
"""
from bottle import request, Bottle, abort
import gevent
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
import json, requests
import rx

class WikiFinder:
    tmpl = 'http://en.wikipedia.org/w/api.php'
    tmpl += '?action=opensearch&search=%s&format=json'

    def __init__(self, term):
        self.res = r = gevent.event.AsyncResult()
        gevent.spawn(lambda: requests.get(self.tmpl % term).text).link(r)

    def subscribe(self, on_next, on_err, on_compl):
        try:
            self.res.get()
            on_next(self.res.value)
        except Exception as ex:
            on_err(ex.args)
        on_compl()


app, PORT = Bottle(), 8081
scheduler = rx.concurrency.GEventScheduler()


@app.route('/ws')
def handle_websocket():

    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        abort(400, 'Expected WebSocket request.')
    stream = rx.subjects.Subject()
    query = stream.map(
        lambda x: x["term"]
    ).filter(
        lambda text: len(text) > 2  # Only if text is longer than 2 characters
    ).debounce(
        0.750,  # Pause for 750ms
        scheduler=scheduler
    ).distinct_until_changed()  # Only if the value has changed

    searcher = query.flat_map_latest(lambda term: WikiFinder(term))

    def send_response(x):
        wsock.send(x)

    def on_error(ex):
        print(ex)

    searcher.subscribe(send_response, on_error)

    while True:
        try:
            message = wsock.receive()
            # like {'term': '<current textbox val>'}
            obj = json.loads(message)
            stream.on_next(obj)
        except WebSocketError:
            break



@app.route('/static/autocomplete.js')
def get_js():
    # blatantly ignoring bottle's template engine:
    return open('autocomplete.js').read().replace('8080', str(PORT))

@app.route('/')
def get_index():
    return open("index.html").read()


if __name__ == '__main__':
    h = ('0.0.0.0', PORT)
    server = gevent.pywsgi.WSGIServer(h, app, handler_class=WebSocketHandler)
    server.serve_forever()

