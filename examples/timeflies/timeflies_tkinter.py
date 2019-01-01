from tkinter import Tk, Label, Frame

from rx import Observable
from rx.subjects import Subject
from rx.concurrency import TkinterScheduler

from rx.operators.delay import delay
from rx.operators.map import map
from rx.operators.flatmap import flat_mapi


def main():
    root = Tk()
    root.title("Rx for Python rocks")
    scheduler = TkinterScheduler(root)

    mousemove = Subject()

    frame = Frame(root, width=600, height=600)

    frame.bind("<Motion>", mousemove.on_next)

    text = 'TIME FLIES LIKE AN ARROW'
    labels = [Label(frame, text=c) for c in text]

    def on_next(info):
        label, ev, i = info
        label.place(x=ev.x + i*12 + 15, y=ev.y)

    def handle_label(label, i):
        label.config(dict(borderwidth=0, padx=0, pady=0))

        mapper = map(lambda ev: (label, ev, i))
        delayer = delay(i*100)

        return mousemove.pipe(
            delayer,
            mapper
        )

    labler = flat_mapi(handle_label)

    Observable.from_(labels).pipe(
        labler
    ).subscribe_(on_next, scheduler=scheduler)

    frame.pack()
    root.mainloop()


if __name__ == '__main__':
    main()
