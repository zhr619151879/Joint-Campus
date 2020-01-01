# -*- coding: utf-8 -*-
import time
import wx
import wx.grid
# import sqlite3
import pymysql as mysql
from time import localtime, strftime
import os
import io
import zlib
import dlib  # 人脸识别的库dlib
import numpy as np  # 数据处理的库numpy
import cv2  # 图像处理的库OpenCv
import managerWin
import dataLayer


haobo_path = "/Users/zhuhaoran/Desktop/V3.0/"

# 还要加入操作数据库操作（管理员密码）
# 菜单项ID
ID_NEW_REGISTER = 1
ID_FINISH_REGISTER = 2
ID_START_PUNCHCARD = 3
ID_END_PUNCARD = 4
ID_OPEN_LOGCAT = 5
ID_CLOSE_LOGCAT = 6
ID_LOGIN_MANAGER = 7
ID_EXIT_MANAGER = 8
ID_WORKER_UNAVIABLE = -1
font = cv2.FONT_HERSHEY_SIMPLEX

# 人脸数据文件
PATH_FACE = "/Users/zhuhaoran/Desktop/V3.0/data/face_img_database/"

# 提取人脸
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(
    '/Users/zhuhaoran/Desktop/V3.0/model/shape_predictor_68_face_landmarks.dat')

# face recognition model, the object maps human faces into 128D vectors
facerec = dlib.face_recognition_model_v1(
    "/Users/zhuhaoran/Desktop/V3.0/model/dlib_face_recognition_resnet_model_v1.dat")


# 计算欧式距离
def return_euclidean_distance(feature_1, feature_2):
    feature_1 = np.array(feature_1)
    feature_2 = np.array(feature_2)
    dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
    print("欧式距离: ", dist)
    if dist > 0.4:
        return "diff"
    else:
        return "same"


# initialize
class WAS(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="刷脸签到考勤系统", size=(920, 560))
        self.data = dataLayer.DataBaseWorker()
        self.initMenu()
        self.initInfoText()
        self.initGallery()
        # self.initDatabase()
        self.initData()

    def initData(self):
        self.name = ""
        self.id = ID_WORKER_UNAVIABLE
        self.face_feature = ""
        self.pic_num = 0
        self.flag_registed = False
        self.puncard_time = "9:00:00"
        self.data.loadDataBase(1)

    def initMenu(self):

        menuBar = wx.MenuBar()  # 生成菜单栏
        menu_Font = wx.Font()  # Font(faceName="consolas",pointsize=20)
        menu_Font.SetPointSize(14)
        menu_Font.SetWeight(wx.BOLD)

        registerMenu = wx.Menu()  # 生成菜单
        self.new_register = wx.MenuItem(registerMenu, ID_NEW_REGISTER, "新建录入")
        self.new_register.SetBitmap(
            wx.Bitmap("/Users/zhuhaoran/Desktop/V3.0/drawable/new_register.png"))

        # self.new_register.SetTextColour("SLATE BLUE")
        self.new_register.SetFont(menu_Font)
        registerMenu.Append(self.new_register)
        registerMenu.AppendSeparator()

        self.finish_register = wx.MenuItem(registerMenu, ID_FINISH_REGISTER, "完成录入")
        self.finish_register.SetBitmap(
            wx.Bitmap("/Users/zhuhaoran/Desktop/V3.0/drawable/finish_register.png"))

        self.finish_register.SetTextColour("SLATE BLUE")
        self.finish_register.SetFont(menu_Font)
        # 没点新建就设为unable
        self.finish_register.Enable(False)
        registerMenu.Append(self.finish_register)
        registerMenu.AppendSeparator()

        puncardMenu = wx.Menu()
        self.start_punchcard = wx.MenuItem(puncardMenu, ID_START_PUNCHCARD, "开始签到")
        self.start_punchcard.SetBitmap(
            wx.Bitmap("/Users/zhuhaoran/Desktop/V3.0/drawable/start_punchcard.png"))

        self.start_punchcard.SetTextColour(wx.RED)
        self.start_punchcard.SetFont(menu_Font)
        puncardMenu.Append(self.start_punchcard)
        puncardMenu.AppendSeparator()

        self.end_puncard = wx.MenuItem(puncardMenu, ID_END_PUNCARD, "结束签到")
        self.end_puncard.SetBitmap(
            wx.Bitmap("/Users/zhuhaoran/Desktop/V3.0/drawable/end_puncard.png"))
        self.end_puncard.SetTextColour(wx.RED)
        self.end_puncard.SetFont(menu_Font)
        self.end_puncard.Enable(False)
        puncardMenu.Append(self.end_puncard)
        puncardMenu.AppendSeparator()

        logcatMenu = wx.Menu()
        self.open_logcat = wx.MenuItem(logcatMenu, ID_OPEN_LOGCAT, "打开日志")
        self.open_logcat.SetBitmap(
            wx.Bitmap("/Users/zhuhaoran/Desktop/V3.0/drawable/open_logcat.png"))
        self.open_logcat.SetFont(menu_Font)
        self.open_logcat.SetTextColour("SLATE BLUE")
        logcatMenu.Append(self.open_logcat)
        logcatMenu.AppendSeparator()

        self.close_logcat = wx.MenuItem(logcatMenu, ID_CLOSE_LOGCAT, "关闭日志")
        self.close_logcat.SetBitmap(
            wx.Bitmap("/Users/zhuhaoran/Desktop/V3.0/drawable/close_logcat.png"))
        self.close_logcat.SetFont(menu_Font)
        self.close_logcat.SetTextColour("SLATE BLUE")
        self.close_logcat.Enable(False)
        logcatMenu.Append(self.close_logcat)
        logcatMenu.AppendSeparator()

        managerMenu = wx.Menu()
        self.manager_login = wx.MenuItem(managerMenu, ID_LOGIN_MANAGER, '登录')
        self.manager_login.SetBitmap(
            wx.Bitmap("/Users/zhuhaoran/Desktop/V3.0/drawable/start_punchcard.png")
        )
        self.manager_login.SetFont(menu_Font)
        self.manager_login.SetTextColour("SLATE BLUE")
        self.manager_login.Enable(True)
        managerMenu.Append(self.manager_login)
        managerMenu.AppendSeparator()

        self.manager_exit = wx.MenuItem(managerMenu, ID_EXIT_MANAGER, '注销')
        self.manager_exit.SetBitmap(
            wx.Bitmap("/Users/zhuhaoran/Desktop/V3.0/drawable/end_puncard.png")
        )
        self.manager_exit.SetFont(menu_Font)
        self.manager_exit.SetTextColour("SLATE BLUE")
        self.manager_exit.Enable(False)
        managerMenu.Append(self.manager_exit)
        managerMenu.AppendSeparator()

        menuBar.Append(registerMenu, "人脸录入")
        menuBar.Append(puncardMenu, "刷脸签到")
        menuBar.Append(logcatMenu, "考勤日志")
        menuBar.Append(managerMenu, "管理")

        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.OnNewRegisterClicked, id=ID_NEW_REGISTER)
        self.Bind(wx.EVT_MENU, self.OnFinishRegisterClicked, id=ID_FINISH_REGISTER)
        self.Bind(wx.EVT_MENU, self.OnStartPunchCardClicked, id=ID_START_PUNCHCARD)
        self.Bind(wx.EVT_MENU, self.OnEndPunchCardClicked, id=ID_END_PUNCARD)
        self.Bind(wx.EVT_MENU, self.OnOpenLogcatClicked, id=ID_OPEN_LOGCAT)
        self.Bind(wx.EVT_MENU, self.OnCloseLogcatClicked, id=ID_CLOSE_LOGCAT)
        self.Bind(wx.EVT_MENU, self.onLoginManagerClicked, id=ID_LOGIN_MANAGER)
        self.Bind(wx.EVT_MENU, self.onExitManagerClicked, id=ID_EXIT_MANAGER)

    def ifLoginValid(self):
        login_flag = 0

        def on_but_login(event):
            user_name = entry_user.GetValue()
            pass_word = (entry_pass.GetValue())
            print(user_name, pass_word)
            if (not user_name or not pass_word):
                show_message('用户名或密码不能为空')
            if user_name == acc and pass_word == str(pwd):
                show_message('登录成功')
                frame.Destroy()
                # 传入数据库对象
                self.frame1 = managerWin.ManagerWin(self.data)
                self.manager_login.Enable(False)
                self.manager_exit.Enable(True)
                self.frame1.Show()
            else:
                show_message('用户名或密码错误')
                entry_user.Clear()
                entry_pass.Clear()

        def show_message(word=""):
            dlg = wx.MessageDialog(None, word, u"提示")

            if dlg.ShowModal() == wx.ID_YES:
                pass
            dlg.Destroy()

        acc = 'root'
        pwd = 123456
        # self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        # 判断是否管理员
        frame = wx.Frame(parent=None, title='Login', size=(200, 200))
        panel = wx.Panel(frame, -1)
        label_user = wx.StaticText(panel, -1, "usr:", pos=(0, 30))
        label_pass = wx.StaticText(panel, -1, "pwd:", pos=(0, 80))
        entry_user = wx.TextCtrl(panel, -1, size=(50, 20), pos=(50, 30))
        entry_pass = wx.TextCtrl(panel, -1, size=(50, 20), pos=(50, 80), style=wx.TE_PASSWORD)
        but_login = wx.Button(panel, -1, "登陆", size=(60, 40), pos=(50, 120))
        # 给按钮绑定事件
        frame.Bind(wx.EVT_BUTTON, on_but_login, but_login)
        frame.Show()
        # print(login_flag)
        return login_flag

    def onLoginManagerClicked(self, event):
        self.ifLoginValid()

    def onExitManagerClicked(self, event):
        self.manager_login.Enable(True)
        self.manager_exit.Enable(False)
        # self.frame1.OnCloseWindow(event)

    # 点击了打开日记事件
    def OnOpenLogcatClicked(self, event):

        if (self.id ==  ID_WORKER_UNAVIABLE):
            wx.MessageBox('请先刷脸签到!', '温馨提示', wx.OK)
            return

        self.open_logcat.Enable(False)
        self.close_logcat.Enable(True)

        # 加载数据库
        self.data.loadDataBase(2)  # 用一个列表返回数据库 不要赋值给self (data = xx.loadDataBase() )
        # 必须要变宽才能显示 scroll
        self.SetSize(980, 560)
        grid = wx.grid.Grid(self, pos=(320, 0), size=(640, 500))
        # 行数列数
        grid.CreateGrid(100, 4)
        # 画水平与垂直线
        for i in range(100):
            for j in range(4):
                grid.SetCellAlignment(i, j, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        # name of first row
        grid.SetColLabelValue(0, "工号")
        grid.SetColLabelValue(1, "姓名")
        grid.SetColLabelValue(2, "打卡时间")
        grid.SetColLabelValue(3, "是否迟到")
        # Size of each col
        grid.SetColSize(0, 120)
        grid.SetColSize(1, 120)
        grid.SetColSize(2, 150)
        grid.SetColSize(3, 150)

        grid.SetCellTextColour(wx.BLUE)

        # 建立请求连接
        host_ip = "47.96.157.49"
        host_usr = "root"
        host_psw = "123lalala"
        host_db = "inspurer"
        conn = mysql.connect(host_ip, host_usr, host_psw, host_db)
        mycursor = conn.cursor()
        sqlQuery = 'Select id, name, datetime, late from logcat where id = %s'
        val = self.id
        print(val)
        print(type(self.id), type(val))
        mycursor.execute(sqlQuery, val)
        origin = mycursor.fetchall()
        logcat_id = []
        logcat_name = []
        logcat_datetime = []
        logcat_late = []
        for row in origin:
            logcat_id.append(row[0])
            logcat_name.append(row[1])
            logcat_datetime.append(row[2])
            logcat_late.append(row[3])
        mycursor.close()
        conn.close()

        # for i, id in enumerate(self.data.logcat_id):
        for i, id in enumerate(logcat_id):
            grid.SetCellValue(i, 0, str(id))
            grid.SetCellValue(i, 1, logcat_name[i])
            grid.SetCellValue(i, 2, logcat_datetime[i])
            grid.SetCellValue(i, 3, logcat_late[i])
            grid.SetCellTextColour(i, 3, wx.RED) if logcat_late[i] == 'yes' else grid.SetCellTextColour(i, 3,wx.GREEN)
        # Not allowed to edit
        grid.EnableEditing(False)
        pass

    def OnCloseLogcatClicked(self, event):
        self.SetSize(920, 560)
        self.open_logcat.Enable(True)
        self.close_logcat.Enable(False)
        self.initGallery()
        pass

    # 新录入信息
    def register_cap(self, event):
        # 创建 cv2 摄像头对象
        self.cap = cv2.VideoCapture(0)
        # cap.set(propId, value)
        # 设置视频参数，propId设置的视频参数，value设置的参数值
        # self.cap.set(3, 600)
        # self.cap.set(4,600)
        # cap是否初始化成功
        while self.cap.isOpened():
            # cap.read()
            # 返回两个值：
            #    一个布尔值true/false，用来判断读取视频是否成功/是否到视频末尾
            flag, im_rd = self.cap.read()

            # 每帧数据延时1ms，延时为0读取的是静态帧
            cv2.waitKey(1)
            # 人脸数 dets
            dets = detector(im_rd, 1)
            # 检测到人脸
            if len(dets) != 0:
                biggest_face = dets[0]
                # 取占比最大的脸（即离最近）
                maxArea = 0
                for det in dets:
                    w = det.right() - det.left()
                    h = det.top() - det.bottom()
                    if w * h > maxArea:
                        biggest_face = det
                        maxArea = w * h
                        # 绘制矩形框

                # cv2.rectangle(im_rd, tuple([biggest_face.left(), biggest_face.top()]),
                #               tuple([biggest_face.right(), biggest_face.bottom()]),
                #               (255, 0, 0), 2)
                cv2.rectangle(im_rd, (biggest_face.left(), biggest_face.top()),
                              (biggest_face.right(), biggest_face.bottom()),
                              (255, 0, 0), 2)
                cv2.putText(im_rd, 'Recording_Face', (biggest_face.left(), biggest_face.top() - 7), font, 1,
                            (255, 0, 0),
                            1)
                cv2.namedWindow('new')
                cv2.imshow('Picture', im_rd)
                cv2.waitKey(500)
                # shape[0]得到图片的高 shape[1]得到图片的宽 shape[2]得到图片的图像通道数量 (即行和列）
                img_height, img_width = im_rd.shape[:2]
                # OpenCV默认把图像读成BGR格式 因此需要转化
                # image1 = cv2.cvtColor(im_rd, cv2.COLOR_BGR2RGB)
                # 显示图片
                # pic = wx.Bitmap.FromBuffer(img_width, img_height, image1)
                # self.bmp.SetBitmap(pic)

                # 获取当前捕获到的图像的所有人脸的特征，存储到 features_cap_arr(第二个参数是指定人脸位置）
                shape = predictor(im_rd, biggest_face)  # 灰化处理
                features_cap = facerec.compute_face_descriptor(im_rd, shape)

                # 对于某张人脸，遍历所有存储的人脸特征
                for i, knew_face_feature in enumerate(self.data.knew_face_feature):
                    # 将某张人脸与存储的所有人脸数据进行比对 （欧式距离）
                    compare = return_euclidean_distance(features_cap, knew_face_feature)
                    if compare == "same":  # 找到了相似脸
                        self.infoText.AppendText(self.getDateAndTime() + "工号:" + str(self.data.knew_id[i])
                                                 + " 姓名:" + self.data.knew_name[i] + " 的人脸数据已存在\r\n")
                        # 录入取消
                        self.flag_registed = True
                        self.OnFinishRegister()
                        return

                        # print(features_known_arr[i][-1])
                face_height = biggest_face.bottom() - biggest_face.top()
                face_width = biggest_face.right() - biggest_face.left()
                # 三维,(高，宽，RGB通道）
                im_blank = np.zeros((face_height, face_width, 3), np.uint8)
                # 复制
                try:
                    for ii in range(face_height):
                        for jj in range(face_width):
                            im_blank[ii][jj] = im_rd[biggest_face.top() + ii][biggest_face.left() + jj]

                    # 解决python3下使用cv2.imwrite存储带有中文路径图片
                    if len(self.name) > 0:
                        # cv2.imwrite(PATH_FACE + self.name +  "/img_face_" + str(self.pic_num) + ".jpg", im_blank)
                        cv2.imencode('.jpg', im_blank)[1].tofile(
                            PATH_FACE + str(self.id) + self.name + "/img_face_" + str(self.pic_num) + ".jpg")  # 正确方法
                        self.pic_num += 1
                        print(self.pic_num)
                        print("写入本地：",
                              str(PATH_FACE + str(self.id) + self.name) + "/img_face_" + str(self.pic_num) + ".jpg")
                        self.infoText.AppendText(
                            self.getDateAndTime() + "图片:" + str(self.name) + "/img_face_" + str(
                                self.pic_num) + ".jpg保存成功\r\n")
                except:
                    print("保存照片异常,请对准摄像头")

                # cv2.imshow('Picture', im_rd)

            if self.pic_num == 10:
                break
        self.cap.release()
        cv2.destroyAllWindows()
        self.OnFinishRegister()
        # if self.new_register.IsEnabled():
        #     _thread.exit()
        #     pass
        # if self.pic_num == 10:
        #     self.OnFinishRegister()
        #     _thread.exit()

    def OnNewRegisterClicked(self, event):
        self.new_register.Enable(False)
        self.finish_register.Enable(True)
        self.data.loadDataBase(1)
        while self.id == ID_WORKER_UNAVIABLE:
            self.id = wx.GetNumberFromUser(message="请输入您的工号(-1退出)",
                                           prompt="工号", caption="温馨提示",
                                           value=ID_WORKER_UNAVIABLE,
                                           parent=self.bmp, max=100000000, min=ID_WORKER_UNAVIABLE)

            if self.id == -1:
                self.new_register.Enable(True)
                self.finish_register.Enable(False)
                break

            for knew_id in self.data.knew_id:
                if knew_id == self.id:
                    self.id = ID_WORKER_UNAVIABLE
                    wx.MessageBox(message="工号已存在，请重新输入", caption="警告")

            while self.name == '':
                self.name = wx.GetTextFromUser(message="请输入您的的姓名,用于创建姓名文件夹",
                                               caption="温馨提示",
                                               default_value="", parent=self.bmp)

                # 监测是否重名
                for exsit_name in (os.listdir(PATH_FACE)):
                    if (str(self.id) + self.name) == exsit_name:
                        wx.MessageBox(message="工号+姓名已存在，请重新输入", caption="警告")
                        self.name = ''
                        break
            os.makedirs(PATH_FACE + str(self.id) + self.name)
            # threading.Thread(target=self.register_cap, args=(event,)).start()
            self.register_cap(event)

    # 完成注册事件
    def OnFinishRegister(self):
        self.new_register.Enable(True)
        self.finish_register.Enable(False)
        self.cap.release()
        cv2.destroyAllWindows()
        self.bmp.SetBitmap(wx.Bitmap(self.pic_index))

        if self.flag_registed == True:
            dir = PATH_FACE + str(self.id) + self.name
            print(dir)
            for file in os.listdir(dir):
                os.remove(dir + "/" + file)
                print("已删除已录入人脸的图片", dir + "/" + file)
            os.rmdir(PATH_FACE + str(self.id) + self.name)
            print("已删除已录入人脸的姓名文件夹", dir)
            self.initData()
            return

        if self.pic_num > 0:
            pics = os.listdir(PATH_FACE + str(self.id) + self.name)
            feature_list = []
            feature_average = []
            for i in range(len(pics)):
                pic_path = PATH_FACE + str(self.id) + self.name + "/" + pics[i]
                print("正在读的人脸图像：", pic_path)
                img = cv2.imread(pic_path)
                # img = iio.imread(pic_path)
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                dets = detector(img_gray, 1)
                if len(dets) != 0:
                    shape = predictor(img_gray, dets[0])
                    face_descriptor = facerec.compute_face_descriptor(img_gray, shape)
                    # 将第 i 个图片的特征点加入到列表中
                    feature_list.append(face_descriptor)
                else:
                    face_descriptor = 0
                    print("未在照片中识别到人脸")

            if len(feature_list) > 0:
                for j in range(128):
                    # 防止越界
                    feature_average.append(0)
                    for i in range(len(feature_list)):
                        feature_average[j] += feature_list[i][j]
                    feature_average[j] = (feature_average[j]) / len(feature_list)
                self.data.insertARow([self.id, self.name, feature_average], 1)
                self.infoText.AppendText(self.getDateAndTime() + "工号:" + str(self.id)
                                         + " 姓名:" + self.name + " 的人脸数据已成功存入\r\n")

        else:
            os.rmdir(PATH_FACE + str(self.id) + self.name)
            print("已删除空文件夹", PATH_FACE + str(self.id) + self.name)
        self.initData()

    def OnFinishRegisterClicked(self, event):
        self.OnFinishRegister()
        pass

    def punchcard_cap(self, event):
        self.cap = cv2.VideoCapture(0)
        # cap.set(propId, value)
        # 设置视频参数，propId设置的视频参数，value设置的参数值
        # self.cap.set(3, 600)
        # self.cap.set(4,600)
        # cap是否初始化成功
        while self.cap.isOpened():
            flag, im_rd = self.cap.read()
            # 每帧数据延时1ms，延时为0读取的是静态帧
            kk = cv2.waitKey(1)
            # 人脸数 dets
            dets = detector(im_rd, 1)

            # 检测到人脸
            if len(dets) != 0:
                biggest_face = dets[0]
                # 取占比最大的脸
                maxArea = 0
                for det in dets:
                    w = det.right() - det.left()
                    h = det.top() - det.bottom()
                    if w * h > maxArea:
                        biggest_face = det
                        maxArea = w * h
                        # 绘制矩形框

                cv2.rectangle(im_rd, (biggest_face.left(), biggest_face.top()),
                              (biggest_face.right(), biggest_face.bottom()),
                              (255, 0, 255), 2)

                img_height, img_width = im_rd.shape[:2]
                # image1 = cv2.cvtColor(im_rd, cv2.COLOR_BGR2RGB)
                # pic = wx.Bitmap.FromBuffer(img_width, img_height, image1)
                # 显示图片在panel上
                # self.bmp.SetBitmap(pic)

                cv2.namedWindow('new')
                cv2.imshow('recognizing...', im_rd)

                # 获取当前捕获到的图像的所有人脸的特征，存储到 features_cap_arr
                shape = predictor(im_rd, biggest_face)
                features_cap = facerec.compute_face_descriptor(im_rd, shape)

                # 对于某张人脸，遍历所有存储的人脸特征
                for i, knew_face_feature in enumerate(self.data.knew_face_feature):
                    # 将某张人脸与存储的所有人脸数据进行比对
                    compare = return_euclidean_distance(features_cap, knew_face_feature)
                    if compare == "same":  # 找到了相似脸
                        cv2.putText(im_rd, self.data.knew_name[i], (biggest_face.left(), biggest_face.top() - 7), font,
                                    1,
                                    (255, 0, 0))
                        cv2.imshow('recognizing...', im_rd)
                        cv2.waitKey(2000)
                        print("same")
                        flag = 0
                        # time
                        nowdt = self.getDateAndTime()
                        # 查看日志里当天是否已经有该名字
                        for j, logcat_name in enumerate(self.data.logcat_name):
                            # 将时间 [2018-09-28 19:04:09] 前半部分提取出来
                            print(logcat_name, nowdt[1:nowdt.index(" ")])
                            print(self.data.logcat_datetime[j][1:self.data.logcat_datetime[j].index(" ")])
                            if logcat_name == self.data.knew_name[i] and nowdt[1:nowdt.index(" ")] == \
                                    self.data.logcat_datetime[
                                        j][
                                    1:self.data.logcat_datetime[
                                        j].index(" ")]:
                                self.infoText.AppendText(nowdt + "工号:" + str(self.data.knew_id[i])
                                                         + " 姓名:" + self.data.knew_name[i] + " 签到失败,重复签到\r\n")
                                self.id = self.data.knew_id[i]
                                flag = 1
                                break

                        if flag == 1:
                            self.OnEndPunchCardClicked(event)
                            self.cap.release()
                            cv2.destroyAllWindows()
                            return

                        # 取时间的后一部分 [2018-09-28 19:04:09]
                        if time.strptime(nowdt[nowdt.index(" ") + 1:-1], '%H:%M:%S') \
                                <= time.strptime(self.puncard_time, '%H:%M:%S'):
                            self.infoText.AppendText(nowdt + "工号:" + str(self.data.knew_id[i])
                                                     + " 姓名:" + self.data.knew_name[i] + " 成功签到,且未迟到\r\n")
                            # 将签到数据写入数据库
                            self.data.insertARow([self.data.knew_id[i], self.data.knew_name[i], nowdt, "no"], 2)
                        else:
                            self.infoText.AppendText(nowdt + "工号:" + str(self.data.knew_id[i])
                                                     + " 姓名:" + self.data.knew_name[i] + " 成功签到,但迟到了\r\n")
                            self.data.insertARow([self.data.knew_id[i], self.data.knew_name[i], nowdt, "yes"], 2)


                        self.id = self.data.knew_name[i]

                        # 更新数据库
                        self.data.loadDataBase(2)
                        # break
                        self.OnEndPunchCardClicked(event)
                        self.cap.release()
                        cv2.destroyAllWindows()
                        return

                cv2.putText(im_rd, 'Unknown', (biggest_face.left(), biggest_face.top() - 7), font, 1, (255, 0, 0))
                cv2.imshow('recognizing...', im_rd)
                if (self.start_punchcard.IsEnabled()):
                    self.cap.release()
                    cv2.destroyAllWindows()
                    return

                    # 按下结束签到后...
                    # if self.start_punchcard.IsEnabled():
                    #     self.bmp.SetBitmap(wx.Bitmap(self.pic_index))
                    # _thread.exit()
                    # return

    def OnStartPunchCardClicked(self, event):
        # cur_hour = datetime.datetime.now().hour
        # print(cur_hour)
        # if cur_hour>=8 or cur_hour<6:
        #     wx.MessageBox(message='''您错过了今天的签到时间，请明天再来\n
        #     每天的签到时间是:6:00~7:59''', caption="警告")
        #     return
        self.start_punchcard.Enable(False)
        self.end_puncard.Enable(True)
        self.data.loadDataBase(2)
        # threading.Thread(target=self.punchcard_cap, args=(event,)).start()
        # _thread.start_new_thread(self.punchcard_cap,(event,))
        self.punchcard_cap(event)
        pass

    def OnEndPunchCardClicked(self, event):
        self.start_punchcard.Enable(True)
        self.end_puncard.Enable(False)
        pass

    def initInfoText(self):
        info = "\r\n" + self.getDateAndTime() + "程序初始化成功\r\n"
        # 第二个参数水平混动条
        self.infoText = wx.TextCtrl(parent=self, size=(320, 500),
                                    style=(wx.TE_MULTILINE | wx.HSCROLL | wx.TE_READONLY))
        # 前景色，也就是字体颜色
        self.infoText.SetForegroundColour((100, 149, 237))
        # self.infoText.SetLabel(self.info)
        self.infoText.AppendText(info)
        font = wx.Font()
        font.SetPointSize(12)
        font.SetWeight(wx.BOLD)
        font.SetUnderlined(True)

        self.infoText.SetFont(font)
        # self.infoText.SetBackgroundColour('TURQUOISE')
        self.infoText.SetBackgroundColour((255, 218, 185))
        pass

    def initGallery(self):
        self.pic_index = wx.Image("/Users/zhuhaoran/Desktop/V3.0/drawable/index.png",
                                  wx.BITMAP_TYPE_ANY).Scale(600, 500)
        self.bmp = wx.StaticBitmap(parent=self, pos=(320, 0), bitmap=wx.Bitmap(self.pic_index))
        pass

    def getDateAndTime(self):
        date_and_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        return "[" + date_and_time + "]"




app = wx.App()
frame = WAS()
frame.Show()
app.MainLoop()
