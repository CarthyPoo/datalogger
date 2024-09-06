# JCT Technology Ltd Datalogger 1.0
# by Andrew Keeley (andy@pcman.ca)
# April 2018

# Recorder class
# logs data to a csv file

# standard / third party libraries
import os
import datetime

# project libraries
import config

OPENOK = 1
OPENERR = 2
CLOSED = 3


class Recorder():
	def __init__(self, mainui, regmap):
		self.ui = mainui
		self.file = None
		self.filename = None
		self.regmap = regmap

	def open(self):
		dte = str(self.ui.edtDate.date().toString("yyyyMMdd")) + "-" + datetime.datetime.now().strftime("%H%M%S")
		self.filename = os.path.join(self.logfilepath(), dte + ".csv")
		try:
			self.file = open(self.filename, "w")
			self.file.write('"Time",')
			for n in self.regmap:
				self.file.write(self.makecsvsafe(n[0]) + ",")
			self.file.write('"Annotation"\n')
			return OPENOK, self.filename
		except IOError:
			self.file = None
			return OPENERR, self.filename

	def logfilepath(self):
		cst = self.makefilenamesafe(str(self.ui.edtCustomerName.text()))
		loc = self.makefilenamesafe(str(self.ui.edtLocation.text()))
		if not os.path.exists(os.path.join(config.LOG_PATH, cst, loc)):
			try:
				os.makedirs(os.path.join(config.LOG_PATH, cst, loc))
			except OSError:
				pass
		return os.path.join(config.LOG_PATH, cst, loc)

	def close(self):
		if self.file is not None:
			try:
				self.file.close()
				self.file = None
			except IOError:
				pass
		return CLOSED, self.filename

	def write(self, time, values, annotation):
		if self.file is not None:
			try:
				self.file.write(time + ",")
				for i, v in enumerate(values):
					f = "%." + "%df" % self.regmap[i][3]
					if self.regmap[i][2] == "F":
						self.file.write(f % v + ",")
					else:
						self.file.write(f % (float(v) / 10**self.regmap[i][3]) + ",")
				if annotation is not "":
					self.file.write(self.makecsvsafe(str(annotation)))
				self.file.write('\n')
			except IOError:
				pass

	def click(self):
		if self.file is None:
			return self.open()
		else:
			return self.close()

	def isrecording(self):
		return self.file is not None

	@staticmethod
	def makecsvsafe(s):
		return "\"" + "".join("\"\"" if c == "\"" else c for c in s) + "\""

	@staticmethod
	def makefilenamesafe(s):
		return "".join(c if c.isalnum() else '_' for c in s)
