import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QPoint

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.points = []  # 폴리곤을 구성하는 점들을 저장할 리스트

    def mousePressEvent(self, event):
        # 마우스 왼쪽 버튼 클릭 시 점 추가
        if event.button() == Qt.LeftButton:
            self.points.append(event.pos())
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        painter.setPen(pen)

        # 점들 사이를 선으로 연결
        n = len(self.points)
        for i in range(1, n):
            painter.drawLine(self.points[i-1], self.points[i])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)
        self.setWindowTitle("PyQt Continuous Line Drawing Example")
        self.setGeometry(100, 100, 800, 600)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
