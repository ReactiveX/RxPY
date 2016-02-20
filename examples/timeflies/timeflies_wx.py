from rx.subjects import Subject
from rx.concurrency import WxScheduler

import wx


class Frame(wx.Frame):

    def __init__(self):
        super(Frame, self).__init__(None)
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

    text = 'TIME FLIES LIKE AN ARROW'
    labels = [wx.StaticText(frame, label=char) for char in text]

    def handle_label(i, label):

        def on_next(pos):
            x, y = pos
            label.MoveXY(x + i*12 + 15, y)
            label.Show()

        frame.mousemove.delay(i*100, scheduler=scheduler).subscribe(on_next)

    for i, label in enumerate(labels):
        handle_label(i, label)
        label.Hide()

    frame.Bind(wx.EVT_CLOSE, lambda e: (scheduler.cancel_all(), e.Skip()))
    app.MainLoop()


if __name__ == '__main__':
    main()
