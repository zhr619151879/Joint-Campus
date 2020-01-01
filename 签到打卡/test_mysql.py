import io
from time import localtime, strftime
import numpy as np
import zlib
import pymysql as mysql


def getDateAndTime():
    date_and_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
    return "[" + date_and_time + "]"


host_ip = "47.96.157.49"
host_usr = "root"
host_psw = "123lalala"
host_db = "inspurer"


# conn = mysql.connect("localhost", "root", "123lalala", "inspurer", port=3306)

conn = mysql.connect(host_ip, host_usr, host_psw, host_db, port=3306)
mycursor = conn.cursor()

sql = "INSERT INTO logcat (datetime, id, name, late) VALUES (%s, %s, %s, %s)"
val = ("2019", 123, "xbxbx", "nope")
mycursor.execute(sql, val)

conn.commit()
mycursor.execute(sql, val)

print("写日志成功")


# conn = mysql.connect("localhost", "root", "123lalala", "inspurer", port=3306)
# cur = conn.cursor()
# sql = "CREATE TABLE t1 (c1 CHAR(10))"
# cur.execute(sql)
# print("eyhsui")
#
#
# sql = "INSERT INTO t1 (c1) values('xy')"
# cur.execute(sql)
# print("fr3vr")

