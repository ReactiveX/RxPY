import rx
from rx import operators as ops
from rx.subjects import Subject
from rx.scheduler.mainloopscheduler import GtkScheduler

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class Window(Gtk.Window):

    def __init__(self):
        super().__init__()
        self.resize(600, 600)

        self.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
        self.connect('motion-notify-event', self.on_mouse_move)

        self.mousemove = Subject()

    def on_mouse_move(self, widget, event):
        self.mousemove.on_next((event.x, event.y))


def main():
    scheduler = GtkScheduler()
    scrolled_window = Gtk.ScrolledWindow()

    window = Window()
    window.connect("delete-event", Gtk.main_quit)

    container = Gtk.Fixed()

    scrolled_window.add(container)
    window.add(scrolled_window)
    text = 'TIME FLIES LIKE AN ARROW'

    def on_next(info):
        label, (x, y), i = info
        container.move(label, x + i*12 + 15, y)
        label.show()

    def handle_label(label, i):
        delayer = ops.delay(i*0.100)
        mapper = ops.map(lambda xy: (label, xy, i))

        return window.mousemove.pipe(
            delayer,
            mapper,
        )

    def make_label(char):
        label = Gtk.Label(label=char)
        container.put(label, 0, 0)
        label.hide()
        return label

    mapper = ops.map(make_label)
    labeler = ops.flat_map_indexed(handle_label)

    rx.from_(text).pipe(
        mapper,
        labeler,
    ).subscribe(on_next, on_error=print, scheduler=scheduler)

    window.show_all()

    Gtk.main()


if __name__ == '__main__':
    main()
