import os

from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler, StaticFileHandler, Application, url
from tornado.escape import json_decode
from tornado import ioloop

from rx import operators as ops
from rx.subject import Subject

UP, DOWN, LEFT, RIGHT, B, A = 38, 40, 37, 39, 66, 65
codes = [UP, UP, DOWN, DOWN, LEFT, RIGHT, LEFT, RIGHT, B, A]


class WSHandler(WebSocketHandler):
    def open(self):
        print("WebSocket opened")

        # A Subject is both an observable and observer, so we can both subscribe
        # to it and also feed (on_next) it with new values
        self.subject = Subject()

        # Now we take on our magic glasses and project the stream of bytes into
        # a ...
        query = self.subject.pipe(
            # 1. stream of keycodes
            ops.map(lambda obj: obj["keycode"]),
            # 2. stream of windows (10 ints long)
            ops.window_with_count(10, 1),
            # 3. stream of booleans, True or False
            ops.flat_map(lambda win: win.pipe(ops.sequence_equal(codes))),
            # 4. stream of Trues
            ops.filter(lambda equal: equal)
        )
        # 4. we then subscribe to the Trues, and signal Konami! if we see any
        query.subscribe_(lambda x: self.write_message("Konami!"))

    def on_message(self, message):
        obj = json_decode(message)
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
