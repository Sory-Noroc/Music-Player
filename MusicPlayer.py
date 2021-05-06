# MP3 Player
# Python 3.6
# The program was designed in Windows

import os
from threading import Thread
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
from tkinter import Tk, filedialog
from time import sleep
from datetime import timedelta
from sqldb import Database

QMediaPlayer = QtMultimedia.QMediaPlayer
QMediaPlaylist = QtMultimedia.QMediaPlaylist
QMediaContent = QtMultimedia.QMediaContent


class UiMainWindow(QtWidgets.QMainWindow):
    ''' Main class that builds the music player'''
    
    width = 15

    def __init__(self):
        # Next we add the minimize and close buttons to the window

        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)

        # Initiating the music player
        self.playlist = QMediaPlaylist()
        self.player = QMediaPlayer()
        self.player.mediaStatusChanged.connect(self.status_changed)
        self.player.stateChanged.connect(self.state_changed)
        self.player.positionChanged.connect(self.position_changed)
        self.player.volumeChanged.connect(self.volume_changed)
        self.player.setVolume(60)
        self.player.setPlaylist(self.playlist)
        self.state = None  # -1 -> stopped; 0 -> paused; 1 -> playing;

        # Initializing the GUI
        self.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(self)

        # Initiating the frames, buttons and labels
        self.centralframe = QtWidgets.QVBoxLayout()
        self.centralwidget.setLayout(self.centralframe)

        button_frame = QtWidgets.QHBoxLayout()
        timer_frame = QtWidgets.QHBoxLayout()
        volume_frame = QtWidgets.QHBoxLayout()

        self.play_pause_button = QtWidgets.QPushButton(self.centralwidget)
        self.stop_button = QtWidgets.QPushButton(self.centralwidget)
        self.add_new_song_button = QtWidgets.QPushButton(self.centralwidget)
        self.remove_song_button = QtWidgets.QPushButton(self.centralwidget)
        self.restart_button = QtWidgets.QPushButton(self.centralwidget)
        self.next_button = QtWidgets.QPushButton(self.centralwidget)
        self.previous_button = QtWidgets.QPushButton(self.centralwidget)
        self.volume_slider = QtWidgets.QSlider(self.centralwidget)
        self.checkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.time_slider = QtWidgets.QSlider(self.centralwidget)
        self.timer = QtCore.QTimer(self.centralwidget) 
        self.time_label = QtWidgets.QLabel(self.centralwidget)
        self.time_length_label = QtWidgets.QLabel(self.centralwidget)
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.ui_song_list = QtWidgets.QListWidget(self.centralwidget)

        self.current_audio = ''  # To prevent errors when trying to play nothing
        self.audio_paths = {}  # This will be needed when running the audio
        self.retranslate_ui(self)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.centralframe.addWidget(self.title)
        self.title.setFont(QtGui.QFont('Arial', 20))
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.set_box_frame(volume_frame)
        self.set_box_frame(button_frame)
        self.set_box_frame(timer_frame)

        #  self.play_pause_song is the function that is linked to that button
        self.play_pause_button.clicked.connect(self.play_pause_song)
        self.stop_button.clicked.connect(self.stop_song)
        self.add_new_song_button.clicked.connect(self.add_song)
        self.remove_song_button.clicked.connect(self.remove_song)
        self.restart_button.clicked.connect(self.restart_song)
        self.next_button.clicked.connect(self.next_song)
        self.previous_button.clicked.connect(self.previous_song)

        # Adding the buttons in the order of their appearance
        button_frame.addWidget(self.add_new_song_button)
        button_frame.addWidget(self.stop_button)
        button_frame.addWidget(self.previous_button)
        button_frame.addWidget(self.play_pause_button)
        button_frame.addWidget(self.next_button)
        button_frame.addWidget(self.restart_button)
        button_frame.addWidget(self.remove_song_button)

        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(100)
        volume_frame.addWidget(self.volume_slider, alignment=QtCore.Qt.AlignLeft)
        self.volume_slider.setOrientation(QtCore.Qt.Horizontal)
        self.volume_slider.valueChanged.connect(self.volume)

        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(10000)
        self.time_slider.setValue(0)
        self.time_slider.setSingleStep(1)
        self.time_slider.setOrientation(QtCore.Qt.Horizontal)
        self.time_slider.sliderMoved.connect(self.slider_moved)
        timer_frame.addWidget(self.time_label)
        timer_frame.addWidget(self.time_slider)
        timer_frame.addWidget(self.time_length_label)

        self.checkbox.stateChanged.connect(self.auto_play)
        volume_frame.addWidget(self.checkbox, alignment=QtCore.Qt.AlignRight)

        self.timer.timeout.connect(self.time_hit) 
        self.timer.start(400)

        icon_path = os.path.join('.', 'images/note.png')
        self.icon = QtGui.QIcon(icon_path)
        self.ui_song_list.setEnabled(True)
        self.ui_song_list.setStyleSheet('background-color: lightgray;')
        self.ui_song_list.itemClicked.connect(self.play_song)  # This function will be called when an audio gets clicked
        self.centralframe.addWidget(self.ui_song_list)  # Adding the audio list widget to the interface
        self.get_saved_music()  # Adding all the previously saved music
        self.show()

    def set_box_frame(self, frame):
        '''For creating the main frames'''
        widget = QtWidgets.QWidget()
        widget.setLayout(frame)
        self.centralframe.addWidget(widget)

    def add_image(self, list_widget, text, icon):
        '''Adds the image to each added song'''
        item = QtWidgets.QListWidgetItem(icon, text)  # Making a list item with both an image and song
        size = QtCore.QSize()
        size.setHeight(100)
        item.setSizeHint(size)
        list_widget.addItem(item)

    def status_changed(self):
        pass

    def state_changed(self):
        pass
        
    def position_changed(self, pos, stype=False):
        pass

    def volume_changed(self):
        pass

    def get_saved_music(self):
        '''Adds the songs that are in the database'''
        audios = database.extract_audio()
        if isinstance(audios, list):  # If there are more songs
            for name, path in audios:
                self.add_image(self.ui_song_list, name, self.icon)
                self.audio_paths[name] = path
                media = list(map(lambda x:QMediaContent(QtCore.QUrl(x)), self.audio_paths.values()))
                self.playlist.addMedia(media)
        # Updating
        self.audio_widgets = self.ui_song_list.findItems('', QtCore.Qt.MatchContains)
        self.all_audios = list(map(lambda x: x.text(), self.audio_widgets))  # Extracting audio names

    def play_song(self, selected_audio):
        '''This is called when a song is clicked'''
        print('play_song::', selected_audio)
        self.state = 1
        self.current_audio = selected_audio.text()  # Setting the new audio
        self.player.stop()  
        audio_index = self.all_audios.index(self.current_audio)          
        self.playlist.setCurrentIndex(audio_index)
        self.player.play()

    def play_pause_song(self):
        '''The event for the 'Pause' button'''
        if not self.current_audio:  # If no audio is chosen, just the first one
            self.default_song()  # This calls/plays the first audio
        else:
            if self.player.state() == QMediaPlayer.PlayingState:  # If any sound is playing
                self.player.pause()
                self.paused = True
                self.play_pause_button.setText('Play')  # Button caption

            else:
                self.play_pause_button.setText('Pause')  # Button caption
                self.paused = False
                self.player.play()

    def stop_song(self):
        '''Stops the current playing audio'''
        self.state = 0
        self.player.stop()
        self.play_pause_button.setText('Play')  # 'Play' button caption

    def previous_song(self):
        '''Plays the previous song, in the order it was added'''

        playlist = self.player.playlist()
        playlist.previous()

    def next_song(self):
        '''Plays the next audio'''

        playlist = self.player.playlist()
        playlist.next()

    def restart_song(self):
        '''Restarts the player'''
        self.stop_song()
        self.player.play()  # Replay

    def remove_song(self):
        '''Removes the audio from the ui and database'''
        self.player.stop()
        for audio in self.all_audios:
            if audio == self.current_audio:
                database.delete_audio(self.current_audio)
                self.audio_paths.pop(self.current_audio)
                self.all_audios.remove(audio)
                # Next, removing from the GUI list
                self.ui_song_list.takeItem(self.ui_song_list.currentRow())
                break

    def add_song(self):
        '''Asks for mp3 and wav files then adds them to db and ui'''
        Tk().withdraw()  # Creating the interface for choosing songs
        filetypes = [('mp3 files', '*.mp3'), ('wav files', '*.wav')]  # Only audio should pe added
        audios_list = filedialog.askopenfilenames(title='Choose audio files', filetypes=filetypes)
        for audio_path in audios_list:
            path, ext = os.path.splitext(audio_path)  # taking only the audio path without the extension
            audio_name = os.path.basename(path)                                                                                                                                                                                                                                                   
            self.audio_paths[audio_name] = audio_path
            self.add_image(self.ui_song_list, audio_name, self.icon)
            database.insert_in_table((audio_name, audio_path))  # Inserting the audio
        self.all_songs = self.ui_song_list.findItems('', QtCore.Qt.MatchContains)

    def time_hit(self):
        '''This tracks and updates the time of the song and it's length'''
        if self.player.state() == QMediaPlayer.PlayingState:
            length = str(timedelta(seconds=self.player.duration() // 1000))  # miliseconds to seconds
            current_time = str(timedelta(seconds = self.player.position() // 1000))
            self.time_label.setText(str(current_time))
            self.time_length_label.setText(str(length))

            self.time_slider.setValue(self.player.position()*10000) # update slide bar
        else:
            sleep(1)

    def slider_moved(self, pos):
        '''This is called when the user moves the slider'''                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
        self.player.setPosition(pos)

    def slider_changed(self, pos):
        '''This is called when the song time slider is moved'''
        if self.player.state() == QMediaPlayer.PlayingState:  # If any song is playing
            self.time_slider.setValue(position)
            self.player.set_position(self.time_slider.value()/10000)

    def volume(self, _=None):  # _ is an unused argument that is passed
        self.player.audio_set_volume(self.volume_slider.value())

    def auto_play(self):
        '''When it is chosen to play automatically the next song'''
        if self.checkbox.isChecked():  # If you chose it
            self.auto_next = True  # This is going to control the checking thread
            if not self.checking_thread:  # To avoid playing multiple songs at once when spamming next/previous button
                self.checking_thread = Thread(target=self.check_playing)
                self.checking_thread.setDaemon(True)  # The thread will finish with the program
                self.checking_thread.start()
        else:  # If you chose not to play automatically next song
            self.auto_next = False  # Kill the thread that checks

    def check_playing(self):
        '''A thread function that will play the next song when the current one is done'''
        while self.auto_next:
            if self.checkbox.isChecked():
                if self.player.state() == QMediaPlayer.PlayingState or self.paused:
                    sleep(1)  # To have a slight delay
                else:
                    self.next_song()
                    sleep(2)
                    self.check_playing()
            else:
                self.player.stop()
                break

    def default_song(self):
        '''Assigns the first song of the list'''
        try:  # Can raise an exception if no music was added
            self.current_audio = self.all_audios[0].text()
            self.ui_song_list.setCurrentItem(self.all_audios[0])
            self.play_song(self.all_audios[0])
        except IndexError:
            pass  # Do nothing if buttons are clicked, while there are no songs

    def retranslate_ui(self, main_window):
        '''Setting the text for all the buttons and labels'''
        main_window.setCentralWidget(self.centralwidget)
        main_window.setWindowTitle("MP3 Player")
        self.play_pause_button.setText("Play")
        self.stop_button.setText("Stop")
        self.add_new_song_button.setText("Add Songs")
        self.remove_song_button.setText("Remove")
        self.restart_button.setText("Restart")
        self.next_button.setText("Next")
        self.previous_button.setText("Previous")
        self.checkbox.setText("Autoplay")
        self.time_label.setText('0:00:00')
        self.time_length_label.setText('0:00:00')
        self.title.setText("MP3 Player")
        # self.volume_label.setText("Volume")

if __name__ == "__main__":
    import sys
    database = Database(os.path.abspath('music_database.db'))  # Creating/opening the database file
    app = QtWidgets.QApplication(sys.argv)
    # Creating the app background, with an image
    app.setStyleSheet("""
    QMainWindow {
        background-image: url("images/bg.jpg"); 
        background-repeat: no-repeat; 
        background-position: center;
    }
""")
    ui = UiMainWindow()
    sys.exit(app.exec_())
