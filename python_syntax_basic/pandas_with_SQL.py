import pandas as pd
import mysql.connector
import sys
import os
import datetime
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from lecture_practice.pwd import mysql_credentials, xing_credentials
#read_sql_table
#read_sql_query
#read_sql
#DataFrame.to_sql

connection = mysql.connector.connect(user=mysql_credentials["user"], password=mysql_credentials["password"], host=mysql_credentials["host"], database="backtest")
test_df = pd.read_sql_query("select * from sh005930 limit 50", connection, index_col="date")
#test_df = pd.read_sql_query("select * from sh005930 limit 50", connection)

print(type(test_df))

## pd 데이터 다루기
#### 1) series의 iteration
'''
for item in test_df["open"]:
    print(item)
'''
#### 2) dataframe iteration -> iterrows()
'''
for item in test_df.iterrows():
    print(item[1])
'''
####  3) dataframe iteration -> itertuples():
'''
for item in test_df.itertuples():
    #print(item.oepn) # itertuples 메쏘드는 구조체로 반환해 줘서 item.open과 같이 다루기 쉽게 네임을 붙여줌
    print(item)
'''

## pd.loc, pd.iloc (슬라이싱)
#### 1) iloc 사용하기
'''
print(test_df["open"].iloc[0:4])
'''
#### 2) loc 사용하기
'''
print(test_df.loc[datetime.date(2019,1,4): datetime.date(2019,1,8), ("open", "close")])
'''