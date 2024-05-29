import sys

from PyQt5 import QtWidgets


class Label(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        if not event.buttons():
            print(event.pos())
        super().mouseMoveEvent(event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Label()
    w.resize(640, 480)
    w.show()
    sys.exit(app.exec_())