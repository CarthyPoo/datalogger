# JCT Technology Ltd Datalogger 1.0
# by Andrew Keeley (andy@pcman.ca)
# March 2018

# standard / third party libraries
from PyQt4 import QtCore, QtGui
import datetime

# project libraries
from inc.main_ui import Ui_MainWindow
import inc.resources_rc
from config import *


class MainUI(Ui_MainWindow):
	def __init__(self, window, regmap):
		super(MainUI, self).__init__()										# initialise superclass
		self.setupUi(window)												# create layout in window
		window.resized.connect(self.winresized)								# intercept window resize event
		self.actionExit.triggered.connect(window.close)
		self.actionAbout.triggered.connect(self.about)
		self.actionSetup.triggered.connect(window.reset)

		self.splashpm = QtGui.QPixmap(":/images/logo.png")
		self.splash = QtGui.QSplashScreen(self.splashpm, QtCore.Qt.WindowStaysOnTopHint)

		# set icons
		ico = QtGui.QIcon()
		ico.addFile(':/images/icon 16x16.png', QtCore.QSize(16,16))
		ico.addFile(':/images/icon 24x24.png', QtCore.QSize(24,24))
		ico.addFile(':/images/icon 32x32.png', QtCore.QSize(32,32))
		ico.addFile(':/images/icon 48x48.png', QtCore.QSize(48,48))
		window.setWindowIcon(ico)

		self.centralwidget.setStyleSheet("QToolTip {background-color:#444; border:0px;}")

		# configure ui with default values
		self.lblCommError.setVisible(False)									# error invisible at startup
		self.edtDate.setDate(datetime.datetime.now())						# populate date box to today

		# disable auto buttons
		self.btnAutoY1.setEnabled(False)
		self.btnAutoY2.setEnabled(False)

		self.lcdNumber1.display("")
		self.lcdNumber2.display("")
		self.lcdNumber3.display("")
		self.lcdNumber4.display("")
		self.lcdNumber5.display("")
		self.lcdNumber6.display("")
		self.lcdNumber7.display("")
		self.lcdNumber8.display("")

		self.cmbPlot1a.addItem("None")
		self.cmbPlot1b.addItem("None")
		self.cmbPlot1c.addItem("None")
		self.cmbPlot2a.addItem("None")
		self.cmbPlot2b.addItem("None")
		self.cmbPlot2c.addItem("None")
		self.cmbPlot3a.addItem("None")
		self.cmbPlot3b.addItem("None")
		self.cmbPlot3c.addItem("None")
		self.cmbPlot4a.addItem("None")
		self.cmbPlot4b.addItem("None")
		self.cmbPlot4c.addItem("None")
		self.cmbDigital1.addItem("None")
		self.cmbDigital2.addItem("None")
		self.cmbDigital3.addItem("None")
		self.cmbDigital4.addItem("None")
		self.cmbDigital5.addItem("None")
		self.cmbDigital6.addItem("None")
		self.cmbDigital7.addItem("None")
		self.cmbDigital8.addItem("None")

		for reg in regmap:
			self.cmbPlot1a.addItem(reg[0])  									# add modbus registers to comboboxes
			self.cmbPlot1b.addItem(reg[0])
			self.cmbPlot1c.addItem(reg[0])
			self.cmbPlot2a.addItem(reg[0])
			self.cmbPlot2b.addItem(reg[0])
			self.cmbPlot2c.addItem(reg[0])
			self.cmbPlot3a.addItem(reg[0])
			self.cmbPlot3b.addItem(reg[0])
			self.cmbPlot3c.addItem(reg[0])
			self.cmbPlot4a.addItem(reg[0])
			self.cmbPlot4b.addItem(reg[0])
			self.cmbPlot4c.addItem(reg[0])
			self.cmbDigital1.addItem(reg[0])
			self.cmbDigital2.addItem(reg[0])
			self.cmbDigital3.addItem(reg[0])
			self.cmbDigital4.addItem(reg[0])
			self.cmbDigital5.addItem(reg[0])
			self.cmbDigital6.addItem(reg[0])
			self.cmbDigital7.addItem(reg[0])
			self.cmbDigital8.addItem(reg[0])

		# set annotation text
		try:
			self.btnAnn1.setText(ANNOTATION_1)  							# set custom text on button
			self.btnAnn1.setVisible(ANNOTATION_1 != "")  					# hide button if no text
		except NameError:
			self.btnAnn1.setVisible(False)  							# hide button if custom text not defined

		try:
			self.btnAnn2.setText(ANNOTATION_2)
			self.btnAnn2.setVisible(ANNOTATION_2 != "")
		except NameError:
			self.btnAnn2.setVisible(False)

		try:
			self.btnAnn3.setText(ANNOTATION_3)
			self.btnAnn3.setVisible(ANNOTATION_3 != "")
		except NameError:
			self.btnAnn3.setVisible(False)

		try:
			self.btnAnn4.setText(ANNOTATION_4)
			self.btnAnn4.setVisible(ANNOTATION_4 != "")
		except NameError:
			self.btnAnn4.setVisible(False)

		try:
			self.btnAnn5.setText(ANNOTATION_5)
			self.btnAnn5.setVisible(ANNOTATION_5 != "")
		except NameError:
			self.btnAnn5.setVisible(False)

		try:
			self.btnAnn6.setText(ANNOTATION_6)
			self.btnAnn6.setVisible(ANNOTATION_6 != "")
		except NameError:
			self.btnAnn6.setVisible(False)

	def about(self):
		self.splash.show()

	def winresized(self):													# extend window resize event handler
		x = self.centralwidget.width()										# get x dimension of window
		self.lcd5.setVisible(x > 700)										# show LCD and 5 its combo if width > 800
		self.lcd6.setVisible(x > 900)										# show LCD and 6 its combo if width > 1000
		self.lcd7.setVisible(x > 1100)										# show LCD and 7 its combo if width > 1200
		self.lcd8.setVisible(x > 1300)										# show LCD and 8 its combo if width > 1400
