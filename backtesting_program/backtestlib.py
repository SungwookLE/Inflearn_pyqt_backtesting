##나만의 백테스팅 프로그램 작성하기
### - userBank : 실제 은행처럼 백테스팅을 진행할 금액, 수수료, 슬리피지
### - Boss : 여러 tradeManager에게 유저가 원하는 종목별 비중을 조절해서 tradeManager에게 백테스트를 시키고 전체적인 결과를 계산함. tradeManager에게 추후 각종목별로 종목1은 알고리즘1번 종목 2는 알고리즘번과같이 매매 방식도 전달 가능하도록 진행할 예정
### - StockData : 전체적인 백테스트에 필요한 데이터를 전부 여기서 관리
### - Algorithm : 추후 전체적인 백테스트 프로그램 완성 이후 이 알고리즘이란 클래스만 작성하면 되도록 프로그래밍할 예정

import mysql.connector
import matplotlib.pyplot as plt
from pwd import mysql_credentials, xing_credentials
import pandas as pd
import datetime
from talib import SMA

class Boss:
    # backtest_list = [("shcode", 비중), ("shcode", 비중)]
    def __init__(self, backtest_list, s_date, e_date, user_bank):
        self.group = backtest_list
        self.s_date = s_date
        self.e_date = e_date
        self.bank = user_bank

        self.start_money = self.bank.money

        self.total_ratio_sum = 0
        for ratio in self.group:
            self.total_ratio_sum += ratio[1]
        
        self.manager_list = []
        fig, ax = plt.subplots(len(self.group), 1)
        for idx, company in enumerate(self.group):
            money = self.start_money * (company[1] / self.total_ratio_sum )
            self.manager_list.append(tradeManager(self.s_date, self.e_date, company[0] , money, self.bank.commission, self.bank.slippage, ax[idx], show_result=True))
        
        self.show_result()
        plt.show()
    
    def show_result(self):
        total_money =0

        for manager in self.manager_list:
            money_after_trading=manager.report_boss()
            total_money += money_after_trading
        
        print('BOSS Said:================================================================')
        print("[*]전체적인 백테스트 결과: 시작금액({:.1f}) -> 최종({:.1f}).".format(self.start_money, total_money))
        print("[!]수익률: {:.3f}%".format( total_money/self.start_money* 100 - 100))
        print('==========================================================================')

class userBank:
    def __init__(self, money, commission, slippage):
        self.money = money
        self.commission = commission
        self.slippage = slippage

class stockData:
    def __init__(self, s_date, e_date, shcode):
        self.connection = mysql.connector.connect(user=mysql_credentials["user"], password=mysql_credentials["password"], host=mysql_credentials["host"], database="backtest")
        self.df = pd.read_sql_query("select * from sh{}".format(shcode), self.connection, index_col='date').loc[s_date:e_date]
        #print(self.df)
        self.precalculated_data()
    
    def precalculated_data(self):
        self.sma_5 = SMA(self.df["close"], timeperiod=5)
        self.sma_20 = SMA(self.df["close"], timeperiod=20)


class tradeManager:
    def __init__(self, s_date, e_date, shcode, s_money, commission, slippage, ax, show_result = False):
        self.commission = commission
        self.slippage = slippage

        self.stock_data = stockData(s_date, e_date, shcode)
        self.start_money = s_money
        self.money = s_money
        self.shcode = shcode

        self.total_quantity = []
        self.order_tracking = []
        self.asset = dict()

        self.run_backtest()
        if show_result == True:
            self.show_result(s_money, shcode, ax)

    def run_backtest(self):
        integer_index = 0
        for daily_stock_date in self.stock_data.df.itertuples():
            #print(daily_stock_date)
            is_buy_signal = self.buy_signal(daily_stock_date, integer_index)
            is_sell_signal = self.sell_signal(daily_stock_date, integer_index)

            if (is_buy_signal == True) and (is_sell_signal == True):
                try:
                    quantity = self.total_quantity[-1]
                except IndexError:
                    self.total_quantity.append(0)
                else:
                    self.total_quantity.append(quantity)

            elif (is_buy_signal == True) and (is_sell_signal == False):
                self.buy(daily_stock_date)
            elif (is_buy_signal == False) and (is_sell_signal == True):
                self.sell(daily_stock_date)
            else:
                try:
                    quantity = self.total_quantity[-1]
                except IndexError:
                    self.total_quantity.append(0)
                else:
                    self.total_quantity.append(quantity)

            self.asset[daily_stock_date.Index]= self.money + self.total_quantity[-1] * daily_stock_date.close

            integer_index+=1

    def buy_signal(self, data, integer_index):
        if integer_index == 0 :
            return False
        else:
            if (self.stock_data.sma_5[integer_index] >= self.stock_data.sma_20[integer_index]) and (self.stock_data.sma_5[integer_index-1] < self.stock_data.sma_20[integer_index-1]):
                return True
            else:
                return False

    def sell_signal(self, data, integer_index):
        if integer_index == 0:
            return False
        else:
            if (self.stock_data.sma_5.iloc[integer_index] <= self.stock_data.sma_20[integer_index]) and (self.stock_data.sma_5[integer_index-1] > self.stock_data.sma_20[integer_index-1]):
                return True
            else:
                return False
    
    def buy(self, data):
        buy_price = data.close
        quantity = self.money // buy_price
        if quantity != 0:
            # 꼭 필요하지 않을수도 있음...
            self.money = self.money - ( quantity * buy_price )
            self.total_quantity.append(quantity)
            self.order_tracking.append((data.Index, buy_price, quantity))
        else:
            print("[-]WARNING {}: BUY as ZERO @{}".format(self.shcode, data.Index))
            self.total_quantity.append(0)

    def sell(self, data):
        sell_price = data.close

        try:
            quantity = self.total_quantity[-1]
        except IndexError:
            print("첫날 매도 시그널 발생")
        else:
            if quantity != 0:
                self.money = self.money + (quantity * sell_price)
                #전량 매도했기 때문에 보유주식수 =0
                self.total_quantity.append(0)
                self.order_tracking.append((data.Index, sell_price, -quantity))
            else:
                print("[-]WARNING {}: SELL as ZERO @{}".format(self.shcode, data.Index))
                self.total_quantity.append(0)

    def show_result(self, s_money, shcode, ax):
        print("Trader Said:--------------------------------------------------------------")
        print("시작 금액: {:.1f}".format(s_money))
        #print("거래 내역: ", self.order_tracking)
        print("자산 변동 내역: {:.1f}".format(self.asset[self.order_tracking[-1][0]]))
        print()
        print("Total Length of Data: ")
        print(len(self.total_quantity) ,len(self.stock_data.df),len(self.asset) )
        print("--------------------------------------------------------------------------")

        x = self.stock_data.df.index
        y = self.stock_data.df["close"]

        y_sma_5 = self.stock_data.sma_5
        y_sma_20 = self.stock_data.sma_20

        #plt.plot(x,y)
        ax.plot(x, y_sma_5, '#fc037b', label = "MA_5")
        ax.plot(x,y_sma_20, '#03fc56', label= "MA_20")
        for order in self.order_tracking:
            if (order[2] > 0):
                # 전량 매수
                #plt.scatter(order[0], order[1], marker='o', color='#03b1fc') 
                ax.axvline(order[0] ,color='#03b1fc',linewidth=1 )
                ax.text(order[0], order[1], "B", color='#03b1fc',fontsize=10)
                #ax.text(order[0], order[1], "BUY: {}".format(self.asset[order[0]]))
            elif (order[2] < 0):
                # 전량 매도
                #plt.scatter(order[0], order[1], marker='o', color='#fc03db') 
                ax.axvline(order[0], color='#fc03db', linewidth=1 )
                ax.text(order[0], order[1], "S", color ='#fc03db',fontsize=10)
                #ax.text(order[0], order[1], "SELL: {}".format(self.asset[order[0]]))

        ax.legend()
        ax.set_title(shcode)
        #plt.show()

    def report_boss(self, is_gui =False):
        if is_gui == True:
            return ["Trader의 '{}' 개별 종목 거래 결과입니다.".format(self.shcode),"Trader의 시작 금액: {:.1f}".format(self.start_money), "Trader의 자산 변동 내역: {:.1f}".format(self.asset[self.order_tracking[-1][0]]), self.asset[self.order_tracking[-1][0]]]

        else:
            print("Trader report to BOSS:----------------------------------------------------")
            print("{} 개별 종목 거래 결과입니다.".format(self.shcode))
            print("시작 금액: {:.1f}".format(self.start_money))
            print("자산 변동 내역: {:.1f}".format(self.asset[self.order_tracking[-1][0]]))
            print("--------------------------------------------------------------------------")
            return self.asset[self.order_tracking[-1][0]]

if __name__ == "__main__":
    s_date = datetime.date(2015,6,12)
    e_date = datetime.date(2022,3,25)

    #tradeManager(s_date, e_date, "000020", 100000000, True)
    user_bank = userBank(1000000000, 0, 0)
    backtest_list = [ ("000040", 1), ("000020", 1)]
    Boss(backtest_list, s_date, e_date, user_bank)