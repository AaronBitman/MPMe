from mpme_constants import MpmeConstants

class RadioReceiver():
    """ Class to simulate a radio receiver """

    def __init__(self, freq, volume):
        """ Start the receiver switched off with the set volume. """
        self.freq = freq
        self.volume = volume

    def change_freq(self, freq):
        """ Change the radio frequency. """
        self.freq = freq
        return False

    def change_volume(self, volume):
        """ Change the radio volume. """
        self.volume = volume

    def receiving_signal(self, station):
        """ Determine if the radio is receiving a
            "signal" (really the simulation of one). """
        SIGNAL_FILE = MpmeConstants.ROOT_FOLDER + \
            MpmeConstants.SETTINGS_FOLDER + "\\receiving_stations.txt"
        try:
            with open(SIGNAL_FILE) as file_object:
                for line in file_object:
                    if line.rstrip('\n') == station:
                        return True
        except FileNotFoundError:
            return False
        return False                
