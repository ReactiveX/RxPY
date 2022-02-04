from typing import Any, Tuple
from tkinter import Tk, Label, Frame, Event
import tkinter

import rx
from rx import operators as ops, Observable
from rx.subject import Subject
from rx.scheduler.mainloop import TkinterScheduler


def main():
    root = Tk()
    root.title("Rx for Python rocks")
    scheduler = TkinterScheduler(root)

    mousemove: Subject[Event[Any]] = Subject()

    frame = Frame(root, width=600, height=600)

    frame.bind("<Motion>", mousemove.on_next)

    text = "TIME FLIES LIKE AN ARROW"

    def on_next(info: Tuple[tkinter.Label, tkinter.Event[Any], int]):
        label, ev, i = info
        label.place(x=ev.x + i * 12 + 15, y=ev.y)

    def handle_label(
        label: tkinter.Label, i: int
    ) -> Observable[Tuple[tkinter.Label, tkinter.Event[Any], int]]:
        label.config(dict(borderwidth=0, padx=0, pady=0))

        mapper = ops.map(lambda ev: (label, ev, i))
        delayer = ops.delay(i * 0.1)

        return mousemove.pipe(delayer, mapper)

    mapper = ops.map(lambda c: Label(frame, text=c))
    labeler = ops.flat_map_indexed(handle_label)

    rx.from_(text).pipe(mapper, labeler).subscribe(
        on_next, on_error=print, scheduler=scheduler
    )

    frame.pack()
    root.mainloop()


if __name__ == "__main__":
    main()
