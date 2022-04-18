import mysql.connector
from pwd import mysql_credentials #password파일은 비공개로 하기위해 해당 라인처럼 파일 관리


# Connect with the MySQL Server
connection = mysql.connector.connect(user=mysql_credentials["user"], password = mysql_credentials["password"], host=mysql_credentials["host"])
# Get buffered cursors
cursor_a = connection.cursor(buffered = True)
# Query to get the table data
print("-------init-----------")
sql = "select * from backtest_db.table_test"
cursor_a.execute(sql)
for item in cursor_a:
    print(item)

print("\n-------delete-----------")
cursor_a.execute("delete from backtest_db.table_test")

connection.rollback() #되돌리기
sql = "select * from backtest_db.table_test"
cursor_a.execute(sql)

for item in cursor_a:
    print(item)
    
# commit()은 저장하기이고, rollback()은 되돌리기임
#connection.commit()
