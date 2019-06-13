from tkinter import Tk, Label, Frame

import rx
from rx import operators as ops
from rx.subject import Subject
from rx.scheduler.mainloop import TkinterScheduler


def main():
    root = Tk()
    root.title("Rx for Python rocks")
    scheduler = TkinterScheduler(root)

    mousemove = Subject()

    frame = Frame(root, width=600, height=600)

    frame.bind("<Motion>", mousemove.on_next)

    text = 'TIME FLIES LIKE AN ARROW'

    def on_next(info):
        label, ev, i = info
        label.place(x=ev.x + i*12 + 15, y=ev.y)

    def handle_label(label, i):
        label.config(dict(borderwidth=0, padx=0, pady=0))

        mapper = ops.map(lambda ev: (label, ev, i))
        delayer = ops.delay(i*0.1)

        return mousemove.pipe(
            delayer,
            mapper
        )

    labeler = ops.flat_map_indexed(handle_label)
    mapper = ops.map(lambda c: Label(frame, text=c))

    rx.from_(text).pipe(
        mapper,
        labeler
    ).subscribe(on_next, print, scheduler=scheduler)

    frame.pack()
    root.mainloop()


if __name__ == '__main__':
    main()
