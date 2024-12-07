import customtkinter as CTk
import os
from PIL import Image, ImageTk
import pygame
import time
import random
import json
from songsdata import songs_data
from artists import artists
import util_img
from config import *

CTk.set_default_color_theme("green")
CTk.set_appearance_mode("Dark")
class App(CTk.CTk):
    def __init__(self):
        super().__init__()
        #paths
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lyrics.json")
        with open(file_path, "r", encoding="utf-8") as file:
            self.lyrics_data=json.load(file)
        #main window configuration
        self.title("Spotify")
        self.geometry("1200x800")
        self.resizable(False, False)
        self.wm_iconbitmap(os.path.join(image_path,"spotify-logo.ico"))
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(1, weight=1)
        #init pygame
        pygame.mixer.init()
        #variables
        self.music_playing = False
        self.music_paused = False
        self.music_length = 0
        self.is_seeking = False
        self.start_time = 0
        self.paused_time = 0
        self.current_song = None
        self.current_playlist = None
        self.shuffle=False
        self.repeat=False
        self.shuffle_mode = False
        self.current_artist = None
        self.repeat_mode = False 
        self.current_song_path = None
        self.current_album_image = None
        self.current_artist_songs = None
        btn_width= 200 // 5
        btn_height= 200 // 5
        #images       
        self.logo_image = util_img.re_img("spotify_logo.png", (130,40))        
        self.image_icon_image = util_img.re_img("image_icon_light.png", (20, 20))
        self.home_image = CTk.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.chat_image = CTk.CTkImage(light_image=Image.open(os.path.join(image_path, "chat_dark.png")),
                                                dark_image=Image.open(os.path.join(image_path, "chat_light.png")), size=(20, 20))
        self.music_icon = util_img.re_img("music_icon.png", (100, 100))
        self.play_img = util_img.re_img("play.png", (25, 25))
        self.stop_img = util_img.re_img("stop.png", (25, 25))
        self.pause_img = util_img.re_img("pause.png", (25, 25))
        self.next_img = util_img.re_img("next.png", (25, 25))
        self.previous_img = util_img.re_img("previous.png", (25, 25))
        self.repeat_on_img = util_img.re_img("repeat_on.png", (25, 25))
        self.repeat_off_img = util_img.re_img("repeat_off.png", (25, 25))
        self.shuffle_on_img = util_img.re_img("shuffle_on.png", (25, 25))
        self.shuffle_off_img = util_img.re_img("shuffle_off.png", (25, 25))
        self.volume_on_img = util_img.re_img("volume_on.png", (25, 25))
        self.volume_off_img = util_img.re_img("volume_off.png", (25, 25))
        #navigation frame
        self.navigation_frame = CTk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = CTk.CTkLabel(self.navigation_frame, text="", image=self.logo_image, text_color=GREEN,
                                                        compound="left", font=CTk.CTkFont(size=30, family=FONT, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=10, pady=(20, 100), sticky="n")

        self.home_button = CTk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="HOME",
                                                font=CTk.CTkFont(size=20, family=FONT, weight="bold"),
                                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = CTk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="LYRICS",
                                                font=CTk.CTkFont(size=20, family=FONT, weight="bold"),
                                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                image=self.chat_image, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = CTk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="",
                                                    fg_color="transparent", text_color=("gray10", "gray90"), hover_color="",
                                                    anchor="w", command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, pady=(300, 0), sticky="ew")
        #home frame
        self.home_frame = CTk.CTkScrollableFrame(self, corner_radius=0, fg_color=BLACK, scrollbar_button_color=GREEN)
        self.home_frame.grid_columnconfigure(0, weight=1)

        for i, artist in enumerate(artists):

            label_artist = CTk.CTkLabel(self.home_frame, text=artist.upper(), font=CTk.CTkFont(size=18, family=FONT, weight="bold"))
            label_artist.grid(row=i*2, column=0, padx=20, pady=20, sticky="w")

            frame_artist = CTk.CTkScrollableFrame(self.home_frame, orientation="horizontal", fg_color=GRAY, scrollbar_button_color=GREEN,
                                                    width=900, height=200)
            frame_artist.grid(row=i*2+1, column=0, padx=20, pady=0, sticky="n")

            for j, (song_name, img_name, audio_path) in enumerate(songs_data[artist]):
                img_tk = util_img.re_img(img_name, (150, 150))

                song_button = CTk.CTkButton(
                    frame_artist, text="", image=img_tk, width=150, height=150, fg_color="transparent",
                    command=lambda path=audio_path, name=song_name, img=img_name, 
                    artist_songs=songs_data[artist]: self.play_song(path, name, img, artist_songs)
                )
                song_button.image = img_tk
                song_button.grid(row=0, column=j, padx=10, pady=0, sticky="w")

                song_label = CTk.CTkLabel(frame_artist, font=CTk.CTkFont(family=FONT, weight="bold"), text=song_name.upper(), width=150)
                song_label.grid(row=1, column=j, padx=0, pady=0, sticky="n")
        #lyrics frame
        self.second_frame = CTk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.second_frame.grid(sticky="nsew")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.info_label = CTk.CTkLabel(self.second_frame, text="Lyrics", font=CTk.CTkFont(size=30, family=FONT, weight="bold"))
        self.info_label.grid(row=0, column=0, padx=20, pady=10, sticky="n")

        self.music_icon_label = CTk.CTkLabel(self.second_frame, text="", width=500, height=500, image=self.music_icon)
        self.music_icon_label.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.music_name_label = CTk.CTkLabel(self.second_frame, text="name of music", font=CTk.CTkFont(size=30, family=FONT, weight="bold"))
        self.music_name_label.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        self.lyrics_frame = CTk.CTkScrollableFrame(self.second_frame, width = 420, height = 600)
        self.lyrics_frame.grid(row=0, rowspan = 3, column = 1, padx = (0,20), pady = (20,0), sticky = "e")

        self.lyrics_label = CTk.CTkLabel(self.lyrics_frame, text="LYRICS", font=CTk.CTkFont(family=FONT), width=400, height=580)
        self.lyrics_label.grid(row=0, column=0, sticky="nsew")
        #frame for navigation music
        self.song_navigation_frame = CTk.CTkFrame(self, corner_radius=0, height=100, bg_color='#1F1F1F', fg_color='#1F1F1F')
        self.song_navigation_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.song_navigation_frame.grid_columnconfigure(0, weight=1)
        self.song_navigation_frame.grid_rowconfigure(0, weight=1)
        
        self.album_cover = CTk.CTkButton(self.song_navigation_frame, text="", image=self.music_icon, fg_color="transparent", 
                                            text_color="white", anchor="center", width=110, height=110,
                                            command=self.info_song)
        self.album_cover.grid(row=0, column=0, columnspan=3, padx=0, pady=5, sticky="n")

        self.label_song_name = CTk.CTkLabel(self.song_navigation_frame, text='PLS CHOOSE ANY MUSIC',  font=CTk.CTkFont(family=FONT),)
        self.label_song_name.grid(row=1, column=0, columnspan=3, padx=0, pady=0, sticky="n")

        self.music_slider = CTk.CTkSlider(self.song_navigation_frame, from_=0, to=100, width=750, progress_color=GREEN, command=self.seek_music)
        self.music_slider.grid(row=1, column=3, columnspan=15, sticky="n")

        self.time_label = CTk.CTkLabel(self.song_navigation_frame, font=CTk.CTkFont(family=FONT), text="0:00 / 0:00", anchor="n")
        self.time_label.grid(row=1, column=18, columnspan=6, padx=0, pady=(0, 10), sticky="n")

        self.volume_slider = CTk.CTkSlider(self.song_navigation_frame, from_=0, to=1, width=150, progress_color=GREEN, command=self.adjust_volume)
        self.volume_slider.grid(row=0, column=20, columnspan=4, padx=10, pady=10, sticky="e")
        self.volume_slider.set(0.5) 

        self.shuffle_btn = CTk.CTkButton(self.song_navigation_frame, text="", image=self.shuffle_off_img, text_color="black", 
                                            fg_color="transparent", width=btn_width, height=btn_height, command=self.shuffle_song)
        self.shuffle_btn.grid(row=0, column=8, padx=0, pady=10, sticky="e")

        self.previous_btn = CTk.CTkButton(self.song_navigation_frame, text="", image=self.previous_img, text_color="black", 
                                            fg_color="transparent", width=btn_width, height=btn_height, command=self.play_previous_song)
        self.previous_btn.grid(row=0, column=9, padx=0, pady=10, sticky="e")
        
        self.play_pause_btn = CTk.CTkButton(self.song_navigation_frame, state="disable", text="", image=self.play_img, 
                                            fg_color="transparent", text_color="black", width=btn_width, height=btn_height, 
                                            command=self.play_pause_song)
        self.play_pause_btn.grid(row=0, column=10, padx=0, pady=10)

        self.next_btn = CTk.CTkButton(self.song_navigation_frame, text="", image=self.next_img, text_color="black", 
                                        fg_color="transparent", width=btn_width, height=btn_height, command=self.play_next_song)
        self.next_btn.grid(row=0, column=11, padx=0, pady=10, sticky="w")

        self.repeat_btn = CTk.CTkButton(self.song_navigation_frame, text="", image=self.repeat_off_img, text_color="black", 
                                        fg_color="transparent", width=btn_width, height=btn_height, command=self.repeat_song)
        self.repeat_btn.grid(row=0, column=12, padx=0, pady=10, sticky="w")

        self.volume_btn = CTk.CTkButton(self.song_navigation_frame, text="", image=self.volume_on_img, 
                                        fg_color="transparent", width=btn_width, height=btn_height, command=self.volume_on_off)
        self.volume_btn.grid(row=0, column=18, columnspan=2)
        #3rd frame
        self.third_frame = CTk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.third_frame.grid_columnconfigure(0, weight=1)

        self.secret_label = CTk.CTkLabel(self.third_frame, text="palauchort", font=CTk.CTkFont(family=FONT, weight="bold", size=50))
        self.secret_label.grid(pady=300, sticky="n")

        self.update_slider()
 
        # select default frame
        self.select_frame_by_name("home")

    def select_frame_by_name(self, name):

        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")
      
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "frame_2":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()
        if name == "frame_3":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")
   
    def frame_3_button_event(self):
        self.select_frame_by_name("frame_3")

    def play_song(self, path, song_name, img, artist_songs):

        music_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "songs")
        pygame.mixer.music.load(os.path.join(music_path, path))
        pygame.mixer.music.play()
        #Balausa<3
        self.music_length = pygame.mixer.Sound(os.path.join(music_path, path)).get_length()
        self.music_slider.configure(to=self.music_length)
        self.start_time = time.time()

        self.music_playing = True
        self.music_paused = False
        self.current_song = song_name
        self.current_song_path = path
        self.current_album_image = img
        self.current_artist_songs = artist_songs
        self.label_song_name.configure(text=song_name.upper())

        self.current_artist = next((artist for artist, songs in songs_data.items() if (song_name, img, path) in songs), None)
        lyrics = self.lyrics_data.get(self.current_artist, {}).get(song_name, "Lyrics not found.")

        self.lyrics_label.configure(text=lyrics)
        self.info_label.configure(text=self.current_artist.upper())

        album_img = util_img.re_img(img, (100,100))
        self.album_cover.configure(image=album_img)
        self.play_pause_btn.configure(image=self.pause_img, state="normal")

        album_img = util_img.re_img(img, (500, 500))
        self.music_icon_label.configure(image=album_img)
        self.music_name_label.configure(text=song_name.upper())

        self.update_slider()

    def play_next_song(self):
        if self.shuffle_mode:
            random_artist = random.choice(list(songs_data.keys()))
            random_song = random.choice(songs_data[random_artist])
            self.play_song(random_song[2], random_song[0], random_song[1], songs_data[random_artist])
        else:
            if self.current_song is None or not self.current_artist_songs:
                return

            current_index = next((i for i, song in enumerate(self.current_artist_songs) if song[0] == self.current_song), None)
            next_index = (current_index + 1) % len(self.current_artist_songs) if current_index is not None else 0
            next_song = self.current_artist_songs[next_index]
            self.play_song(next_song[2], next_song[0], next_song[1], self.current_artist_songs)

    def play_previous_song(self):

        if self.current_song is None or not self.current_artist_songs:
            return

        current_index = next((i for i, song in enumerate(self.current_artist_songs) if song[0] == self.current_song), None)

        if current_index is not None:
            previous_index = (current_index - 1) % len(self.current_artist_songs)
            previous_song = self.current_artist_songs[previous_index]
            self.play_song(previous_song[2], previous_song[0], previous_song[1], self.current_artist_songs)

    def update_slider(self):
        if self.music_playing and not self.music_paused and not self.is_seeking:
            current_time = time.time() - self.start_time
            self.music_slider.set(current_time)

            minutes, seconds = divmod(int(current_time), 60)
            total_minutes, total_seconds = divmod(int(self.music_length), 60)
            self.time_label.configure(text=f"{minutes}:{seconds:02d} / {total_minutes}:{total_seconds:02d}")

            if current_time >= self.music_length:
                if self.repeat_mode:
                    self.play_song(self.current_song_path, self.current_song, self.current_album_image, self.current_artist_songs)
                else:
                    self.play_next_song()

        self.after(250, self.update_slider)

    def seek_music(self, value):
        self.is_seeking = True
        pygame.mixer.music.pause()
        pygame.mixer.music.play(start=float(value))
        self.start_time = time.time() - float(value)
        self.is_seeking = False

    def play_pause_song(self):
        if self.music_playing:
            if not self.music_paused:
                pygame.mixer.music.pause()
                self.music_paused = True
                self.paused_time = time.time() - self.start_time 
                self.play_pause_btn.configure(image=self.play_img) 
            else:
                pygame.mixer.music.unpause()
                self.music_paused = False
                self.start_time = time.time() - self.paused_time 
                self.play_pause_btn.configure(image=self.pause_img)  
        else:
            pass

        if not self.music_paused:
            self.update_slider()

    def adjust_volume(self, value):
        pygame.mixer.music.set_volume(float(value))
        if value==0:
            self.volume_btn.configure(image=self.volume_off_img)
        else:
            self.volume_btn.configure(image=self.volume_on_img)

    def shuffle_song(self):
        self.shuffle_mode = not self.shuffle_mode
        self.shuffle_btn.configure(image=self.shuffle_on_img if self.shuffle_mode else self.shuffle_off_img)

    def repeat_song(self):
        self.repeat_mode = not self.repeat_mode
        self.repeat_btn.configure(image=self.repeat_on_img if self.repeat_mode else self.repeat_off_img)

    def volume_on_off(self):
        pass

    def info_song(self):
        self.select_frame_by_name("frame_2")

if __name__ == "__main__":
    app = App()
    app.mainloop()