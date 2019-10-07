# pyapp/gtk_common_ui.py
# Copyright 2013--2018, Trinity College
# Last modified: 30 May 2018

import os
import sys
import gtk
import weakref
import new
import pyapp.i18n

class CommonUI(object):
	def __init__(self, main_window, builder):
		self.main_window = main_window
		self.builder = builder

		self.statusbar = self.builder.get_object("MainStatusbar")
		self.contextid = self.statusbar.get_context_id("general")

		self.builder.add_from_file(os.path.join(sys.path[0], "pyapp", "gtk_common_ui.glade"))

	def ask_save_cancel_discard(self, markup=_("Discard unsaved changes?")):
		dialog = self.builder.get_object("SaveCancelDiscardDialog")
		dialog.set_transient_for(self.main_window)
		dialog.set_markup(markup)
		answer = dialog.run()
		dialog.hide()
		# 0--close without saving
		# 1--cancel
		# 2--save
		# -4- user clicked x on title bar
		if answer == 0:
			return "discard"
		elif answer == 2:
			return "save"
		else:
			return "cancel"

	def ask_yesno_question(self, question):
		dialog = self.builder.get_object("YesNoDialog")
		dialog.set_transient_for(self.main_window)
		dialog.set_markup(question)
		answer = dialog.run()
		dialog.hide()
		if answer == -4:		# user clicked x on title bar
			return None
		elif answer:
			return True
		else:
			return False

	def ask_overwrite(self):
		dialog = self.builder.get_object("OverwriteConfirmDialog")
		dialog.set_transient_for(self.main_window)
		answer = dialog.run()
		dialog.hide()
		if answer == 1:
			return True
		else:
			return False

	def error(self, error_message):
		self.error_dialog(_("Operation Failed"), error_message)

	def error_dialog(self, title, error_message):
		#print "%s: %s" % (title, error_message)
		print "+=================================================================+"
		print "| %50s" % title
		print "+=================================================================+"
		print "| %s" % (error_message.replace("\n","\n|"))
		print "+=================================================================+"

		dialog = self.builder.get_object("ErrorDialog")
		dialog.set_transient_for(self.main_window)
		dialog.set_title(title)
		codeview = self.builder.get_object("ErrorDialogCodeView")

		# If the message already contains line breaks, split off all of the
		# lines after the first and display them in a label widget under the
		# main error message. This makes stack backtraces look much better.
		lines = error_message.split("\n")
		if len(lines) > 1:
			error_message = lines[0]
			codeview.set_label("\n".join(lines[1:]))
			codeview.show()
			dialog.set_property('default_width',1000)
		else:
			codeview.hide()
			dialog.set_property('default_width',600)

		# XML escape the error message and insert the text
		dialog.set_markup(error_message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))

		# Display the error dialog box and wait for the user
		# to press the OK button.
		dialog.run()
		dialog.hide()

	def error_dialog_exception(self, operation, e):
		if type(e) == CanceledByUser:
			print "CanceledByUser caught"
		else:
			import traceback
			(e_type, e_value, e_traceback) = sys.exc_info()
			message = _("Unexpected error during operation \"{operation_name}\": {error_type}: {error_value}\n" \
				"{traceback}").format(
					operation_name=operation,
					error_type="%s.%s" % (e_type.__module__, e_type.__name__),
					error_value=e_value,
					traceback=traceback.format_exc(e_traceback)
					)
			self.error_dialog(_("Operation failed: {operation_name}").format(operation_name=operation), message)

	def show_status(self, status_text):
		if status_text != "":
			print "STATUSBAR:", status_text
		self.statusbar.remove_all(self.contextid)
		self.statusbar.push(self.contextid, status_text)
		# make sure message shows up right away
		while gtk.events_pending():
			gtk.main_iteration(False)

	def busy(self, message):
		return Busy(self.main_window, self.statusbar, message)

	def progress_dialog(self):
		return Progress(self.main_window, self.builder)

#=============================================================
# Busy cursor handling
#=============================================================
class Busy(object):
	def __init__(self, main_window, statusbar, message):
		print "BUSY:", message
		self.main_window = main_window
		self.statusbar = statusbar
		self.main_window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
		self.contextid = self.statusbar.get_context_id("busy")
		self.statusbar.remove_all(self.contextid)
		self.statusbar.push(self.contextid, message)
		while gtk.events_pending():
			gtk.main_iteration(False)
	def __del__(self):
		self.main_window.window.set_cursor(None)
		self.statusbar.remove_all(self.contextid)

#=============================================================
# Progress bar dialog box
# We use and reuse a progress dialog box defined using Glade.
#=============================================================

class Progress(object):
	def __init__(self, main_window, builder):
		self.dialog = ProgressDialog(main_window, builder)

		self.dialog.primary_message.set_text("")
		self.primary_part = 0.0
		self.primary_whole = 1.0

		self.dialog.secondary_message.set_text("")
		self.secondary_part = 0.0
		self.secondary_whole = 1.0

		self.bump_amount = 0.0

	def __del__(self):
		print "Progress: out-of-scope"
		self.dialog.destroy()

	# First level of progress: indicate the current task
	def progress(self, part, whole, message):
		if part is not None:
			self.primary_part = float(part)
		if whole is not None:
			self.primary_whole = float(whole)
		if message is not None:
			self.dialog.primary_message.set_text(message)
		self.secondary_part = 0.0
		self.secondary_whole = 1.0
		self.bump_amount = 0.0
		self.dialog.secondary_message.set_text("")
		self._update_bar()
		self.dialog.dialog.show()
		self.handle_events()

	# Second level of progress: how far along in the current task
	def sub_progress(self, part, whole, message):
		if part is not None:
			self.secondary_part = float(part)
		if whole is not None:
			self.secondary_whole = float(whole)
		if message is not None:
			self.dialog.secondary_message.set_text(message)
		self.bump_amount = 0.0
		self._update_bar()
		self.handle_events()

	def bump(self, bump_amount):
		self.bump_amount = min(bump_amount, 1.0)
		self._update_bar()
		self.handle_events()

	# Compute the new position of the progress bar
	def _update_bar(self):
		fraction = self.primary_part / self.primary_whole \
			+ ((self.secondary_part+self.bump_amount) / self.secondary_whole / self.primary_whole)
		if False:
			print "primary: %d/%d" % (self.primary_part, self.primary_whole)
			print "secondary: %d/%d" % (self.secondary_part, self.secondary_whole)
			print "fraction: %f" % fraction
		self.dialog.bar.set_fraction(fraction)
		self.dialog.bar.set_text("%d%%" % int(fraction / 1.0 * 100.0 + 0.5))

	def handle_events(self):
		#print "progress refcount:", sys.getrefcount(self)
		while gtk.events_pending():	
			gtk.main_iteration(False)
		if self.dialog.canceled:
			print "Progress: raising CanceledByUser..."
			raise CanceledByUser

# We put some of class Progress into this class so that Progress would
# not have circular references. Do not use this class directly.
class ProgressDialog(object):
	def __init__(self, main_window, builder):
		self.dialog = builder.get_object("ProgressDialog")
		self.cancel_button = builder.get_object("ProgressCancelButton")
		self.primary_message = builder.get_object("ProgressMessage1")
		self.secondary_message = builder.get_object("ProgressMessage2")
		self.bar = builder.get_object("ProgressBar")

		self.dialog.set_transient_for(main_window)
		self.dialog.set_title(_("%s: Progress") % main_window.get_title())

		self.canceled = False
		self.button_handler = self.cancel_button.connect('clicked', self._cancel_cb)
		self.delete_handler = self.dialog.connect('delete-event', self._delete_cb)

	def destroy(self):
		self.dialog.hide()
		self.cancel_button.disconnect(self.button_handler)
		self.dialog.disconnect(self.delete_handler)

	def __del__(self):
		print "Progress: ProgressDialog out-of-scope"	

	def _delete_cb(self, widget, event):
		print "Progress: window close"
		self.canceled = True
		self.dialog.hide()
		return True

	def _cancel_cb(self, widget):
		print "Progress: cancel button pressed"
		self.canceled = True
		self.dialog.hide()
		return True

# Progress class thows this as soon as it detects that the Cancel button has been pressed.
class CanceledByUser(Exception):
	pass

