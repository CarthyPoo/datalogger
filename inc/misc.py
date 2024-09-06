# JCT Technology Ltd Datalogger 1.0
# by Andrew Keeley (andy@pcman.ca)
# March 2018

# standard / third party libraries
from PyQt4 import QtGui, QtCore


def yesnobox(win, title, text, info):
	msg = QtGui.QMessageBox(win)  											# create a Qt message box
	msg.setIcon(QtGui.QMessageBox.Question)  								# with a question icon
	msg.setInformativeText(info)  											# set informative text
	msg.setWindowTitle(title)  												# set the title text
	msg.setText(text)  														# set the question text
	msg.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)  	# add yes and no buttons
	return msg.exec_() == QtGui.QMessageBox.Yes  							# show message box and return True if yes


def messagebox(win, title, text, info):
	msg = QtGui.QMessageBox(win)
	msg.setIcon(QtGui.QMessageBox.NoIcon)
	msg.setInformativeText(info)  											# set informative text
	msg.setWindowTitle(title)  												# set the title text
	msg.setText(text)  														# set the warning text

	w = msg.fontMetrics().width(info)
	spc = QtGui.QSpacerItem(w + 100, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
	lay = msg.layout()
	lay.addItem(spc, lay.rowCount(), 0, 1, lay.columnCount())

	msg.exec_()


def errorbox(win, title, text, info):
	msg = QtGui.QMessageBox(win)
	msg.setIcon(QtGui.QMessageBox.Critical)
	msg.setInformativeText(info)  											# set informative text
	msg.setWindowTitle(title)  												# set the title text
	msg.setText(text)  														# set the warning text

	w = msg.fontMetrics().width(info)
	spc = QtGui.QSpacerItem(w + 100, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
	lay = msg.layout()
	lay.addItem(spc, lay.rowCount(), 0, 1, lay.columnCount())

	msg.exec_()


