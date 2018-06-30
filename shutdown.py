#!/usr/bin/env python3

import os
import pwd

from subprocess import Popen, PIPE
from gi.repository import Gtk

try:
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)
except ImportError:
    dbus = None


BIG = 48
SMALL = 24


def get_username():
    """ Returns the current username """
    return pwd.getpwuid(os.getuid()).pw_name


def delete_event(*_, **__):
    """ Cancel/exit event """
    Gtk.main_quit()
    return False


def suspend(_):
    """ Suspend event """
    Popen(
        "dbus-send --system --print-reply "
        "--dest=org.freedesktop.login1 "
        "/org/freedesktop/login1 "
        "org.freedesktop.login1.Manager.Suspend "
        "boolean:true")
    Gtk.main_quit()


def hibernate(_):
    """ Hibernate event """
    Popen(
        "dbus-send --system --print-reply "
        "--dest=org.freedesktop.login1 "
        "org/freedesktop/login1 "
        "org.freedesktop.login1.Manager.Hibernate "
        "boolean:true")
    Gtk.main_quit()


def reboot(_):
    """ Reboot event """
    Popen(
        "dbus-send --system --print-reply "
        "--dest=org.freedesktop.ConsoleKit "
        "/org/freedesktop/ConsoleKit/Manager "
        "org.freedesktop.ConsoleKit.Manager.Restart")


def shutdown(_):
    """ Shutdown event """
    Popen(
        "dbus-send --system --print-reply "
        "--dest=org.freedesktop.ConsoleKit "
        "/org/freedesktop/ConsoleKit/Manager "
        "org.freedesktop.ConsoleKit.Manager.Stop")


def logout(_):
    """ Log out event. Relies on systemd and logind. """
    try:
        sessions = Popen("loginctl", stdout=PIPE)
        username = get_username()
        session_id = None

        for line in sessions.stdout:
            vals = line.split()
            if vals[2] == username:
                session_id = vals[1]

        Popen(
            "dbus-send --system --print-reply "
            "--dest=org.freedesktop.login1 "
            "/org/freedesktop/login1 "
            "'org.freedesktop.login1.Manager.TerminateSession' "
            "string:{}".format(session_id))
    except Exception:
        print("Unable to log out via systemd. "
              "Try other means via Terminal")


def lock_session(_):
    """ Lock screen event. Only works if you have a screensaver running. """
    session_bus = dbus.SessionBus()
    dbus_services = session_bus.list_names()
    can_lock_screen = "org.gnome.ScreenSaver" in dbus_services

    if can_lock_screen:
        Popen("gnome-screensaver-command --lock")
    else:
        can_lock_screen = "org.freedesktop.ScreenSaver" in dbus_services

        if can_lock_screen:
            Popen("xscreensaver-command --lock")

    Gtk.main_quit()


class LogOutDialog:
    """ Creates a GTK dialog to shutdown/restart your system """

    def __init__(self):
        self.settings = Gtk.Settings.get_default()
        self.settings.set_property("gtk-button-images", True)

        self.icon_theme = Gtk.IconTheme.get_default()

        # Create a new window
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.set_title("Shutdown")
        self.window.set_resizable(False)
        self.window.set_position(1)
        self.window.connect("delete_event", delete_event)
        self.window.set_border_width(10)

        # Create a box to pack widgets into
        self.main_box = Gtk.VBox(False, 0)
        self.window.add(self.main_box)

        # Create the shutdown button frame.
        self.frame1 = Gtk.Frame()
        self.frame1.set_shadow_type(Gtk.ShadowType.NONE)
        self.box1 = Gtk.VBox(False, 0)
        self.frame1.add(self.box1)
        self.main_box.add(self.frame1)

        # Create shutdown button
        self.button1 = self.styled_button(
            "<span font_weight=\"bold\">Shut Down</span>\n"
            "<span font_weight=\"light\" size=\"small\">"
                "Ends your session and turns off the power."
            "</span>", "system-shutdown", BIG, 10)
        self.button1.connect("clicked", shutdown)
        self.box1.pack_start(self.button1, True, True, 0)
        self.button1.show()

        # Create reboot button
        self.button2 = self.styled_button(
            "<span font_weight=\"bold\">Reboot</span>\n"
            "<span font_weight=\"light\" size=\"small\">"
                "Ends your session and restarts the computer."
            "</span>", "reload", BIG, 10)
        self.button2.connect("clicked", reboot)
        self.box1.pack_start(self.button2, True, True, 0)
        self.button2.show()

        # Create suspend button
        self.button3 = self.styled_button(
            "<span font_weight=\"bold\">Suspend</span>\n"
            "<span font_weight=\"light\" size=\"small\">"
                "Suspends your session quickly, using \n"
                "minimal power while the computer stands by."
            "</span>", "sleep", BIG, 10)
        self.button3.connect("clicked", suspend)
        self.box1.pack_start(self.button3, True, True, 0)
        self.button3.show()

        # Create hibernate button
        self.button4 = self.styled_button(
            "<span font_weight=\"bold\">Hibernate</span>\n"
            "<span font_weight=\"light\" size=\"small\">"
                "Suspends your session, using no power \n"
                "until the computer is restarted."
            "</span>", "filesave", BIG, 10)
        self.button4.connect("clicked", hibernate)
        self.box1.pack_start(self.button4, True, True, 0)
        self.button4.show()

        # Create the cancel/logout/lock button frame.
        self.frame2 = Gtk.Frame()
        self.frame2.set_shadow_type(Gtk.ShadowType.NONE)
        self.box2 = Gtk.HBox(False, 0)
        self.frame2.add(self.box2)
        self.main_box.add(self.frame2)

        # Create cancel button
        self.button5 = self.styled_button("Cancel", "stop", SMALL, 3)
        self.button5.connect("clicked", delete_event, "Changed my mind.")
        self.box2.pack_start(self.button5, True, True, 0)
        self.button5.show()

        # Create log out button
        self.button6 = self.styled_button("Log Out", "system-log-out", SMALL, 3)
        self.button6.connect("clicked", logout)
        self.box2.pack_start(self.button6, True, True, 0)
        self.button6.show()

        # Create lock button
        self.button7 = self.styled_button("Lock Screen", "lock", SMALL, 3)
        self.button7.connect("clicked", lock_session)
        self.box2.pack_start(self.button7, True, True, 0)
        self.button7.show()

        self.window.show_all()


    # Made this because basic buttons didn't have the style capabilities I
    # needed if I were to replicate the GNOME logout panel.
    def styled_button(self, text, icon, size, space):
        """ Produces a stylized button """
        box = Gtk.HBox(False, 0)
        button = Gtk.Button()
        button.add(box)

        image_pixbuf = Gtk.IconTheme.load_icon(
            self.icon_theme, icon, size, Gtk.IconLookupFlags.GENERIC_FALLBACK)
        image = Gtk.Image.new_from_pixbuf(image_pixbuf)
        box.pack_start(image, False, False, space)

        label = Gtk.Label()
        label.set_use_markup(True)
        label.set_markup(text)
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, False, False, space)

        image.set_alignment(0.0, 0.5)
        button.set_alignment(0.0, 0.5)
        button.set_border_width(5)

        return button


def main():
    """ Main method """
    Gtk.main()


if __name__ == "__main__":
    LogOutDialog()
    main()
