import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtGui import QPainter, QPolygon, QPen
from PyQt5.QtCore import Qt, QPoint

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.points = []  # 폴리곤을 구성하는 점들을 저장할 리스트
        self.polygons = []  # 완성된 폴리곤들의 리스트

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 마우스 왼쪽 버튼 클릭 시 점 추가
            self.points.append(event.pos())
            self.setMouseTracking(True)
            
        elif event.button() == Qt.RightButton and self.points:
            # 마우스 오른쪽 버튼 클릭으로 폴리곤 완성
            self.setMouseTracking(False)
            self.polygons.append(self.points)
            self.points = []  # 새 폴리곤을 위해 점 리스트 초기화
            self.update()

    def mouseMoveEvent(self, event):
        if len(self.points)>1:
          del self.points[-1]
        self.points.append(event.pos())
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        painter.setPen(pen)

        # 미완성 폴리곤 그리기
        if self.points:
            n = len(self.points)
            for i in range(n - 1):
                painter.drawLine(self.points[i], self.points[i + 1])
            # 현재 그리는 선 표시
            painter.drawLine(self.points[-1], self.points[0])

        # 완성된 폴리곤 그리기
        for polygon in self.polygons:
            if polygon:
                painter.drawPolygon(QPolygon(polygon))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)
        self.setWindowTitle("PyQt Polygon Drawing Example")
        self.setGeometry(100, 100, 800, 600)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
