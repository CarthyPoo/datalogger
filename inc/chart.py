

from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import GraphicsView
from pyqtgraph.graphicsItems.PlotItem import PlotItem
from pyqtgraph.graphicsItems.ScatterPlotItem import ScatterPlotItem

__all__ = ['PlotWidget']


class PlotWidget(GraphicsView):
	sigRangeChanged = QtCore.Signal(object, object)
	sigTransformChanged = QtCore.Signal(object)

	def __init__(self, parent=None, background='default', **kargs):
		GraphicsView.__init__(self, parent, background=background)
		self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		self.enableMouse(False)
		self.plotItem = [(PlotItem(**kargs)) for _ in range(7)]
		self.scatterItem = ScatterPlotItem(size=15, pen=None, pxMode=True)
		self.setCentralItem(self.plotItem[0])
		for m in ['addItem', 'removeItem', 'autoRange', 'clear', 'setXRange',
				  'setYRange', 'setRange', 'setAspectLocked', 'setMouseEnabled',
				  'setXLink', 'setYLink', 'enableAutoRange', 'disableAutoRange',
				  'setLimits', 'register', 'unregister', 'viewRect']:
			setattr(self, m, getattr(self.plotItem[0], m))
		self.plotItem[0].sigRangeChanged.connect(self.viewRangeChanged)

	def close(self):
		self.plotItem[0].close()
		self.plotItem[0] = None
		self.plotItem[1].close()
		self.plotItem[1] = None
		self.plotItem[2].close()
		self.plotItem[2] = None
		self.setParent(None)
		super(PlotWidget, self).close()

	def __getattr__(self, attr):
		if hasattr(self.plotItem[0], attr):
			m = getattr(self.plotItem[0], attr)
			if hasattr(m, '__call__'):
				return m
		raise NameError(attr)

	def viewRangeChanged(self, view, range):
		self.sigRangeChanged.emit(self, range)

	def widgetGroupInterface(self):
		return (None, PlotWidget.saveState, PlotWidget.restoreState)

	def saveState(self, index):
		return self.plotItem[index].saveState()

	def restoreState(self, index, state):
		return self.plotItem[index].restoreState(state)

	def getPlotItem(self, index):
		return self.plotItem[index]

	def getScatterPlotItem(self):
		return self.scatterItem
