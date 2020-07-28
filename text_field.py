import tkinter as tk

class TextField(tk.Entry):
    """ A tkinter Entry widget with functionality
        to execute editing commands """
    def __init__(self, master, **kw):
        """ Initialize the Entry widget. """
        tk.Entry.__init__(self, master, kw)
        self.bind('<Button-1>', self.button_down)
        self.master = master

    def button_down(self, event):
        """ Indicate that this is the text field currently in focus. """
        self.master.set_current_text_field(self)
