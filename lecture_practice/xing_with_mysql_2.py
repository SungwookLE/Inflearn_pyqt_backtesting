from pwd import xing_credentials, mysql_credentials
import win32com.client
import pythoncom
import time
import mysql.connector

class loginEventHandler:
    is_login = False #클래스 변수, 클래스 인스턴스 간 공유 변수
    # print(dir(loginEventHandler)) #클래스의 메쏘드와 공유 변수 출력할 수 있다.

    def OnLogin(self, code, msg):
        self.instance_var = 0 #인스턴스 변수, 인스턴스 개별적으로 사용하는 독립적인 변수

        print(code, msg)
        print("로그인 완료")
        loginEventHandler.is_login = True
    
    def OnDisconnect(self):
        pass

class t8430eventHandler:
    is_called = False

    def OnReceiveData(self, tr):
        print("불러오기 완료")
        print(tr)
        t8430eventHandler.is_called = True

session = win32com.client.DispatchWithEvents("XA_Session.XASession", loginEventHandler) #내가 만든 Handler 클래스를 다중 상속시키는 것이다.
session.ConnectServer("hts.ebestsec.co.kr", 20001)
print(session.IsConnected())
if session.IsConnected():
    session.Login(xing_credentials["ID"], xing_credentials["password"], xing_credentials["cert_password"], 0, 0)

while loginEventHandler.is_login == False:
    pythoncom.PumpWaitingMessages()

t8430_session = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", t8430eventHandler)
t8430_session.ResFileName = 'C:\\eBEST\\xingAPI\\Res\\t8430.res'
t8430_session.SetFieldData("t8430InBlock", "gubun", 0 , 0)
t8430_session.Request(0)

while t8430eventHandler.is_called == False:
    pythoncom.PumpWaitingMessages()

count=t8430_session.GetBlockCount("t8430OutBlock")

print(count)

#mysql 에 접속하기
connection = mysql.connector.connect(user = mysql_credentials["user"] , password = mysql_credentials["password"], host = mysql_credentials["host"])
cursor_a = connection.cursor(buffered = True)
# db 생성
cursor_a.execute("create schema backtest")

# table 생성, table 생성에 이름은 `를 붙여주어야 한다
sql = "CREATE TABLE `backtest`.`total_company_list` (`hname` VARCHAR(45) NOT NULL, `shcode` VARCHAR(20) NULL, `expcode` VARCHAR(45) NULL, `etfgubun` VARCHAR(5) NULL, `uplmtprice` INT NULL, `dnlmtprice` INT NULL, `jinlclose` INT NULL, `memeda` VARCHAR(45) NULL, `recprice` INT NULL, `gubun` VARCHAR(5) NULL)"
cursor_a.execute(sql)
cursor_a.execute("use backtest")

for index in range(count):
    hname = t8430_session.GetFieldData("t8430OutBlock", "hname", index)
    shcode = t8430_session.GetFieldData("t8430OutBlock", "shcode", index)
    expcode = t8430_session.GetFieldData("t8430OutBlock", "expcode", index)
    etfgubun = t8430_session.GetFieldData("t8430OutBlock", "etfgubun", index)
    uplmtprice = t8430_session.GetFieldData("t8430OutBlock", "uplmtprice", index)
    dnlmtprice = t8430_session.GetFieldData("t8430OutBlock", "dnlmtprice", index)
    jnilclose = t8430_session.GetFieldData("t8430OutBlock", "jnilclose", index)
    memedan = t8430_session.GetFieldData("t8430OutBlock", "memedan", index)
    recprice = t8430_session.GetFieldData("t8430OutBlock", "recprice", index)
    gubun = t8430_session.GetFieldData("t8430OutBlock", "gubun", index)
    cursor_a.execute("insert into total_company_list values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(hname, shcode, expcode, etfgubun, uplmtprice, dnlmtprice, jnilclose, memedan, recprice, gubun))
    #print("insert into total_company_list values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(hname, shcode, expcode, etfgubun, uplmtprice, dnlmtprice, jnilclose, memedan, recprice, gubun))

# commit하여 최종 저장
connection.commit()

