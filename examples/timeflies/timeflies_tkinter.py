from tkinter import Tk, Label, Frame

from rx import from_
from rx import operators
from rx.subjects import Subject
from rx.concurrency import TkinterScheduler


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

        mapper = operators.map(lambda ev: (label, ev, i))
        delayer = operators.delay(i*100)

        return mousemove.pipe(
            delayer,
            mapper
        )

    labler = operators.flat_mapi(handle_label)
    mapper = operators.map(lambda c: Label(frame, text=c))

    from_(text).pipe(
        mapper,
        labler
    ).subscribe_(on_next, on_error=lambda ex: print(ex), scheduler=scheduler)

    frame.pack()
    root.mainloop()


if __name__ == '__main__':
    main()
