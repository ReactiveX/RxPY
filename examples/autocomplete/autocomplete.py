import os

import tornado
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler, StaticFileHandler, Application, url
from tornado.escape import json_encode, json_decode
from tornado import ioloop

from rx.subjects import Subject

# Search Wikipedia for a given term
def search_wikipedia(term):
    url = 'http://en.wikipedia.org/w/api.php'

    def handle_request(response):
        if response.error:
            print("Error:", response.error)
        else:
            print(response.body)

    data = {
        "action": 'opensearch',
        "format": 'json',
        "search": term
    }

    http_client = AsyncHTTPClient()
    http_client.fetch(url, handle_request)


class WSHandler(WebSocketHandler):
    def open(self):
        print("WebSocket opened")

        # A Subject is both an observable and observer, so we can both subscribe
        # to it and also feed (on_next) it with new values
        self.subject = Subject()

        # Get all distinct key up events from the input and only fire if long enough and distinct
        query = self.subject.filter(
            lambda text: len(length) > 2 # Only if the text is longer than 2 characters
        ).throttle(
            750 # Pause for 750ms
        ).distinct_until_changed() # Only if the value has changed

        searcher = query.flat_map_latest(search_wikipedia)

        searcher.subscribe(lambda x: self.write_message(x))

    def on_message(self, message):
        obj = json_decode(message)
        print(obj)
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
