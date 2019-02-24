import os
from tkinter import *
from tkinter import filedialog
import tkinter.messagebox
from pygame import mixer
from mutagen.mp3 import MP3
import time
import threading


class Player:

    def __init__(self):
        self.paused = False
        self.music_stopped = True
        self.muted = False
        self.filename_path = None
        self.playlist = []              # full plath + filename

    def show_details(self, current_song):

        file_data = os.path.splitext(current_song)

        # Check if extension is mp3 or something else so total length of song cab be determined
        if file_data[1] == '.mp3':
            audio = MP3(current_song)
            total_length = audio.info.length
        else:
            a = mixer.sounds(current_song)
            total_length = a.get.length()

        # format the total length
        mins, secs = divmod(total_length, 60)
        timeformat = '{:02d}:{:02d}'.format(round(mins), round(secs))
        lengthLabel['text'] = "Total Length - " + timeformat

        # create new thread to continuously update current time of music track playing
        t1 = threading.Thread(target=self.start_count, args=(total_length, ))
        t1.start()

    def start_count(self, t):

        current_time = 0
        time.sleep(0.2)  # allow some time for music to play
        print('t =' + str(t) + ',  Music stopped = ' + str(self.music_stopped))
        while current_time <= t and not self.music_stopped:           # Returns False when we press stop button

            if self.paused:
                continue
            else:
                # print('Music player is busy')
                mins, secs = divmod(current_time, 60)
                timeformat = '{:02d}:{:02d}'.format(round(mins), round(secs))
                current_timeLabel['text'] = "Current Time - " + timeformat
                time.sleep(1)
                current_time += 1

    def play_music(self):

        if not self.paused:

            try:
                self.stop_music()   # Terminate show_details thread so a max. of one is ever running
                time.sleep(1)
                selected_song = playListBox.curselection()  # return a tuple containing index
                selected_song = int(selected_song[0])
                play_it = self.playlist[selected_song]

                mixer.music.load(play_it)
                mixer.music.play()
                player.show_details(play_it)
                self.music_stopped = False
                statusBar['text'] = 'Playing Music - ' + os.path.basename(play_it)
            except Exception as err:
                print('An exception in play_music has occurred: ' + str(err))
                tkinter.messagebox.showerror('File not found',
                                             'Groove could not find the file. Please choose a music file to play')
        else:
            mixer.music.unpause()
            self.paused = False
            statusBar['text'] = 'Playing Music - ' + os.path.basename(self.filename_path)

    def stop_music(self):
        mixer.music.stop()
        self.music_stopped = True
        statusBar['text'] = 'Music stopped'

    def pause_music(self):

        if not self.paused:
            mixer.music.pause()
            self.paused = True
            statusBar['text'] = 'Music paused'

        else:
            self.play_music()

    def rewind_music(self):
        self.play_music()
        statusBar['text'] = 'Music rewound'

    def mute_music(self):

        if self.muted:  # unmute the music
            mixer.music.set_volume(0.7)
            volumeBtn.configure(image=volumePhoto)
            scale.set(70)  # implement the default value of the volume slider
            self.muted = False
        else:           # mute the music
            mixer.music.set_volume(0)
            volumeBtn.configure(image=mutePhoto)
            scale.set(0)  # implement the default value of the volume slider
            self.muted = True

    def browse_file(self):

        self.filename_path = filedialog.askopenfilename()
        print(self.filename_path)
        self.add_to_playlist(self.filename_path)

    def add_to_playlist(self, file):

        playListBox.insert(END, os.path.basename(file))
        playListBox.pack()
        self.playlist.append(file)   # add to end of playlist

    def delete_song(self):

        selected_song = playListBox.curselection()  # return a tuple containing index
        selected_song = int(selected_song[0])
        playListBox.delete(selected_song)
        self.playlist.pop(selected_song)    # pop() removes song based on index rather than name

    @staticmethod
    def about_us():

        tkinter.messagebox.showinfo('About Groove', 'This is a music player built using python and tkinter')

    @staticmethod
    def set_volume(val):
        # val is set by the slider tkinter widget

        volume = int(val)/100   # mixer only takes value between 0 and 1
        mixer.music.set_volume(volume)


def on_closing():
    player.stop_music()
    root.destroy()


# Create Player object
player = Player()

# Create main window = contains status_bar, Left Frame, RightFrame
root = Tk()

# Create window frames
left_frame = Frame(root)  # Contains The listbox (playlist)
right_frame = Frame(root)  # Contains Top_frame, Middle_Frame and Bottom frame
top_frame = Frame(right_frame)
middle_frame = Frame(right_frame)  # Frame for play, stop and pause buttons
bottom_frame = Frame(right_frame)  # Frame for rewind, mute and volume slider


# Create Menu
menu_bar = Menu(root)
root.config(menu=menu_bar)

subMenu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Open", command=player.browse_file)
subMenu.add_command(label="Exit",  command=root.destroy)

# it appears we can re-use subMenu variable and re-assign it
subMenu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=subMenu)
subMenu.add_command(label="About Us", command=player.about_us)

# Initialise Mixer
mixer.init()

# Create and set the main window
root.title("Groove")
root.wm_iconbitmap(r'favicon.ico')

# Create Labels
# fileLabel = Label(root, text="Lets make some noise!")
lengthLabel = Label(top_frame, text='Total length : --:--')
current_timeLabel = Label(top_frame, text='current time : --:--', relief=GROOVE)

# Create and arrange widgets
playListBox = Listbox(left_frame)
playListBox.pack()

addButton = Button(left_frame, text="+ Add", command=player.browse_file)
addButton.pack(side='left')

deleteButton = Button(left_frame, text="- Delete", command=player.delete_song)
deleteButton.pack(side='left', padx=5)

playPhoto = PhotoImage(file='play-button.png')
playBtn = Button(middle_frame, image=playPhoto, command=player.play_music)
playBtn.grid(row=0, column=0, padx=10)

stopPhoto = PhotoImage(file='stop-button.png')
stopBtn = Button(middle_frame, image=stopPhoto, command=player.stop_music)
stopBtn.grid(row=0, column=1, padx=10)

pausePhoto = PhotoImage(file='pause-button.png')
pauseBtn = Button(middle_frame, image=pausePhoto, command=player.pause_music)
pauseBtn.grid(row=0, column=2, padx=10)

rewindPhoto = PhotoImage(file='rewind-button.png')
rewindBtn = Button(bottom_frame, image=rewindPhoto, command=player.rewind_music)
rewindBtn.grid(row=0, column=0, padx=2)

mutePhoto = PhotoImage(file='mute-button.png')
volumePhoto = PhotoImage(file='volume-button.png')
volumeBtn = Button(bottom_frame, image=volumePhoto, command=player.mute_music)
volumeBtn.grid(row=0, column=1)

# Create and set volume slider
scale = Scale(bottom_frame, from_=0, to=100, orient=HORIZONTAL, command=player.set_volume)
scale.set(70)  # set default slider and and volume
player.set_volume(70)
scale.grid(row=0, column=2, pady=15, padx=3)

statusBar = Label(root, text='Welcome to Groove', relief=SUNKEN, anchor=W)
statusBar.pack(side=BOTTOM, fill=X)

# Pack frames
left_frame.pack(side='left', padx=30)
right_frame.pack()
top_frame.pack()
middle_frame.pack(pady=30, padx=30)
bottom_frame.pack()
lengthLabel.pack(pady=5)
current_timeLabel.pack()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Keep main window displayed
root.mainloop()
