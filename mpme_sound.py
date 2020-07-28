import pygame as pg
import soundfile as sf
from mutagen.mp3 import MP3

class MpmeSound:
    """ The sound file class """

    def __init__(self, settings):
        """ Initialize the sound object. """
        # set up the mixer
        # Here are the original settings:
        #freq = 44100     # audio CD quality
        # A frequency of 44100 works well with the MP3
        # files that I buy. I found that recordings I make
        # have a frequency more like 48000 or even 48500.
        #bitsize = -16    # unsigned 16 bit
        #channels = 2     # 1 is mono, 2 is stereo
        #buffer = 2048    # number of samples (experiment to get best sound)

        self.set_settings(settings)

    def set_volume(self, volume):
        """ Set the volume to a value from 0.0 to 1.0. """
        pg.mixer.music.set_volume(volume)

    def play(self, music_file_name):
        """ Stream music with the mixer.music module in a blocking manner.
            This will stream the sound from the disk while playing. """
        music_file_type = music_file_name[-3:].lower()

        if music_file_type == "wav":
            sf_object = sf.SoundFile(music_file_name)
            self.music_file_length = int(len(sf_object) / sf_object.samplerate)
        else: # presumably it must be "MP3"
            self.music_file_length = int(MP3(music_file_name).info.length)

        clock = pg.time.Clock()

        try:
            # Load the song we want.
            pg.mixer.music.load(music_file_name)
        except pg.error:
            # If the music file wasn't found, do nothing.
            return
        pg.mixer.music.play()
        
    def pause(self):
        """ Pause the song. """
        pg.mixer.music.pause()

    def unpause(self):
        """ Unpause the song. """
        pg.mixer.music.unpause()

    def stop(self):
        """ Stop the song """
        pg.mixer.music.stop()

    def get_position(self):
        """ Get the position - that is, how many
            seconds into the song we currently are. """
        return pg.mixer.music.get_pos()//1000

    def set_position(self, position):
        """ Set the position - that is, how many seconds
            into the song to which we should jump. """
        pg.mixer.music.rewind() # ...or else the position will be relative.
        pg.mixer.music.set_pos(position)

    def get_length(self):
        """ Return the length of the music file. """
        if hasattr(self, 'music_file_length'):
            return self.music_file_length
        else:
            return 0

    def song_is_over(self):
        """ Returns True if the song is over and False if a song is playing """
        return not pg.mixer.music.get_busy()

    def set_settings(self, settings):
        """ Set the settings( the frequency, volume, etc)
            and initialize the sound object. """
        pg.mixer.quit() #...in case it was already initialized.
        freq = int(settings['freq'])
        buffer = int(settings['buffer'])
        pg.mixer.init(freq, settings['bitsize'], settings['channels'], buffer)
        self.set_volume(settings['volume']/100)
