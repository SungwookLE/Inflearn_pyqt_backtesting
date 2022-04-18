##나만의 백테스팅 프로그램 작성하기
### - userBank : 실제 은행처럼 백테스팅을 진행할 금액, 수수료, 슬리피지
### - Boss : 여러 tradeManager에게 유저가 원하는 종목별 비중을 조절해서 tradeManager에게 백테스트를 시키고 전체적인 결과를 계산함. tradeManager에게 추후 각종목별로 종목1은 알고리즘1번 종목 2는 알고리즘번과같이 매매 방식도 전달 가능하도록 진행할 예정
### - StockData : 전체적인 백테스트에 필요한 데이터를 전부 여기서 관리
### - Algorithm : 추후 전체적인 백테스트 프로그램 완성 이후 이 알고리즘이란 클래스만 작성하면 되도록 프로그래밍할 예정

import mysql.connector
import os
import sys
import matplotlib.pyplot as plt

#상위 경로 폴더를 가져오기 위해 선언
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from lecture_practice.pwd import mysql_credentials, xing_credentials
import pandas as pd
import datetime
from talib import SMA

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
    def __init__(self, s_date, e_date, shcode, s_money, show_result = False):
        self.stock_data = stockData(s_date, e_date, shcode)
        self.money = s_money

        self.total_quantity = []
        self.order_tracking = []
        self.asset = []

        self.run_backtest()
        if show_result == True:
            self.show_result(s_money, shcode)

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

            self.asset.append( self.money + self.total_quantity[-1] * daily_stock_date.close)

            integer_index+=1

    def buy_signal(self, data, integer_index):
        if integer_index == 0 :
            return False
        else:
            if (self.stock_data.sma_5[integer_index] > self.stock_data.sma_20[integer_index]) and (self.stock_data.sma_5[integer_index-1] < self.stock_data.sma_20[integer_index-1]):
                return True
            else:
                return False

    def sell_signal(self, data, integer_index):
        if integer_index == 0:
            return False
        else:
            if (self.stock_data.sma_5.iloc[integer_index] < self.stock_data.sma_20[integer_index]) and (self.stock_data.sma_5[integer_index-1] > self.stock_data.sma_20[integer_index-1]):
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
            print("**WARN: BUY ZERO@{}".format(data.Index))
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
                print("**WARN: SELL ZERO @{}".format(data.Index))
                self.total_quantity.append(0)

    def show_result(self, s_money, shcode):
        print("------------------------------------------------------------")
        print("시작 금액: {}".format(s_money))
        print("거래 내역: ", self.order_tracking)
        print("자산 변동 내역 :", self.asset)
        print("------------------------------------------------------------")
        print("Total Length of Data: ")
        print(len(self.total_quantity))
        print(len(self.stock_data.df))
        print(len(self.asset))
        print("------------------------------------------------------------")


        x = self.stock_data.df.index
        y = self.stock_data.df["close"]

        y_sma_5 = self.stock_data.sma_5
        y_sma_20 = self.stock_data.sma_20

        #plt.plot(x,y)
        plt.plot(x, y_sma_5, '#fc037b', label = "MA_5")
        plt.plot(x,y_sma_20, '#03fc56', label= "MA_20")
        for order in self.order_tracking:
            if (order[2] > 0):
                # 전량 매수
                #plt.scatter(order[0], order[1], marker='o', color='#03b1fc') 
                plt.axvline(order[0] ,color='#03b1fc' )
            elif (order[2] < 0):
                # 전량 매도
                #plt.scatter(order[0], order[1], marker='o', color='#fc03db') 
                plt.axvline(order[0], color='#fc03db' )

        plt.legend()


        plt.title(shcode)
        plt.show()

if __name__ == "__main__":
    s_date = datetime.date(2015,6,12)
    e_date = datetime.date(2022,3,25)

    tradeManager(s_date, e_date, "000020", 100000000, True)