import sys

# Without this stupid hack, MS-Windows will put our window behind
# the explorer window because our launcher is already minimized.
# Note that .present() does not work, it just makes the icon
# on the taskbar blink.
def raise_window(window):
	if sys.platform == "win32":
		window.set_keep_above(True)
		window.set_keep_above(False)

