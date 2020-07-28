import tkinter as tk

class PositionSlider(tk.Scale):
    """ A Scale object - that is, a slide-control - for reporting
        and changing the current position in the song. """
    def __init__(self, master, **kw):
        """ Initialize the slider and bind the events for
            clicking, dragging, and releasing an item in it."""
        tk.Scale.__init__(self, master, kw)
        self.bind('<ButtonRelease-1>', self.button_release)

    def button_release(self, event):
        self.master.jump(self.get())

