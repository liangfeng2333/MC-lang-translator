# -- coding: utf-8 --**、
import json
import linecache
import os
import re
import http.client
import hashlib
import urllib
import random
import codecs
from PyQt5.Qt import *
from PyQt5.uic import loadUi
from PyQt5 import uic
from PyQt5.QtWidgets import QFileDialog
from threading import Thread
from PyQt5.QtCore import pyqtSignal, QObject
import configparser

from PyQt5.uic.properties import QtWidgets

global input_file
global output_path
global text_output
global text_output1
global text_output2
filePath = ""
input_path = ""
count = 0
count_now = 1
file = ""
file_name = ""

api_read = open('config.json', 'r')
api_read1 = api_read.read()
api_read2 = json.loads(api_read1)
dict_api = eval(str(api_read2))
appid = dict_api['baidu_id']  # 填写你的appid
secretKey = dict_api['baidu_key']  # 填写你的密钥
api_read.close()


# 信号库

class SignalStore(QObject):
    # 定义一种信号
    progress_update = pyqtSignal(int)

    # 还可以定义其他作用的信号


so = SignalStore()


class Child:
    def __init__(self):
        self.api = uic.loadUi("api.ui")
        self.ui = uic.loadUi("fanyi.ui")


class Trans(Child):

    def __init__(self):
        # 从文件中加载UI定义
        super().__init__()
        self.ui.pushButton_3.clicked.connect(self.handleCalc)
        self.ui.pushButton_2.clicked.connect(self.output)
        self.ui.pushButton.clicked.connect(self.input)
        self.ui.pushButton_4.clicked.connect(self.writeapi)
        self.ui.lineEdit.textChanged.connect(self.input_text_edit)
        self.ui.lineEdit_2.textChanged.connect(self.output_path_edit)

    # def closeEvent(self, event):
    #     sys.exit(app.exec_())

    def input_text_edit(self):
        global input_file
        input_file = self.ui.lineEdit.text()

    def output_path_edit(self):
        global output_path
        output_path = self.ui.lineEdit_2.text()

    def input(self):
        global input_file
        input_file, _ = QFileDialog.getOpenFileName(
            self.ui,  # 父窗口对象
            "选择.lang文件",  # 标题
            r"d:\\",  # 起始目录
            "文本类型(*.txt *.lang)"  # 选择类型过滤项，过滤内容在括号中
        )
        self.ui.lineEdit.setText(str(input_file))

    def output(self):
        global output_path
        output_path = QFileDialog.getExistingDirectory(self.ui, "选择存储路径")
        self.ui.lineEdit_2.setText(str(output_path))

    def handleCalc(self):
        def start():
            global file
            global count
            file = input_file

            # print(file)
            count = len(open(file, 'r', encoding='utf-8').readlines())  # 行数
            # print("总行数：", count)
            self.ui.progressBar.setRange(0, count)
            str_start = "="  # 检索的起始字符
            text_ext = []  # 提取字符

            b = "1"
            a = "1" in b  # 用于后面判断是否存在§

            self.while1()

        worker1 = Thread(target=start)
        worker1.start()

    def while1(self):
        def run(count_now=0):
            while count_now <= count:  # 遍历行

                text = linecache.getline(input_file, count_now)
                # print(text)
                text_ext1 = re.findall(r'(?<==).+', text)  # 匹配等号后内容
                text_ext1 = ''.join(text_ext1)  # 去掉[]括号
                # print(text_ext1)
                # text_ext2 = "§" in str(text_ext1) #判断是否存在§
                # if text_ext2 == 1:  #暂时不判断
                #     print("存在§")
                # else:
                #     print("不存在§")

                ####————————————————————————————————————————百度翻译API
                from winreg import REG_FULL_RESOURCE_DESCRIPTOR

                # appid = '20190609000305977'  # 填写你的appid
                # secretKey = 'sBeKPb3neYafb3qD4hjE'  # 填写你的密钥

                httpClient = None
                myurl = '/api/trans/vip/translate'

                fromLang = 'en'  # 原文语种
                toLang = 'zh'  # 译文语种

                httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
                salt = random.randint(32768, 65536)
                q = text_ext1
                sign = appid + q + str(salt) + secretKey
                sign = hashlib.md5(sign.encode()).hexdigest()
                myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
                    q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
                    salt) + '&sign=' + sign
                httpClient.request('GET', myurl, 'TIMEOUT=3')
                # response是HTTPResponse对象
                response = httpClient.getresponse()
                result_all = response.read().decode("utf-8")
                httpClient.close()

                ##——————————笨逼解析
                result = json.loads(result_all)
                if 'trans_result' in result:
                    result1 = result['trans_result']
                    result2 = result1[0]
                    result3 = result2['dst']
                else:
                    result3 = ""

                ####————————————————————————————————————————翻译

                # global text_output1
                # global text_output2
                #
                # text_output1 = (str(count_now) + "/" + str(count)+text_ext1)
                # text_output2 = (str(count_now) + "/" + str(count)+result3)
                # self.ui.textBrowser.append(text_output1)
                # self.ui.textBrowser_2.append(text_output2)

                text_top = re.findall(r'.+(?<==)', text)  # =以及之前内容
                text_top = ''.join(text_top)  # 去掉[]括号
                # print(text_top)
                count_now = count_now + 1  # 当前行数
                self.ui.progressBar.setValue(count_now)

                # print(result)

                # ————————写入
                file_name = str(output_path) + '/zh_CN.lang'  # 输出文件
                # print(file_name)
                with codecs.open(file_name, 'a', encoding='utf-8') as out_put_file:
                    out_put_file.write(str(text_top) + str(result3) + '\n')
                # self.read_now()
            else:
                count_now = 0
                # print("终止")

        your_thread = Thread(target=run())
        # 设置线程为守护线程，防止退出主线程时，子线程仍在运行
        your_thread.setDaemon(True)
        # 新线程启动
        your_thread.start()

        # worker2 = Thread(target=run())
        # worker2.run()

    def writeapi(self):
        child = Child()
        child.api.show()

    # def closeEvent(self, event):
    #     """
    #     对MainWindow的函数closeEvent进行重构
    #     退出软件时结束所有进程
    #     :param event:
    #     :return:
    #     """
    #     reply = QtWidgets.QMessageBox.question(self,
    #                                            '本程序',
    #                                            "是否要退出程序？",
    #                                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
    #                                            QtWidgets.QMessageBox.No)
    #     if reply == QtWidgets.QMessageBox.Yes:
    #         event.accept()
    #         os._exit(0)
    #     else:
    #         event.ignore()

app = QApplication([])

stats = Trans()
stats.ui.show()
app.exec_()
os._exit(0)

