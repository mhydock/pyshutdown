#===============================================================================
# Date Created:		23 December 2011
# Last Updated:		23 December 2011
#
# File Name:		shutdown.py
# File Author:		M Matthew Hydock
#
# File Description:	A basic Python script, intended for Openbox, which emulates
#					the shut down panel in GNOME. Cobbled together from code
#					found online and from YAMA (an applet for AWN that builds
#					an applications menu, with additional places menu and
#					session controls).
#
#					The original code was found in the following forum post:
#					https://bbs.archlinux.org/viewtopic.php?pid=979060#p979060
#===============================================================================
#!/usr/bin/env python3

import pygtk
pygtk.require('2.0')
import gtk
import os
import re

try:
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)
except ImportError:
    dbus = None

xdg_data_dirs = [os.path.expanduser("~/.local/share")] + os.environ["XDG_DATA_DIRS"].split(":")
big = 48
small = 24

class DoTheLogOut:

	# Cancel/exit
	def delete_event(self, widget, event, data=None):
		gtk.main_quit()
		return False

	# Suspend
	def suspend(self, widget):
		os.system("dbus-send --system --print-reply --dest=org.freedesktop.UPower /org/freedesktop/UPower org.freedesktop.UPower.Suspend")
		gtk.main_quit()
		
	# Hibernate
	def hibernate(self, widget):
		os.system("dbus-send --system --print-reply --dest=org.freedesktop.UPower /org/freedesktop/UPower org.freedesktop.UPower.Hibernate")
		gtk.main_quit()
		
	# Reboot
	def reboot(self, widget):
		os.system("dbus-send --system --print-reply  --dest=org.freedesktop.ConsoleKit /org/freedesktop/ConsoleKit/Manager  org.freedesktop.ConsoleKit.Manager.Restart")

	# Shutdown
	def shutdown(self, widget):
		os.system("dbus-send --system --print-reply  --dest=org.freedesktop.ConsoleKit /org/freedesktop/ConsoleKit/Manager  org.freedesktop.ConsoleKit.Manager.Stop")

	# Log out
	def logout(self, widget):
		os.system("openbox --exit");
		
	# Lock screen
	def lock_session(self, widget):
		session_bus = dbus.SessionBus()
		dbus_services = session_bus.list_names()
		can_lock_screen = "org.gnome.ScreenSaver" in dbus_services
        
		if can_lock_screen:
			os.system("gnome-screensaver-command --lock");
		else:
			can_lock_screen = "org.freedesktop.ScreenSaver" in dbus_services
        
			if can_lock_screen:
				os.system("xscreensaver-command --lock")
			
		gtk.main_quit()
        
        
	def __init__(self):
		self.settings = gtk.settings_get_default()
		self.settings.props.gtk_button_images = True

		self.icon_theme = gtk.icon_theme_get_default()
	
		# Create a new window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title("Openbox Shutdown")
		self.window.set_resizable(False)
		self.window.set_position(1)
		self.window.connect("delete_event", self.delete_event)
		self.window.set_border_width(10)

		# Create a box to pack widgets into
		self.main_box = gtk.VBox(False, 0)
		self.window.add(self.main_box)

		# Create the shutdown button frame.
		self.frame1 = gtk.Frame()
		self.frame1.set_shadow_type(gtk.SHADOW_NONE)
		self.box1 = gtk.VBox(False,0)
		self.frame1.add(self.box1)
		self.main_box.add(self.frame1)

		# Create shutdown button
		self.button1 = self.makeSuperButton("<span font_weight=\"bold\">Shut Down</span>\n<span font_weight=\"light\" size=\"small\">Ends your session and turns off the power.</span>","system-shutdown",big)
		self.button1.connect("clicked", self.shutdown)
		self.box1.pack_start(self.button1, True, True, 0)
		self.button1.show()

		# Create reboot button
		self.button2 = self.makeSuperButton("<span font_weight=\"bold\">Reboot</span>\n<span font_weight=\"light\" size=\"small\">Ends your session and restarts the computer.</span>","reload", big)
		self.button2.connect("clicked", self.reboot)
		self.box1.pack_start(self.button2, True, True, 0)
		self.button2.show()
        
		# Create suspend button
		self.button3 = self.makeSuperButton("<span font_weight=\"bold\">Suspend</span>\n<span font_weight=\"light\" size=\"small\">Suspends your session quickly, using\nminimal power while the computer stands by.</span>","sleep", big)
		self.button3.connect("clicked", self.suspend)
		#self.button3.connect("clicked", self.delete_event, "Force removal :(")
		self.box1.pack_start(self.button3, True, True, 0)
		self.button3.show()

		# Create hibernate button
		self.button4 = self.makeSuperButton("<span font_weight=\"bold\">Hibernate</span>\n<span font_weight=\"light\" size=\"small\">Suspends your session, using no power\nuntil the computer is restarted.</span>","filesave", big)
		self.button4.connect("clicked", self.hibernate)
		self.box1.pack_start(self.button4, True, True, 0)
		self.button4.show()

		
		# Create the cancel/logout/lock button frame.
		self.frame2 = gtk.Frame()
		self.frame2.set_shadow_type(gtk.SHADOW_NONE)
		self.box2 = gtk.HBox(False,0)
		self.frame2.add(self.box2)
		self.main_box.add(self.frame2)
		
		# Create cancel button
		self.button5 = gtk.Button("Cancel")
		icon_pixbuf = self.get_pixbuf_icon("stop", small)
		self.button5.set_image(gtk.image_new_from_pixbuf(icon_pixbuf))
		self.button5.set_image_position(gtk.POS_LEFT);
		self.button5.set_border_width(5)
		self.button5.connect("clicked", self.delete_event, "Changed my mind.")
		self.box2.pack_start(self.button5, True, True, 0)
		self.button5.show()
		
		# Create log out button
		self.button6 = gtk.Button("Log Out")
		icon_pixbuf = self.get_pixbuf_icon("system-log-out", small)
		self.button6.set_image(gtk.image_new_from_pixbuf(icon_pixbuf))
		self.button6.set_image_position(gtk.POS_LEFT);
		self.button6.set_border_width(5)
		self.button6.connect("clicked", self.logout)
		self.box2.pack_start(self.button6, True, True, 0)
		self.button6.show()
		
        # Create lock button
		self.button7 = gtk.Button("Lock Screen")
		icon_pixbuf = self.get_pixbuf_icon("lock", small)
		self.button7.set_image(gtk.image_new_from_pixbuf(icon_pixbuf))
		self.button7.set_image_position(gtk.POS_LEFT);
		self.button7.set_border_width(5)
		self.button7.connect("clicked", self.lock_session)
		self.box2.pack_start(self.button7, True, True, 0)
		self.button7.show()
        
		self.window.show_all()
	
	# Made this because basic buttons didn't have the style capabilities I
	# needed if I were to replicate the GNOME logout panel.
	def makeSuperButton(self, text, icon, size):
		box = gtk.HBox(False,0)
		button = gtk.Button()
		button.add(box)
		
		image_pixbuf = self.get_pixbuf_icon(icon, size)
		image = gtk.image_new_from_pixbuf(image_pixbuf)
		box.pack_start(image, False, False, 10)
		
		label = gtk.Label()
		label.set_use_markup(True)
		label.set_markup(text)
		label.set_justify(gtk.JUSTIFY_LEFT)
		box.pack_start(label, False, False, 10)
		
		image.set_alignment(0.0,0.5)
		button.set_alignment(0.0,0.5)
		button.set_border_width(5)

		return button
		
	# Taken wholesale from YAMA, an AWN applet to display an applications menu.
	def get_pixbuf_icon(self, icon_value, size):
		if not icon_value:
			return None

		if os.path.isabs(icon_value):
			if os.path.isfile(icon_value):
				try:
					return gtk.gdk.pixbuf_new_from_file_at_size(icon_value, size, size)
				except glib.GError:
					return None
			icon_name = os.path.basename(icon_value)
		else:
			icon_name = icon_value

		if re.match(".*\.(png|xpm|svg)$", icon_name) is not None:
			icon_name = icon_name[:-4]
		try:
			return self.icon_theme.load_icon(icon_name, size, gtk.ICON_LOOKUP_FORCE_SIZE)
		except:
			for dir in xdg_data_dirs:
				for i in ("pixmaps", "icons"):
					path = os.path.join(dir, i, icon_value)
					if os.path.isfile(path):
						return gtk.gdk.pixbuf_new_from_file_at_size(path, size, size)
		
def main():
	gtk.main()

if __name__ == "__main__":
	gogogo = DoTheLogOut()
	main()
