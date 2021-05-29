# MP3 Player
# Python 3.6
# The program was designed in Windows

import os
import sys
from threading import Thread
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
from tkinter import Tk, filedialog
from time import sleep
from datetime import timedelta
from sqldb import Database

QMediaPlayer = QtMultimedia.QMediaPlayer
QMediaPlaylist = QtMultimedia.QMediaPlaylist
QMediaContent = QtMultimedia.QMediaContent


class ListWidget(QtWidgets.QListWidget):
    ''' Class for the modified list widget, that is able to respond to right clicks '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):
        self.menu = QtWidgets.QMenu(self)
        renameAction = QtWidgets.QAction('Remove', self)
        renameAction.triggered.connect(lambda: self.remove(event))
        self.menu.addAction(renameAction)
        # add other required actions
        self.menu.popup(QtGui.QCursor.pos())
        # return super().contextMenuEvent(a0)

    def remove(self, event, *args, **kwargs):
        '''Removes the audio from the ui, all_audios and database'''

        # row = self.rowAt(event.pos().y())
        index = self.indexFromItem(self.itemAt(event.pos().x(), event.pos().y())).row()
        print('remove index: ', index)
        ui.delete_audio(index)  # To finish the deletion from the ui and database

class UiMainWindow(QtWidgets.QMainWindow):
    ''' Main class that builds the music player'''
    
    width = 15

    def __init__(self, *args, **kwargs):
        # Next we add the minimize and close buttons to the window

        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)

        # Initiating the music player
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist(self.player)
        self.player.mediaStatusChanged.connect(self.status_changed)
        self.player.stateChanged.connect(self.state_changed)
        self.player.positionChanged.connect(self.position_changed)
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
        self.restart_button = QtWidgets.QPushButton(self.centralwidget)
        self.next_button = QtWidgets.QPushButton(self.centralwidget)
        self.previous_button = QtWidgets.QPushButton(self.centralwidget)
        self.volume_slider = QtWidgets.QSlider(self.centralwidget)
        self.time_slider = QtWidgets.QSlider(self.centralwidget)
        self.time_label = QtWidgets.QLabel(self.centralwidget)
        self.time_length_label = QtWidgets.QLabel(self.centralwidget)
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.ui_song_list = ListWidget(self.centralwidget)

        self.current_audio = ''  # To prevent errors when trying to play nothing
        self.retranslate_ui(self)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.centralframe.addWidget(self.title)
        self.title.setFont(QtGui.QFont('Arial', 20))
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.set_box_frame(volume_frame)
        self.set_box_frame(button_frame)
        self.set_box_frame(timer_frame)

        # Linking functions to each button
        self.play_pause_button.clicked.connect(self.play_pause_song)
        self.stop_button.clicked.connect(self.stop_song)
        self.add_new_song_button.clicked.connect(self.add_song)
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

        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(100)
        volume_frame.addWidget(self.volume_slider, alignment=QtCore.Qt.AlignLeft)
        self.volume_slider.setOrientation(QtCore.Qt.Horizontal)
        self.volume_slider.valueChanged.connect(self.set_volume)

        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(100)
        self.time_slider.setValue(0)
        self.time_slider.setSingleStep(1)
        self.time_slider.setOrientation(QtCore.Qt.Horizontal)
        self.time_slider.sliderMoved.connect(self.slider_moved)
        timer_frame.addWidget(self.time_label)
        timer_frame.addWidget(self.time_slider)
        timer_frame.addWidget(self.time_length_label)

        icon_path = os.path.join('.', 'images/note.png')
        self.icon = QtGui.QIcon(icon_path)
        self.duration = 0
        self.ui_song_list.setEnabled(True)
        self.ui_song_list.setStyleSheet('background-color: lightgray;')
        self.ui_song_list.itemClicked.connect(self.audio_clicked)  # This function will be called when an audio gets clicked
        self.centralframe.addWidget(self.ui_song_list)  # Adding the audio list widget to the interface
        self.get_saved_music()  # Adding all the previously saved music
        self.show()

    def set_box_frame(self, frame, *args, **kwargs):
        '''For creating the main frames'''
        widget = QtWidgets.QWidget()
        widget.setLayout(frame)
        self.centralframe.addWidget(widget)

    def add_image(self, list_widget, text, icon, *args, **kwargs):
        '''Adds the image to each added song'''
        item = QtWidgets.QListWidgetItem(icon, text)  # Making a list item with both an image and song
        size = QtCore.QSize()
        size.setHeight(100)
        item.setSizeHint(size)
        list_widget.addItem(item)

    def status_changed(self, *args, **kwargs):
        ''' Signal method triggered when the player status changes ex. noMedia -> Media '''
        pass

    def state_changed(self, *args, **kwargs):
        ''' Signal method triggered when the player state changes ex. playing -> stopped '''
        pass
        
    def position_changed(self, pos, is_playing=True, *args, **kwargs):
        '''This is called when the player emits audio'''
        if is_playing == True:  # The explicit way
            if self.duration != self.player.duration():
                self.duration = self.player.duration()
                self.time_slider.setMaximum(self.duration)
            self.time_slider.setValue(pos)
        # The position() method returns miliseconds, so we convert them to seconds
        current_time = str(timedelta(seconds=self.player.position()//1000))
        length = str(timedelta(seconds=self.player.duration()//1000))

        self.time_label.setText(str(current_time))
        self.time_length_label.setText(str(length))

    def add_to_playlist(self, audio_path, *args, **kwargs):
        ''' Adds the audio with the given path to the playlist '''
        media = QMediaContent(QtCore.QUrl(audio_path))
        self.playlist.addMedia(media)

    def get_saved_music(self, *args, **kwargs):
        '''Adds the songs that are in the database'''
        audios = database.extract_audio()
        if isinstance(audios, list):  # If there are more songs
            for name, path in audios:
                self.add_image(self.ui_song_list, name, self.icon)
                self.add_to_playlist(path)
        # Updating
        self.audio_widgets = self.ui_song_list.findItems('', QtCore.Qt.MatchContains)
        self.all_audios = list(map(lambda x: x.text(), self.audio_widgets))  # Extracting audio names

    def delete_audio(self, index):
        self.player.stop()
        # if there was any audio in the playlist
        mediapath = self.playlist.currentMedia().canonicalUrl().fileName()
        curmedia = self.convert_filename(mediapath)
        if self.playlist.removeMedia(index):
            database.delete_audio(curmedia)
            self.all_audios.remove(curmedia)
            # Next, removing from the GUI list
            self.ui_song_list.takeItem(index)

    def audio_clicked(self, selected_audio, *args, **kwargs):
        '''This is called when a song is clicked'''
        self.state = 1
        current_audio = selected_audio.text()  # Setting the new audio
        print('current:', current_audio)
        self.player.stop()  
        audio_index = self.ui_song_list.currentIndex().row()
        print('index:', audio_index)         
        self.playlist.setCurrentIndex(audio_index)
        self.player.play()

    def play_pause_song(self, *args, **kwargs):
        '''The event for the 'Pause' button'''
        if not self.player.currentMedia():  # If no audio is chosen, just the first one
            self.default_song()  # This calls/plays the first audio
        else:
            if self.player.state() == QMediaPlayer.PlayingState:  # If any sound is playing
                self.player.pause()
                self.state = 0
                self.play_pause_button.setText('Play')  # Button caption

            else:
                self.play_pause_button.setText('Pause')  # Button caption
                self.state = 1
                self.player.play()

    def stop_song(self, *args, **kwargs):
        '''Stops the current playing audio'''
        self.state = 0
        self.player.stop()
        self.play_pause_button.setText('Play')  # 'Play' button caption

    def previous_song(self, *args, **kwargs):
        '''Plays the previous song, in the order it was added'''
        print(self.playlist.previous())

    def next_song(self, *args, **kwargs):
        '''Plays the next audio'''
        playlist = self.player.playlist()
        playlist.next()

    def restart_song(self, *args, **kwargs):
        '''Restarts the player'''
        self.stop_song()
        self.player.play()  # Replay

    def add_song(self, *args, **kwargs):
        '''Asks for mp3 and wav files then adds them to db and ui'''
        Tk().withdraw()  # Creating the interface for choosing songs
        filetypes = [('mp3 files', '*.mp3'), ('wav files', '*.wav')]  # Only audio should pe added
        audios_list = filedialog.askopenfilenames(title='Choose audio files', filetypes=filetypes)
        for audio_path in audios_list:
            audio_name = self.convert_filename(audio_path)
            self.all_audios.append(audio_name)
            self.add_to_playlist(audio_path)
            # Updating
            self.add_image(self.ui_song_list, audio_name, self.icon)
            database.insert_in_table((audio_name, audio_path))  # Inserting the audio

    def slider_moved(self, pos, *args, **kwargs):
        ''' This is called when the user moves the slider '''
        if self.player.isSeekable():
            self.player.setPosition(pos)

    def default_song(self, *args, **kwargs):
        ''' Assigns the first song of the list '''
        try:  # Can raise an exception if no music was added
            self.current_audio = self.all_audios[0].text()
            self.ui_song_list.setCurrentItem(self.all_audios[0])
            self.audio_clicked(self.all_audios[0])
        except IndexError:
            pass  # Do nothing if buttons are clicked, while there are no songs

    def set_volume(self, pos, *args, **kwargs):
        self.player.setVolume(pos)

    def retranslate_ui(self, main_window, *args, **kwargs):
        ''' Setting the text for all the buttons and labels '''
        main_window.setCentralWidget(self.centralwidget)
        main_window.setWindowTitle("MP3 Player")
        self.play_pause_button.setText("Play")
        self.stop_button.setText("Stop")
        self.add_new_song_button.setText("Add Songs")
        self.restart_button.setText("Restart")
        self.next_button.setText("Next")
        self.previous_button.setText("Previous")
        self.time_label.setText('0:00:00')
        self.time_length_label.setText('0:00:00')
        self.title.setText("MP3 Player")
        # self.volume_label.setText("Volume")

    @staticmethod
    def convert_filename(path):
        ''' Converts file path to file name without extension '''
        pathpart, ext = os.path.splitext(path)  # taking only the audio path without the extension
        audio_name = os.path.basename(pathpart)
        return audio_name

if __name__ == "__main__":
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
