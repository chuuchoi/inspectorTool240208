import sys
import json
import cv2
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os

#CSV 파일초기화
columns = ["file_path_1", "information", "count"]
result_df = pd.DataFrame(columns=columns)
columns1 = ["file_path_1", "information", "count"]
result_df1 = pd.DataFrame(columns=columns1)
columns2 = ["file_name_1", "count"]
result_df2 = pd.DataFrame(columns=columns2)

class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Folder Browser")
        self.setGeometry(100, 100, 1200, 900)

        layout = QHBoxLayout()
        layout1 = QVBoxLayout()
        self.setLayout(layout)
        layout.addLayout(layout1)

        self.folderPathBtn = QPushButton("폴더 경로 선택")
        self.folderPathBtn.clicked.connect(self.selectFolderPath)
        layout1.addWidget(self.folderPathBtn)

        self.folderPathBtn = QPushButton("상위 폴더로 이동")
        self.folderPathBtn.clicked.connect(self.goToParentFolder)
        layout1.addWidget(self.folderPathBtn)

        self.folderPathBtn = QPushButton("csv추출")
        self.folderPathBtn.clicked.connect(self.readAllJson)
        layout1.addWidget(self.folderPathBtn)

        self.folderPathLabel = QLabel('폴더가 선택되지 않았습니다.')
        self.folderPathLabel.setFixedWidth(200)
        self.folderPathLabel.setWordWrap(True)
        layout1.addWidget(self.folderPathLabel)

        self.folderContentsList = QListWidget()
        self.folderContentsList.clicked.connect(self.listItemClicked)
        layout1.addWidget(self.folderContentsList)

        self.imageView = QLabel("이미지가 여기에 표시됩니다")
        self.imageView.setAlignment(Qt.AlignCenter)
        self.imageView.setFixedSize(900, 900)
        layout.addWidget(self.imageView)

        self.currentFolderPath = ''  # 현재 폴더 경로 저장

    def selectFolderPath(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.currentFolderPath = folder_path
            self.folderPathLabel.setText(folder_path)
            self.populateFolderContents(folder_path)

    def goToParentFolder(self):
        parent_folder_path = os.path.dirname(self.currentFolderPath)
        if parent_folder_path and os.path.exists(parent_folder_path):
            self.currentFolderPath = parent_folder_path
            self.populateFolderContents(parent_folder_path)

    def readAllJson(self):
        if self.currentFolderPath == '':
            return
        lst_vt = []
        lst_rt = []
        lst_type = []
        for (root,dirs,files) in os.walk("."):
           for file in files:
               if os.path.splitext(file)[1] == ".json":
                   try:
                       with open(os.path.join(root,file), 'r', encoding='utf-8') as f:
                           data = json.load(f)
                           info = data.get('info','No info key found')
                           imgdata = data.get('image_data','No image_data key found')
                           lst_type.append(info["type"])
                           if info["type"]=="VT":
                            lst_vt.append(info["type"]+info["material"]+","+imgdata["information"])
                           if info["type"]=="RT":
                            lst_rt.append(info["type"]+info["material"]+","+imgdata["information"])
                          
                           
                   except json.JSONDecodeError:
                       print('Invalid JSON format')
                   except:
                       print('Error reading',file)
        my_dict = {i:lst_vt.count(i) for i in lst_vt}
        my_dict1 = {i:lst_rt.count(i) for i in lst_rt}
        my_dict2 = {i:lst_type.count(i) for i in lst_type}
        print(my_dict)
        print(my_dict1)
        print(my_dict2)
        for item in my_dict.items():
            fp =item[0].split(',')[0]
            info =item[0].split(',')[1]
            c =item[1]
            result_df.loc[len(result_df)] = [fp, info, c]
        for item in my_dict1.items():
            fp =item[0].split(',')[0]
            info =item[0].split(',')[1]
            c =item[1]
            result_df1.loc[len(result_df1)] = [fp, info, c]
        for item in my_dict2.items():
            result_df2.loc[len(result_df2)] = [item[0], item[1]]
            

        result_df.to_csv("VT 데이터 유형별 불량 데이터 분포.csv", index=False, encoding="utf-8", errors='ignore')
        result_df1.to_csv("RT 데이터 유형별 불량 데이터 분포.csv", index=False, encoding="utf-8", errors='ignore')
        result_df2.to_csv("전체 데이터 규모.csv", index=False, encoding="utf-8", errors='ignore')
               

    def populateFolderContents(self, folder_path):
        self.folderContentsList.clear()
        for entry in os.listdir(folder_path):
            if os.path.splitext(entry)[1] in [".json",".png",".jpg",'.jpeg', '.bmp'] or os.path.isdir(os.path.join(folder_path,entry)) :
              self.folderContentsList.addItem(entry)
        self.folderContentsList.folder_path = folder_path

    def listItemClicked(self, index):
        selected_item = self.folderContentsList.item(index.row()).text()
        selected_path = os.path.join(self.folderContentsList.folder_path, selected_item)
        if os.path.isdir(selected_path):
            self.currentFolderPath = selected_path
            self.folderPathLabel.setText(selected_path)
            self.populateFolderContents(selected_path)
        elif os.path.isfile(selected_path) and selected_item.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            pixmap = QPixmap(selected_path)
            self.imageView.setPixmap(pixmap.scaled(900, 900, Qt.KeepAspectRatio))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = AppDemo()
    demo.show()
    sys.exit(app.exec_())
