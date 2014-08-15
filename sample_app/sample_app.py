#! /usr/bin/python

import os
import sys
import gtk

import pyapp.gtk_common_ui
import pyapp.save

class App(object):

	def __init__(self, filename):
		self.filename = None
		self.changes = False

		self.builder = gtk.Builder()
		self.builder.add_from_file(os.path.join(sys.path[0], "sample_app.glade"))
		self.builder.connect_signals(self)
 
		self.window = self.builder.get_object("MainWindow")
		self.ui = pyapp.gtk_common_ui.CommonUI(self.window, self.builder)

		self.load(filename)
   
	def show(self):
		self.window.show()
 
	def load(self, filename):
		self.filename = filename
		fh = open(self.filename, 'r')

	def on_file_save(self, widget, data=None):
		print "File->Save"
		self.save()

	def on_file_save_as(self, widget):
		print "File->Save As"
		chooser = gtk.FileChooserDialog(title="Save As", action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK)) 
		response = chooser.run()
		filename = chooser.get_filename()
		chooser.destroy()
		if response != gtk.RESPONSE_OK:
			return
		if os.path.exists(filename) and not self.ui.ask_overwrite():
			return
		self.filename = filename
		self.save()

	def save(self):
		busy = self.ui.busy(_("Saving..."))
		fh = pyapp.save.SaveOpen(self.filename)

	# Exit menu items and buttons call this
	def on_exit(self, widget, data=None):
		print "File->Exit"
		if self.changes:
			print " There are unsaved changes."
			choice = self.ui.ask_save_cancel_discard()
			print " Dialog choice:", choice
			if choice == "cancel":
				return True
			if choice == "save":
				self.save()
		gtk.main_quit()
		return True			# prevent default actions

	def on_help_about(self, widget):
		print "Help->About"
		dialog = self.builder.get_object("AboutDialog")
		answer = dialog.run()
		dialog.hide()
		return True

if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.stderr.write("Usage: %s <filename>\n")
		sys.exit(1)
	filename = sys.argv[1]
	app = App(filename)
	app.show()
	gtk.main()

