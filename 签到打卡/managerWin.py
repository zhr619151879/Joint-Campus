# -*- coding:utf-8 -*-
# @Time : 2019/12/20 10:11 上午
# @Author: zhr619151879
# @Keymap: 「command+1:surround command+p:parameter ctr+o overide」
# @File : managerWin.py

import wx
import wx.grid
import sqlite3
import Manager_worker_win
import dataLayer
from time import localtime, strftime
import os
from skimage import io as iio
import io
import zlib
import dlib  # 人脸识别的库dlib
import numpy as np  # 数据处理的库numpy
import cv2  # 图像处理的库OpenCv


class ManagerWin(wx.Frame):

    def __init__(self, data):
        wx.Frame.__init__(self, parent=None, title="管理员登录", size=(200, 200))
        self.acc = 'root'
        self.pwd = 123456
        st = wx.StaticText(parent = self, label = '  欢迎管理员  '+self.acc+' 登录',
                               size = wx.DefaultSize, style =0 )
        st.SetOwnForegroundColour(wx.RED)
        st.SetFont(wx.Font(18,wx.DECORATIVE,wx.ITALIC,wx.NORMAL))
        self.initButton()
        self.data = data


    # 定义一个消息弹出框的函数
    def show_message(self, word=""):
        dlg = wx.MessageDialog(None, word, u"提示")

        if dlg.ShowModal() == wx.ID_YES:
            pass
        dlg.Destroy()


    def OnCloseWindow(self, event):
        self.Destroy()



    def initButton(self):
        self.open_log_btn = wx.Button(self, -1, '查看日志', pos = (0, 50))
        self.Bind(wx.EVT_BUTTON, self.OnOpenLogcatClicked, self.open_log_btn)

        self.close_log_btn = wx.Button(self,-1, '关闭日志', pos = (100,50))
        self.close_log_btn.Enable(False)

        self.Bind(wx.EVT_BUTTON, self.onCloseLogcatClicked, self.close_log_btn)

        self.manager_worker_btn = wx.Button(self,-1,'管理员工',pos = (0,100))
        self.Bind(wx.EVT_BUTTON, self.onManagerWorkerClicked,self.manager_worker_btn)
        pass

    # 管理员工按钮点击事件
    def onManagerWorkerClicked(self, event):
        frame = Manager_worker_win.WorkerWin(self.data).Show()


    def onCloseLogcatClicked(self, event):
        self.open_log_btn.Enable(True)
        self.close_log_btn.Enable(False)
        self.SetSize(200,200)
        self.grid.Destroy()

    # 点击了打开日记按钮
    def OnOpenLogcatClicked(self, event):
        self.open_log_btn.Enable(False)
        self.close_log_btn.Enable(True)
        self.SetSize(700, 560)
        # 加载数据库
        self.data.loadDataBase(2)
        # 必须要变宽才能显示 scroll
        self.SetSize(980, 560)
        self.grid = wx.grid.Grid(self, pos=(200, 0), size=(640, 500))
        # 行数列数
        self.grid.CreateGrid(100, 4)
        # 画水平与垂直线
        for i in range(100):
            for j in range(4):
                self.grid.SetCellAlignment(i, j, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        # name of first row
        self.grid.SetColLabelValue(0, "工号")
        self.grid.SetColLabelValue(1, "姓名")
        self.grid.SetColLabelValue(2, "打卡时间")
        self.grid.SetColLabelValue(3, "是否迟到")
        # Size of each col
        self.grid.SetColSize(0, 120)
        self.grid.SetColSize(1, 120)
        self.grid.SetColSize(2, 150)
        self.grid.SetColSize(3, 150)

        self.grid.SetCellTextColour(wx.BLUE)
        for i, id in enumerate(self.data.logcat_id):
            self.grid.SetCellValue(i, 0, str(id))
            self.grid.SetCellValue(i, 1, self.data.logcat_name[i])
            self.grid.SetCellValue(i, 2, self.data.logcat_datetime[i])
            self.grid.SetCellValue(i, 3, self.data.logcat_late[i])

            self.grid.SetCellTextColour(i, 3, wx.RED) if self.data.logcat_late[i] == 'yes' else self.grid.SetCellTextColour(i, 3,
                                                                                                           wx.GREEN)
        self.grid.EnableEditing(True)
        pass

    def eventHandler(self, event):
        pass



if __name__ == '__main__':
    app = wx.App()
    frame = ManagerWin()
    frame.Show()
    app.MainLoop()