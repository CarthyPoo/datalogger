# JCT Technology Ltd Datalogger 1.0
# by Andrew Keeley (andy@pcman.ca)
# March 2018

# Circular Buffer object class.
# Used to hold history of data received.

# standard / third party libraries
import datetime
import numpy
import copy
from PyQt4 import QtCore, QtGui


class CircularBuffer():
	def __init__(self, regmap):
		self.regmap = regmap
		self.length = 86400															# seconds in 24 hours
		self.width = len(self.regmap)													# one for each modbus register

		self.timeaxis = numpy.array(['00:00:00' for _ in range(self.length)])		# initialise string array for x-axis
		self.livedata = []
		self.liveannotations = {}
		self.pausedposition = [-1, -1]												# -1 indicates not paused
		self.pausedannotations = [{}, {}]
		for r in self.regmap:
			self.livedata.append(numpy.zeros(self.length, dtype='f'))  				# intitialise arrays of floats

		self.liveposition = 0
		self.new = True

		self.colours = [
			QtGui.QColor(0, 128, 255),			# blue
			QtGui.QColor(255, 0, 0),			# red
			QtGui.QColor(255, 0, 255),			# magenta
			QtGui.QColor(0, 255, 0),			# green
			QtGui.QColor(0, 255, 255),			# cyan
			QtGui.QColor(255, 128, 0)]			# yellow

		self.symbols = [11, 6, 0, 5, 3, 4]

		self.pauseddata = []
		for _ in range(2):
			self.pauseddata.append(copy.deepcopy(self.livedata))

		timestamp = datetime.datetime(2018, 3, 8, 0, 0, 0)							# get midnight time (date not used)
		delta = datetime.timedelta(seconds=1)										# 1 second steps
		for i in range(self.length):												# for every second of the day
			self.timeaxis[i] = timestamp.strftime("%H:%M:%S")						# create an x-axis label
			timestamp += delta														# add 1 second for next time
		now = datetime.datetime.now()												# get current time
		self.liveposition = now.hour * 3600 + now.minute * 60 + now.second			# set position to current time

	def readtime(self, chart):
		i = self.pausedposition[chart] if self.pausedposition[chart] != -1 else self.liveposition
		return numpy.append(self.timeaxis[i:self.length], self.timeaxis[0:i])

	def read(self, c, chart):
		if self.pausedposition[chart] == -1:
			i = self.liveposition
			return numpy.append(self.livedata[c][i:self.length], self.livedata[c][0:i])
		else:
			i = self.pausedposition[chart]
			return numpy.append(self.pauseddata[chart][c][i:self.length], self.pauseddata[chart][c][0:i])

	def write(self, values, index, annotation):
		if self.new:
			for i, v in enumerate(values):
				if self.regmap[i][2] != "F":
					v = float(v) / 10**self.regmap[i][3]
				for x in range(self.length):
					self.livedata[i][x] = v
			self.new = False

		for i, v in enumerate(values):
			if self.regmap[i][2] != "F":
				v = float(v) / 10 ** self.regmap[i][3]
			self.livedata[i][index] = v
		self.addannotation(index, annotation)
		self.liveposition = (index + 1) % self.length

	def repeat(self, index, annotation):
		source = index - 1 if index > 0 else self.length
		for i in range(self.width):
			self.livedata[i][index] = self.livedata[i][source]
		self.addannotation(index, annotation)
		self.liveposition = (index + 1) % self.length

	def togglepause(self, chart):
		if self.pausedposition[chart] != -1:
			self.pausedposition[chart] = self.liveposition
			self.pauseddata[chart] = copy.deepcopy(self.livedata)
			self.pausedannotations[chart] = copy.deepcopy(self.liveannotations)
		else:
			self.pausedposition[chart] = -1
		return self.pausedposition[chart] != -1

	def ispaused(self, chart):
		return self.pausedposition[chart] != -1

	def unpause(self, chart):
		self.pausedposition[chart] = -1

	def pause(self, chart):
		self.pausedposition[chart] = self.liveposition
		self.pauseddata[chart] = copy.deepcopy(self.livedata)
		self.pausedannotations[chart] = copy.deepcopy(self.liveannotations)

	def syncpause(self, chart):
		self.pausedposition[0 if chart == 1 else 1] = self.pausedposition[chart]
		self.pauseddata[0 if chart == 1 else 1] = copy.deepcopy(self.pauseddata[chart])
		self.pausedannotations[0 if chart == 1 else 1] = copy.deepcopy(self.pausedannotations[chart])

	def addannotation(self, index, annotation):
		if annotation == 0:
			if index in self.liveannotations:
				self.liveannotations.__delitem__(index)
		else:
			self.liveannotations[index] = annotation-1

	def readannotations(self, chart):
		if self.pausedposition[chart] == -1:
			return self.makeannotations(self.liveannotations, self.liveposition)
		else:
			return self.makeannotations(self.pausedannotations[chart], self.pausedposition[chart])

	def makeannotations(self, annotations, position):
		ret = []
		for k, v in annotations.items():
			if v == 0:
				ret.append({'pos': [self.length-position+k, 0], 'brush': self.colours[v], 'symbol': self.symbols[v], 'size': 17.})
			elif v == 2:
				ret.append({'pos': [self.length-position+k, 0], 'brush': self.colours[v], 'symbol': self.symbols[v], 'size': 13.})
			else:
				ret.append({'pos': [self.length-position+k, 0], 'brush': self.colours[v], 'symbol': self.symbols[v]})
		return ret

	def readannotationsexport(self, chart, size):
		if self.pausedposition[chart] == -1:
			return self.makeannotationsexport(self.liveannotations, self.liveposition, size)
		else:
			return self.makeannotationsexport(self.pausedannotations[chart], self.pausedposition[chart], size)

	def makeannotationsexport(self, annotations, position, size):
		ret = []
		for k, v in annotations.items():
			if v == 0:
				ret.append({'pos': [self.length - position + k, 0], 'brush': QtGui.QColor(0, 0, 255), 'symbol': self.symbols[v], 'size': size*1.15})
			elif v == 2:
				ret.append({'pos': [self.length - position + k, 0], 'brush': self.colours[v], 'symbol': self.symbols[v], 'size': size/1.15})
			else:
				ret.append({'pos': [self.length - position + k, 0], 'brush': self.colours[v], 'symbol': self.symbols[v]})
		return ret

	def annotationpresent(self, chart, start, end, ann):
		if self.pausedposition[chart] == -1:
			for k, v in self.liveannotations.iteritems():
				k += self.length - self.liveposition
				if v == ann and start <= k <= end:
					return True
			return False
		else:
			for k, v in self.pausedannotations[chart].iteritems():
				k += self.length - self.pausedposition[chart]
				if v == ann and start <= k <= end:
					return True
			return False
