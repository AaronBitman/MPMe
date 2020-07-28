import tkinter as tk
from file_lister import FileLister
from position_slider import PositionSlider
from volume_slider import VolumeSlider
from radio_volume_slider import RadioVolumeSlider
from radio_freq_slider import RadioFreqSlider
from mpme_sound import MpmeSound
from time_display import TimeDisplay
from repeated_timer import RepeatedTimer
from mpme_settings import MpmeSettings
from text_field import TextField
from radio_receiver import RadioReceiver
from mpme_file_manager import MpmeFileManager

class Mpme(tk.Tk):
    """ The window class """

    def __init__(self, *args, **kwargs):
        """ Initialize the window. """
        tk.Tk.__init__(self, *args, **kwargs)
        # Set the title of the main window.
        self.title('MPMe')
        # Set the size of the main window.
        self.geometry('300x350')

        # Install a protocol handler for closing the window.
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Check that the necessary folders are there; if not, create them.
        MpmeFileManager.initialize_folders()
        
        # Create an object for holding the settings.
        self.settings_object = MpmeSettings()
 
        # Create the sound file (nonvisual) object.
        self.sound_object = MpmeSound(self.settings_object.get_settings())

        # this container contains all the pages
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        # Make the cell in the grid cover the entire window.
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {} # These are pages to which we want to navigate.

        # For each page...
        for F in (MpmeStartPage, MpmeFolderPage,
                  MpmeSettingsPage, MpmeRadioPage):
            # ...create the page...
            frame = F(container, self)
            # ...store it in a frame...
            self.frames[F] = frame
            # ..and position the page in the container.
            frame.grid(row=0, column=0, sticky='nsew')

        # The first page is StartPage.
        self.show_frame(MpmeStartPage)
 
    def show_frame(self, name):
        """ Show the frame, that is, the container for all the pages. """
        self.frames[name].tkraise()
        # If the Radio page comes up, stop the MP3 file (if any) from playing.
        if name == MpmeRadioPage:
            self.frames[MpmeFolderPage].stop()
            self.frames[MpmeRadioPage].start_reception()
        # If the Start page comes up, stop the radio (in case it's on).
        elif name == MpmeStartPage:
            self.frames[MpmeRadioPage].stop_reception()

    def on_closing(self):
        """ Before closing the window, save the order in case we're in the
            Folder view and stop the song in case there's one playing. """
        self.frames[MpmeFolderPage].file_display.write_order()
        self.frames[MpmeFolderPage].stop()
        self.frames[MpmeRadioPage].stop_reception()
        self.destroy()

class MpmeStartPage(tk.Frame):
    """ Class to hold the highest-level page """

    def __init__(self, parent, controller):
        """ Initilize the start page with buttons for all the other pages. """
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text='Start')
        label.pack(pady=10, padx=10) # center alignment

        # Display the company name and logo.
        company_name = tk.Label(self, text='BP&M', font=('', 16))
        product_name = tk.Label(self, text='MPMe', font=('', 16))
        self.company_logo = tk.PhotoImage(file = 'BP&M Logo.gif')
        company_logo_label = tk.Label(self, image = self.company_logo)

        # When the user clicks on these buttons, call the show_frame
        #   method to make the Folders, Settings, or Radio screen appear.
        self.folders_icon = tk.PhotoImage(file = 'folder.gif')
        button_folders = tk.Button(self, text='Folders',
            image = self.folders_icon, compound=tk.LEFT,
            command=lambda : controller.show_frame(MpmeFolderPage))
        self.settings_icon = tk.PhotoImage(file = 'settings.gif')
        button_settings = tk.Button(self, text='Settings',
            image = self.settings_icon, compound=tk.LEFT,
            command=lambda : controller.show_frame(MpmeSettingsPage))
        self.radio_icon = tk.PhotoImage(file = 'radio.gif')
        button_radio = tk.Button(self, text='Radio',
            image = self.radio_icon, compound=tk.LEFT,
            command=lambda : controller.show_frame(MpmeRadioPage))

        # Pack the controls.
        company_name.pack()
        product_name.pack()
        company_logo_label.pack()
        button_folders.pack()
        button_settings.pack()
        button_radio.pack()

class MpmeFolderPage(tk.Frame):
    """ Class for the Folder page for accessing all the folders and files """

    def __init__(self, parent, controller):
        """ Initialize the page and create its objects. """
        tk.Frame.__init__(self, parent)

        self.paused = False # Whether or not a song is paused

        self.controller = controller

        # When the user clicks on this button, call the
        #   show_frame method to make the main screen appear.
        button_start = tk.Button(self, text='Start',
                    command=lambda : self.save_and_start())
        self.button_pause = tk.Button(self, text='Pause',
                    command=lambda : self.pause())
        self.button_pause["state"] = "disable"
        #button_stop = tk.Button(self, text='■',
        #            command=lambda : self.stop())
        # We're getting rid of the Stop button; we don't need it.

        # Specify the geometry to place the buttons.
        button_start.grid(row=1, column=1)
        self.button_pause.grid(row=1, column=2)

        # Create the file lister object.
        self.file_display = FileLister(self, 2, 1, 1, 4)
       
        # Create the Volume slide control.
        volume_slider = VolumeSlider(self, from_=0, to=100,
                            orient=tk.HORIZONTAL, label="VOLUME", length=290)
        volume_slider.set(self.controller.settings_object.get_volume())
        # Specify the geometry to place the Volume slide control.
        volume_slider.grid(row=3, column=1, columnspan=4)

        # Create the Position slide control.
        self.position_slider = PositionSlider(self, from_=0, to=100,
                        orient=tk.HORIZONTAL, label="POSITION", length=290)
        # Specify the geometry to place the Position slide control.
        self.position_slider.grid(row=4, column=1, columnspan=4)

        # Create the time display.
        self.current_time = TimeDisplay(self, 1)
        # Specify the geometry to place the time display.
        self.current_time.grid(row=5, column=1)

        # Create the display for the song's total length.
        self.total_time = TimeDisplay(self, 0)
        # Specify the geometry to place the "total" time display.
        self.total_time.grid(row=5, column=2)
        
        # Create the display for the amount of time left.
        self.time_left = TimeDisplay(self, -1)
        # Specify the geometry to place the time-left display.
        self.time_left.grid(row=5, column=3)

        # The following variable is to indicate if, while the song is
        # paused, the user jumped to a different point in the song.
        self.jump_pending = False

    def save_and_start(self):
        """ Save the order and THEN return to the Start page. """
        self.file_display.write_order()
        self.controller.show_frame(MpmeStartPage)

    def play(self, sound_file):
        """ Play a file and configure the rest of the window accordingly. """
        # (But first check if there's a timer
        # currently running and if so, stop it.)
        if hasattr(self, 'timer'):
            self.timer.stop()
        self.position_slider.set(0)
        self.controller.sound_object.play(sound_file)
        self.current_time.move_timer(0)
        self.total_time.move_timer(self.controller.sound_object.get_length())
        self.time_left.move_timer(self.controller.sound_object.get_length())
        self.timer = RepeatedTimer(1, self.increment_timers)
        self.button_pause["state"] = "normal"
        self.button_pause.config(relief=tk.RAISED)
        self.paused = False
        self.song_now_playing = sound_file
        self.path_now_playing = self.file_display.get_current_path()

    def pause(self):
        """ Toggle between a "paused" and "non-paused" state. """
        if self.paused:
            self.button_pause.config(relief=tk.RAISED)
            # Theoretically, if the user pauses and unpauses
            # many times during the same song, the timers
            # could get thrown off. So adjust the timers.
            if not self.jump_pending:
                self.current_time.move_timer(
                    self.controller.sound_object.get_position())
                self.time_left.move_timer(
                    self.controller.sound_object.get_length() -
                    self.controller.sound_object.get_position())
                self.position_slider.set(self.current_time.timer_seconds /
                    self.controller.sound_object.get_length() * 100)
            self.jump_pending = False
            self.controller.sound_object.unpause()
            self.timer = RepeatedTimer(1, self.increment_timers)
        else:
            self.button_pause.config(relief=tk.SUNKEN)
            self.controller.sound_object.pause()
            self.timer.stop()
        self.paused = not self.paused

    def stop(self):
        """ Stop the song and the timer. """
        self.controller.sound_object.stop()
        self.button_pause.config(relief=tk.RAISED)
        self.paused = False
        self.button_pause["state"] = "disable"
        self.jump_pending = False
        if hasattr(self, 'timer'):
            self.timer.stop()

    def increment_timers(self):
        """ Add a seoond to the time, subtract a second from the time
            left, and push the position slider forward in proportion. """
        # (But first check if the song is over,
        # in which case play the next song.)
        if self.controller.sound_object.song_is_over():
            # Stop the song, find the next song, and play it. 
            self.play(self.file_display.next_file(
                self.path_now_playing, self.song_now_playing))
        else:
            self.current_time.increment()
            self.time_left.increment()
            self.position_slider.set(self.current_time.timer_seconds /
                self.controller.sound_object.get_length() * 100)
   
    def change_volume(self, volume):
        """ Change the song's audio volume. """
        self.controller.sound_object.set_volume(volume/100)
        self.controller.settings_object.save_volume(volume)

    def jump(self, position_percentage):
        """ Jump to a specified position. For instance, if position_percentage
            is 37 then jump to a point 37% of the way into the song. """
        position_in_seconds = position_percentage * \
                self.controller.sound_object.get_length() // 100
        self.controller.sound_object.set_position(position_in_seconds)
        self.current_time.move_timer(position_in_seconds)
        self.time_left.move_timer(self.controller.sound_object.get_length() -
                                  position_in_seconds)
        if self.paused:
            self.jump_pending = True

class MpmeSettingsPage(tk.Frame):
    """ Class for the Settings page """

    def __init__(self, parent, controller):
        """ Initialize the page. """

        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.INITIAL_MESSAGE = '"Official" CD quality may have a ' + \
            'frequency of\n44,100. Some "underground" files may' + \
            ' have\na frequency more like 48,000 or even 48,500.'
        self.SAVED_MESSAGE = 'The settings were saved.'
        self.successful_save = False

        # When the user clicks on this button, call the
        #   show_frame method to make the main screen appear.
        button_start = tk.Button(self, text='Start',
                    command=lambda : self.leave_page())

        # Here's a button for saving the settings.
        button_save = tk.Button(self, text='Save',
            command=lambda : self.save_settings())

        # This button restores the default values.
        button_restore = tk.Button(self, text='Restore',
            command=lambda : self.restore())

        # Create the widgets. First for the frequency:
        self.freq_value = tk.StringVar()
        freq_label = tk.Label(self, text='Frequency: ')
        freq_entry = TextField(self, textvariable=self.freq_value)

        # Now for the number of channels:
        self.channels_value = tk.IntVar()
        channels_label = tk.Label(self, text='Channels: ')
        stereo_entry = tk.Radiobutton(self, text='2 (Stereo)',
            variable=self.channels_value, value=2)
        mono_entry = tk.Radiobutton(self, text='1 (Mono)',
            variable=self.channels_value, value=1)

        # Now for the buffer (the number of samples):
        self.buffer_value = tk.StringVar()
        buffer_label = tk.Label(self, text='Buffer: ')
        buffer_entry = TextField(self, textvariable=self.buffer_value)

        # And we'll want a place for messages to the user.
        self.message_label = tk.Label(self, text=self.INITIAL_MESSAGE)

        # Now the keypad:
        button_7 = tk.Button(self, text='  7  ',
            command=lambda : self.keypad('7'))
        button_8 = tk.Button(self, text='  8  ',
            command=lambda : self.keypad('8'))
        button_9 = tk.Button(self, text='  9  ',
            command=lambda : self.keypad('9'))
        button_4 = tk.Button(self, text='  4  ',
            command=lambda : self.keypad('4'))
        button_5 = tk.Button(self, text='  5  ',
            command=lambda : self.keypad('5'))
        button_6 = tk.Button(self, text='  6  ',
            command=lambda : self.keypad('6'))
        button_1 = tk.Button(self, text='  1  ',
            command=lambda : self.keypad('1'))
        button_2 = tk.Button(self, text='  2  ',
            command=lambda : self.keypad('2'))
        button_3 = tk.Button(self, text='  3  ',
            command=lambda : self.keypad('3'))
        button_0 = tk.Button(self, text='  0  ',
            command=lambda : self.keypad('0'))
        button_delete = tk.Button(self, text='Del',
            command=lambda : self.keypad('Delete'))
        button_clear= tk.Button(self, text='Clr ',
            command=lambda : self.keypad('Clear'))
       
        # Specify the geometry to place the widgets.
        button_start.grid(row=1, column=1)
        button_save.grid(row=1, column=3)
        button_restore.grid(row=1, column=5)
        freq_label.grid(row=2, column=1)
        freq_entry.grid(row=2, column=2, columnspan=3, sticky='ew')
        channels_label.grid(row=3, column=1)
        stereo_entry.grid(row=3, column=2, columnspan=3)
        mono_entry.grid(row=3, column=5)
        buffer_label.grid(row=4, column=1)
        buffer_entry.grid(row=4, column=2, columnspan=3, sticky='ew')
        button_7.grid(row=5, column=2)
        button_8.grid(row=5, column=3)
        button_9.grid(row=5, column=4)
        button_4.grid(row=6, column=2)
        button_5.grid(row=6, column=3)
        button_6.grid(row=6, column=4)
        button_1.grid(row=7, column=2)
        button_2.grid(row=7, column=3)
        button_3.grid(row=7, column=4)
        button_0.grid(row=8, column=2)
        button_delete.grid(row=8, column=3)
        button_clear.grid(row=8, column=4)
        self.message_label.grid(row=9, column=1, rowspan=3, columnspan=5)

        # Get the settings and populate the fields with them.
        self.current_settings = self.controller.settings_object.get_settings()
        self.freq_value.set(self.current_settings.get("freq"))
        self.channels_value.set(self.current_settings.get("channels"))
        self.buffer_value.set(self.current_settings.get("buffer"))

        self.current_text_field = None # the text field in which the user types

    def set_current_text_field(self, current_text_field):
        """ Indicate that the given text field is the current one,
            so we'll know where the typed numbers should go. """
        self.current_text_field = current_text_field

    def keypad(self, entry):
        """ Type the entry into the text field which has focus. """
        if self.current_text_field == None:
            return
        elif entry == 'Delete':
            # Delete the last character in the field.
            self.current_text_field.delete(len(self.current_text_field.get())
                                           - 1)
            # Put the cursor at the end of the field.
            self.current_text_field.icursor(len(self.current_text_field.get()))
        elif entry == 'Clear':
            self.current_text_field.delete(0,
                len(self.current_text_field.get()))
        else:
            self.current_text_field.insert(tk.INSERT, entry)

    def save_settings(self):
        """ Save the settings the user specified. """
        # (But first validate the user's requested values.)
        requested_freq = self.freq_value.get()
        requested_buffer = self.buffer_value.get()
        validation_message = self.controller.settings_object.valid(
            requested_freq, requested_buffer)
        if validation_message == "": # No errors were found so far.
            self.controller.frames[MpmeFolderPage].stop()
            self.current_settings['freq'] = requested_freq
            self.current_settings['channels'] = self.channels_value.get()
            self.current_settings['buffer'] = requested_buffer
            validation_message = \
                self.controller.settings_object.save_settings(
                    self.current_settings)
            self.controller.sound_object.set_settings(self.current_settings)
        if validation_message == "":
            # Presumably the save went without errors.
            self.message_label.config(text=self.SAVED_MESSAGE)
            self.successful_save = True
        else:
            self.message_label.config(text=validation_message)
            self.successful_save = False

    def restore(self):
        self.freq_value.set(
            self.controller.settings_object.default_freq())
        self.channels_value.set(
            self.controller.settings_object.default_channels())
        self.buffer_value.set(
            self.controller.settings_object.default_buffer())

    def leave_page(self):
        """ Leave the page, but first restore the message if appropriate. """
        if self.successful_save:
            self.message_label.config(text=self.INITIAL_MESSAGE)
        self.controller.show_frame(MpmeStartPage)

class MpmeRadioPage(tk.Frame):
    """ Class for the Radio page """

    def __init__(self, parent, controller):
        """ Initialize the page. """
        tk.Frame.__init__(self, parent)

        self.MINIMUM_FREQ = 87.5
        self.MAXIMUM_FREQ = 108.0

        self.controller = controller
        self.radio_freq_value = self.controller.settings_object.get_radio_freq()
        self.radio_volume = self.controller.settings_object.get_radio_volume()

        # When the user clicks on this button, call the
        # show_frame method to make the main screen appear.
        button_start = tk.Button(self, text='Start',
            command=lambda : self.controller.show_frame(MpmeStartPage))

        # This control displays the frequency.
        self.frequency_display = tk.Label(self,
            text=self.radio_freq_value, font=('', 16))

        # This control is for the radio volume.
        radio_volume_slider = VolumeSlider(self, from_=0, to=100,
            orient=tk.HORIZONTAL, label="VOLUME", length=290)
        radio_volume_slider.set(
            self.controller.settings_object.get_radio_volume())

        # This slide control can control the radio frequency.
        self.radio_freq_slider = RadioFreqSlider(self, from_=self.MINIMUM_FREQ,
            to=self.MAXIMUM_FREQ, resolution=0.1, length=290,
            orient=tk.HORIZONTAL, label='FREQUENCY',
            variable=self.radio_freq_value)
        self.radio_freq_slider.set(float(self.radio_freq_value))

        # These buttons can also change the radio frequency.
        scan_back = tk.Button(self, text='<< Scan',
                    command=lambda : self.scan(-.1))
        adjust_back = tk.Button(self, text='<',
                    command=lambda : self.adjust_freq(-.1))
        adjust_forward = tk.Button(self, text='>',
                    command=lambda : self.adjust_freq(.1))
        scan_forward = tk.Button(self, text='Scan >>',
                    command=lambda : self.scan(.1))

        # The preset buttons
        preset_1 = tk.Button(self, text=self.controller.settings_object.
            get_preset(1), command=lambda : self.preset(1))
        preset_2 = tk.Button(self, text=self.controller.settings_object.
            get_preset(2), command=lambda : self.preset(2))
        preset_3 = tk.Button(self, text=self.controller.settings_object.
            get_preset(3), command=lambda : self.preset(3))
        preset_4 = tk.Button(self, text=self.controller.settings_object.
            get_preset(4), command=lambda : self.preset(4))
        preset_5 = tk.Button(self, text=self.controller.settings_object.
            get_preset(5), command=lambda : self.preset(5))
        preset_6 = tk.Button(self, text=self.controller.settings_object.
            get_preset(6), command=lambda : self.preset(6))
        preset_7 = tk.Button(self, text=self.controller.settings_object.
            get_preset(7), command=lambda : self.preset(7))
        preset_8 = tk.Button(self, text=self.controller.settings_object.
            get_preset(8), command=lambda : self.preset(8))
        self.presets = [preset_1, preset_2, preset_3, preset_4,
                        preset_5, preset_6, preset_7, preset_8]

        # The controls to delete all presets
        delete_button = tk.Button(self, text='Delete all presets',
            command=lambda : self.confirm_delete())
        self.confirmation_label = tk.Label(self, text='Are you sure?')
        self.button_yes = tk.Button(self, text='Yes',
            command=lambda : self.delete_all_presets())
        self.button_no = tk.Button(self, text='No',
            command=lambda : self.hide_confirmation())

        # Specify the geometry to place the widgets.
        button_start.grid(row=1,column=1)
        self.frequency_display.grid(row=1, column=2)
        radio_volume_slider.grid(row=2, column=1, columnspan=4)
        self.radio_freq_slider.grid(row=3, column=1, columnspan=4)
        scan_back.grid(row=4, column=1)
        adjust_back.grid(row=4, column=2)
        adjust_forward.grid(row=4, column=3)
        scan_forward.grid(row=4, column=4)
        preset_1.grid(row=5, column=1)
        preset_2.grid(row=5, column=2)
        preset_3.grid(row=5, column=3)
        preset_4.grid(row=5, column=4)
        preset_5.grid(row=6, column=1)
        preset_6.grid(row=6, column=2)
        preset_7.grid(row=6, column=3)
        preset_8.grid(row=6, column=4)
        delete_button.grid(row=7, column=1, columnspan=4)

        # Start the simulated radio reception.
        self.radio_receiver = RadioReceiver(
            self.radio_freq_value, self.radio_volume)

    def start_reception(self):
        self.timer = RepeatedTimer(1, self.receive_signal)

    def receive_signal(self):
        """ Receive the simulated "radio signal". """
        # Do this by checking the file of stations that are "broadcasting".
        if self.radio_receiver.receiving_signal(self.radio_freq_value):
            # Indicate we're getting the signal with an * after the frequency.
            self.frequency_display.config(text=self.radio_freq_value + '*')
        else:
            self.frequency_display.config(text=self.radio_freq_value)

    # I need to look into this! This method can't be right!
    def stop_reception(self):
        """ Turn off the simulated "radio reception". """
        if hasattr(self, 'timer'):
            self.timer.stop()

    def change_radio_freq(self, freq):
        """ Change the radio frequency. """
        self.radio_freq_value = str(freq)
        self.frequency_display.config(text=self.radio_freq_value)
        self.receive_signal()
        self.controller.settings_object.save_radio_freq(self.radio_freq_value)

    def preset(self, preset):
        """ When the user hits a preset button do one of two things. If
            the button has no station assigned to it then assign it the
            current frequency. If it has one then change the station. """
        text = self.controller.settings_object.get_preset(preset)
        try:
            text = round(float(text), 1)
            preset_is_set = True
        except:
            preset_is_set = False
        if preset_is_set:
            self.change_radio_freq(text)
            self.radio_freq_slider.set(text)
        else:
            # Extract the preset number (from 1 to 8) from the button text.
            preset_number = preset
            # Write the frequency on the button.
            self.presets[preset_number-1].config(text=self.radio_freq_value)
            # Also, write that preset to the settings file.
            self.controller.settings_object.save_preset(
                preset_number, self.radio_freq_value)

    def scan(self, increment):
        """ Scan the radio (by -.1 or +.1) until it gets a signal. """
        getting_signal = False
        original_radio_freq_value = self.radio_freq_value
        while True:
            self.adjust_freq(increment)
            getting_signal = self.radio_receiver.receiving_signal(
                self.radio_freq_value)
            if getting_signal or \
               self.radio_freq_value == original_radio_freq_value:
                return

    def adjust_freq(self, increment):
        """ Adjust the radio frequency by "increment" (-.1 or +.1). """
        freq = round(float(self.radio_freq_value) + increment, 1)
        if freq > self.MAXIMUM_FREQ:
            freq = self.MINIMUM_FREQ
        elif freq < self.MINIMUM_FREQ:
            freq = self.MAXIMUM_FREQ
        self.change_radio_freq(freq)
        self.radio_freq_slider.set(freq)

    def change_volume(self, volume):
        """ Change the radio's audio volume. """
        self.radio_receiver.change_volume(volume)
        self.controller.settings_object.save_radio_volume(volume)

    def confirm_delete(self):
        """ Ask the user to confirm that (s)he
            wants to delete all the presets. """
        self.confirmation_label.grid(row=8, column=1, columnspan=2)
        self.button_yes.grid(row=8, column=3)
        self.button_no.grid(row=8, column=4)

    def hide_confirmation(self):
        """ Hide the confirmation question and the answer buttons. """
        self.confirmation_label.grid_forget()
        self.button_yes.grid_forget()
        self.button_no.grid_forget()

    def delete_all_presets(self):
        """ Wipe out all the radio station presets,
            leaving just Pre 1, Pre 2, etc """
        for i in range(len(self.presets)):
            self.presets[i].config(text='Pre ' + str(i+1))
            self.controller.settings_object.save_preset(
                i+1, 'Pre ' + str(i+1))
        self.hide_confirmation()
        
        
if __name__ == '__main__':
    app = Mpme()
    app.mainloop()
