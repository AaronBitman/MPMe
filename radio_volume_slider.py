import tkinter as tk

class RadioVolumeSlider(tk.Scale):
    """ A Scale object - that is, a slide-control - for
        reporting and changing the current volume. """
    def __init__(self, master, **kw):
        """ Initialize the slider and bind the events for
            clicking, dragging, and releasing an item in it."""
        tk.Scale.__init__(self, master, kw)
        self.bind('<B1-Motion>', self.shift_selection)
        self.bind('<ButtonRelease-1>', self.button_release)
        self.master = master

    def shift_selection(self, event):
        """ Define what to do while the user drags the slider. """
        self.master.change_radio_volume(self.get())

    def button_release(self, event):
        """ Define what to do when the user releases the mouse button. """
        self.master.change_radio_volume(self.get())

