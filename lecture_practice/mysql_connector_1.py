import mysql.connector
from pwd import mysql_credentials #password파일은 비공개로 하기위해 해당 라인처럼 파일 관리

'''
방법1) database.table를 query문에 직접 입력
'''
# Connect with the MySQL Server
connection = mysql.connector.connect(user=mysql_credentials["user"], password = mysql_credentials["password"], host=mysql_credentials["host"])
# Get buffered cursors
cursor_a = connection.cursor(buffered = True)
# Query to get the table data
sql = "select * from backtest_db.table_test"
cursor_a.execute(sql)
print("방법1) database.table를 query문에 직접 입력")
for item in cursor_a:
    print(item)

'''
방법2) sql문을 이용하여 `use database`를 입력
'''
# Connect with the MySQL Server
connection = mysql.connector.connect(user=mysql_credentials["user"], password = mysql_credentials["password"], host=mysql_credentials["host"])

# Get buffered cursors
cursor_a = connection.cursor(buffered = True)
cursor_a.execute("use backtest_db")
# Query to get the table data
sql = "select * from table_test"
cursor_a.execute(sql)
print("방법2) sql문을 이용하여 `use database`를 입력")
for item in cursor_a:
    print(item)

'''
방법3) connect에서 database를 명기
'''
# Connect with the MySQL Server
connection = mysql.connector.connect(user=mysql_credentials["user"], password = mysql_credentials["password"], host=mysql_credentials["host"], database="backtest_db")
# Get buffered cursors
cursor_a = connection.cursor(buffered = True)
# Query to get the table data
sql = "select * from table_test"
cursor_a.execute(sql)
print("방법3) connect에서 database를 명기")
for item in cursor_a:
    print(item)

