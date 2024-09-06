#!/usr/bin/env python

# JCT Technology Ltd Datalogger 1.0
# by Andrew Keeley (andy@pcman.ca)
# March 2018

# standard / third party libraries
import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph
import time
import gc

# project libraries
from config import *
from inc.logger import Logger
from inc.circbuff import CircularBuffer
from inc.mainui import MainUI
from inc.mainwin import MainWindow
from inc.persist import Persist
from inc.recorder import Recorder
from modbus import ModbusClient

class ModBusRX:
    def __init__(self, modbus_client, registermap):
        self.modbus_client = modbus_client
        self.registermap = registermap

    def start(self):
        self.modbus_client.start()

    def stop(self):
        self.modbus_client.stop()

    def updatedata(self):
        # implementation of updatedata method
        pass

def prepareregisters():
    # ...
    return regmap

if __name__ == "__main__":
    pyqtgraph.setConfigOptions(antialias=True)

    app = QtGui.QApplication(sys.argv)                                                    
    splashpm = QtGui.QPixmap(":/images/logo.png")
    splash = QtGui.QSplashScreen(splashpm, QtCore.Qt.WindowStaysOnTopHint)

    while True:
        splash.show()
        app.processEvents()

        registers = [(30001, 'U2'), (30002, 'U2')]  # define your register map here
        modbus_client = ModbusClient(('localhost', 1700), registers, 1)
        modbus = ModBusRX(modbus_client, registers)  
        modbus_client.start()

        win = MainWindow(app)                                                        
        ui = MainUI(win, registers[0])                                            
        appname = str(win.windowTitle())
        history = CircularBuffer(registers[0])                                       
        recorder = Recorder(ui, registers[0])
        persist = Persist(ui, appname)
        logger = Logger(registers[0], win, ui, history, recorder, persist, modbus)  

        persist.connect()

        time.sleep(1)
        win.show()                                                                    
        splash.finish(win)

        # pyqtgraph bug workaround
        g = win.geometry()
        win.resize(g.width()-1,g.height())
        win.resize(g.width(), g.height())

        modbus.start()
        modbus.updatedata.connect(logger.modbusupdate)

        exitcode = app.exec_()                                                        
        recorder.close()
        persist.close()
        modbus.stop()
        while not modbus.hasstopped():
            time.sleep(0.1)

        del logger
        del recorder
        del win
        del ui
        del history
        del modbus
        del persist

        gc.collect()

        if exitcode != -1:
            break