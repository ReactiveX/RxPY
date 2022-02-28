from typing import Any, Tuple
from tkinter import Tk, Label, Frame, Event
import tkinter

import reactivex
from reactivex import operators as ops, Observable
from reactivex.subject import Subject
from reactivex.scheduler.mainloop import TkinterScheduler


def main():
    root = Tk()
    root.title("Rx for Python rocks")
    scheduler = TkinterScheduler(root)

    mousemoves: Subject[Event[Any]] = Subject()

    frame = Frame(root, width=600, height=600)
    frame.bind("<Motion>", mousemoves.on_next)

    text = "TIME FLIES LIKE AN ARROW"

    def on_next(info: Tuple[tkinter.Label, "Event[Frame]", int]):
        label, ev, i = info
        label.place(x=ev.x + i * 12 + 15, y=ev.y)

    def label2stream(
        label: tkinter.Label, index: int
    ) -> Observable[Tuple[tkinter.Label, "Event[Frame]", int]]:
        label.config(dict(borderwidth=0, padx=0, pady=0))

        return mousemoves.pipe(
            ops.map(lambda ev: (label, ev, index)),
            ops.delay(index * 0.1),
        )

    def char2label(char: str) -> Label:
        return Label(frame, text=char)

    reactivex.from_(text).pipe(
        ops.map(char2label),
        ops.flat_map_indexed(label2stream),
    ).subscribe(on_next, on_error=print, scheduler=scheduler)

    frame.pack()
    root.mainloop()


if __name__ == "__main__":
    main()
