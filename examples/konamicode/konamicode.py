import tornado
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler, StaticFileHandler, Application, url
from tornado import ioloop

from rx.subjects import Subject

codes = [
    224, 72, # up
    224, 72, # up
    224, 80, # down
    224, 80, # down
    224, 75, # left
    224, 77, # right
    224, 75, # left
    224, 77, # right
    98, # b
    97  # a
]

# A Subject is both an observable and observer, so we can both subscribe to it
# and also feed it with values
observable = observer = Subject()

# Now we take on our magic glasses and project the stream of bytes into ...
#   1. a stream of integer ordinals
#   1. a stream of windows (18 ints long)
#   2. a stream of booleans, True or False
#   3. a strues of Trues
#   4. we then subscribe to the Trues, and write Konami! if we see any
query = observable \
    .select(lambda byte: ord(byte)) \
    .window_with_count(18, 1) \
    .select_many(lambda win: win.sequence_equal(codes)) \
    .where(lambda equal: equal)

#query.subscribe(lambda x: print("Konami!"))

class WSHandler(WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        print("message: %s" % message)
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")

class MainHandler(RequestHandler):
    def get(self):
        self.render("index.html")

def main():
    port = 8080
    app = Application([
        (r'/ws', WSHandler),
        url(r"/", MainHandler),
        (r'/static/(.*)', StaticFileHandler, {'path': "."})
    ])
    print("Starting server at port: %s" % port)
    app.listen(port)
    ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()
