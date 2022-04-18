import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication
from test_ui import Ui_MainWindow

class testClass(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.practice_button1.clicked.connect(self.test_function1)
        self.practice_button2.clicked.connect(self.test_function2)
    
    def test_function1(self):
        print("버튼1이 클릭되었습니다.")
    
    def test_function2(self):
        print("버튼2이 클릭되었습니다.")

app = QApplication(sys.argv)
test_window = testClass()
test_window.show()

app.exec_()
