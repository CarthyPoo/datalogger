# JCT Technology Ltd Datalogger 1.0
# by Andrew Keeley (andy@pcman.ca)
# March 2018

# standard / third party libraries
import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph
import os
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import landscape, letter
import warnings
import pyqtgraph.exporters

# project libraries
from recorder import OPENOK, OPENERR, CLOSED
import misc

ITEMS = 86400
COLOUR1 = '#FFA020'		# orange
COLOUR2 = '#A00000'		# red
COLOUR3 = '#8000FF'		# purple
COLOUR4 = '#0070FF'		# blue
COLOUR5 = '#00A000'		# green
COLOUR6 = '#40C0FF'		# cyan


class Logger():
	def __init__(self, regmap, win, ui, history, recorder, persist, modbus):
		self.regmap = regmap
		self.win = win
		self.ui = ui
		self.history = history
		self.recorder = recorder
		self.persist = persist
		self.modbus = modbus
		self.win.resized.connect(self.resized)  										# intercept window resize event

		# initialise local copies of range
		self.ch1xrange = (0, 0)
		self.ch2xrange = (0, 0)
		self.scl1yrange = (0, 0)
		self.scl2yrange = (0, 0)
		self.scl3yrange = (0, 0)
		self.scl4yrange = (0, 0)
		self.ticks = [[],[]]
		self.annotationindex = 0
		self.annotationtext = ""

		self.autoY2Enabled = False
		self.autoY4Enabled = False

		self.ch1axisleft = False
		self.ch1axisbottom = False
		self.ch1axisright = False
		self.ch2axisleft = False
		self.ch2axisbottom = False
		self.ch2axisright = False

		ui.btnAutoY1.clicked.connect(lambda: self.vb1l.enableAutoRange(self.vb1l.YAxis, True))
		ui.btnAutoY2.clicked.connect(lambda: self.vb1r.enableAutoRange(self.vb1r.YAxis, True))
		ui.btnCh1Pause.clicked.connect(lambda: self.togglepause(ui.btnCh1Pause))
		ui.btnCh2Pause.clicked.connect(lambda: self.togglepause(ui.btnCh2Pause))
		ui.btnCh11min.clicked.connect(lambda: self.vb1.setXRange(ITEMS-61,ITEMS, padding=0))
		ui.btnCh12min.clicked.connect(lambda: self.vb1.setXRange(ITEMS-121,ITEMS, padding=0))
		ui.btnCh15min.clicked.connect(lambda: self.vb1.setXRange(ITEMS-301,ITEMS, padding=0))
		ui.btnCh110min.clicked.connect(lambda: self.vb1.setXRange(ITEMS-601,ITEMS, padding=0))
		ui.btnCh130min.clicked.connect(lambda: self.vb1.setXRange(ITEMS-1801,ITEMS, padding=0))

		ui.btnAutoY3.clicked.connect(lambda: self.vb2l.enableAutoRange(self.vb2l.YAxis, True))
		ui.btnAutoY4.clicked.connect(lambda: self.vb2r.enableAutoRange(self.vb2r.YAxis, True))
		ui.btnCh21min.clicked.connect(lambda: self.vb2.setXRange(ITEMS-61,ITEMS, padding=0))
		ui.btnCh22min.clicked.connect(lambda: self.vb2.setXRange(ITEMS-121,ITEMS, padding=0))
		ui.btnCh25min.clicked.connect(lambda: self.vb2.setXRange(ITEMS-301,ITEMS, padding=0))
		ui.btnCh210min.clicked.connect(lambda: self.vb2.setXRange(ITEMS-601,ITEMS, padding=0))
		ui.btnCh230min.clicked.connect(lambda: self.vb2.setXRange(ITEMS-1801,ITEMS, padding=0))

		ui.btnAnn1.clicked.connect(self.annotationclicked)
		ui.btnAnn2.clicked.connect(self.annotationclicked)
		ui.btnAnn3.clicked.connect(self.annotationclicked)
		ui.btnAnn4.clicked.connect(self.annotationclicked)
		ui.btnAnn5.clicked.connect(self.annotationclicked)
		ui.btnAnn6.clicked.connect(self.annotationclicked)

		ui.btnRec.clicked.connect(self.recordclicked)

		# create combo box change event handlers
		ui.cmbPlot1a.currentIndexChanged.connect(lambda: self.change1(self.ui.cmbPlot1a, self.plt1a))
		ui.cmbPlot1b.currentIndexChanged.connect(lambda: self.change1(self.ui.cmbPlot1b, self.plt1b))
		ui.cmbPlot1c.currentIndexChanged.connect(lambda: self.change1(self.ui.cmbPlot1c, self.plt1c))
		ui.cmbPlot2a.currentIndexChanged.connect(lambda: self.change2(self.ui.cmbPlot2a, self.plt2a))
		ui.cmbPlot2b.currentIndexChanged.connect(lambda: self.change2(self.ui.cmbPlot2b, self.plt2b))
		ui.cmbPlot2c.currentIndexChanged.connect(lambda: self.change2(self.ui.cmbPlot2c, self.plt2c))
		ui.cmbPlot3a.currentIndexChanged.connect(lambda: self.change3(self.ui.cmbPlot3a, self.plt3a))
		ui.cmbPlot3b.currentIndexChanged.connect(lambda: self.change3(self.ui.cmbPlot3b, self.plt3b))
		ui.cmbPlot3c.currentIndexChanged.connect(lambda: self.change3(self.ui.cmbPlot3c, self.plt3c))
		ui.cmbPlot4a.currentIndexChanged.connect(lambda: self.change4(self.ui.cmbPlot4a, self.plt4a))
		ui.cmbPlot4b.currentIndexChanged.connect(lambda: self.change4(self.ui.cmbPlot4b, self.plt4b))
		ui.cmbPlot4c.currentIndexChanged.connect(lambda: self.change4(self.ui.cmbPlot4c, self.plt4c))

		ui.chart1.getViewBox().sigResized.connect(self.resized)
		ui.chart2.getViewBox().sigResized.connect(self.resized)

		ui.actionTwo_Charts.triggered.connect(self.twocharts)
		ui.actionLock_X_Axes.triggered.connect(self.lockxaxes)
		ui.actionReset_Totalisers.triggered.connect(lambda: self.modbus.resettotalisers())
		ui.btnCh1Export.clicked.connect(lambda: self.export(0))
		ui.btnCh2Export.clicked.connect(lambda: self.export(1))
		ui.btnCh1LockY.clicked.connect(lambda: self.lockch1yaxes())
		ui.btnCh2LockY.clicked.connect(lambda: self.lockch2yaxes())

		# create references to chart objects
		self.ch1 = ui.chart1
		self.ch2 = ui.chart2

		# create view boxes
		self.vb1 = self.ch1.getViewBox()
		self.vb2 = self.ch2.getViewBox()

		# create plot items
		self.pi1 = self.ch1.getPlotItem(0)
		self.pi2 = self.ch2.getPlotItem(0)
		self.pi1a = self.ch1.getPlotItem(1)
		self.pi1b = self.ch1.getPlotItem(2)
		self.pi1c = self.ch1.getPlotItem(3)
		self.pi2a = self.ch1.getPlotItem(4)
		self.pi2b = self.ch1.getPlotItem(5)
		self.pi2c = self.ch1.getPlotItem(6)
		self.pi3a = self.ch2.getPlotItem(1)
		self.pi3b = self.ch2.getPlotItem(2)
		self.pi3c = self.ch2.getPlotItem(3)
		self.pi4a = self.ch2.getPlotItem(4)
		self.pi4b = self.ch2.getPlotItem(5)
		self.pi4c = self.ch2.getPlotItem(6)
		self.si1 = self.ch1.getScatterPlotItem()
		self.si2 = self.ch2.getScatterPlotItem()

		# hide autoranging buttons
		self.pi1.hideButtons()
		self.pi2.hideButtons()
		self.pi1a.hideButtons()
		self.pi1b.hideButtons()
		self.pi1c.hideButtons()
		self.pi2a.hideButtons()
		self.pi2b.hideButtons()
		self.pi2c.hideButtons()
		self.pi3a.hideButtons()
		self.pi3b.hideButtons()
		self.pi3c.hideButtons()
		self.pi4a.hideButtons()
		self.pi4b.hideButtons()
		self.pi4c.hideButtons()

		# disable context menus
		self.pi1.setMenuEnabled(False)
		self.pi2.setMenuEnabled(False)

		# create y axes
		self.vb1l = pyqtgraph.ViewBox(enableMenu=False)
		self.vb1r = pyqtgraph.ViewBox(enableMenu=False)
		self.vb2l = pyqtgraph.ViewBox(enableMenu=False)
		self.vb2r = pyqtgraph.ViewBox(enableMenu=False)

		# initialise plots
		self.plt1a = self.pi1a.plot(pen=pyqtgraph.mkPen(color=COLOUR1))
		self.plt1b = self.pi1b.plot(pen=pyqtgraph.mkPen(color=COLOUR2))
		self.plt1c = self.pi1c.plot(pen=pyqtgraph.mkPen(color=COLOUR3))
		self.plt2a = self.pi2a.plot(pen=pyqtgraph.mkPen(color=COLOUR6))
		self.plt2b = self.pi2b.plot(pen=pyqtgraph.mkPen(color=COLOUR5))
		self.plt2c = self.pi2c.plot(pen=pyqtgraph.mkPen(color=COLOUR4))
		self.plt3a = self.pi3a.plot(pen=pyqtgraph.mkPen(color=COLOUR1))
		self.plt3b = self.pi2b.plot(pen=pyqtgraph.mkPen(color=COLOUR2))
		self.plt3c = self.pi2c.plot(pen=pyqtgraph.mkPen(color=COLOUR3))
		self.plt4a = self.pi4a.plot(pen=pyqtgraph.mkPen(color=COLOUR6))
		self.plt4b = self.pi4b.plot(pen=pyqtgraph.mkPen(color=COLOUR5))
		self.plt4c = self.pi4c.plot(pen=pyqtgraph.mkPen(color=COLOUR4))

		# signal when user pans or scales an x-axis
		self.vb1.sigXRangeChanged.connect(self.updatexrange)
		self.vb2.sigXRangeChanged.connect(self.updatexrange)

		# signal when user or autoscale causes change to Y range
		self.vb1l.sigYRangeChanged.connect(self.updateyrange)
		self.vb1r.sigYRangeChanged.connect(self.updateyrange)
		self.vb2l.sigYRangeChanged.connect(self.updateyrange)
		self.vb2r.sigYRangeChanged.connect(self.updateyrange)

		# signal when plot state changes so we can enable/disable auto Y buttons
		self.vb1l.sigStateChanged.connect(self.statechange)
		self.vb1r.sigStateChanged.connect(self.statechange)
		self.vb2l.sigStateChanged.connect(self.statechange)
		self.vb2r.sigStateChanged.connect(self.statechange)

		self.initgraphs()

	def initgraphs(self):
		# hide x-axes until they are configured
		self.hideaxis(self.ch1, 'bottom')
		self.hideaxis(self.ch2, 'bottom')
		self.hideaxis(self.ch1, 'left')
		self.hideaxis(self.ch2, 'left')
		self.hideaxis(self.ch1, 'right')
		self.hideaxis(self.ch2, 'right')

		# enable mouse x-axis only scaling
		self.vb1.setMouseEnabled(x=True, y=False)
		self.vb2.setMouseEnabled(x=True, y=False)

		# set default combo items
		# ui.cmbPlot1.setCurrentIndex(1)
		# ui.cmbPlot2.setCurrentIndex(2)
		# ui.cmbPlot3.setCurrentIndex(3)
		# ui.cmbPlot4.setCurrentIndex(4)

		# add chart 1 left plots
		self.vb1.scene().addItem(self.vb1l)
		self.ch1.getAxis('left').linkToView(self.vb1l)
		self.vb1l.setXLink(self.vb1)
		self.vb1l.addItem(self.plt1a)
		self.vb1l.addItem(self.plt1b)
		self.vb1l.addItem(self.plt1c)
		self.vb1l.setGeometry(self.vb1.sceneBoundingRect())
		self.vb1l.linkedViewChanged(self.vb1, self.vb1l.XAxis)
		self.ch1.getAxis('left').setPen(pyqtgraph.mkPen(color=COLOUR1, width=1))
		# self.showaxis(self.ch1, 'left')

		# add chart 1 right plots
		self.vb1.scene().addItem(self.vb1r)
		self.ch1.getAxis('right').linkToView(self.vb1r)
		self.vb1r.setXLink(self.vb1)
		self.vb1r.addItem(self.plt2a)
		self.vb1r.addItem(self.plt2b)
		self.vb1r.addItem(self.plt2c)
		self.vb1r.setGeometry(self.vb1.sceneBoundingRect())
		self.vb1r.linkedViewChanged(self.vb1, self.vb1r.YAxis)
		self.ch1.getAxis('right').setPen(pyqtgraph.mkPen(color=COLOUR6, width=1))
		# self.showaxis(self.ch1, 'right')

		# add annotations to chart 1
		self.vb1.addItem(self.si1)

		# add chart 2 left plots
		self.vb2.scene().addItem(self.vb2l)
		self.ch2.getAxis('left').linkToView(self.vb2l)
		self.vb2l.setXLink(self.vb2)
		self.vb2l.addItem(self.plt3a)
		self.vb2l.addItem(self.plt3b)
		self.vb2l.addItem(self.plt3c)
		self.vb2l.setGeometry(self.vb2.sceneBoundingRect())
		self.vb2l.linkedViewChanged(self.vb2, self.vb2l.XAxis)
		self.ch2.getAxis('left').setPen(pyqtgraph.mkPen(color=COLOUR1, width=1))
		# self.showaxis(self.ch2, 'left')

		# add chart 2 right plots
		self.vb2.scene().addItem(self.vb2r)
		self.ch2.getAxis('right').linkToView(self.vb2r)
		self.vb2r.setXLink(self.vb2)
		self.vb2r.addItem(self.plt4a)
		self.vb2r.addItem(self.plt4b)
		self.vb2r.addItem(self.plt4c)
		self.vb2r.setGeometry(self.vb2.sceneBoundingRect())
		self.vb2r.linkedViewChanged(self.vb2, self.vb2r.YAxis)
		self.ch2.getAxis('right').setPen(pyqtgraph.mkPen(color=COLOUR6, width=1))
		# self.showaxis(self.ch2, 'right')

		# add annotations to chart 2
		self.vb2.addItem(self.si2)

		# show grid lines
		self.pi1.showGrid(True, True)
		self.pi2.showGrid(True, True)

		# set scaling and panning limits
		self.vb1.setLimits(xMax=86399, xMin=0, minXRange=10)
		self.vb2.setLimits(xMax=86399, xMin=0, minXRange=10)

		# create margins between end of chart and right edge
		self.vb1l.translate(-25, 0)
		self.vb1r.translate(-25, 0)
		self.ch1.getAxis('bottom').translate(-25, 0)
		# self.showaxis(self.ch1, 'bottom')
		self.vb2l.translate(-25, 0)
		self.vb2r.translate(-25, 0)
		self.ch2.getAxis('bottom').translate(-25, 0)
		# self.showaxis(self.ch2, 'bottom')
		self.vb1.translate(-25, 0)
		self.vb2.translate(-25, 0)

		# enable autoranging on both axes
		self.updatetimes(self.vb1)
		self.updatetimes(self.vb2)
		self.vb1l.setYRange(0, 50)
		self.vb2l.setYRange(0, 50)
		self.vb1r.setYRange(0, 50)
		self.vb2r.setYRange(0, 50)
		self.vb1l.enableAutoRange(self.vb1l.YAxis, True)
		self.vb1r.enableAutoRange(self.vb1r.YAxis, True)
		self.vb2l.enableAutoRange(self.vb2l.YAxis, True)
		self.vb2r.enableAutoRange(self.vb2r.YAxis, True)
		self.vb1.setYRange(-10, 10)
		self.vb2.setYRange(-10, 10)

		# set to two minute X range
		self.vb1.setXRange(ITEMS-121, ITEMS, padding=0)
		self.vb2.setXRange(ITEMS-121, ITEMS, padding=0)

	def lockxaxes(self):
		if self.ui.actionLock_X_Axes.isChecked():
			if self.ch2xrange != self.ch1xrange:
				self.ch2.setXRange(self.ch1xrange[0], self.ch1xrange[1], padding=0)
			self.history.syncpause(0)
			self.updatetimes(self.vb2)
			self.update3()
			self.update4()
			self.updateannotations2()

	def twocharts(self):
		self.ui.chart2.setVisible(self.ui.actionTwo_Charts.isChecked())
		self.ui.ch2controls.setVisible(self.ui.actionTwo_Charts.isChecked())
		self.ui.actionLock_X_Axes.setEnabled(self.ui.actionTwo_Charts.isChecked())

	def togglepause(self, btn):
		if btn is self.ui.btnCh1Pause:
			c = 0
			other = self.ui.btnCh2Pause
		else:
			c = 1
			other = self.ui.btnCh1Pause
		if btn.isChecked():
			self.history.pause(c)
		else:
			self.history.unpause(c)
		if self.ui.actionLock_X_Axes.isChecked():
			self.history.syncpause(c)
			other.setChecked(btn.isChecked())

	def updatexrange(self, view, rnge):
		if view is self.vb1:
			self.ch1xrange = rnge
			self.updatetimes(self.vb1)
			if self.ui.actionLock_X_Axes.isChecked():
				if self.ch2xrange != rnge:
					self.ch2.setXRange(rnge[0], rnge[1], padding=0)
		else:
			self.ch2xrange = rnge
			self.updatetimes(self.vb2)
			if self.ui.actionLock_X_Axes.isChecked():
				if self.ch1xrange != rnge:
					self.ch1.setXRange(rnge[0], rnge[1], padding=0)

	def updateyrange(self, view, rnge):
		if view is self.vb1l:
			self.scl1yrange = rnge
			self.ch1.invalidateScene()
		elif view is self.vb1r:
			self.scl2yrange = rnge
			self.ch1.invalidateScene()
		elif view is self.vb2l:
			self.scl3yrange = rnge
			self.ch2.invalidateScene()
		elif view is self.vb2r:
			self.scl4yrange = rnge
			self.ch2.invalidateScene()

	def resized(self):
		r = self.vb1.sceneBoundingRect()
		self.vb1l.setGeometry(r)
		self.vb1r.setGeometry(r)
		r = self.vb2.sceneBoundingRect()
		self.vb2l.setGeometry(r)
		self.vb2r.setGeometry(r)
		self.updatetimes(self.vb1)
		self.updatetimes(self.vb2)

	def statechange(self, view):
		if view is self.vb1l:
			self.ui.btnAutoY1.setEnabled(not view.state['autoRange'][1])
		elif view is self.vb1r:
			if not self.ui.btnCh1LockY.isChecked():
				self.ui.btnAutoY2.setEnabled(not view.state['autoRange'][1])
		elif view is self.vb2l:
			self.ui.btnAutoY3.setEnabled(not view.state['autoRange'][1])
		elif view is self.vb2r:
			if not self.ui.btnCh2LockY.isChecked():
				self.ui.btnAutoY4.setEnabled(not view.state['autoRange'][1])

	def updatetimes(self, view):
		if view is self.vb1:
			width = self.vb1.sceneBoundingRect().width()
			_min = self.ch1xrange[0]
			_min = int(_min) + 1
			_min = max(0, _min)
			_max = self.ch1xrange[1]
			_max = int(round(_max))
			_max = min(ITEMS - 1, _max)
		else:
			width = self.vb2.sceneBoundingRect().width()
			_min = self.ch2xrange[0]
			_min = int(_min) + 1
			_min = max(0, _min)
			_max = self.ch2xrange[1]
			_max = int(round(_max))
			_max = min(ITEMS - 1, _max)

		count = _max - _min
		if count > 0:
			density = count / width
			numticks = width / 60									# minimum of 60 pixels for the timestamp width
			step = int(count / numticks)
			left = int(_min + 60 * density)							# allow 60 pixel left margin on x-axis

			if step == 0:
				step = 1
			if count / step > numticks:
				step += 1

			# print "min=", _min, "max=", _max, "width=", width, "count=", count, "dens=", density, "ticks=", ticks, "step=", step, "start=", stt
			# print _min, stt, stt-_min

			ticks = []
			i = _max
			while i >= left:
				ticks.append(i)
				i -= step
			ticks.reverse()
			if view is self.vb1:
				self.ticks[0] = [list(zip(ticks, [self.history.readtime(0)[i] for i in ticks]))]
				self.ch1.getAxis('bottom').setTicks(self.ticks[0])
			else:
				self.ticks[1] = [list(zip(ticks, [self.history.readtime(1)[i] for i in ticks]))]
				self.ch2.getAxis('bottom').setTicks(self.ticks[1])

	def scale1hasanyplots(self):
		return self.ui.cmbPlot1a.currentIndex() + self.ui.cmbPlot1b.currentIndex() + self.ui.cmbPlot1c.currentIndex() > 0

	def scale2hasanyplots(self):
		return self.ui.cmbPlot2a.currentIndex() + self.ui.cmbPlot2b.currentIndex() + self.ui.cmbPlot2c.currentIndex() > 0

	def scale3hasanyplots(self):
		return self.ui.cmbPlot3a.currentIndex() + self.ui.cmbPlot3b.currentIndex() + self.ui.cmbPlot3c.currentIndex() > 0

	def scale4hasanyplots(self):
		return self.ui.cmbPlot4a.currentIndex() + self.ui.cmbPlot4b.currentIndex() + self.ui.cmbPlot4c.currentIndex() > 0

	def updatedisplay(self):
		self.updatetimes(self.vb1)
		self.update1()
		self.update2()
		self.updateannotations1()
		self.updatetimes(self.vb2)
		self.update3()
		self.update4()
		self.updateannotations2()

	def updateannotations1(self):
		self.si1.clear()
		self.si1.addPoints(self.history.readannotations(0))

	def updateannotations2(self):
		self.si2.clear()
		self.si2.addPoints(self.history.readannotations(1))

	def update1(self):
		self.updateplot(self.ui.cmbPlot1a, self.plt1a, 0)
		self.updateplot(self.ui.cmbPlot1b, self.plt1b, 0)
		self.updateplot(self.ui.cmbPlot1c, self.plt1c, 0)
		self.update1controls()

	def update2(self):
		self.updateplot(self.ui.cmbPlot2a, self.plt2a, 0)
		self.updateplot(self.ui.cmbPlot2b, self.plt2b, 0)
		self.updateplot(self.ui.cmbPlot2c, self.plt2c, 0)
		self.update2controls()

	def update3(self):
		self.updateplot(self.ui.cmbPlot3a, self.plt3a, 1)
		self.updateplot(self.ui.cmbPlot3b, self.plt3b, 1)
		self.updateplot(self.ui.cmbPlot3c, self.plt3c, 1)
		self.update3controls()

	def update4(self):
		self.updateplot(self.ui.cmbPlot4a, self.plt4a, 1)
		self.updateplot(self.ui.cmbPlot4b, self.plt4b, 1)
		self.updateplot(self.ui.cmbPlot4c, self.plt4c, 1)
		self.update4controls()

	def change1(self, cmb, plt):
		self.updateplot(cmb, plt, 0)
		self.update1controls()

	def change2(self, cmb, plt):
		self.updateplot(cmb, plt, 0)
		self.update2controls()

	def change3(self, cmb, plt):
		self.updateplot(cmb, plt, 1)
		self.update3controls()

	def change4(self, cmb, plt):
		self.updateplot(cmb, plt, 1)
		self.update4controls()

	def updateplot(self, cmb, plt, ch):
		i = cmb.currentIndex()
		if i > 0:
			plt.setData(self.history.read(i - 1, ch)[-ITEMS:])
		else:
			plt.clear()

	def update1controls(self):
		ch = 0
		if self.ui.btnCh1LockY.isChecked():
			if self.scale1hasanyplots() or self.scale2hasanyplots():
				ch += self.showaxis(self.ch1, 'left')
				ch += self.showaxis(self.ch1, 'bottom')
				self.ui.ch1shuttle.setEnabled(True)
			else:
				ch += self.hideaxis(self.ch1, 'left')
				ch += self.hideaxis(self.ch1, 'bottom')
				self.ui.ch1shuttle.setEnabled(False)
		else:
			if self.scale1hasanyplots():
				ch += self.showaxis(self.ch1, 'left')
				ch += self.showaxis(self.ch1, 'bottom')
				self.ui.ch1shuttle.setEnabled(True)
			else:
				ch += self.hideaxis(self.ch1, 'left')
				if not self.scale2hasanyplots():
					ch += self.hideaxis(self.ch1, 'bottom')
					self.ui.ch1shuttle.setEnabled(False)
		if ch:
			self.redrawwidget(self.ch1)

	def update2controls(self):
		ch = 0
		if self.ui.btnCh1LockY.isChecked():
			ch += self.hideaxis(self.ch1, 'right')
		else:
			if self.scale2hasanyplots():
				ch += self.showaxis(self.ch1, 'right')
				ch += self.showaxis(self.ch1, 'bottom')
				self.ui.ch1shuttle.setEnabled(True)
			else:
				ch += self.hideaxis(self.ch1, 'right')
				if not self.scale1hasanyplots():
					ch += self.hideaxis(self.ch1, 'bottom')
					self.ui.ch1shuttle.setEnabled(False)
		if ch:
			self.redrawwidget(self.ch1)

	def update3controls(self):
		ch = 0
		if self.ui.btnCh2LockY.isChecked():
			if self.scale3hasanyplots() or self.scale4hasanyplots():
				ch += self.showaxis(self.ch2, 'left')
				ch += self.showaxis(self.ch2, 'bottom')
				self.ui.ch2shuttle.setEnabled(True)
			else:
				ch += self.hideaxis(self.ch2, 'left')
				ch += self.hideaxis(self.ch2, 'bottom')
				self.ui.ch2shuttle.setEnabled(False)
		else:
			if self.scale3hasanyplots():
				ch += self.showaxis(self.ch2, 'left')
				ch += self.showaxis(self.ch2, 'bottom')
				self.ui.ch2shuttle.setEnabled(True)
			else:
				ch += self.hideaxis(self.ch2, 'left')
				if not self.scale4hasanyplots():
					ch += self.hideaxis(self.ch2, 'bottom')
					self.ui.ch2shuttle.setEnabled(False)
		if ch:
			self.redrawwidget(self.ch2)

	def update4controls(self):
		ch = 0
		if self.ui.btnCh2LockY.isChecked():
			ch += self.hideaxis(self.ch2, 'right')
		else:
			if self.scale4hasanyplots():
				ch += self.showaxis(self.ch2, 'right')
				ch += self.showaxis(self.ch2, 'bottom')
				self.ui.ch2shuttle.setEnabled(True)
			else:
				ch += self.hideaxis(self.ch2, 'right')
				if not self.scale3hasanyplots():
					ch += self.hideaxis(self.ch2, 'bottom')
					self.ui.ch2shuttle.setEnabled(False)
		if ch:
			self.redrawwidget(self.ch2)

	def lockch1yaxes(self):
		if self.ui.btnCh1LockY.isChecked():
			self.autoY2Enabled = self.ui.btnAutoY2.isEnabled()
			self.ui.btnAutoY2.setEnabled(False)
			self.vb1r.removeItem(self.plt2a)
			self.vb1r.removeItem(self.plt2b)
			self.vb1r.removeItem(self.plt2c)
			self.vb1l.addItem(self.plt2a)
			self.vb1l.addItem(self.plt2b)
			self.vb1l.addItem(self.plt2c)
		else:
			self.ui.btnAutoY2.setEnabled(self.autoY2Enabled)
			self.vb1l.removeItem(self.plt2a)
			self.vb1l.removeItem(self.plt2b)
			self.vb1l.removeItem(self.plt2c)
			self.vb1r.addItem(self.plt2a)
			self.vb1r.addItem(self.plt2b)
			self.vb1r.addItem(self.plt2c)
		self.update1controls()
		self.update2controls()

	def lockch2yaxes(self):
		if self.ui.btnCh2LockY.isChecked():
			self.autoY4Enabled = self.ui.btnAutoY4.isEnabled()
			self.ui.btnAutoY4.setEnabled(False)
			self.vb2r.removeItem(self.plt4a)
			self.vb2r.removeItem(self.plt4b)
			self.vb2r.removeItem(self.plt4c)
			self.vb2l.addItem(self.plt4a)
			self.vb2l.addItem(self.plt4b)
			self.vb2l.addItem(self.plt4c)
		else:
			self.ui.btnAutoY4.setEnabled(self.autoY2Enabled)
			self.vb2l.removeItem(self.plt4a)
			self.vb2l.removeItem(self.plt4b)
			self.vb2l.removeItem(self.plt4c)
			self.vb2r.addItem(self.plt4a)
			self.vb2r.addItem(self.plt4b)
			self.vb2r.addItem(self.plt4c)
		self.update3controls()
		self.update4controls()

	def hideaxis(self, ch, axis):
		r = 0
		if ch is self.ch1:
			if axis.upper() == 'LEFT':
				if self.ch1axisleft:
					r = 1
				self.ch1axisleft = False
			elif axis.upper() == 'BOTTOM':
				if self.ch1axisbottom:
					r = 1
				self.ch1axisbottom = False
			elif axis.upper() == 'RIGHT':
				if self.ch1axisright:
					r = 1
				self.ch1axisright = False
		elif ch is self.ch2:
			if axis.upper() == 'LEFT':
				if self.ch2axisleft:
					r = 1
				self.ch2axisleft = False
			elif axis.upper() == 'BOTTOM':
				if self.ch2axisbottom:
					r = 1
				self.ch2axisbottom = False
			elif axis.upper() == 'RIGHT':
				if self.ch2axisright:
					r = 1
				self.ch2axisright = False
		ch.hideAxis(axis)
		return r

	def showaxis(self, ch, axis):
		r = 0
		if ch is self.ch1:
			if axis.upper() == 'LEFT':
				if not self.ch1axisleft:
					r = 1
				self.ch1axisleft = True
			elif axis.upper() == 'BOTTOM':
				if not self.ch1axisbottom:
					r = 1
				self.ch1axisbottom = True
			elif axis.upper() == 'RIGHT':
				if not self.ch1axisright:
					r = 1
				self.ch1axisright = True
		elif ch is self.ch2:
			if axis.upper() == 'LEFT':
				if not self.ch2axisleft:
					r = 1
				self.ch2axisleft = True
			elif axis.upper() == 'BOTTOM':
				if not self.ch2axisbottom:
					r = 1
				self.ch2axisbottom = True
			elif axis.upper() == 'RIGHT':
				if not self.ch2axisright:
					r = 1
				self.ch2axisright = True
		ch.showAxis(axis)
		return r

	@staticmethod
	def redrawwidget(widget):				# This is dumb. There should be a better way
		h = widget.height()
		w = widget.width()
		widget.resize(w-1, h)
		widget.resize(w, h)

	def modbusupdate(self, status, registers, timenow):
		index = timenow.hour * 3600 + timenow.minute * 60 + timenow.second
		self.updatecommessage(status)

		self.history.write(registers, index, self.annotationindex)					# save to history

		self.updatelcd(self.ui.lcdNumber1, self.ui.cmbDigital1, registers)			# update the LCD displays
		self.updatelcd(self.ui.lcdNumber2, self.ui.cmbDigital2, registers)
		self.updatelcd(self.ui.lcdNumber3, self.ui.cmbDigital3, registers)
		self.updatelcd(self.ui.lcdNumber4, self.ui.cmbDigital4, registers)
		self.updatelcd(self.ui.lcdNumber5, self.ui.cmbDigital5, registers)
		self.updatelcd(self.ui.lcdNumber6, self.ui.cmbDigital6, registers)
		self.updatelcd(self.ui.lcdNumber7, self.ui.cmbDigital7, registers)
		self.updatelcd(self.ui.lcdNumber8, self.ui.cmbDigital8, registers)

		self.recorder.write(timenow.strftime("%H:%M:%S"), registers, self.annotationtext)
		self.annotationindex = 0
		self.annotationtext = ""
		self.ui.grpAnnotations.setEnabled(True)
		self.updatedisplay()

	def updatecommessage(self, status):
		if False not in status:
			self.ui.lblCommError.setVisible(False)
		else:
			c = 0
			for s in status:
				if not s:
					c += 1
					if c > 1:
						break
			t = 'Server' + ('s ' if c > 1 else ' ')
			for i, s in enumerate(status):
				if not s:
					t += '%d, ' % (i + 1)
			t = t[:-2]
			self.ui.lblCommError.setText(t + ' not responding')
			self.ui.lblCommError.setVisible(True)

	def updatelcd(self, lcd, combo, registers):
		i = combo.currentIndex()
		if i <= 0:
			lcd.display('')
		else:
			i -= 1
			f = "%." + "%df" % self.regmap[i][3]
			if self.regmap[i][2] == 'F':
				t = f % registers[i]
			else:
				t = f % (float(registers[i]) / 10 ** self.regmap[i][3])
			lcd.display(t)

	def export(self, c):
		cmb1a = self.ui.cmbPlot1a.currentIndex() if c == 0 else self.ui.cmbPlot3a.currentIndex()
		cmb1b = self.ui.cmbPlot1b.currentIndex() if c == 0 else self.ui.cmbPlot3b.currentIndex()
		cmb1c = self.ui.cmbPlot1c.currentIndex() if c == 0 else self.ui.cmbPlot3c.currentIndex()
		cmb2a = self.ui.cmbPlot2a.currentIndex() if c == 0 else self.ui.cmbPlot4a.currentIndex()
		cmb2b = self.ui.cmbPlot2b.currentIndex() if c == 0 else self.ui.cmbPlot4b.currentIndex()
		cmb2c = self.ui.cmbPlot2c.currentIndex() if c == 0 else self.ui.cmbPlot4c.currentIndex()
		locky = self.ui.btnCh1LockY.isChecked() if c == 0 else self.ui.btnCh2LockY.isChecked()

		rangex = self.ch1xrange if c == 0 else self.ch2xrange
		rangeyl = self.scl1yrange if c == 0 else self.scl3yrange
		rangeyr = self.scl2yrange if c == 0 else self.scl4yrange

		pyqtgraph.setConfigOption('background', 'w')

		ch = pyqtgraph.PlotWidget()
		pi = ch.getPlotItem()
		vb = pi.getViewBox()
		sipng = pyqtgraph.ScatterPlotItem(size=20, pen=None, pxMode=True)
		sipdf = pyqtgraph.ScatterPlotItem(size=36, pen=None, pxMode=True)
		vbl = pyqtgraph.ViewBox()
		vbr = pyqtgraph.ViewBox()
		plt1a = pi.plot(pen=pyqtgraph.mkPen(COLOUR1, width=2))
		plt1b = pi.plot(pen=pyqtgraph.mkPen(COLOUR2, width=2))
		plt1c = pi.plot(pen=pyqtgraph.mkPen(COLOUR3, width=2))
		plt2a = pi.plot(pen=pyqtgraph.mkPen(COLOUR6, width=2))
		plt2b = pi.plot(pen=pyqtgraph.mkPen(COLOUR5, width=2))
		plt2c = pi.plot(pen=pyqtgraph.mkPen(COLOUR4, width=2))

		if cmb1a > 0:
			plt1a.setData(self.history.read(cmb1a - 1, c)[-ITEMS:])
		if cmb1b > 0:
			plt1b.setData(self.history.read(cmb1b - 1, c)[-ITEMS:])
		if cmb1c > 0:
			plt1c.setData(self.history.read(cmb1c - 1, c)[-ITEMS:])
		if cmb2a > 0:
			plt2a.setData(self.history.read(cmb2a - 1, c)[-ITEMS:])
		if cmb2b > 0:
			plt2b.setData(self.history.read(cmb2b - 1, c)[-ITEMS:])
		if cmb2c > 0:
			plt2c.setData(self.history.read(cmb2c - 1, c)[-ITEMS:])

		sipng.addPoints(self.history.readannotationsexport(c, 20))
		sipdf.addPoints(self.history.readannotationsexport(c, 36))
		ch.getAxis('bottom').setTicks(self.ticks[c])

		p = self.vb1.viewPixelSize()[0] if c == 0 else self.vb2.viewPixelSize()[0]
		# r = self.vb1.viewRange()[0][1] if c == 0 else self.vb2.viewRange()[0][1]
		rangex = (rangex[0] + 25 * p, rangex[1] + 25 * p)

		vb.setXRange(rangex[0], rangex[1], padding=0)
		vbl.setYRange(rangeyl[0], rangeyl[1], padding=0)
		vbr.setYRange(rangeyr[0], rangeyr[1], padding=0)

		path = self.recorder.logfilepath()
		prevtype = self.persist.read('exporttype')
		if prevtype == 'PNG':
			deffilt = "Portable Network Graphic file (*.png)"
		elif prevtype == 'PDF':
			deffilt = "Portable Document Format file (*.pdf)"
		else:
			deffilt = ""
		name = QtGui.QFileDialog.getSaveFileName(
			self.win, "Export Chart", path, "Portable Document Format file (*.pdf);;Portable Network Graphic file (*.png)", deffilt)
		if name == "":
			return
		ext = str(name[-3:]).upper()
		self.persist.save("exporttype", ext)

		labell = ""
		labelr = ""
		if not locky:
			if cmb1a + cmb1b + cmb1c > 0:
				if cmb1a > 0:
					labell += '<span style="color: ' + COLOUR1 + '">' + self.ui.cmbPlot1a.itemText(cmb1a) + '</span>'
					labell += '<span style="color: black">&nbsp;/&nbsp;</span>'
				if cmb1b > 0:
					labell += '<span style="color: ' + COLOUR2 + '">' + self.ui.cmbPlot1a.itemText(cmb1b) + '</span>'
					labell += '<span style="color: black">&nbsp;/&nbsp;</span>'
				if cmb1c > 0:
					labell += '<span style="color: ' + COLOUR3 + '">' + self.ui.cmbPlot1a.itemText(cmb1c) + '</span>'
				else:
					labell = labell[:-47]
			else:
				ch.hideAxis('left')
			if cmb2a + cmb2b + cmb2c > 0:
				if cmb2c > 0:
					labelr += '<span style="color: ' + COLOUR4 + '">' + self.ui.cmbPlot1a.itemText(cmb2c) + '</span>'
					labelr += '<span style="color: black">&nbsp;/&nbsp;</span>'
				if cmb2b > 0:
					labelr += '<span style="color: ' + COLOUR5 + '">' + self.ui.cmbPlot1a.itemText(cmb2b) + '</span>'
					labelr += '<span style="color: black">&nbsp;/&nbsp;</span>'
				if cmb2a > 0:
					labelr += '<span style="color: ' + COLOUR6 + '">' + self.ui.cmbPlot1a.itemText(cmb2a) + '</span>'
				else:
					labelr = labelr[:-47]
			else:
				ch.hideAxis('right')
		else:
			if cmb1a > 0:
				labell += '<span style="color: ' + COLOUR1 + '">' + self.ui.cmbPlot1a.itemText(cmb1a) + '</span>'
				labell += '<span style="color: black">&nbsp;/&nbsp;</span>'
			if cmb1b > 0:
				labell += '<span style="color: ' + COLOUR2 + '">' + self.ui.cmbPlot1a.itemText(cmb1b) + '</span>'
				labell += '<span style="color: black">&nbsp;/&nbsp;</span>'
			if cmb1c > 0:
				labell += '<span style="color: ' + COLOUR3 + '">' + self.ui.cmbPlot1a.itemText(cmb1c) + '</span>'
				labell += '<span style="color: black">&nbsp;/&nbsp;</span>'
			if cmb2c > 0:
				labell += '<span style="color: ' + COLOUR4 + '">' + self.ui.cmbPlot1a.itemText(cmb2c) + '</span>'
				labell += '<span style="color: black">&nbsp;/&nbsp;</span>'
			if cmb2b > 0:
				labell += '<span style="color: ' + COLOUR5 + '">' + self.ui.cmbPlot1a.itemText(cmb2b) + '</span>'
				labell += '<span style="color: black">&nbsp;/&nbsp;</span>'
			if cmb2a > 0:
				labell += '<span style="color: ' + COLOUR6 + '">' + self.ui.cmbPlot1a.itemText(cmb2a) + '</span>'
			else:
				labell = labell[:-47]
			ch.hideAxis('right')

		if ext == "PNG":
			redstyle = {'font-size': '12pt', 'font-weight': 'bold', 'color':'#800'}
			bluestyle = {'font-size': '12pt', 'font-weight': 'bold', 'color':'#008'}
		elif ext == "PDF":
			redstyle = {'font-size': '27pt', 'font-weight': 'normal', 'color':'#800'}
			bluestyle = {'font-size': '27pt', 'font-weight': 'normal', 'color':'#008'}
		elif ext == "SVG":
			redstyle = {'font-size': '6pt; font-weight: normal; color:#800'}
			bluestyle = {'font-size': '6pt; font-weight: normal; color:#008'}
		else:
			redstyle = {}
			bluestyle = {}

		if labell:
			pi.getAxis('left').setLabel(labell, "", **redstyle)
		else:
			ch.hideAxis('left')
		if labelr:
			pi.getAxis('right').setLabel(labelr, "", **bluestyle)
		else:
			ch.hideAxis('right')

		if ext == "PNG":
			ch.resize(1920, 1080)
			ch.scene().addItem(vbl)
			ch.getAxis('left').linkToView(vbl)
			vbl.setXLink(vb)
			vbl.addItem(plt1a)
			vbl.addItem(plt1b)
			vbl.addItem(plt1c)
			if locky:
				vbl.addItem(plt2a)
				vbl.addItem(plt2b)
				vbl.addItem(plt2c)
			vbl.linkedViewChanged(vb, vbl.XAxis)
			ch.getAxis('left').setPen(pyqtgraph.mkPen(color='#800000', width=1))
			if labell:
				ch.showAxis('left')
			vbl.setYRange(0, 10)

			if not locky:
				ch.scene().addItem(vbr)
				pi.getAxis('right').linkToView(vbr)
				vbr.setXLink(vb)
				vbr.addItem(plt2a)
				vbr.addItem(plt2b)
				vbr.addItem(plt2c)
				vbr.linkedViewChanged(vb, vbr.XAxis)
				pi.getAxis('right').setPen(pyqtgraph.mkPen(color='#000080', width=1))
				if labelr:
					pi.showAxis('right')
				vbr.setYRange(0, 10)

			vb.addItem(sipng)

			# print vb.sceneBoundingRect().width(), vb.sceneBoundingRect().height()
			# pd = QtGui.QPixmap(vb.sceneBoundingRect().width(), vb.sceneBoundingRect().height())
			# pt = QtGui.QPainter(pd)
			# ch.render(pt)
			# px = pd.toImage()
			# rgb = px.pixel(301,229)
			# print rgb

			pi.showGrid(True, True)
			#vbl.translate(-40, 0)
			#vbr.translate(-40, 0)
			#vb.translate(-40, 0)							# contains annotations
			vb.setYRange(-10, 10)							# vertically centred
			#ch.getAxis('bottom').translate(-40, 0)

			vb.setXRange(rangex[0], rangex[1], padding=0)
			vbl.setYRange(rangeyl[0], rangeyl[1], padding=0)
			vbr.setYRange(rangeyr[0], rangeyr[1], padding=0)

			font = QtGui.QFont()
			font.setPixelSize(12)
			font.setBold(True)
			ch.getAxis('left').tickFont = font
			ch.getAxis('right').tickFont = font
			ch.getAxis('bottom').tickFont = font
			ch.getAxis('left').setWidth(80)
			ch.getAxis('right').setWidth(80)
			ch.getAxis('bottom').setHeight(40)
			ch.getAxis('bottom').setStyle(tickTextOffset=10)

			legend = '<span style="font-size: 14pt;">'
			if self.history.annotationpresent(c, rangex[0], rangex[1], 0):
				legend += '<span style="font-size: 14pt; color: blue">&#x2605;</span>&nbsp;' + self.ui.btnAnn1.text()
				legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			if self.history.annotationpresent(c, rangex[0], rangex[1], 1):
				legend += '<span style="font-size: 20pt; color: red">&#x2666;</span>&nbsp;' + self.ui.btnAnn2.text()
				legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			if self.history.annotationpresent(c, rangex[0], rangex[1], 2):
				legend += '<span style="font-size: 20pt; color: magenta">&#x25CF;</span>&nbsp;' + self.ui.btnAnn3.text()
				legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			if self.history.annotationpresent(c, rangex[0], rangex[1], 3):
				legend += '<span style="font-size: 20pt; color: #00FF00;">&#x25C0;</span>&nbsp;' + self.ui.btnAnn4.text()
				legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			if self.history.annotationpresent(c, rangex[0], rangex[1], 4):
				legend += '<span style="font-size: 14pt; color: cyan">&#x25B2;</span>&nbsp;' + self.ui.btnAnn5.text()
				legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			if self.history.annotationpresent(c, rangex[0], rangex[1], 5):
				legend += '<span style="font-size: 20pt; color: #FF8000;">&#x25B6;</span>&nbsp;' + self.ui.btnAnn6.text()
				legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			legend = legend[:-24]
			legend += '</span>'

			# legend = '<span style="font-size: 14pt;">'
			# if self.ui.btnAnn1.isVisible():
			# 	legend += '<span style="font-size: 14pt; color: blue">&#x2605;</span>&nbsp;' + self.ui.btnAnn1.text()
			# 	legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			# if self.ui.btnAnn2.isVisible():
			# 	legend += '<span style="font-size: 20pt; color: red">&#x2666;</span>&nbsp;' + self.ui.btnAnn2.text()
			# 	legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			# if self.ui.btnAnn3.isVisible():
			# 	legend += '<span style="font-size: 20pt; color: magenta">&#x25CF;</span>&nbsp;' + self.ui.btnAnn3.text()
			# 	legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			# if self.ui.btnAnn4.isVisible():
			# 	legend += '<span style="font-size: 20pt; color: #00FF00;">&#x25C0;</span>&nbsp;' + self.ui.btnAnn4.text()
			# 	legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			# if self.ui.btnAnn5.isVisible():
			# 	legend += '<span style="font-size: 14pt; color: cyan">&#x25B2;</span>&nbsp;' + self.ui.btnAnn5.text()
			# 	legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			# if self.ui.btnAnn6.isVisible():
			# 	legend += '<span style="font-size: 20pt; color: #FF8000;">&#x25B6;</span>&nbsp;' + self.ui.btnAnn6.text()
			# 	legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			# legend = legend[:-24]
			# legend += '</span>'

			title = '<span style="font-size: 24pt; color: black;">'
			title += self.ui.edtDate.date().toString("d MMM yyyy")
			if self.ui.edtCustomerName.text() != '':
				title += ' - ' + self.ui.edtCustomerName.text()
			if self.ui.edtLocation.text() != '':
				title += ' - ' + self.ui.edtLocation.text()
			if self.ui.edtServiceOrder.text() != '':
				title += ' - ' + self.ui.edtServiceOrder.text()
			title += '</span>'
			pi.setTitle('<table><tr><td align="center">' + title + '</td></tr><tr><td align="center">' + legend + '</td></tr></table>')

			pi.layout.setRowFixedHeight(0, 120)
			pi.layout.setRowAlignment(0, QtCore.Qt.AlignCenter)

			pi.setGeometry(QtCore.QRectF(ch.geometry()))
			vbl.setGeometry(vb.sceneBoundingRect())
			vbr.setGeometry(vb.sceneBoundingRect())

			with warnings.catch_warnings():
				warnings.filterwarnings("ignore")
				exp = pyqtgraph.exporters.ImageExporter(ch.scene())
				try:
					exp.export(name)
				except IOError:
					misc.errorbox(self.win, "Error", "Could not export the chart:", name)

		elif ext == "PDF":
			# penwidth = (rangex[1] - rangex[0]) / 750
			# penwidth = 0
			# #pltl = pil.plot(pen=pyqtgraph.mkPen(QtGui.QColor(128, 0, 0), width=1, cosmetic=False))
			# pltl = pil.plot(pen=QtGui.QPen(QtCore.Qt.darkRed, penwidth, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
			# pltr = pir.plot(pen=pyqtgraph.mkPen(QtGui.QColor(0, 0, 128), width=penwidth, cosmetic=False))
			#
			# ch.scene().addItem(vbl)
			# ch.getAxis('left').linkToView(vbl)
			# vbl.setXLink(vb)
			# vbl.addItem(pltl)
			# vbl.linkedViewChanged(vb, vbl.XAxis)
			# ch.getAxis('left').setPen(pyqtgraph.mkPen(color='#800000', width=0))
			# ch.showAxis('left')
			# vbl.setYRange(0, 10)
			#
			# ch.scene().addItem(vbr)
			# pi.getAxis('right').linkToView(vbr)
			# vbr.setXLink(vb)
			# vbr.addItem(pltr)
			# vbr.linkedViewChanged(vb, vbr.XAxis)
			# pi.getAxis('right').setPen(pyqtgraph.mkPen(color='#000080', width=0))
			# pi.showAxis('right')
			# vbr.setYRange(0, 10)
			#
			# vb.setXRange(rangex[0], rangex[1], padding=0)
			# vbl.setYRange(rangeyl[0], rangeyl[1], padding=0)
			# vbr.setYRange(rangeyr[0], rangeyr[1], padding=0)
			#
			# pi.showGrid(True, True)
			# vbl.translate(-40, 0)
			# vbr.translate(-40, 0)
			# ch.getAxis('bottom').translate(-40, 0)
			#
			# redstyle = {'font-size':'6pt; font-weight: normal; color:#800'}
			# bluestyle = {'font-size':'6pt; font-weight: normal; color:#008'}
			#
			# i = lcmb.currentIndex()
			# if i > 0:
			# 	pltl.setData(history.read(i - 1, c)[-ITEMS:])
			# 	pi.getAxis('left').setLabel(lcmb.currentText(), "", **redstyle)
			# else:
			# 	ch.hideAxis('left')
			#
			# i = rcmb.currentIndex()
			# if i > 0:
			# 	pltr.setData(history.read(i - 1, c)[-ITEMS:])
			# 	pi.getAxis('right').setLabel(rcmb.currentText(), "", **bluestyle)
			# else:
			# 	ch.hideAxis('right')
			#
			# ch.getAxis('bottom').setTicks(self.ticks[c])
			# font = QtGui.QFont()
			# font.setPixelSize(6)
			# font.setBold(False)
			# ch.getAxis('left').tickFont = font
			# ch.getAxis('right').tickFont = font
			# ch.getAxis('bottom').tickFont = font
			# ch.getAxis('left').setWidth(40)
			# ch.getAxis('right').setWidth(40)
			# ch.getAxis('bottom').setHeight(40)
			# ch.getAxis('bottom').setStyle(tickTextOffset=10)
			#
			# titlestyle = {'color':'#000', 'size':'10pt'}
			# title = ui.edtDate.date().toString("d MMM yyyy")
			# if ui.edtCustomerName.text() != '':
			# 	title += ' - ' + ui.edtCustomerName.text()
			# if ui.edtLocation.text() != '':
			# 	title += ' - ' + ui.edtLocation.text()
			# if ui.edtServiceOrder.text() != '':
			# 	title += ' - ' + ui.edtServiceOrder.text()
			# pi.setTitle(title, **titlestyle)
			# pi.layout.setRowFixedHeight(0, 60)
			# pi.layout.setRowAlignment(0, QtCore.Qt.AlignVCenter)
			#
			# ch.resize(640,460)
			# pi.setGeometry(QtCore.QRectF(ch.geometry()))
			# pil.setGeometry(QtCore.QRectF(ch.geometry()))
			# pir.setGeometry(QtCore.QRectF(ch.geometry()))
			# vbl.setGeometry(vb.sceneBoundingRect())
			# vbr.setGeometry(vb.sceneBoundingRect())
			#
			# try:
			# 	printer = QtGui.QPrinter(QtGui.QPrinter.ScreenResolution)
			# 	printer.setPageSize(QtGui.QPrinter.Letter)
			# 	printer.setOrientation(QtGui.QPrinter.Landscape)
			# 	printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
			# 	printer.setOutputFileName(name)
			#
			# 	p = QtGui.QPainter()
			# 	if p.begin(printer):
			# 		ch.render(p)
			# 		p.end()
			# 	else:
			# 		raise IOError
			# except IOError:
			# 	errorbox("Error", "Could not export the chart:", name)

			w = 10
			h = 7
			ch.resize(w * 300, h * 300)

			ch.scene().addItem(vbl)
			ch.getAxis('left').linkToView(vbl)
			vbl.setXLink(vb)
			vbl.addItem(plt1a)
			vbl.addItem(plt1b)
			vbl.addItem(plt1c)
			if locky:
				vbl.addItem(plt2a)
				vbl.addItem(plt2b)
				vbl.addItem(plt2c)
			vbl.linkedViewChanged(vb, vbl.XAxis)
			ch.getAxis('left').setPen(pyqtgraph.mkPen(color='#800000', width=1))
			if labell:
				ch.showAxis('left')
			vbl.setYRange(0, 10)

			if not locky:
				ch.scene().addItem(vbr)
				pi.getAxis('right').linkToView(vbr)
				vbr.setXLink(vb)
				vbr.addItem(plt2a)
				vbr.addItem(plt2b)
				vbr.addItem(plt2c)
				vbr.linkedViewChanged(vb, vbr.XAxis)
				pi.getAxis('right').setPen(pyqtgraph.mkPen(color='#000080', width=1))
				if labelr:
					pi.showAxis('right')
				vbr.setYRange(0, 10)

			vb.addItem(sipdf)

			pi.showGrid(True, True)
			#vbl.translate(-40, 0)
			#vbr.translate(-40, 0)
			#vb.translate(-40, 0)							# contains annotations
			vb.setYRange(-10, 10)							# vertically centred
			#ch.getAxis('bottom').translate(-40, 0)

			vb.setXRange(rangex[0], rangex[1], padding=0)
			vbl.setYRange(rangeyl[0], rangeyl[1], padding=0)
			vbr.setYRange(rangeyr[0], rangeyr[1], padding=0)

			font = QtGui.QFont()
			font.setPixelSize(27)
			font.setBold(False)
			ch.getAxis('left').tickFont = font
			ch.getAxis('right').tickFont = font
			ch.getAxis('bottom').tickFont = font
			ch.getAxis('left').setWidth(120)
			ch.getAxis('right').setWidth(120)
			ch.getAxis('bottom').setHeight(60)
			ch.getAxis('bottom').setStyle(tickTextOffset=20)

			legend = '<span style="font-size: 24pt;">'
			if self.history.annotationpresent(c, rangex[0], rangex[1], 0):
				legend += '<span style="font-size: 24pt; color: blue">&#x2605;</span>&nbsp;' + self.ui.btnAnn1.text()
				legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			if self.history.annotationpresent(c, rangex[0], rangex[1], 1):
				legend += '<span style="font-size: 36pt; color: red">&#x2666;</span>&nbsp;' + self.ui.btnAnn2.text()
				legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			if self.history.annotationpresent(c, rangex[0], rangex[1], 2):
				legend += '<span style="font-size: 36pt; color: magenta">&#x25CF;</span>&nbsp;' + self.ui.btnAnn3.text()
				legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			if self.history.annotationpresent(c, rangex[0], rangex[1], 3):
				legend += '<span style="font-size: 36pt; color: #00FF00;">&#x25C0;</span>&nbsp;' + self.ui.btnAnn4.text()
				legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			if self.history.annotationpresent(c, rangex[0], rangex[1], 4):
				legend += '<span style="font-size: 44pt; color: cyan">&#x25B4;</span>&nbsp;' + self.ui.btnAnn5.text()
				legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			if self.history.annotationpresent(c, rangex[0], rangex[1], 5):
				legend += '<span style="font-size: 36pt; color: #FF8000;">&#x25B6;</span>&nbsp;' + self.ui.btnAnn6.text()
				legend += '&nbsp;&nbsp;&nbsp;&nbsp;'
			legend = legend[:-24]
			legend += '</span>'

			title = '<span style="font-size: 48pt; color: black;">'
			title += self.ui.edtDate.date().toString("d MMM yyyy")
			if self.ui.edtCustomerName.text() != '':
				title += ' - ' + self.ui.edtCustomerName.text()
			if self.ui.edtLocation.text() != '':
				title += ' - ' + self.ui.edtLocation.text()
			if self.ui.edtServiceOrder.text() != '':
				title += ' - ' + self.ui.edtServiceOrder.text()
			pi.setTitle('<table><tr><td align="center">' + title + '</td></tr><tr><td align="center">' + legend + '</td></tr></table>')
			pi.layout.setRowFixedHeight(0, 150)
			pi.layout.setRowAlignment(0, QtCore.Qt.AlignCenter)

			pi.setGeometry(QtCore.QRectF(ch.geometry()))
			vbl.setGeometry(vb.sceneBoundingRect())
			vbr.setGeometry(vb.sceneBoundingRect())

			with warnings.catch_warnings():
				warnings.filterwarnings("ignore")
				exp = pyqtgraph.exporters.ImageExporter(ch.scene())
				try:
					exp.export(name + "_tmp.png")
					pdf = renderPDF.Canvas(str(name), pagesize=landscape(letter))
					pdf.drawImage(str(name) + "_tmp.png", letter[1]/2-(w*72/2), letter[0]/2-(h*72/2), w*72, h*72)
					pdf.showPage()
					pdf.save()
				except IOError:
					misc.errorbox(self.win, "Error", "Could not export the chart:", name)
				finally:
					os.remove(str(name) + "_tmp.png")

		elif ext == "SVG":
			penwidth = (rangex[1] - rangex[0]) / 750
			penwidth = 0
			# pltl = pil.plot(pen=pyqtgraph.mkPen(QtGui.QColor(128, 0, 0), width=1, cosmetic=False))
			pltl = pi.plot(
				pen=QtGui.QPen(QtCore.Qt.darkRed, penwidth, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
			pltr = pi.plot(pen=pyqtgraph.mkPen(QtGui.QColor(0, 0, 128), width=penwidth, cosmetic=True))

			ch.scene().addItem(vbl)
			ch.getAxis('left').linkToView(vbl)
			vbl.setXLink(vb)
			vbl.addItem(plt1a)
			vbl.addItem(plt1b)
			vbl.addItem(plt1c)
			if not locky:
				vbl.addItem(plt2a)
				vbl.addItem(plt2b)
				vbl.addItem(plt2c)
			vbl.linkedViewChanged(vb, vbl.XAxis)
			ch.getAxis('left').setPen(pyqtgraph.mkPen(color='#800000', width=1))
			if labell:
				ch.showAxis('left')
			vb.setYRange(0, 10)

			if not locky:
				ch.scene().addItem(vbr)
				pi.getAxis('right').linkToView(vbr)
				vbr.setXLink(vb)
				vbr.addItem(plt2a)
				vbr.addItem(plt2b)
				vbr.addItem(plt2c)
				vbr.linkedViewChanged(vb, vbr.XAxis)
				pi.getAxis('right').setPen(pyqtgraph.mkPen(color='#000080', width=1))
				if labelr:
					pi.showAxis('right')
				vbr.setYRange(0, 10)

			pi.showGrid(True, True)
			vbl.translate(-40, 0)
			vbr.translate(-40, 0)
			ch.getAxis('bottom').translate(-40, 0)

			vb.setXRange(0, int(rangex[1]-rangex[0]), padding=0)
			vbl.setYRange(rangeyl[0], rangeyl[1], padding=0)
			vbr.setYRange(rangeyr[0], rangeyr[1], padding=0)

			ch.getAxis('bottom').setTicks(self.ticks[c])
			font = QtGui.QFont()
			font.setPixelSize(6)
			font.setBold(False)
			ch.getAxis('left').tickFont = font
			ch.getAxis('right').tickFont = font
			ch.getAxis('bottom').tickFont = font
			ch.getAxis('left').setWidth(40)
			ch.getAxis('right').setWidth(40)
			ch.getAxis('bottom').setHeight(40)
			ch.getAxis('bottom').setStyle(tickTextOffset=10)

			titlestyle = {'color': '#000', 'size': '10pt'}
			title = self.ui.edtDate.date().toString("d MMM yyyy")
			if self.ui.edtCustomerName.text() != '':
				title += ' - ' + self.ui.edtCustomerName.text()
			if self.ui.edtLocation.text() != '':
				title += ' - ' + self.ui.edtLocation.text()
			if self.ui.edtServiceOrder.text() != '':
				title += ' - ' + self.ui.edtServiceOrder.text()
			pi.setTitle(title, **titlestyle)
			pi.layout.setRowFixedHeight(0, 60)
			pi.layout.setRowAlignment(0, QtCore.Qt.AlignVCenter)

			ch.resize(640, 460)
			pi.setGeometry(QtCore.QRectF(ch.geometry()))
			vbl.setGeometry(vb.sceneBoundingRect())
			vbr.setGeometry(vb.sceneBoundingRect())

			# with warnings.catch_warnings():
			# 	warnings.filterwarnings("ignore")
			QtGui.QApplication.processEvents()
			exp = pyqtgraph.exporters.SVGExporter(ch.scene())
			exp.export(name)

	def recordclicked(self):
		if self.recorder.isrecording():
			self.ui.btnRec.setChecked(True)
			if not misc.yesnobox(self.win, "Please Confirm", "Stop Recording", "Are you sure?"):
				return
		r, p = self.recorder.click()
		if r == OPENERR:
			misc.errorbox(self.win, "Error", "Could not create the log file:", p)
		if r == OPENOK:
			self.ui.btnRec.setChecked(True)
			self.ui.btnRec.setToolTip("Recording to file: " + p)
		else:
			self.ui.btnRec.setChecked(False)
			self.ui.btnRec.setToolTip("")
		if r == CLOSED:
			misc.messagebox(self.win, "Log File", "Recorded data was saved to:", p)

	def annotationclicked(self):
		self.annotationtext = str(self.win.sender().text())
		self.annotationindex = int(self.win.sender().objectName()[-1:])
		self.ui.grpAnnotations.setEnabled(False)
