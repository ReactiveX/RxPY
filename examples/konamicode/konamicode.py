from vase import Vase
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

query.subscribe(lambda x: print("Konami!"))

app = Vase(__name__)

@app.route(path="/")
def hello(request):
    return "Hello Vase!"

@app.endpoint(path="/ws/echo")
class EchoEndpoint:
    """
    WebSocket endpoint
    Has the following attributes:
    `bag` - a dictionary that is shared between all instances of this endpoint
    `transport` - used to send messages into the websocket
    """
    def on_connect(self):
        print("You are successfully connected")

    def on_message(self, message):
        # print(ord(input))
        # print(chr(ord(input)))  # show some activity
        # observer.on_next(input) # feed observer and notify subscribers

        self.transport.send(message)

    def on_close(self, exc=None):
        print("Connection closed")

if __name__ == '__main__':
    app.run()
