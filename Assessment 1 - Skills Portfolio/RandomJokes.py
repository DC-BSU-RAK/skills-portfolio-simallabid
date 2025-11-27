import tkinter as tk
from tkinter import messagebox
import tkinter.font as font
import random
import os
import pygame

#colors used
COLOR_BACKGROUND = "#0F0F0F"   
COLOR_PRIMARY = "#00E5FF"  
COLOR_SECONDARY = "#FFEA00"   
COLOR_ACCENT_BUTTONS = "#FF3D00"
COLOR_TEXT_DARK = "#0F0F0F"     
COLOR_WHITE = "#FFFFFF"          

#CUSTOM FONT
CUSTOM_FONT_FAMILY = "Rampart One" 

class Emoji:  
    def __init__(self, canvas, image, x, y, speed_x, speed_y):
        self.canvas = canvas
        self.image = image
        self.id = self.canvas.create_image(x, y, image=self.image, anchor=tk.CENTER)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.size = 50 

    def move(self):
        self.canvas.move(self.id, self.speed_x, self.speed_y)
        x, y = self.canvas.coords(self.id)

        #Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        #Check bounds using coordinates and size
        if x + self.size/2 >= canvas_width or x - self.size/2 <= 0:
            self.speed_x *= -1
        if y + self.size/2 >= canvas_height or y - self.size/2 <= 0:
            self.speed_y *= -1

class JokeApp:
    def __init__(self, master):
        self.master = master
        master.title("Daily Dose of LOLs - Electric Neon")
        
        #Audio setup
        self.sound_enabled = False
        self.music_enabled = False
        self.bg_music_file = 'jokesbg.mp3'
        
        try:
            pygame.mixer.init()
            self.click_sound = pygame.mixer.Sound('clicks.mp3')
            self.laugh_sound = pygame.mixer.Sound('laugh.mp3')
            self.sound_enabled = True

            if os.path.exists(self.bg_music_file):
                pygame.mixer.music.load(self.bg_music_file)
                self.music_enabled = True
                self.play_background_music()
            
        except pygame.error as e:
            messagebox.showwarning("Audio Warning",
                                   "Could not load all audio files. Audio features disabled.")
            self.sound_enabled = False
            self.music_enabled = False
        
        #Custom font
        custom_font_file = 'RampartOne-Regular.ttf'
        try:
            if os.path.exists(custom_font_file):
                self.master.tk.call('lappend', 'auto_path', os.path.dirname(os.path.abspath(custom_font_file)))
        except Exception:
            pass 

        #Font definition
        try:
            self.font_title = font.Font(family=CUSTOM_FONT_FAMILY, size=60, weight='bold') 
            self.font_joke = font.Font(family=CUSTOM_FONT_FAMILY, size=40, weight='bold') 
            self.font_medium = font.Font(family=CUSTOM_FONT_FAMILY, size=28)
            self.font_button = font.Font(family=CUSTOM_FONT_FAMILY, size=24, weight='bold') 
            self.font_nav = font.Font(family=CUSTOM_FONT_FAMILY, size=18, weight='bold')
            self.font_header = font.Font(family=CUSTOM_FONT_FAMILY, size=30, weight='bold')
        except Exception:
            #Fallback
            self.font_title = font.Font(family='Arial', size=60, weight='bold')
            self.font_joke = font.Font(family='Arial', size=40, weight='bold')
            self.font_medium = font.Font(family='Arial', size=28)
            self.font_button = font.Font(family='Arial', size=24, weight='bold')
            self.font_nav = font.Font(family='Arial', size=18, weight='bold')
            self.font_header = font.Font(family='Arial', size=30, weight='bold')
        
        # GUI Setup
        master.geometry("800x600")
        master.minsize(500, 500)
        master.config(bg=COLOR_BACKGROUND) 
        
        self.file_path = 'randomJokes.txt'
        self.current_joke = None
        self.jokes = self.load_jokes()

        self.welcome_frame = tk.Frame(master, bg=COLOR_BACKGROUND)
        self.joke_frame = tk.Frame(master, bg=COLOR_BACKGROUND)

        self.emojis = []
        self.emoji_photos = [] 
        self.emoji_image_paths = ['laughing_emoji_1.png', 'laughing_emoji_2.png', 'laughing_emoji_3.png']

        self.create_welcome_page()
        self.create_joke_page()

        self.show_frame(self.welcome_frame)
        
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    #Audio Methods
    def on_closing(self):
        if self.music_enabled:
            pygame.mixer.music.stop()
        self.master.destroy()

    def play_background_music(self):
        if self.music_enabled:
            pygame.mixer.music.play(-1)

    def play_click(self):
        if self.sound_enabled:
            self.click_sound.play()

    def play_laugh(self):
        if self.sound_enabled:
            self.laugh_sound.play()
            
    #Frame Control
    def show_frame(self, frame):
        self.welcome_frame.pack_forget()
        self.joke_frame.pack_forget()
        frame.pack(fill=tk.BOTH, expand=True)
        
        if frame == self.joke_frame:
            self.play_click()
            self.show_setup()
            self.start_emoji_animation()
        else:
            self.stop_emoji_animation()

    #Welcome page
    def create_welcome_page(self):
        
        self.welcome_frame.config(bg=COLOR_BACKGROUND)
        
        # Header bar
        header_placeholder = tk.Frame(self.welcome_frame, bg=COLOR_SECONDARY, height=60)
        header_placeholder.pack(fill=tk.X)

        # Main Content Frame
        content_frame = tk.Frame(self.welcome_frame, bg=COLOR_BACKGROUND)
        content_frame.pack(expand=True, padx=40, pady=40)
        
        #Title
        title = tk.Label(content_frame, text="😂 DAILY DOSE\nOF LOLS 😂",
                             font=self.font_title, fg=COLOR_WHITE, bg=COLOR_BACKGROUND, 
                             justify=tk.CENTER)
        title.pack(pady=(20, 30))

        #Description
        description = tk.Label(content_frame, text="KICK START YOUR DAY WITH\nSIDE-SPLITTING, RANDOM HUMOR!",
                                 font=self.font_medium, fg=COLOR_WHITE, bg=COLOR_BACKGROUND, 
                                 justify=tk.CENTER, wraplength=450)
        description.pack(pady=20)

        #CTA
        cta = tk.Label(content_frame, text="READY FOR A COMEDY BREAK?",
                         font=self.font_medium, fg=COLOR_PRIMARY, bg=COLOR_BACKGROUND,
                         justify=tk.CENTER, wraplength=450)
        cta.pack(pady=(10, 50))

        #Button
        make_me_laugh_button = tk.Button(content_frame, text="MAKE ME LAUGH!",
                                             command=lambda: self.show_frame(self.joke_frame),
                                             font=self.font_button, bg=COLOR_PRIMARY, fg=COLOR_TEXT_DARK,
                                             activebackground=COLOR_SECONDARY, activeforeground=COLOR_TEXT_DARK,
                                             relief=tk.FLAT, padx=30, pady=15, borderwidth=0)
        make_me_laugh_button.pack(pady=20)
        make_me_laugh_button.config(width=20)

    #JOKE PAGE
    def create_joke_page(self):
        
        self.joke_frame.config(bg=COLOR_BACKGROUND)

        #Header Frame
        header_frame = tk.Frame(self.joke_frame, bg=COLOR_SECONDARY, height=70) 
        header_frame.pack(fill=tk.X)
        
        #Header Title
        header_title = tk.Label(header_frame, text="🤣 ALEXA TELL ME A JOKE 🤣",
                                 font=self.font_header, fg=COLOR_TEXT_DARK, bg=COLOR_SECONDARY)
        header_title.pack(expand=True, padx=20, pady=10) 

        #Quit Button
        quit_button = tk.Button(header_frame, text="QUIT", command=self.on_closing,
                                 font=self.font_button, fg=COLOR_WHITE, bg=COLOR_ACCENT_BUTTONS,
                                 activebackground=COLOR_PRIMARY, activeforeground=COLOR_TEXT_DARK,
                                 relief=tk.FLAT, padx=15, borderwidth=0)
        quit_button.place(relx=1.0, rely=0.5, anchor=tk.E, x=-20)


        #Main content area as a Canvas 
        self.content_canvas = tk.Canvas(self.joke_frame, bg=COLOR_BACKGROUND, highlightthickness=0)
        self.content_canvas.pack(fill=tk.BOTH, expand=True)

        #Label for the joke text
        self.joke_text_label = tk.Label(self.content_canvas, text="",
                                         font=self.font_joke, fg=COLOR_SECONDARY, bg=COLOR_BACKGROUND,
                                         wraplength=700, justify=tk.CENTER)
        self.joke_text_label.place(relx=0.5, rely=0.35, anchor=tk.CENTER) 

        #Q Mark Canvas Button
        self.q_mark_canvas = tk.Canvas(self.content_canvas, width=120, height=120, 
                                         bg=COLOR_BACKGROUND, highlightthickness=0)
        
        #Create a colored circle
        self.q_mark_oval = self.q_mark_canvas.create_oval(5, 5, 115, 115, 
                                                         fill=COLOR_PRIMARY, outline=COLOR_SECONDARY, width=3)
        #Text for '?'
        self.q_mark_text = self.q_mark_canvas.create_text(60, 60, text="?", 
                                                         font=(CUSTOM_FONT_FAMILY, 75, 'bold'), 
                                                         fill=COLOR_TEXT_DARK) 
        self.q_mark_canvas.bind("<Button-1>", self.show_punchline_event)
        self.q_mark_canvas.config(cursor="hand2")
        self.q_mark_canvas.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

        #Navigation Frame 
        nav_frame = tk.Frame(self.content_canvas, bg=COLOR_BACKGROUND)
        nav_frame.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        #Next Joke Button
        self.next_joke_button = tk.Button(nav_frame, text="NEXT JOKE", command=self.show_setup_with_click,
                                             font=self.font_button, fg=COLOR_WHITE, bg=COLOR_ACCENT_BUTTONS, 
                                             activebackground=COLOR_PRIMARY, activeforeground=COLOR_TEXT_DARK,
                                             relief=tk.FLAT, padx=20, pady=10, borderwidth=0,
                                             width=15)
        self.next_joke_button.pack(padx=10)

    #Emoji method. (took assistance from AI)
    def setup_emojis(self):
        self.emojis = []
        self.emoji_photos = [] 
        self.content_canvas.delete("all") 

        canvas_width = self.content_canvas.winfo_width()
        canvas_height = self.content_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return 
            
        target_size = 40 
        num_duplicates_per_emoji = 5 
            
        for path in self.emoji_image_paths:
            if os.path.exists(path):
                try:
                    original_photo = tk.PhotoImage(file=path)
                    
                    subsample_x = max(1, original_photo.width() // target_size)
                    subsample_y = max(1, original_photo.height() // target_size)
                    
                    resized_image = original_photo.subsample(subsample_x, subsample_y)
                    self.emoji_photos.append(resized_image) 

                    for _ in range(num_duplicates_per_emoji):
                        x = random.randint(target_size, canvas_width - target_size)
                        y = random.randint(target_size, canvas_height - target_size)
                        speed_x = random.choice([-1.5, -1, 1, 1.5]) 
                        speed_y = random.choice([-1.5, -1, 1, 1.5])
                        
                        self.emojis.append(Emoji(self.content_canvas, resized_image, x, y, speed_x, speed_y))
                    
                except tk.TclError as e:
                    print(f"Error loading image {path}: {e}")
            else:
                print(f"Warning: Emoji image file not found: {path}")

    def animate_emojis(self):
        for emoji in self.emojis:
            emoji.move()
        self.animation_job = self.master.after(50, self.animate_emojis) 

    def start_emoji_animation(self):
        if not self.emojis: 
            self.master.after(100, lambda: self._start_animation_after_setup())
        else:
            if hasattr(self, 'animation_job'):
                self.master.after_cancel(self.animation_job)
            self.animate_emojis()
            
    def _start_animation_after_setup(self):
        self.setup_emojis()
        if self.emojis:
            self.animate_emojis()

    def stop_emoji_animation(self):
        if hasattr(self, 'animation_job'):
            self.master.after_cancel(self.animation_job)
            del self.animation_job 
        
        for emoji in self.emojis:
            self.content_canvas.delete(emoji.id) 
        self.emojis = [] 
        self.emoji_photos = [] 

    #Joke logic
    def load_jokes(self):
        try:
            if not os.path.exists(self.file_path):
                messagebox.showerror("File Error",
                                     f"Joke file not found: '{self.file_path}'. Please ensure it exists.")
                return []
                
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            jokes_list = []
            for line in lines:
                line = line.strip()
                if line:
                    parts = line.split('?', 1) 
                    if len(parts) == 2:
                        setup = parts[0].strip()
                        punchline = parts[1].strip()
                        jokes_list.append((setup, punchline))
                        
            if not jokes_list:
                     messagebox.showwarning("No Jokes",
                                            f"The file '{self.file_path}' was read but contains no jokes in the expected format.")
                                            
            return jokes_list
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading jokes from the file: {e}")
            return []

    def get_random_joke(self):
        if self.jokes:
            self.current_joke = random.choice(self.jokes)
            return True
        return False
        
    def show_setup_with_click(self):
        self.play_click()
        self.show_setup()

    def show_setup(self):
        """Displays the setup text in Neon Yellow."""
        
        self.q_mark_canvas.place(relx=0.5, rely=0.65, anchor=tk.CENTER)
        self.q_mark_canvas.config(cursor="hand2")
        self.q_mark_canvas.itemconfigure(self.q_mark_oval, fill=COLOR_PRIMARY)
        self.q_mark_canvas.itemconfigure(self.q_mark_text, fill=COLOR_TEXT_DARK) 

        if self.get_random_joke():
            setup = self.current_joke[0]
            #Setup text in Neon Yellow
            self.joke_text_label.config(text=f"Q: {setup}?",
                                         font=self.font_joke, fg=COLOR_SECONDARY) 
        else:
            self.joke_text_label.config(text="NO JOKES FOUND. CHECK FILE.",
                                         font=self.font_medium, fg=COLOR_SECONDARY) 
            self.q_mark_canvas.place_forget()

    def show_punchline_event(self, event):
        self.play_click()
        self.show_punchline()

    def show_punchline(self):
        """Displays the punchline in Electric Cyan."""
        if self.current_joke:
            self.play_laugh()
            
            punchline = self.current_joke[1]
            
            full_text = self.joke_text_label.cget("text") + f"\n\nA: {punchline}"
            
            # Punchline in Electric Cyan
            self.joke_text_label.config(text=full_text,
                                         font=self.font_joke,
                                         fg=COLOR_PRIMARY,
                                         justify=tk.CENTER)
            
            self.q_mark_canvas.place_forget()


if __name__ == "__main__":
    if 'PYGAME_INITTED' not in os.environ:
        os.environ['PYGAME_INITTED'] = '1'
        
    root = tk.Tk()
    app = JokeApp(root)
    root.mainloop()