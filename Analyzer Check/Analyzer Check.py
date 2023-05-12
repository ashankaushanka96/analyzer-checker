import sys
from _thread import *
import time
import datetime
import socket
import pyttsx3
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets,QtGui
from  PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy
import configparser

# tmp = configparser.ConfigParser()
# tmp.read('temp.tmp')
tmp = configparser.ConfigParser()

config = configparser.ConfigParser()
config.read('client_config.ini')

engine = pyttsx3.init()

host = socket.gethostname()
# host = '172.20.202.151'
port = 1241

class ComboSelection:
    def __init__(self, selection):
        self.selection = selection

def voice(phrase):
    engine.setProperty("rate", 100)
    voice = engine.getProperty('voices')
    engine.setProperty('voice', voice[1].id)
    engine.say(phrase)
    engine.runAndWait()


def decode_message(msg):
    msg = msg[:-1]
    msg_split = (msg).split(",")
    for comp_msg in msg_split:
        comp_msg_split = comp_msg.split("=")
        try:
            
            tmp.read('temp.tmp')
            comp_short_code = comp_msg_split[0]
            now_status = comp_msg_split[1]
            early_status = tmp[comp_short_code]['status']
            holiday = tmp[comp_short_code]['holiday']

            startTime = tmp[comp_short_code]['startime']
            endTime = tmp[comp_short_code]['endtime']
            runninngDates = tmp[comp_short_code]['runninngdates']

            currenttime = datetime.datetime.now().strftime("%H:%M:%S")
            weekdaytime = datetime.datetime.now().weekday()
            if (str(weekdaytime) in str(runninngDates)):
                if startTime < currenttime and currenttime < endTime:
                    
                    if holiday == '1':
                        status = '4'
                    elif early_status == '0' and now_status == '1':
                        status = now_status
                        print(f"{comp_short_code} Anlayzer Started")
                        name = config[comp_short_code]['name']
                        phrase = f"{name} is Started"
                        voice(phrase)
                    elif  now_status == '0':
                        print(f"{comp_short_code} Anlayzer Down")
                        status = now_status
                        name = config[comp_short_code]['name']
                        phrase = f"{name} is Down, Please check"
                        voice(phrase)
                    else:
                        status = now_status
                else:
                    status = '2'
            else:
                status = '3'
            tmp[comp_short_code]['status'] = status      
            with open('temp.tmp', 'w+') as configfile:
                tmp.write(configfile)
                configfile.close()
            
        except Exception as e:
            print(f"error : {e}")
            continue

class client:
    def __init__(self):
        ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Waiting for connection')
        try:
            ClientSocket.connect((host, port))
        except socket.error as e:
            print(str(e))
        self.ClientSocket = ClientSocket

    def getmsg(self):
        Response = self.ClientSocket.recv(2048)
        msg = Response.decode('utf-8')
        decode_message(msg)
        return msg
        self.ClientSocket.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("table_2.ui", self)
        self.tableWidget.setColumnWidth(0,250)
        self.tableWidget.setColumnWidth(1,150)
        self.tableWidget.setColumnWidth(2,200)
        self.tableWidget.setColumnWidth(3,200)
        self.tableWidget.setColumnWidth(4,200)
        self.tableWidget.setColumnWidth(5,250)
        self.tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        list = ["Select the Analyzer"]
        tmp.read('temp.tmp')
        for section_name in tmp.sections():
            name = tmp[section_name]['name']
            list.append(name)
        self.comboBox.addItems(list)
        self.comboBox.setCurrentIndex(0)
        self.comboBox.currentTextChanged.connect(self.combo_selected)

        self.pushButtonHoliday.clicked.connect(self.pushbuttonholiday)
        self.pushButtonOpen.clicked.connect(self.pushbuttonopen)

        self.loadPermanantData()
        start_new_thread(self.loaddata, ())
    
    def combo_selected(self):
        selection = self.comboBox.currentText()
        combo = ComboSelection(selection)
        return combo
    
    def pushbuttonholiday(self):
        name = self.combo_selected().selection
        tmp.read('temp.tmp')
        for section_name in tmp.sections():
            if tmp[section_name]['name'] == name:
                tmp[section_name]['holiday'] = '1'      
                with open('temp.tmp', 'w+') as configfile:
                    tmp.write(configfile)
                    configfile.close()
                row = tmp.sections().index(section_name)
                self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem('Processing'))
                self.tableWidget.item(row, 2).setTextAlignment(4)
                self.tableWidget.item(row, 2).setBackground(QtGui.QColor(251, 254, 1))

    def pushbuttonopen(self):
        name = self.combo_selected().selection
        tmp.read('temp.tmp')
        for section_name in tmp.sections():
            if tmp[section_name]['name'] == name:
                tmp[section_name]['holiday'] = '0'      
                with open('temp.tmp', 'w+') as configfile:
                    tmp.write(configfile)
                    configfile.close()
                row = tmp.sections().index(section_name)
                self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem('Processing'))
                self.tableWidget.item(row, 2).setTextAlignment(4)
                self.tableWidget.item(row, 2).setBackground(QtGui.QColor(251, 254, 1))

    def update_table_data(self):
        tmp.read('temp.tmp')
        for section_name in tmp.sections():
            row = tmp.sections().index(section_name)
            status = tmp[section_name]['status']

            if status == '0':
                self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem('Not Running'))
                self.tableWidget.item(row, 2).setTextAlignment(4)
                self.tableWidget.item(row, 2).setBackground(QtGui.QColor(255, 0, 0))
            elif status == '1':
                self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem('Running'))
                self.tableWidget.item(row, 2).setTextAlignment(4)
                self.tableWidget.item(row, 2).setBackground(QtGui.QColor(0, 255, 0))
            elif status == '2':
                self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem('Not Run This Time'))
                self.tableWidget.item(row, 2).setTextAlignment(4)
                self.tableWidget.item(row, 2).setBackground(QtGui.QColor(251, 254, 1))
            elif status == '3':
                self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem('Not Run For Today'))
                self.tableWidget.item(row, 2).setTextAlignment(4)
                self.tableWidget.item(row, 2).setBackground(QtGui.QColor(251, 254, 1))
            elif status == '4':
                self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem('Market Holiday'))
                self.tableWidget.item(row, 2).setTextAlignment(4)
                self.tableWidget.item(row, 2).setBackground(QtGui.QColor(251, 254, 1))
            elif status == '5':
                self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem('Processing'))
                self.tableWidget.item(row, 2).setTextAlignment(4)
                self.tableWidget.item(row, 2).setBackground(QtGui.QColor(251, 254, 1))
            
        self.tableWidget.viewport().update()
    def rundates(self,runninngdates):
        # weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        if '6' in runninngdates:
            return 'Sunday - Friday'
        if '4' in runninngdates:
            return 'Monday - Friday'

        
    def loadPermanantData(self):
        self.tableWidget.setRowCount(len(tmp.sections()))
        tmp.read('temp.tmp')
        for section_name in tmp.sections():
            row = tmp.sections().index(section_name)
            name = tmp[section_name]['name']
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(name))
            self.tableWidget.item(row, 0).setTextAlignment(1)
            self.tableWidget.item(row, 0).setBackground(QtGui.QColor(200, 147, 32))

            ip = tmp[section_name]['ip']
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(ip))
            self.tableWidget.item(row, 1).setTextAlignment(4)
            self.tableWidget.item(row, 1).setBackground(QtGui.QColor(184, 27, 222))

            startime = tmp[section_name]['startime']
            print(type(startime))
            self.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(startime + ' GMT'))
            self.tableWidget.item(row, 3).setTextAlignment(4)
            self.tableWidget.item(row, 3).setBackground(QtGui.QColor(184, 27, 222))

            endtime = tmp[section_name]['endtime']
            self.tableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(endtime + ' GMT'))
            self.tableWidget.item(row, 4).setTextAlignment(4)
            self.tableWidget.item(row, 4).setBackground(QtGui.QColor(184, 27, 222))

            runninngdates = tmp[section_name]['runninngdates']
            self.tableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem(self.rundates(runninngdates)))
            self.tableWidget.item(row, 5).setTextAlignment(4)
            self.tableWidget.item(row, 5).setBackground(QtGui.QColor(184, 27, 222))

    def loaddata(self):
        while True:
            self.update_table_data()
            time.sleep(1)      

def create_temp():
    for section_name in config.sections():
        ip = config[section_name]['ip']
        name = config[section_name]['name']
        starttime = config[section_name]['startTime']
        endtime = config[section_name]['endTime']
        runninngdates = config[section_name]['runninngDates']
        config[section_name] = {'ip': ip, 'name': name, 'startime':starttime,'endtime':endtime, 'runninngdates':runninngdates, 'holiday': '0', 'status': '5'}
    print("Here")
    with open('temp.tmp', 'w+') as configfile:
        config.write(configfile)
        configfile.close()
create_temp()

app = QApplication(sys.argv)
mainWindow = MainWindow()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainWindow)
widget.show()


c= client()
def client_start():    
    while True:
        c.getmsg()
        time.sleep(2)


try:
    start_new_thread(client_start, ())
    sys.exit(app.exec_())
except:
    print("Existing")

