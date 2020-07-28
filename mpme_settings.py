import json
import os
from mpme_constants import MpmeConstants

class MpmeSettings:
    """ A class to retrieve, store, and write settings """

    def __init__(self):
        """ Establish the constants and initialize the object. """
        self.SETTINGS_FOLDER = MpmeConstants.ROOT_FOLDER + \
            MpmeConstants.SETTINGS_FOLDER
        self.SETTINGS_FILE = "mpme_settings.json"
        self.FREQ_DEFAULT = "44100"
        # ^- The original setting, good for "real" MP3 files, was 44100.
        # Sometimes, it seems like the figure should be more like 48500.
        self.BITSIZE_DEFAULT = -16 # unsigned 16 bit
        self.CHANNELS_DEFAULT = 2  # 1 is mono, 2 is stereo
        self.BUFFER_DEFAULT = "2048"
        # ^- number of samples (experiment to get best sound)
        self.VOLUME_DEFAULT = 100 # Valid values are from 0 to 100.
        self.RADIO_FREQ_DEFAULT = "87.5" # Valid values are from 87.5 to 108.0.
        self.PRESET_1_DEFAULT = "Pre 1"
        self.PRESET_2_DEFAULT = "Pre 2"
        self.PRESET_3_DEFAULT = "Pre 3"
        self.PRESET_4_DEFAULT = "Pre 4"
        self.PRESET_5_DEFAULT = "Pre 5"
        self.PRESET_6_DEFAULT = "Pre 6"
        self.PRESET_7_DEFAULT = "Pre 7"
        self.PRESET_8_DEFAULT = "Pre 8"
        self.load()

    def load(self):
        """ Read the settings and store them. """

        # First, take note of the current path.
        current_path = os.getcwd()

        # Then change to the Settings folder.
        os.chdir(self.SETTINGS_FOLDER)

        # If the file doesn't exist, create it.
        if not os.path.isfile(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, "w") as settings_file:
                settings_file.write("{}")
                settings_file.close()

        # Read the settings.
        with open(self.SETTINGS_FILE, "r") as settings_file:
            self.settings = json.load(settings_file)
        # If some settings are missing (because the file got
        # corrupted or something) get default values for them.
        # Not only will they be needed during the run, but they
        # should be written to the settings file for the future.
        self.check_for_key("freq", self.FREQ_DEFAULT)
        self.check_for_key("bitsize", self.BITSIZE_DEFAULT)
        self.check_for_key("channels", self.CHANNELS_DEFAULT)
        self.check_for_key("buffer", self.BUFFER_DEFAULT)
        self.check_for_key("volume", self.VOLUME_DEFAULT)
        self.check_for_key("radio_freq", self.RADIO_FREQ_DEFAULT)
        self.check_for_key("radio_volume", self.VOLUME_DEFAULT)
        self.check_for_key("pre_1", self.PRESET_1_DEFAULT)
        self.check_for_key("pre_2", self.PRESET_2_DEFAULT)
        self.check_for_key("pre_3", self.PRESET_3_DEFAULT)
        self.check_for_key("pre_4", self.PRESET_4_DEFAULT)
        self.check_for_key("pre_5", self.PRESET_5_DEFAULT)
        self.check_for_key("pre_6", self.PRESET_6_DEFAULT)
        self.check_for_key("pre_7", self.PRESET_7_DEFAULT)
        self.check_for_key("pre_8", self.PRESET_8_DEFAULT)

        # Reset the path back to what it was.
        os.chdir(current_path)

    def check_for_key(self, key, default):
        """ Check for a settings in the settings. """
        if not key in self.settings:
            self.settings[key] = default

    def get_radio_freq(self):
        """ Get the radio frequency from the settings. """
        return self.settings['radio_freq']

    def get_radio_volume(self):
        """ Get the radio volume from the settings. """
        return self.settings['radio_volume']

    def get_settings(self):
        """ Get the settings from the settings. """
        return self.settings

    def get_volume(self):
        """ Get the folder view's volume from the settings. """
        return self.settings['volume']

    def get_preset(self, index):
        """ Get a radio station preset; for example, an index of 1
            would mean to get the station for preset number 1. """
        return self.settings['pre_' + str(index)]

    def save_settings(self, new_settings):
        """ Write the Settings file. """

        # First, take note of the current path.
        current_path = os.getcwd()

        # Then change to the Settings folder.
        os.chdir(self.SETTINGS_FOLDER)

        # Now write the Settings file
        try:
            settings_file = open(self.SETTINGS_FILE, "w")
            json.dump(new_settings, settings_file)
            settings_file.close()
        except:
            message = "Error:\nThe settings failed to save."
        else:
            message = ""
        finally:
            # Reset the path back to what it was.
            os.chdir(current_path)
            return message

    def save_volume(self, new_volume):
        """ Save the Folder view's volume in the settings file. """
        self.settings['volume'] = new_volume
        self.save_settings(self.settings)

    def default_freq(self):
        """ Get the default frequency for MP3 files. """
        return self.FREQ_DEFAULT

    def default_channels(self):
        """ Get the default number of channels. """
        return self.CHANNELS_DEFAULT

    def default_buffer(self):
        """ Get the default buffer size. """
        return self.BUFFER_DEFAULT

    def save_radio_volume(self, new_volume):
        """ Save the radio's volume in the settings file. """
        self.settings['radio_volume'] = new_volume
        self.save_settings(self.settings)

    def save_radio_freq(self, new_radio_freq):
        """ Save the radio frequency to the settings file. """
        self.settings['radio_freq'] = new_radio_freq
        self.save_settings(self.settings)

    def save_preset(self, preset_number, freq):
        """ Save the frequency as the preset of a given number. """
        self.settings['pre_' + str(preset_number)] = freq
        self.save_settings(self.settings)

    def valid(self, requested_freq, requested_buffer):
        """ Validate the settings the user specified. """
        number_of_errors = 0
        message = ""

        # Require values for frequency and buffer.
        if requested_freq == "" or requested_buffer == "":
            return "Error:\nValues may not be null."

        # Reject values with leading zeroes so
        # Python doesn't think they're octals.
        if requested_freq[0] == '0' or requested_buffer[0] == '0':
            return "Error:\nLeading zeroes are prohibited."

        freq_int = int(requested_freq)
        buffer_int = int(requested_buffer)

        # The frequency should be from 100 to 200,000.
        # The buffer should be from 0 to 1,073,741,824.
        if freq_int < 100 or freq_int > 200000:
            number_of_errors = number_of_errors + 1
            message = message + \
                "The frequency should be from 100 to 200,000.\n"
        if buffer_int > 1073741824:
            number_of_errors = number_of_errors + 1
            message = message + "The buffer should not exceed 1,073,741,824.\n"

        if number_of_errors == 1:
            message = "Error:\n" + message
        elif number_of_errors > 1:
            message = "Errors:\n" + message
        return message

