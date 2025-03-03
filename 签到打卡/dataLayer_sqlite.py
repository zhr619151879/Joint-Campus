# -*- coding:utf-8 -*-
# @Time : 2019/12/25 2:16 下午
# @Author: zhr619151879
# @Keymap: 「command+1:surround command+p:parameter ctr+o overide」
# @File : dataLayer.py

import sqlite3
import io
import numpy as np
import zlib


class DataBaseWorker():
    def __init__(self):
        self.initDatabase()

    def initDatabase(self):
        conn = sqlite3.connect(
            "/Users/zhuhaoran/Desktop/V3.0/data/inspurer.db")  # 建立数据库连接
        cur = conn.cursor()  # 得到游标对象
        cur.execute('''create table if not exists worker_info
         (name text not null,
         id int not null primary key,
         face_feature array not null)''')
        cur.execute('''create table if not exists logcat
          (datetime text not null,
          id int not null,
          name text not null,
          late text not null)''')

        conn.commit()
        cur.close()
        conn.close()

    def adapt_array(self, arr):
        out = io.BytesIO()
        # 将arr压缩成二进制文件
        np.save(out, arr)
        out.seek(0)  # position-> start of the stream
        dataa = out.read()
        # 压缩数据流
        return sqlite3.Binary(zlib.compress(dataa, zlib.Z_BEST_COMPRESSION))

    def convert_array(self, text):
        out = io.BytesIO(text)
        out.seek(0)
        dataa = out.read()
        # 解压缩数据流
        out = io.BytesIO(zlib.decompress(dataa))
        return np.load(out)

    def loadDataBase(self, type):

        conn = sqlite3.connect(
            "/Users/zhuhaoran/Desktop/V3.0/data/inspurer.db")  # 建立数据库连接
        cur = conn.cursor()  # 得到游标对象

        if type == 1:
            self.knew_id = []
            self.knew_name = []
            self.knew_face_feature = []
            cur.execute('select id, name, face_feature from worker_info')
            origin = cur.fetchall()
            for row in origin:
                print(row[0])
                self.knew_id.append(row[0])
                print(row[1])
                self.knew_name.append(row[1])
                print(self.convert_array(row[2]))
                self.knew_face_feature.append(self.convert_array(row[2]))
        if type == 2:
            self.logcat_id = []
            self.logcat_name = []
            self.logcat_datetime = []
            self.logcat_late = []
            cur.execute('select id,name,datetime,late from logcat')
            origin = cur.fetchall()
            for row in origin:
                print(row[0])
                self.logcat_id.append(row[0])
                print(row[1])
                self.logcat_name.append(row[1])
                print(row[2])
                self.logcat_datetime.append(row[2])
                print(row[3])
                self.logcat_late.append(row[3])
        cur.close()
        conn.close()

    def insertARow(self, Row, type):
        conn = sqlite3.connect(
            "/Users/zhuhaoran/Desktop/V3.0/data/inspurer.db")  # 建立数据库连接
        cur = conn.cursor()  # 得到游标对象
        if type == 1:
            cur.execute("insert into worker_info (id,name,face_feature) values(?,?,?)",
                        (Row[0], Row[1], self.adapt_array(Row[2])))

            print("adapt_array = ")
            print(self.adapt_array(Row[2]))

            print("写人脸数据成功")
        if type == 2:
            cur.execute("insert into logcat (id,name,datetime,late) values(?,?,?,?)",
                        (Row[0], Row[1], Row[2], Row[3]))
            print("写日志成功")
            pass
        cur.close()
        conn.commit()
        conn.close()
        pass
