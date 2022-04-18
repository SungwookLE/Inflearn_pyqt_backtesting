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

class t8413eventHandler:
    is_called = False

    def OnReceiveData(self, tr):
        print("불러오기 완료")
        print(tr)
        t8413eventHandler.is_called = True

session = win32com.client.DispatchWithEvents("XA_Session.XASession", loginEventHandler) #내가 만든 Handler 클래스를 다중 상속시키는 것이다.
session.ConnectServer("hts.ebestsec.co.kr", 20001)
print(session.IsConnected())
if session.IsConnected():
    session.Login(xing_credentials["ID"], xing_credentials["password"], xing_credentials["cert_password"], 0, 0)

while loginEventHandler.is_login == False:
    pythoncom.PumpWaitingMessages()


cts_date = "start"
edate = "20211213"
while cts_date != "":
    print("-------------------------------------------------------------------------")
    t8413_session = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", t8413eventHandler)
    t8413_session.ResFileName = 'C:\\eBEST\\xingAPI\\Res\\t8413.res'
    t8413_session.SetFieldData("t8413InBlock", "shcode", 0 , "005930") #삼성전자의 shcode임
    t8413_session.SetFieldData("t8413InBlock", "gubun", 0 , 2) #2: 일봉 , #3: 주봉, #4: 월봉
    t8413_session.SetFieldData("t8413InBlock", "sdate", 0 , "20130101")
    t8413_session.SetFieldData("t8413InBlock", "edate", 0 , edate)

    """
    t8413_session.SetFieldData("t8413InBlock", "qrycnt", 0 , 500) #비압축 (비압축은 500개가 최대)
    t8413_session.SetFieldData("t8413InBlock", "comp_yn", 0 , "N") #비압축
    """
    t8413_session.SetFieldData("t8413InBlock", "qrycnt", 0 , 2000) #압축
    t8413_session.SetFieldData("t8413InBlock", "comp_yn", 0 , "Y") #압축

    t8413_session.Request(0)

    while t8413eventHandler.is_called == False:
        pythoncom.PumpWaitingMessages()

    t8413_session.Decompress("t8413OutBlock1")
    count = t8413_session.GetBlockCount("t8413OutBlock1")

    cts_date = t8413_session.GetFieldData("t8413OutBlock", "cts_date", 0)
    if cts_date != "":
        print("연속데이터 있습니다: ", cts_date)
        edate = cts_date
    else:
        print("전부 조회 완료")

    print(count)
    time.sleep(1) # xingAPI 건당 제한 속도 1초에 1건
    t8413eventHandler.is_called = False #리퀘스트를 제대로 기다려주게 하기 위해 `while t8413eventHandler.is_called == False:` 루프마다 초기화
    print("-------------------------------------------------------------------------")

# commit하여 최종 저장
#connection.commit()

