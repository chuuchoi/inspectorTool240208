import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QFileDialog
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtCore import Qt

class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PyQt5 Image Viewer')
        self.setGeometry(160, 90, 1600, 900)

        # 레이아웃 설정
        self.layout = QHBoxLayout(self)
        self.firstLayout = QVBoxLayout()
        
        # 폴더 선택 버튼 및 경로 라벨 레이아웃
        self.buttonLayout = QHBoxLayout()
        self.chooseButton = QPushButton('경로 선택')
        self.chooseButton.clicked.connect(self.chooseFolder)
        self.buttonLayout.addWidget(self.chooseButton)

        self.folderPathLabel = QLabel('폴더가 선택되지 않았습니다.')
        self.buttonLayout.addWidget(self.folderPathLabel)
        self.firstLayout.addStretch(11)
        self.firstLayout.addLayout(self.buttonLayout)

        # 리스트 위젯 설정
        self.listWidget = QListWidget()
        self.firstLayout.addWidget(self.listWidget)
        self.listWidget.currentItemChanged.connect(self.onItemSelected)
        self.layout.addLayout(self.firstLayout)

        # 이미지 라벨
        self.imageLabel = QLabel('이미지가 여기에 표시됩니다.')
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.imageLabel)

    def chooseFolder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Image Folder')
        if folder_path:
            self.folderPathLabel.setText(folder_path)
            self.listImagesInFolder(folder_path)

    def listImagesInFolder(self, folder_path):
        self.listWidget.clear()
        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                self.listWidget.addItem(file_name)

    def onItemSelected(self, current, previous):
        if current:
            image_path = os.path.join(self.folderPathLabel.text(), current.text())
            pixmap = QPixmap(image_path)
            self.imageLabel.setPixmap(pixmap.scaled(900, 900, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def keyReleaseEvent(self, event: QKeyEvent):
        print(event.key(),'/  A :',Qt.Key_Up)
        if event.key() == Qt.Key_Left:
            currentRow = self.listWidget.currentRow()
            totalItems = self.listWidget.count()
            if currentRow < totalItems - 1:
                self.listWidget.setCurrentRow(currentRow + 1)
            else:
                self.listWidget.setCurrentRow(0)  # 리스트의 마지막에 도달했을 때, 다시 첫 항목으로 돌아가기
        if event.key() == Qt.Key_Right:
            currentRow = self.listWidget.currentRow()
            totalItems = self.listWidget.count()
            if currentRow > 0:
                self.listWidget.setCurrentRow(currentRow - 1)
            else:
                self.listWidget.setCurrentRow(totalItems - 1)  # 리스트의 마지막에 도달했을 때, 다시 첫 항목으로 돌아가기
        # else:
            # super().keyReleaseEvent(event)
            
    def resizeEvent(self, event):
        super(ImageViewer, self).resizeEvent(event)
        new_width = self.width() * 0.3  # 창 가로 크기의 30%
        self.listWidget.setFixedWidth(int(new_width))
        self.listWidget.setFixedHeight(240)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageViewer()
    ex.show()
    sys.exit(app.exec_())
