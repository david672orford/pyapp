# pyapp/save.py
# Last modified: 22 May 2014

import os

class SaveOpen(object):
	def __init__(self, filename):
		self.filename = filename

		# MS-DOS naming scheme
		#(base, ext) = os.path.splitext(self.filename)
		#self.tempname = "%s.tmp" % base
		#self.backname = "%s.bak" % base

		# Unix naming scheme
		self.tempname = "%s.tmp" % self.filename
		self.backname = "%s~" % self.filename

		self.fh = open(self.tempname, 'wb')

	def write(self, data):
		self.fh.write(data)

	def close(self):
		self.fh.close()
		if os.path.exists(self.filename):
			if os.path.exists(self.backname):
				os.remove(self.backname)
			os.rename(self.filename, self.backname)
		os.rename(self.tempname, self.filename)

