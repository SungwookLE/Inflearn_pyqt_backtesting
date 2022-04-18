from PyQt5.QtWidgets import *
from backtest_main_ui import Ui_MainWindow
from backtestlib import *
import sys
import mysql.connector
from pwd import mysql_credentials, xing_credentials
from result import resultWindow
import datetime

class mainBacktestWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, debug_mode=False):
        super().__init__()
        self.setupUi(self)
        self.connection = False
        self.backtest_list = []

        if debug_mode ==True:
            self.db_id.setText(mysql_credentials["user"])
            self.db_pwd.setText(mysql_credentials["password"])
            self.db_ip.setText(mysql_credentials["host"])
            self.db_schema.setText("backtest")

        self.db_login.clicked.connect(self.login_db)
        self.search.clicked.connect(self.search_db)
        self.add_backtest.clicked.connect(self.add_to_table)
        self.delete_row.clicked.connect(self.delete_row_item)
        self.start_backtest.clicked.connect(self.show_backtest_result)

        self.statusbar.showMessage("mysql db에 로그인해주세요.")
        self.is_db_logined(False)

        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["종목명","종목코드","비중"])
        
    def login_db(self):
        user = self.db_id.text()
        pwd = self.db_pwd.text()
        ip = self.db_ip.text()
        default_schema = self.db_schema.text()

        try:
            self.connection = mysql.connector.connect(user = user, password = pwd, host= ip, database=default_schema)
        except mysql.connector.Error as err:
            self.statusbar.showMessage("{}".format(str(err)))
        else:
            self.statusbar.showMessage("mysql db 로그인완료")
            self.db_login.setEnabled(False)
            self.is_db_logined(True)
            self.start_backtest.setEnabled(False)

    def is_db_logined(self, status):
        self.search.setEnabled(status)
        self.add_backtest.setEnabled(status)
        self.start_backtest.setEnabled(status)
        self.delete_row.setEnabled(status)

    def search_db(self):
        sh_code = self.shcode.text()
        sql = "select hname from total_company_list where shcode='{}'".format(sh_code)
        cursor_a = self.connection.cursor(buffered=True)
        cursor_a.execute(sql)
        hname= cursor_a.fetchone()
        if hname== None:
            self.stock_name.setText("없는 종목코드입니다.")
        else:
            self.stock_name.setText(hname[0])
            self.add_backtest.setEnabled(True)

    def add_to_table(self):
        ratio_input = self.ratio.text()
        try: 
            ratio_input = int(ratio_input)
        except ValueError:
            self.statusbar.showMessage("올바른 비중을 입력해주세요")
        else:
            if ratio_input <= 0 :
                self.statusbar.showMessage("비중은 양수만 가능합니다.")
            else:
                shcode = self.shcode.text()

                if self.check_if_exists(shcode) == False:
                    self.backtest_list.append([shcode, ratio_input]) 
                    self.statusbar.showMessage("백테스트 리스트에 종목이 추가되었습니다.")
                    row_number = self.tableWidget.rowCount() 
                    self.tableWidget.setRowCount(row_number + 1)
                    self.tableWidget.setItem(row_number, 0, QTableWidgetItem(self.stock_name.text()))
                    self.tableWidget.setItem(row_number, 1, QTableWidgetItem(shcode) )
                    self.tableWidget.setItem(row_number, 2, QTableWidgetItem(str(ratio_input)))
                    self.start_backtest.setEnabled(True)
                else:
                    self.statusbar.showMessage("이미 추가된 항목입니다.")

    def check_if_exists(self, shcode):
        for item in self.backtest_list:
            if item[0] == shcode:
                return True
        return False        

    def delete_row_item(self):
        selected_row = self.tableWidget.currentRow()
        self.tableWidget.removeRow(selected_row)
        self.statusbar.showMessage("{} 종목이 삭제되었습니다.".format(self.backtest_list.pop(selected_row)))
        if len(self.backtest_list) == 0:
            self.start_backtest.setEnabled(False)
        else:
            self.start_backtest.setEnabled(True)

    def show_backtest_result(self):
        s_date_list = self.s_date.text().split("-")
        e_date_list = self.e_date.text().split("-")

        s_date = datetime.date(int(s_date_list[0]), int(s_date_list[1]), int(s_date_list[2]))
        e_date = datetime.date(int(e_date_list[0]), int(e_date_list[1]), int(e_date_list[2]))

        s_money = int(self.s_money.text())
        commission = int(self.commission.text())
        slippage = int(self.slippage.text())

        bank = userBank(s_money, commission, slippage)
        #Boss(self.backtest_list, s_date, e_date, bank)

        self.window = resultWindow(self.backtest_list, s_date, e_date, bank)
        self.window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    backtest_window = mainBacktestWindow(debug_mode=True)
    backtest_window.show()

    app.exec_()