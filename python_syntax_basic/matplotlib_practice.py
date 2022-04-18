import matplotlib.pyplot as plt

import os
import sys
#상위 경로 폴더를 가져오기 위해 선언
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from lecture_practice.backtesting_1 import tradeManager, stockData

import datetime

s_date = datetime.date(2018,12,12)
e_date = datetime.date(2022,3,3)

test_data = stockData(s_date, e_date, "035720")

x = test_data.df.index
y = test_data.df["close"]

y_sma_5 = test_data.sma_5
y_sma_20 = test_data.sma_20

plt.plot(x,y)

plt.plot(x,y_sma_5 ,'r', label="5_MA")

plt.plot(x,y_sma_20 ,'#03fc56', label="20_MA")

plt.legend()
plt.show()
