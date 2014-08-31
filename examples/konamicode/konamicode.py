import tornado
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler, StaticFileHandler, Application, url
from tornado.escape import json_encode, json_decode
from tornado import ioloop

from rx.subjects import Subject

codes = [
    38, # up
    38, # up
    40, # down
    40, # down
    37, # left
    39, # right
    37, # left
    39, # right
    66, # b
    65  # a
]

class WSHandler(WebSocketHandler):
    def open(self):
        print("WebSocket opened")

        # A Subject is both an observable and observer, so we can both subscribe to it
        # and also feed it with values
        self.subject = Subject()

        # Now we take on our magic glasses and project the stream of bytes into a ...    
        query = self.subject.select(
                # 1. stream of keycodes
               lambda obj: obj["keycode"]
            ).window_with_count(
                # 2. stream of windows (10 ints long)
                10, 1
            ).select_many(
                # 3. stream of booleans, True or False
                lambda win: win.sequence_equal(codes)
            ).where(
                # 4. stream of Trues
                lambda equal: equal
            )

        # 4. we then subscribe to the Trues, and signal Konami! if we see any
        query.subscribe(lambda x: self.write_message("Konami!"))

    def on_message(self, message):
        obj = json_decode(message)
        self.subject.on_next(obj)

    def on_close(self):
        print("WebSocket closed")

class MainHandler(RequestHandler):
    def get(self):
        self.render("index.html")

def main():
    port = 8080
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
