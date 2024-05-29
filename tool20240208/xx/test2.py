import sys
import json
import cv2
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
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
        self.rootFolderPath = '' #처음 선택 폴더 경로 저장

    def selectFolderPath(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.rootFolderPath = folder_path
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

    def keyPressEvent(self, event):
        current_row = self.folderContentsList.currentRow()
        total_items = self.folderContentsList.count()

        if event.key() == Qt.Key_Right:
            print('오른족눌림')
            # 위쪽 방향키가 눌렸을 때
            new_row = max(0, current_row - 1)
            self.listItemClicked()
        elif event.key() == Qt.Key_Left:
            print('왼족눌림')
            # 아래쪽 방향키가 눌렸을 때
            new_row = min(total_items - 1, current_row + 1)
            self.listItemClicked()
        else:
            # 다른 키 입력은 부모 클래스에 위임
            super().keyPressEvent(event)
            return

        # 새로운 항목 선택
        self.folderContentsList.setCurrentRow(new_row)

    def listItemClicked(self, index):
        print(index)
        selected_item = self.folderContentsList.item(index.row()).text()
        selected_path = os.path.join(self.folderContentsList.folder_path, selected_item)
        if os.path.isdir(selected_path):
            self.currentFolderPath = selected_path
            self.folderPathLabel.setText(selected_path)
            self.populateFolderContents(selected_path)
        elif os.path.isfile(selected_path) and selected_item.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            combined_list = []
            label_lst = []
            for (root,dirs,files) in os.walk(self.rootFolderPath):
                for file in files:
                    if os.path.splitext(file)[0] == os.path.splitext(selected_item)[0] and os.path.splitext(file)[1] ==".json":
                        try:
                            with open(os.path.join(root,file), 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                annotations = data.get('annotations','No annotations key found')
                                for anno in annotations:
                                    lx = anno["coordinate"]["x"]
                                    ly = anno["coordinate"]["y"]
                                    label = anno["case"]
                                    #x와 y length가 다른 경우 넘김
                                    if len(lx) != len(ly):
                                        print("x y 좌표 길이가 서로 다릅니다")
                                        continue
                                    lst = [[a, b] for a, b in zip(lx, ly)]
                                    combined_list.append(lst)
                                    label_lst.append(label)
                        except json.JSONDecodeError:
                            print('Invalid JSON format')
                        except Exception as e:
                            print('Error reading',file, e)

            # 이미지를 OpenCV를 사용하여 로드, 한글 경로 문제는 cv2.imdecode 함수로 복호화 해결
            img_array = np.fromfile(selected_path, np.uint8)
            cvImg = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if len(combined_list) > 0:
                for idx,coords in enumerate(combined_list):
                    # 폴리곤 좌표와 클래스 라벨을 정의 (예시입니다. 실제 좌표와 라벨을 사용하세요)
                    coordinates = np.array(coords, np.int32).reshape((-1, 1, 2))
                    class_label = label_lst[idx]
                    
                    # 폴리곤 그리기
                    cv2.polylines(cvImg, [coordinates], True, (255, 0, 0), 3)
                    
                    # # 폴리곤 오른쪽 상단에 클래스 라벨 추가
                    # right_top_x = max(coordinates[:,0][:,0])
                    # right_top_y = min(coordinates[:,0][:,1])
                    # 폴리곤의 아래 중앙에 클래스 라벨 추가
                    bottom_center_x = int((max(coordinates[:,0][:,0]) + min(coordinates[:,0][:,0])) / 2)
                    bottom_center_y = max(coordinates[:,0][:,1])
                    
                    # 텍스트 사이즈와 베이스라인을 계산
                    (text_width, text_height), baseline = cv2.getTextSize(class_label, cv2.FONT_HERSHEY_SIMPLEX, 4, thickness=8)

                    # 텍스트의 시작 위치를 중앙 정렬로 조정
                    start_x = bottom_center_x - text_width // 2
                    start_y = bottom_center_y + text_height // 2

                    # 텍스트 그리기 (두껍게 하고 중앙 정렬)
                    cv2.putText(cvImg, class_label, (start_x, start_y), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 0, 0), 8)

            else:
                print('-')

            # OpenCV 이미지를 QPixmap으로 변환하여 QLabel에 표시
            height, width, channel = cvImg.shape
            bytesPerLine = 3 * width
            qImg = QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

            pixmap = QPixmap.fromImage(qImg)
            self.imageView.setPixmap(pixmap.scaled(900, 900, Qt.KeepAspectRatio))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = AppDemo()
    demo.show()
    sys.exit(app.exec_())
