import tkinter as tk

class TimeDisplay(tk.Label):
    """ The timer displayed in the player """

    def __init__(self, master, increment_amount, **kw):
        """ Create the time display - a label - and hook it
            up to a StringVar so that whenever the StringVar
            changes the label will change with it. """
        tk.Label.__init__(self, master, kw)
        self.timer_seconds = 0
        self.timer_readout = tk.StringVar()
        self.config(textvariable=self.timer_readout)
        self.update_timer_readout()
        self.master = master
        self.increment_amount = increment_amount

    def update_timer_readout(self):
        """ Convert the number of seconds to a minute-and-second
            display, e.g. from 62 to '1:02', and display it. """
        self.timer_readout.set('{:01d}:{:02d}'.
                        format(self.timer_seconds//60, self.timer_seconds%60))

    def increment(self):
        """ Add +-1 second to the timer and update the display accordingly. """
        self.timer_seconds = self.timer_seconds + self.increment_amount
        if self.timer_seconds < 0:
            self.timer_seconds = 0
        self.update_timer_readout()

    def move_timer(self, seconds):
        """ Move the timer to the set number of seconds. """
        self.timer_seconds = seconds
        self.update_timer_readout()
