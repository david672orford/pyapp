# pyapp/gtk_activator.py
# Last modified: 5 February 2015

class WidgetActivator(object):
	def __init__(self):
		self.widgets = []
		self.existing_conditions = set()
	def add_widget(self, widget, required_conditions):
		#print "WidgetActivator:add_widget:", widget, required_conditions
		required_conditions = set(required_conditions)
		self.widgets.append((widget, required_conditions))
		widget.set_sensitive(required_conditions <= self.existing_conditions)
	def set_condition(self, condition, state):
		#print "WidgetActivator:set_condition:", condition, state
		if state:
			self.existing_conditions.add(condition)
		else:
			self.existing_conditions.discard(condition)
		for widget, required_conditions in self.widgets:
			widget.set_sensitive(required_conditions <= self.existing_conditions)

