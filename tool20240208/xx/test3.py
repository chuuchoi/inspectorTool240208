import sys
import json
import cv2
import math
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QLineEdit, QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QFileDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPolygon, QPen
from PyQt5.QtCore import QObject, QEvent, Qt, QPoint, QRect
import os
from shapely.geometry import Polygon

#CSV 파일초기화
columns = ["file_path_1", "information", "count"]
result_df = pd.DataFrame(columns=columns)
columns1 = ["file_path_1", "information", "count"]
result_df1 = pd.DataFrame(columns=columns1)
columns2 = ["file_name_1", "count"]
result_df2 = pd.DataFrame(columns=columns2)

guide_txt = "마우스 왼쪽클릭: 폴리곤 점 추가, 마우스 오른쪽클릭: 폴리곤 완성\n중첩률 계산: 1번 폴리곤부터 순서대로 그려야합니다.\n\n"

class JsonViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.json_data = {"":"Data doesn't exist or json reading error."}
        # self.initUI()

        # QTextEdit 위젯 생성 및 설정
        json_text = json.dumps(self.json_data, indent=4)  # JSON 객체를 문자열로 변환
        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)  # 읽기 전용으로 설정
        self.textEdit.setText(json_text)  # JSON 텍스트 설정
        self.textEdit.setMinimumSize(500, 500)  # QTextEdit의 최소 크기 설정
        # 레이아웃 설정 및 위젯 추가
        layout = QVBoxLayout()
        layout.addWidget(self.textEdit)
        self.setLayout(layout)
    
    def initUI(self):
        self.setGeometry(100, 100, 600, 600)  # 메인 윈도우의 크기와 위치 설정
        self.setWindowTitle('JSON Viewer')

    
    def updateText(self):
        json_text = json.dumps(self.json_data, indent=4)  # JSON 객체를 문자열로 변환
        self.textEdit.setText(json_text)  # JSON 텍스트 설정


class Canvas(QLabel):
    def __init__(self):
        super().__init__()
        self.pm = QPixmap()
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setPixmap(testimg.scaled(900, 900, Qt.KeepAspectRatio))
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
            del self.points[-1]
            if len(self.points) < 3:
                pass
            else:
                self.polygons.append(self.points)
            self.points = []  # 새 폴리곤을 위해 점 리스트 초기화
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.RightButton:
            return
        if len(self.points)>1:
          del self.points[-1]
        self.points.append(event.pos())
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        # QSize 객체 생성
        size = self.pm.size()
        # QRect 객체로 변환
        # 여기서는 사각형의 좌상단 점을 (0, 0)으로 가정합니다.
        rect = QRect(0, 0, size.width(), size.height())
        painter.drawPixmap( rect, self.pm)
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        painter.setPen(pen)

        # 미완성 폴리곤 그리기
        if self.points:
            n = len(self.points)
            for i in range(n - 1):
                painter.drawLine(self.points[i], self.points[i + 1])
            # 현재 그리는 선 표시
            # painter.drawLine(self.points[-1], self.points[0])

        # 완성된 폴리곤 그리기
        for polygon in self.polygons:
            if polygon:
                painter.drawPolygon(QPolygon(polygon))

class EventFilter(QObject):
    def eventFilter(self, watched, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Up:
                # print('위쪽 방향키가 눌렸습니다. 기본 동작을 방지합니다.')
                current_row = watched.currentRow()
                total_items = watched.count()
                new_row = max(0, current_row - 1)
                watched.setCurrentRow(new_row)
                watched.displaySelectedItem()  # 선택된 항목을 표시하는 메소드 호출
                return True  # 이벤트를 처리했음을 나타내고 기본 동작을 방지합니다.
            if event.key() == Qt.Key_Down:
                # print('아래쪽 방향키가 눌렸습니다. 기본 동작을 방지합니다.')
                current_row = watched.currentRow()
                total_items = watched.count()
                new_row = min(total_items -1, current_row + 1)
                watched.setCurrentRow(new_row)
                watched.displaySelectedItem()  # 선택된 항목을 표시하는 메소드 호출
                return True  # 이벤트를 처리했음을 나타내고 기본 동작을 방지합니다.
        # 기본 이벤트 처리기를 호출하여 다른 모든 이벤트를 기본적으로 처리합니다.
        return super().eventFilter(watched, event)
    
class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        # self.canvas = Canvas()
        # self.setCentralWidget(self.canvas)
        self.setWindowTitle("PyQt5 Folder Browser")
        self.setGeometry(0, 40, 1920, 1040)

        layout = QHBoxLayout()
        layout1 = QVBoxLayout()
        self.layout2 = QVBoxLayout()
        self.setLayout(layout)
        layout.addLayout(layout1)
        layout.addLayout(self.layout2)

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

        searchLayout = QHBoxLayout()
        self.textInput = QLineEdit()
        self.searchBtn = QPushButton('검색')
        self.searchBtn.clicked.connect(self.searchBtnClicked)
        searchLayout.addWidget(self.textInput)
        searchLayout.addWidget(self.searchBtn)
        layout1.addLayout(searchLayout)

        self.folderContentsList = QListWidget()
        self.folderContentsList.displaySelectedItem = self.displaySelectedItem
        self.eventFilter = EventFilter()
        self.folderContentsList.installEventFilter(self.eventFilter)
        self.folderContentsList.clicked.connect(self.listItemClicked)
        layout1.addWidget(self.folderContentsList)

        hidebtnsLayout = QHBoxLayout()
        self.labelHideBtn = QPushButton("라벨 보이기/감추기")
        self.polygonHideBtn = QPushButton("폴리곤 보이기/감추기")
        self.clearCanvasBtn = QPushButton("그림 지우기")
        self.calcIOUBtn = QPushButton("iou 계산")
        self.labelHideBtn.clicked.connect(self.hideLabels)
        self.polygonHideBtn.clicked.connect(self.hidePolygons)
        self.clearCanvasBtn.clicked.connect(self.clearCanvas)
        self.calcIOUBtn.clicked.connect(self.calcIOU)
        hidebtnsLayout.addWidget(self.labelHideBtn)
        hidebtnsLayout.addWidget(self.polygonHideBtn)
        hidebtnsLayout.addWidget(self.clearCanvasBtn)
        hidebtnsLayout.addWidget(self.calcIOUBtn)
        self.layout2.addLayout(hidebtnsLayout)


        self.iouLabel = QLabel(f"{guide_txt}IOU :")
        self.layout2.addWidget(self.iouLabel)



        self.imageView = None
        self.jsonView = None
        # self.imageView.setAlignment(Qt.AlignCenter)
        # self.imageView.setFixedSize(1300, 900)
        # self.layout2.addWidget(self.imageView)

        self.currentFolderPath = ''  # 현재 폴더 경로 저장
        self.rootFolderPath = '' #처음 선택 폴더 경로 저장
        self.isLabelOn = True
        self.isPolygonOn = True
        self.coords = []
        self.coords_scaled = []
        self.labels = []

    def hidePolygons(self):
        self.isPolygonOn = not self.isPolygonOn
        if self.isPolygonOn:
            self.polygonHideBtn.setText("폴리곤 감추기")
        else:
            self.polygonHideBtn.setText("폴리곤 보이기")
        self.displaySelectedItem()

    def hideLabels(self):
        self.isLabelOn = not self.isLabelOn
        if self.isLabelOn:
            self.labelHideBtn.setText("라벨 감추기")
        else:
            self.labelHideBtn.setText("라벨 보이기")
        self.displaySelectedItem()

    def clearCanvas(self):
        self.imageView.polygons = []
        self.imageView.update()

    def removeCanvas(self):
        if self.imageView == None:
            return
        # Canvas 위젯을 레이아웃에서 제거하고 삭제
        self.layout2.removeWidget(self.imageView)
        self.imageView.deleteLater()
        self.imageView = None  # 참조 제거

    def addCanvas(self):
        self.imageView = Canvas()
        self.imageView.setAlignment(Qt.AlignCenter)
        self.imageView.setFixedSize(1300, 900)
        self.layout2.addWidget(self.imageView)

    def addJsonView(self):
        self.jsonView = JsonViewer()
        # self.jsonView.setAlignment(Qt.AlignCenter)
        self.jsonView.setFixedSize(1300, 900)
        self.layout2.addWidget(self.jsonView)

    def removeJsonView(self):
        if self.jsonView == None:
            return
        self.layout2.removeWidget(self.jsonView)
        self.jsonView.deleteLater()
        self.jsonView = None  # 참조 제거

    def calcIOU(self):
        iou = []
        if self.imageView == None:
            return
        if len(self.coords_scaled) != len(self.imageView.polygons):
            self.iouLabel.setText("사진의 폴리곤 갯수와 그려진 폴리곤 수가 불일치합니다. 중첩률 계산이 되지 않습니다.")
            # print("폴리곤 수 불일치",len(self.coords_scaled),len(self.imageView.polygons))
            return
        
        for i in range(len(self.coords_scaled)):
            poly1 = self.coords_scaled[i]
            qpoly2 = self.imageView.polygons[i]
            poly2 = []
            for qpoint in qpoly2:
                poly2.append([qpoint.x(),qpoint.y()])

            # shapely Polygon 객체 생성
            polygon1 = Polygon(poly1).buffer(0)
            polygon2 = Polygon(poly2).buffer(0)
            # 겹치는 영역(교집합)의 면적 계산
            # print(poly1)
            # print(poly2)
            # print(polygon2)
            intersection_area = polygon1.intersection(polygon2).area
            # 두 영역의 합집합 영역 계산
            union_area = polygon1.union(polygon2).area
            # print(intersection_area)
            # print(union_area)
            iou.append(str(math.floor(intersection_area / union_area * 100) / 100))

        s = ", ".join(iou)
        self.iouLabel.setText(f"{guide_txt}iou : {s}")

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

        if event.key() == Qt.Key_Up:
            print('===========?????')
            new_row = max(0, current_row - 1)
        elif event.key() == Qt.Key_Down:
            new_row = min(total_items - 1, current_row + 1)
        else:
            # 다른 키 입력은 부모 클래스에 위임
            super().keyPressEvent(event)
            return

        self.folderContentsList.setCurrentRow(new_row)
        self.displaySelectedItem()  # 선택된 항목을 표시하는 메소드 호출

    def displaySelectedItem(self):
        current_item = self.folderContentsList.currentItem()
        if current_item is not None:
            self.listItemClicked(current_item)


    def searchBtnClicked(self):
        if not os.path.isdir(self.currentFolderPath):
            print("경로가 설정되어 있지 않습니다.")
            return
        txt = self.textInput.text()
        if txt == '':
            self.populateFolderContents(self.currentFolderPath)
            return
        self.folderContentsList.clear()
        for entry in os.listdir(self.currentFolderPath):
            if os.path.splitext(entry)[1] in [".json",".png",".jpg",'.jpeg', '.bmp'] and txt in os.path.splitext(entry)[0]:
              self.folderContentsList.addItem(entry)
        # print(f"입력된 텍스트: {txt}")


    def listItemClicked(self, index):
        self.coords = []
        self.coords_scaled =[]
        self.labels = []
        selected_item =''
        try:
            selected_item = index.text() #displaySelectedItem을 통해 호출된 경우, 위젯의아이템인경우
        except:
            try:
                selected_item = self.folderContentsList.item(index.row()).text() #마우스 클릭으로 호출된경우
            except:
                pass
        selected_path = os.path.join(self.folderContentsList.folder_path, selected_item)
        if os.path.isdir(selected_path):
            self.currentFolderPath = selected_path
            self.folderPathLabel.setText(selected_path)
            self.populateFolderContents(selected_path)
        elif os.path.isfile(selected_path) and selected_item.lower().endswith(('.json')):
            file_exist = False
            for (root,dirs,files) in os.walk(self.rootFolderPath):
                for file in files:
                    if os.path.splitext(file)[0] == os.path.splitext(selected_item)[0] and os.path.splitext(file)[1] in ['.png', '.jpg', '.jpeg', '.bmp']:
                        file_exist = True
                        self.removeCanvas()
                        if self.jsonView ==  None:
                            self.addJsonView()
                        try:
                            with open(selected_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                self.jsonView.json_data = data
                                self.jsonView.updateText()
                        except json.JSONDecodeError:
                            print('Invalid JSON format')
                        except Exception as e:
                            print('Error reading',file, e)
            if not file_exist:
                QMessageBox.information(self,'title','처음에 선택한 폴더 경로의 하위경로들 중 파일명이 일치하는 이미지 파일이 없습니다')
                return
        elif os.path.isfile(selected_path) and selected_item.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            file_exist = False
            for (root,dirs,files) in os.walk(self.rootFolderPath):
                for file in files:
                    if os.path.splitext(file)[0] == os.path.splitext(selected_item)[0] and os.path.splitext(file)[1] ==".json":
                        file_exist = True
                        self.removeJsonView()
                        if self.imageView ==  None:
                            self.addCanvas()
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
                                    self.coords.append(lst)
                                    self.labels.append(label)
                        except json.JSONDecodeError:
                            print('Invalid JSON format')
                        except Exception as e:
                            print('Error reading',file, e)
            if not file_exist:
                QMessageBox.information(self,'title','처음에 선택한 폴더 경로의 하위경로들 중 파일명이 일치하는 json 파일이 없습니다 ')
                return
            # 이미지를 OpenCV를 사용하여 로드, 한글 경로 문제는 cv2.imdecode 함수로 복호화 해결
            img_array = np.fromfile(selected_path, np.uint8)
            cvImg = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
             # 이미지에 윤곽선 그리기
            # border_color = (250, 0, 0)  # 빨간색 윤곽선
            # thickness = 20  # 윤곽선 두께
            # img_with_border = cv2.copyMakeBorder(cvImg, thickness, thickness, thickness, thickness, cv2.BORDER_CONSTANT, value=border_color)

            height, width, channel = cvImg.shape

            if len(self.coords) > 0:
                for idx,coords in enumerate(self.coords):
                    # 폴리곤 좌표와 클래스 라벨을 정의 (예시입니다. 실제 좌표와 라벨을 사용하세요)
                    coordinates = np.array(coords, np.int32).reshape((-1, 1, 2))
                    class_label = self.labels[idx]
                    
                    # 폴리곤 그리기
                    if self.isPolygonOn:
                        cv2.polylines(cvImg, [coordinates], True, (255, 0, 0), 3)
                    
                    # # 폴리곤 오른쪽 상단에 클래스 라벨 추가
                    # right_top_x = max(coordinates[:,0][:,0])
                    # right_top_y = min(coordinates[:,0][:,1])
                    # 폴리곤의 아래 중앙에 클래스 라벨 추가
                    bottom_center_x = int((max(coordinates[:,0][:,0]) + min(coordinates[:,0][:,0])) / 2)
                    bottom_center_y = max(coordinates[:,0][:,1])
                    
                    original_size = (width, height)  # 원래 이미지 크기
                    scaled_size = (1300, 900)  # 변경된 이미지 크기

                    # 스케일 비율 계산
                    scale_width = scaled_size[0] / original_size[0]
                    scale_height = scaled_size[1] / original_size[1]

                    # KeepAspectRatio에 따라 실제 사용되는 스케일 비율 결정
                    scale_factor = min(scale_width, scale_height)

                    # 텍스트 사이즈와 베이스라인을 계산
                    (text_width, text_height), baseline = cv2.getTextSize(class_label, cv2.FONT_HERSHEY_SIMPLEX, 1 * 1/scale_factor, int(2 * 1/scale_factor))

                    # 텍스트의 시작 위치를 중앙 정렬로 조정
                    start_x = bottom_center_x - text_width // 2
                    start_y = bottom_center_y + text_height // 2

                    # 텍스트 그리기 (두껍게 하고 중앙 정렬)
                    if self.isLabelOn:
                        cv2.putText(cvImg, class_label, (start_x, start_y+4), cv2.FONT_HERSHEY_SIMPLEX, 1 * 1/scale_factor, (255, 0, 0), int(2 * max(1,1/scale_factor)))
                        cv2.putText(cvImg, str(idx+1), (bottom_center_x, start_y+40), cv2.FONT_HERSHEY_SIMPLEX, 1 * 1/scale_factor, (255, 0, 0), int(2 * max(1,1/scale_factor)))

                    # 스케일된 폴리곤 좌표 계산
                    scaled_polygon_coords = [[int(x * scale_factor), int(y * scale_factor)] for x, y in coords]

                    self.coords_scaled.append(scaled_polygon_coords)


            else:
                print('-')

            # OpenCV 이미지를 QPixmap으로 변환하여 QLabel에 표시
            bytesPerLine = 3 * width
            qImg = QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

            pixmap = QPixmap.fromImage(qImg)
            # self.imageView.setPixmap(pixmap.scaled(900, 900, Qt.KeepAspectRatio))
            self.imageView.pm = pixmap.scaled(1300, 900, Qt.KeepAspectRatio)
            self.imageView.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = AppDemo()
    demo.show()
    sys.exit(app.exec_())
