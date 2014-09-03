import os
from collections import OrderedDict

import tornado
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler, StaticFileHandler, Application, url
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat
from tornado.escape import json_encode, json_decode
from tornado.concurrent import Future
from tornado import ioloop

from rx.subjects import Subject

# Search Wikipedia for a given term

def search_wikipedia(term):
    print("search_wikipedia")

    url = 'http://en.wikipedia.org/w/api.php'

    params = OrderedDict([
        ("action", 'opensearch'),
        ("search", term),
        ("format", 'json')
    ])
    headers = {
        "User-Agent": "RxPY/1.0 (https://github.com/dbrattli/RxPY; dag@brattli.net) Tornado/4.0.1",
        "Accept" : "application/json"
    }

    def handle_request(response):
        print(response)

    url = url_concat(url, params)
    print(url)
    http_client = AsyncHTTPClient()
    return http_client.fetch(url, handle_request, method='GET', headers=headers)
    
class WSHandler(WebSocketHandler):
    def open(self):
        print("WebSocket opened")

        # A Subject is both an observable and observer, so we can both subscribe
        # to it and also feed (on_next) it with new values
        self.subject = Subject()

        # Get all distinct key up events from the input and only fire if long enough and distinct
        query = self.subject.select(
            lambda x: x["term"]
        ).filter(
            lambda text: len(text) > 2 # Only if the text is longer than 2 characters
        ).throttle(
            750 # Pause for 750ms
        ).distinct_until_changed() # Only if the value has changed

        searcher = query.flat_map_latest(search_wikipedia)

        def send_response(x):
            print("send_response")
            print(x.body)
            self.write_message(x.body)

        def on_error(ex):
            print(ex)

        searcher.subscribe(send_response, on_error)

    def on_message(self, message):
        obj = json_decode(message)
        print("on_message(%s)" % obj["term"])
        self.subject.on_next(obj)

    def on_close(self):
        print("WebSocket closed")

class MainHandler(RequestHandler):
    def get(self):
        self.render("index.html")

def main():
    port = os.environ.get("PORT", 8080)
    app = Application([
        url(r"/", MainHandler),
        (r'/ws', WSHandler),
        (r'/static/(.*)', StaticFileHandler, {'path': "."})
    ])
    print("Starting server at port: %s" % port)
    app.listen(port)
    ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()
