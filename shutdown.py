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

from gi.repository import Gtk 
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
		Gtk.main_quit()
		return False

	# Suspend
	def suspend(self, widget):
		os.system("dbus-send --system --print-reply --dest=org.freedesktop.UPower /org/freedesktop/UPower org.freedesktop.UPower.Suspend")
		Gtk.main_quit()
		
	# Hibernate
	def hibernate(self, widget):
		os.system("dbus-send --system --print-reply --dest=org.freedesktop.UPower /org/freedesktop/UPower org.freedesktop.UPower.Hibernate")
		Gtk.main_quit()
		
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
			
		Gtk.main_quit()
        
        
	def __init__(self):
		self.settings = Gtk.Settings.get_default()
		self.settings.set_property("gtk-button-images",True)

		self.icon_theme = Gtk.IconTheme.get_default()
	
		# Create a new window
		self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
		self.window.set_title("Openbox Shutdown")
		self.window.set_resizable(False)
		self.window.set_position(1)
		self.window.connect("delete_event", self.delete_event)
		self.window.set_border_width(10)

		# Create a box to pack widgets into
		self.main_box = Gtk.VBox(False, 0)
		self.window.add(self.main_box)

		# Create the shutdown button frame.
		self.frame1 = Gtk.Frame()
		self.frame1.set_shadow_type(Gtk.ShadowType.NONE)
		self.box1 = Gtk.VBox(False,0)
		self.frame1.add(self.box1)
		self.main_box.add(self.frame1)

		# Create shutdown button
		self.button1 = self.makeSuperButton("<span font_weight=\"bold\">Shut Down</span>\n<span font_weight=\"light\" size=\"small\">Ends your session and turns off the power.</span>","system-shutdown",big,10)
		self.button1.connect("clicked", self.shutdown)
		self.box1.pack_start(self.button1, True, True, 0)
		self.button1.show()

		# Create reboot button
		self.button2 = self.makeSuperButton("<span font_weight=\"bold\">Reboot</span>\n<span font_weight=\"light\" size=\"small\">Ends your session and restarts the computer.</span>","reload",big,10)
		self.button2.connect("clicked", self.reboot)
		self.box1.pack_start(self.button2, True, True, 0)
		self.button2.show()
        
		# Create suspend button
		self.button3 = self.makeSuperButton("<span font_weight=\"bold\">Suspend</span>\n<span font_weight=\"light\" size=\"small\">Suspends your session quickly, using\nminimal power while the computer stands by.</span>","sleep",big,10)
		self.button3.connect("clicked", self.suspend)
		#self.button3.connect("clicked", self.delete_event, "Force removal :(")
		self.box1.pack_start(self.button3, True, True, 0)
		self.button3.show()

		# Create hibernate button
		self.button4 = self.makeSuperButton("<span font_weight=\"bold\">Hibernate</span>\n<span font_weight=\"light\" size=\"small\">Suspends your session, using no power\nuntil the computer is restarted.</span>","filesave",big,10)
		self.button4.connect("clicked", self.hibernate)
		self.box1.pack_start(self.button4, True, True, 0)
		self.button4.show()

		
		# Create the cancel/logout/lock button frame.
		self.frame2 = Gtk.Frame()
		self.frame2.set_shadow_type(Gtk.ShadowType.NONE)
		self.box2 = Gtk.HBox(False,0)
		self.frame2.add(self.box2)
		self.main_box.add(self.frame2)
		
		# Create cancel button
		self.button5 = self.makeSuperButton("Cancel","stop",small,3)
		self.button5.connect("clicked", self.delete_event, "Changed my mind.")
		self.box2.pack_start(self.button5, True, True, 0)
		self.button5.show()
		
		# Create log out button
		self.button6 = self.makeSuperButton("Log Out","system-log-out",small,3)
		self.button6.connect("clicked", self.logout)
		self.box2.pack_start(self.button6, True, True, 0)
		self.button6.show()
		
        # Create lock button
		self.button7 = self.makeSuperButton("Lock Screen","lock",small,3)
		self.button7.connect("clicked", self.lock_session)
		self.box2.pack_start(self.button7, True, True, 0)
		self.button7.show()
        
		self.window.show_all()
	
	# Made this because basic buttons didn't have the style capabilities I
	# needed if I were to replicate the GNOME logout panel.
	def makeSuperButton(self, text, icon, size, space):
		box = Gtk.HBox(False,0)
		button = Gtk.Button()
		button.add(box)
		
		image_pixbuf = Gtk.IconTheme.load_icon(self.icon_theme, icon, size, Gtk.IconLookupFlags.GENERIC_FALLBACK)
		image = Gtk.Image.new_from_pixbuf(image_pixbuf)
		box.pack_start(image, False, False, space)
		
		label = Gtk.Label()
		label.set_use_markup(True)
		label.set_markup(text)
		label.set_justify(Gtk.Justification.LEFT)
		box.pack_start(label, False, False, space)
		
		image.set_alignment(0.0,0.5)
		button.set_alignment(0.0,0.5)
		button.set_border_width(5)

		return button
		
def main():
	Gtk.main()

if __name__ == "__main__":
	gogogo = DoTheLogOut()
	main()
