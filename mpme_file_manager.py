import os
from mpme_constants import MpmeConstants

class MpmeFileManager():
    """ Class to store and retrieve the sort order
        in a folder and to sort accordingly """
    # Some constants:
    FOLDER_ICON = "╒  "
    MUSIC_ICON = "♫  "
    ORDER_FILE_NAME = "__MPMe_Order__.txt"

    @staticmethod
    def initialize_folders():
        """ Check if the folder view exists. If it doesn't,
            create it. Ditto for the settings folder. """

        # First, take note of the current path.
        current_path = os.getcwd()

        # Then change to the root folder.
        os.chdir(MpmeConstants.ROOT_FOLDER)

        # If the folder view doesn't exist, create it.
        if not os.path.isdir(MpmeConstants.FOLDER_VIEW):
            try:
                os.mkdir(MpmeConstants.FOLDER_VIEW)
            except OSError:
                print("Creation of Folder View failed.")
            else:
                print("Creation of Folder View succeeded.")

        # If the settings folder doesn't exist, create it.
        if not os.path.isdir(MpmeConstants.SETTINGS_FOLDER):
            try:
                os.mkdir(MpmeConstants.SETTINGS_FOLDER)
            except OSError:
                print("Creation of Settings folder failed.")
            else:
                print("Creation of Settings folder succeeded.")

        # Reset the path back to what it was.
        os.chdir(current_path)

    @staticmethod
    def filename_portion(filename):
        """ Return the real file name - that is without
            the leading folder icon or music icon. """
        return filename.replace(MpmeFileManager.FOLDER_ICON, '',
            1).replace(MpmeFileManager.MUSIC_ICON, '', 1)

    @staticmethod
    def file_index(file_list, file_name, start_with=0):
        """ Determine the index of the file name in the file list.
            This is basically the same as the "index" list operation except
            that it shaves off the icon in the search, and also that if the
            file name isn't in the list, this method will return -1. """
        list_length = len(file_list)
        for index in (range(start_with,list_length)):
            if file_name == MpmeFileManager.filename_portion(file_list[index]):
                return index
        return -1

    @staticmethod
    def write_order(folder_list):
        """ Write the order of the files and folders into a file. """
        # Presumably, the file will be written to the current path.
        file_object = open(MpmeFileManager.ORDER_FILE_NAME, 'w')
        for item in folder_list:
            if item != MpmeFileManager.FOLDER_ICON + "..":
                formatted_item = MpmeFileManager.filename_portion(item)
                file_object.write(formatted_item + '\n')
        file_object.close()

    @staticmethod
    def read_order(folder_list):
        """ Read the order of files and subfolders in a folder and
            sort the list of files and subfolders accordingly. """
        # Presumably, the file was written in the current path.
        try:
            file_object = open(MpmeFileManager.ORDER_FILE_NAME, 'r')
        except IOError:
            return '' # Do nothing; just keep the order as is.

        writing_index = 0
        file_or_folder_name = file_object.readline().strip()
        while file_or_folder_name != "":
            index_of_fof = MpmeFileManager.file_index(
                folder_list, file_or_folder_name, writing_index)
            if index_of_fof != -1:
                element_we_want = folder_list.pop(index_of_fof)
                folder_list.insert(writing_index, element_we_want)
                writing_index = writing_index + 1
            file_or_folder_name = file_object.readline().strip()         
        file_object.close()

    @staticmethod
    def is_folder(file_or_folder_name):
        """ Determine whether an item in the listing is a folder. """
        return (file_or_folder_name[:len(MpmeFileManager.FOLDER_ICON)] ==
                MpmeFileManager.FOLDER_ICON)

    @staticmethod
    def folder_name(path):
        """ Given a path, return the folder name at the end of it. """
        # Assume that there IS a valid path in the argument.
        all_folders = path.split('\\')
        i = len(all_folders) - 1
        if all_folders[i] == '':
            return all_folders[i-1]
        else:
            return all_folders[i]
