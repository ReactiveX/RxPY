from rx.subjects import Subject
from rx.concurrency import QtScheduler
import sys

try:
    from PyQt4 import QtCore
    from PyQt4.QtGui import QWidget, QLabel
    from PyQt4.QtGui import QApplication
except ImportError:
    try:
        from PyQt5 import QtCore
        from PyQt5.QtWidgets import QApplication, QWidget, QLabel
    except ImportError:
        from PySide import QtCore
        from PySide.QtGui import QWidget, QLabel
        from PySide.QtGui import QApplication


class Window(QWidget):

    def __init__(self):
        super(QWidget, self).__init__()
        self.setWindowTitle("Rx for Python rocks")
        self.resize(600, 600)
        self.setMouseTracking(True)

        # This Subject is used to transmit mouse moves to labels
        self.mousemove = Subject()

    def mouseMoveEvent(self, event):
        self.mousemove.on_next((event.x(), event.y()))


def main():
    app = QApplication(sys.argv)
    scheduler = QtScheduler(QtCore)

    window = Window()
    window.show()

    text = 'TIME FLIES LIKE AN ARROW'
    labels = [QLabel(char, window) for char in text]

    def handle_label(i, label):

        def on_next(pos):
            x, y = pos
            label.move(x + i*12 + 15, y)
            label.show()

        window.mousemove.delay(i*100, scheduler=scheduler).subscribe(on_next)

    for i, label in enumerate(labels):
        handle_label(i, label)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
