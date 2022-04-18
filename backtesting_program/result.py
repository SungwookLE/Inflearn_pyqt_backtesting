from PyQt5.QtWidgets import *
from result_ui import Ui_MainWindow
from backtestlib import Boss

class customBossClass(Boss):
    def show_result(self):
        total_money =0
        total_result_list=[]
        for manager in self.manager_list:
            report_list = manager.report_boss(is_gui=True)
            money_after_trading = report_list.pop(3)
            total_result_list.append(report_list)
            total_money += money_after_trading

        return "전체 백테스트 결과: 시작({:.1f}) -> 최종({:.1f})".format(self.start_money, total_money), "수익률: {:.3f}%".format((total_money/self.start_money)* 100 - 100), total_result_list

class resultWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, company_list, s_date, e_date, bank):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.close_window)

        self.Boss = customBossClass(company_list, s_date, e_date, bank)
        total_result, profit_rate, manager_result = self.Boss.show_result()

        self.log_text(total_result)
        self.log_text(profit_rate)

        self.textEdit.append(" ")
        for result in manager_result:
            self.log_text("------------------------------------------------------------")
            for i in result:
                self.log_text(i)
        self.log_text("------------------------------------------------------------")

    def close_window(self):
        self.close()

    def log_text(self, msg):
        self.textEdit.append( "[*] "+ str(msg))