import sys
import os
from PyQt5.QtWidgets import *
from PyQt5 import uic

#pyinstaller 빌드시 ui파일을 포함시키기 위한 코드
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
form = resource_path('dd.ui')
form_class = uic.loadUiType(form)[0]
#pyinstaller 빌드시 ui파일을 포함시키기 위한 코드 spec파일에 아래 두줄 작성
# added_files = [('dd.ui','.')] //ui 포함
# a = Analysis(
#     ['xx.py'],
#     pathex=[],
#     binaries=[],
#     datas=added_files, //added_files 추가

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        QMessageBox.information(self,'dd','ddd')

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    sys.exit(app.exec_())
