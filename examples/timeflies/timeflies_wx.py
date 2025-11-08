import wx

import reactivex
from reactivex import operators as ops
from reactivex.scheduler.mainloop import WxScheduler
from reactivex.subject import Subject


class Frame(wx.Frame):
    def __init__(self):
        super().__init__(None)
        self.SetTitle("Rx for Python rocks")
        self.SetSize((600, 600))

        # This Subject is used to transmit mouse moves to labels
        self.mousemove = Subject()

        self.Bind(wx.EVT_MOTION, self.OnMotion)

    def OnMotion(self, event):
        self.mousemove.on_next((event.GetX(), event.GetY()))


def main():
    app = wx.App()
    scheduler = WxScheduler(wx)

    app.TopWindow = frame = Frame()
    frame.Show()

    text = "TIME FLIES LIKE AN ARROW"

    def on_next(info):
        label, (x, y), i = info
        label.Move(x + i * 12 + 15, y)
        label.Show()

    def handle_label(label, i):
        delayer = ops.delay(i * 0.100)
        mapper = ops.map(lambda xy: (label, xy, i))

        return frame.mousemove.pipe(
            delayer,
            mapper,
        )

    def make_label(char):
        label = wx.StaticText(frame, label=char)
        label.Hide()
        return label

    mapper = ops.map(make_label)
    labeler = ops.flat_map_indexed(handle_label)

    reactivex.from_(text).pipe(
        mapper,
        labeler,
    ).subscribe(on_next, on_error=print, scheduler=scheduler)

    frame.Bind(wx.EVT_CLOSE, lambda e: (scheduler.cancel_all(), e.Skip()))
    app.MainLoop()


if __name__ == "__main__":
    main()
