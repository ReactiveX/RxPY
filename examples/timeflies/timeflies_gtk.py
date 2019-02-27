from rx import operators as ops
from rx.subjects import Subject
from rx.concurrency.mainloopscheduler import GtkScheduler

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

    labels = [Gtk.Label(label=char) for char in text]
    for label in labels:
        container.put(label, 0, 0)

    def handle_label(i, label):

        def on_next(pos):
            x, y = pos
            container.move(label, x + i*12 + 15, y)

        window.mousemove.pipe(
            ops.delay(i*0.100, scheduler=scheduler),
            ).subscribe(on_next)

    for i, label in enumerate(labels):
        handle_label(i, label)

    window.show_all()

    Gtk.main()


if __name__ == '__main__':
    main()
