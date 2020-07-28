import tkinter as tk
import drag_drop_listbox
import os
from mpme_constants import MpmeConstants
from mpme_file_manager import *

class FileLister():
    """ Class to display the files and sub-folders
        and allow the user to interface with them """
    def __init__(self, frm, row, column, rowspan, columnspan):
        """ Create the listbox to display the files and folders. """
        # Constant for the path to the root folder in the folder view:
        self.ROOT_FOLDER = MpmeConstants.ROOT_FOLDER + \
            MpmeConstants.FOLDER_VIEW
        self.frm = frm

        # The scrollbar
        scrollbar = tk.Scrollbar(frm, orient="vertical")
        scrollbar.grid(row=row, column=columnspan, rowspan=rowspan,
                       columnspan=1, sticky='ns')

        # Create the listbox (with drag 'n' drop capability).
        self.playlist = drag_drop_listbox.DragDropListbox(
            frm, self, width=45, yscrollcommand=scrollbar.set)
        self.playlist.grid(row=row, rowspan=rowspan, column=1,
                           columnspan=columnspan-1)
        scrollbar.config(command=self.playlist.yview)
        self.get_list(self.ROOT_FOLDER)

    def click_line(self):
        """ Respond to a user clicking on a line without dragging
            it - that is, change directories if it's a folder
            or play the sound file if it's a file. """
        # (But first write the order of the current folder.)
        self.write_order()
        entry_reading = self.playlist.get(self.playlist.curselection()[0])
        entry_name = entry_reading[len(MpmeFileManager.FOLDER_ICON):]
        if entry_reading.startswith(MpmeFileManager.FOLDER_ICON):
            self.get_list(entry_name)
        else:
            # Presumably it's a sound file.
            self.frm.play(entry_name)

    def write_order(self):
        """ Write the file with the order within the folder. """
        MpmeFileManager.write_order(self.playlist.get(0, tk.END))

    def get_nonvisual_list(self, path):
        """ Return a list of files and folders in the given folder. """
        folder_listing = []
        # Change the directory.
        os.chdir(path)
        # Now get the new (current) complete path in a string.
        current_path = self.trim_off_drive(os.getcwd())
        # List the folders and files in the directory.
        for f in os.listdir(current_path):
            if os.path.isfile(f):
                if (self.acceptable_file(f)):
                    folder_listing.append(MpmeFileManager.MUSIC_ICON + f)
            else: # It must be a folder.
                folder_listing.append(MpmeFileManager.FOLDER_ICON + f)
        # Sort the folders and files into the
        # order the user previously specified.
        MpmeFileManager.read_order(folder_listing)
        # If it's not the official root...
        if current_path != self.ROOT_FOLDER:
            # ...then add a line to go up to the parent folder.
            folder_listing.insert(0, MpmeFileManager.FOLDER_ICON + "..")
        return folder_listing
    def get_list(self, path):
        """ Get a list of the files and folders and
            populate the listbox with them. """
        folder_listing = self.get_nonvisual_list(path)
        # Clear the listbox of any existing content.
        self.playlist.delete(0, tk.END)
        # Insert the folders and files into the listbox.
        for item in folder_listing:
            self.playlist.insert(tk.END, item)

    def get_current_path(self):
        return os.getcwd()

    def next_file(self, current_path, current_file):
        """ Given a file in a folder given in a path navigate to the next
            song and return its filename (including the extension). """

        # (But first write the order of the current
        # folder in case we navigate out of it.)
        self.write_order()
        
        # Start by determining the initial values.
        path_iteration = current_path
        folder_list = self.get_nonvisual_list(path_iteration)
        # Find which element in the list is the current song.
        file_index = MpmeFileManager.file_index(folder_list, current_file)
        # What would cause an error to return a -1? Could the file have been
        # deleted while playing? Is that possible? Could the files have been
        # corrupted? I don't know. What the heck; in such a case the file
        # index will get incremented to 0, the first element in the list.

        # Now loop until we find the right file.
        while True:
            file_index = file_index + 1
            if file_index >= len(folder_list):
                file_index = 0
            filename_portion = MpmeFileManager.filename_portion(
                folder_list[file_index])
            if MpmeFileManager.is_folder(folder_list[file_index]):
                # Change current path to the folder.
                current_folder = MpmeFileManager.folder_name(path_iteration)
                folder_list = self.get_nonvisual_list(filename_portion)
                if filename_portion == "..":
                    # Find the index of the folder from which we're emerging.
                    file_index = MpmeFileManager.file_index(
                        folder_list, current_folder)
                else:
                    # Start at the beginning of the listing in that folder.
                    file_index = 0 # ...so the loop will increment
                    # it to 1, the first item that isn't "..".
                path_iteration = os.getcwd()
            else: # Assume it's a valid sound file; we found our answer!
                self.get_list(path_iteration)
                #self.playlist.select_clear(0, self.playlist.size() - 1)
                self.playlist.select_set(file_index)
                sound_file = MpmeFileManager.filename_portion(
                     self.playlist.get(file_index))
                return(sound_file)


    @staticmethod
    def trim_off_drive(path):
        """ Given a string that's a path, trim off the leading drive. """
        index = path.find(":")
        if index >= 0:
            return path[index+1:]
        else:
            return path
        
    @staticmethod
    def acceptable_file(file_name):
        """ Determine if a file is of an acceptable file type."""
        # Originally we allowed .wav files as well as .mp3 but the
        # pygame.mixer.music.set_pos() method doesn't work with .wav files.
        if file_name.endswith(".mp3"):
            return True
        else:
            return False
