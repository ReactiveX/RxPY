"""
RxPY example running a Tornado server doing search queries against
Wikipedia to populate the autocomplete dropdown in the web UI. Start
using `python autocomplete.py` and navigate your web browser to
http://localhost:8080

Uses the RxPY AsyncIOScheduler (Python 3.4 is required)
"""

import os
import asyncio

from tornado.platform.asyncio import AsyncIOMainLoop
from tornado.escape import json_decode
from tornado.httputil import url_concat
from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler, StaticFileHandler, Application, url
from tornado.websocket import WebSocketHandler

from rx import operators as ops
from rx.scheduler.eventloop import AsyncIOScheduler
from rx.subject import Subject


def search_wikipedia(term):
    """Search Wikipedia for a given term"""
    url = 'http://en.wikipedia.org/w/api.php'

    params = {
        "action": 'opensearch',
        "search": term,
        "format": 'json'
    }
    # Must set a user agent for non-browser requests to Wikipedia
    user_agent = "RxPY/1.0 (https://github.com/dbrattli/RxPY; dag@brattli.net) Tornado/4.0.1"

    url = url_concat(url, params)

    http_client = AsyncHTTPClient()
    return http_client.fetch(url, method='GET', user_agent=user_agent)


class WSHandler(WebSocketHandler):
    def open(self):
        scheduler = AsyncIOScheduler(asyncio.get_event_loop())

        print("WebSocket opened")

        # A Subject is both an observable and observer, so we can both subscribe
        # to it and also feed (send) it with new values
        self.subject = Subject()

        # Get all distinct key up events from the input and only fire if long enough and distinct
        searcher = self.subject.pipe(
            ops.map(lambda x: x["term"]),
            ops.filter(lambda text: len(text) > 2),  # Only if the text is longer than 2 characters
            ops.debounce(0.750),                     # Pause for 750ms
            ops.distinct_until_changed(),            # Only if the value has changed
            ops.flat_map_latest(search_wikipedia)
        )

        def send_response(x):
            self.write_message(x.body)

        def on_error(ex):
            print(ex)

        searcher.subscribe(send_response, on_error, scheduler=scheduler)

    def on_message(self, message):
        obj = json_decode(message)
        self.subject.on_next(obj)

    def on_close(self):
        print("WebSocket closed")


class MainHandler(RequestHandler):
    def get(self):
        self.render("index.html")


def main():
    AsyncIOMainLoop().make_current()

    port = os.environ.get("PORT", 8080)
    app = Application([
        url(r"/", MainHandler),
        (r'/ws', WSHandler),
        (r'/static/(.*)', StaticFileHandler, {'path': "."})
    ])

    print("Starting server at port: %s" % port)
    app.listen(port)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
