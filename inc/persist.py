# JCT Technology Ltd Datalogger 1.0
# by Andrew Keeley (andy@pcman.ca)
# April 2018

# Persist class
# stores and retrieves UI state

# standard / third party libraries
import shelve
import os
from bsddb.db import DBPermissionsError as DBPermissionError


class Persist():
	def __init__(self, mainui, appname):
		self.shelf = None
		self.ui = mainui
		self.appname = appname

		self.ui.edtCustomerName.editingFinished.connect(lambda: self.saveedit(self.ui.edtCustomerName))
		self.ui.edtLocation.editingFinished.connect(lambda: self.saveedit(self.ui.edtLocation))
		self.ui.edtServiceOrder.editingFinished.connect(lambda: self.saveedit(self.ui.edtServiceOrder))
		self.ui.cmbPlot1a.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbPlot1a))
		self.ui.cmbPlot1b.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbPlot1b))
		self.ui.cmbPlot1c.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbPlot1c))
		self.ui.cmbPlot2a.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbPlot2a))
		self.ui.cmbPlot2b.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbPlot2b))
		self.ui.cmbPlot2c.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbPlot2c))
		self.ui.cmbPlot3a.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbPlot3a))
		self.ui.cmbPlot3b.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbPlot3b))
		self.ui.cmbPlot3c.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbPlot3c))
		self.ui.cmbPlot4a.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbPlot4a))
		self.ui.cmbPlot4b.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbPlot4b))
		self.ui.cmbPlot4c.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbPlot4c))
		self.ui.cmbDigital1.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbDigital1))
		self.ui.cmbDigital2.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbDigital2))
		self.ui.cmbDigital3.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbDigital3))
		self.ui.cmbDigital4.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbDigital4))
		self.ui.cmbDigital5.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbDigital5))
		self.ui.cmbDigital6.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbDigital6))
		self.ui.cmbDigital7.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbDigital7))
		self.ui.cmbDigital8.currentIndexChanged.connect(lambda: self.savecombo(self.ui.cmbDigital8))
		self.ui.actionTwo_Charts.triggered.connect(lambda: self.saveoption(self.ui.actionTwo_Charts))
		self.ui.actionLock_X_Axes.triggered.connect(lambda: self.saveoption(self.ui.actionLock_X_Axes))
		self.user = os.path.expanduser("~")

	def connect(self):
		try:
			if not os.path.exists(os.path.join(self.user, self.appname)):
				os.makedirs(os.path.join(self.user, self.appname))
			self.shelf = shelve.open(os.path.join(self.user, self.appname, 'persist.db'))
			self.restoreedit(self.ui.edtCustomerName)
			self.restoreedit(self.ui.edtLocation)
			self.restoreedit(self.ui.edtServiceOrder)
			self.restorecombo(self.ui.cmbPlot1a)
			self.restorecombo(self.ui.cmbPlot1b)
			self.restorecombo(self.ui.cmbPlot1c)
			self.restorecombo(self.ui.cmbPlot2a)
			self.restorecombo(self.ui.cmbPlot2b)
			self.restorecombo(self.ui.cmbPlot2c)
			self.restorecombo(self.ui.cmbPlot3a)
			self.restorecombo(self.ui.cmbPlot3b)
			self.restorecombo(self.ui.cmbPlot3c)
			self.restorecombo(self.ui.cmbPlot4a)
			self.restorecombo(self.ui.cmbPlot4b)
			self.restorecombo(self.ui.cmbPlot4c)
			self.restorecombo(self.ui.cmbDigital1)
			self.restorecombo(self.ui.cmbDigital2)
			self.restorecombo(self.ui.cmbDigital3)
			self.restorecombo(self.ui.cmbDigital4)
			self.restorecombo(self.ui.cmbDigital5)
			self.restorecombo(self.ui.cmbDigital6)
			self.restorecombo(self.ui.cmbDigital7)
			self.restorecombo(self.ui.cmbDigital8)
			self.restoreoption(self.ui.actionTwo_Charts)
			self.restoreoption(self.ui.actionLock_X_Axes)
			return True
		except (ValueError, DBPermissionError, OSError):
			self.shelf = None
			return False

	def close(self):
		if self.shelf is not None:
			self.shelf.close()
			self.shelf = None

	def save(self, name, value):
		if self.shelf is not None:
			self.shelf[str(name)] = value

	def read(self, name):
		if self.shelf is not None:
			if str(name) in self.shelf:
				return self.shelf[(str(name))]
		return None

	def restoreedit(self, obj):
		t = self.read(obj.objectName())
		obj.setText(t if t is not None else "")

	def restorecombo(self, obj):
		s = self.read(obj.objectName())
		obj.setCurrentIndex(s if s is not None else 0)
		if obj.currentIndex() == -1:
			obj.setCurrentIndex(0)

	def restoreoption(self, obj):
		b = self.read(obj.objectName())
		if b is None:
			b = obj is self.ui.actionTwo_Charts					# default to True if two_charts or False if lock_x
		if obj.isChecked() != b:
			obj.trigger()

	def saveedit(self, obj):
		self.save(obj.objectName(), str(obj.text()))

	def savecombo(self, obj):
		self.save(obj.objectName(), obj.currentIndex())

	def saveoption(self, obj):
		self.save(obj.objectName(), obj.isChecked())