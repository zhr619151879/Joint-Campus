# -*- coding:utf-8 -*-
# @Time : 2019/12/23 3:19 下午
# @Author: zhr619151879
# @Keymap: 「command+1:surround command+p:parameter ctr+o overide」
# @File : Manager_worker_win.py

import wx
import wx.grid
import sqlite3
import zlib
import numpy as np  # 数据处理的库numpy


class WorkerWin(wx.Frame):
    def __init__(self, data):
        wx.Frame.__init__(self, parent=None, title='员工信息', size=(500, 500))
        self.data = data
        self.data.loadDataBase(1)
        self.data.loadDataBase(2)  # 删除员工后日志也会改变
        self.initGallery()
        self.initButton()


    def initGallery(self):
        self.grid = wx.grid.Grid(self, pos=(50, 0), size=(400, 450))
        self.grid.CreateGrid(50, 2)
        for i in range(50):
            for j in range(2):
                self.grid.SetCellAlignment(i, j, wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        self.grid.SetColLabelValue(0,'工号')
        self.grid.SetColLabelValue(1,'姓名')
        self.grid.SetColSize(0,150)
        self.grid.SetColSize(1,150)

        sql = 'Select id, name from worker_info'
        res = self.data.CrudHandler(sql)

        # self.grid.SetCellValue(行,列,值)
        for row in range(len(res)):
            for col in range(len(res[0])):
                self.grid.SetCellValue(row, col, str(res[row][col]))

        self.grid.SetDefaultCellTextColour(wx.BLUE)
        self.grid.EnableEditing(True)

    def initButton(self):
        bmp_add = wx.Bitmap('/Users/zhuhaoran/Documents/GitHub/WorkAttendanceSystem/V2.0/drawable/new_register.png')
        self.button_add = wx.BitmapButton(self,-1,bmp_add,pos=(450,50))

        bmp_modify = wx.Bitmap('/Users/zhuhaoran/Documents/GitHub/WorkAttendanceSystem/V2.0/drawable/finish_register.png')
        self.button_modify = wx.BitmapButton(self,-1,bmp_modify,pos=(450,150))

        bmp_cancel = wx.Bitmap('/Users/zhuhaoran/Documents/GitHub/WorkAttendanceSystem/V2.0/drawable/end_puncard.png')
        self.button_cancel = wx.BitmapButton(self,-1,bmp_cancel,pos=(450,250))





if __name__ == '__main__':
    app = wx.App()
    frame = WorkerWin()
    frame.Show()
    app.MainLoop()
