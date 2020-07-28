import tkinter as tk

class DragDropListbox(tk.Listbox):
    """ A tkinter listbox with drag'n'drop reordering of entries. """
    def __init__(self, master, file_display, **kw):
        """ Initialize the listbox and bind the events for
            clicking, dragging, and releasing an item in it."""
        # The user can select only a single row at a time.
        kw['selectmode'] = tk.SINGLE
        tk.Listbox.__init__(self, master, kw)
        self.bind('<Button-1>', self.setCurrent)
        self.bind('<B1-Motion>', self.shiftSelection)
        self.bind('<ButtonRelease-1>', self.checkForClick)
        self.curIndex = None
        self.file_display = file_display

    def setCurrent(self, event):
        """ Note the row on which the user just clicked. """
        self.curIndex = self.nearest(event.y)
        self.clickedWithoutDragging = True

    def shiftSelection(self, event):
        """ Move a row to the place the user is dragging it. """
        self.clickedWithoutDragging = False
        i = self.nearest(event.y)
        if i < self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i+1, x)
            self.curIndex = i
        elif i > self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i-1, x)
            self.curIndex = i

    def checkForClick(self, event):
        """ See if the user left-clicked the mouse AND LET GO OF THE
            LEFT-CLICK MOUSE BUTTON WITHOUT DRAGGING IT IN BETWEEN!!!"""
        if self.clickedWithoutDragging:
            self.file_display.click_line()
