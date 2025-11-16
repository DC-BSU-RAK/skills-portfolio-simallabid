import tkinter as tk
from tkinter import messagebox
import tkinter.font as font
import random
import os
import pygame

# --- NEW VIBRANT COLOR PALETTE ---
COLOR_BACKGROUND = "#FFFACD"  # Bright Light Yellow
COLOR_ACCENT = "#00BFFF"      # Vibrant Electric Blue
COLOR_DARK_TEXT = "#8B008B"   # Rich Magenta (used for setup/title)
COLOR_WHITE = "#FFFFFF"       # High contrast white

# --- FONT FAMILY NAME ---
CUSTOM_FONT_FAMILY = "Londrina Shadow"

# The JokeApp expects 'randomJokes.txt', sound files, and emoji images in the same folder.
# REQUIRED EMOJI IMAGE FILES: 'laughing_emoji_1.png', 'laughing_emoji_2.png', 'laughing_emoji_3.png'

class Emoji:
    """
    Represents a single floating emoji, initialized with a pre-loaded PhotoImage object.
    """
    def __init__(self, canvas, image, x, y, speed_x, speed_y):
        self.canvas = canvas
        self.image = image  # Expects a PhotoImage object
        
        # Create the image item on the canvas
        self.id = self.canvas.create_image(x, y, image=self.image, anchor=tk.CENTER)
        self.speed_x = speed_x
        self.speed_y = speed_y

    def move(self):
        """Moves the emoji and handles boundary collisions."""
        self.canvas.move(self.id, self.speed_x, self.speed_y)
        x1, y1, x2, y2 = self.canvas.bbox(self.id)

        # Get canvas dimensions (must be called when canvas is fully rendered)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Reverse direction if hitting horizontal boundary
        if x2 >= canvas_width or x1 <= 0:
            self.speed_x *= -1 
        # Reverse direction if hitting vertical boundary
        if y2 >= canvas_height or y1 <= 0:
            self.speed_y *= -1 

class JokeApp:
    def __init__(self, master):
        self.master = master
        master.title("Daily Dose of LOLs")

        # --- PYGAME INITIALIZATION FOR SOUND & MUSIC ---
        self.sound_enabled = False
        self.music_enabled = False
        self.bg_music_file = 'jokesbg.mp3'
        
        try:
            pygame.mixer.init()
            print("Pygame mixer initialized.")
            
            self.click_sound = pygame.mixer.Sound('clicks.mp3')
            self.laugh_sound = pygame.mixer.Sound('laugh.mp3')
            print("Sound files loaded successfully.")
            self.sound_enabled = True

            if os.path.exists(self.bg_music_file):
                pygame.mixer.music.load(self.bg_music_file)
                print(f"Background music '{self.bg_music_file}' loaded.")
                self.music_enabled = True
                self.play_background_music()
            else:
                print(f"Background music file not found: '{self.bg_music_file}'. Music disabled.")

        except pygame.error as e:
            print(f"Error initializing Pygame or loading sounds/music: {e}")
            messagebox.showwarning("Audio Warning",
                                   "Could not load all audio files. Audio features disabled.")
            self.sound_enabled = False
            self.music_enabled = False
        # ----------------------------------------

        # --- Define Custom Fonts ---
        try:
            self.font_large = font.Font(family=CUSTOM_FONT_FAMILY, size=28, weight='bold')
            self.font_title = font.Font(family=CUSTOM_FONT_FAMILY, size=40, weight='bold')
            self.font_medium = font.Font(family=CUSTOM_FONT_FAMILY, size=18)
            self.font_button = font.Font(family=CUSTOM_FONT_FAMILY, size=16, weight='bold')
            self.font_nav = font.Font(family=CUSTOM_FONT_FAMILY, size=12, weight='bold')
            self.font_header = font.Font(family=CUSTOM_FONT_FAMILY, size=18, weight='bold')
        except Exception:
            print(f"Warning: Could not load custom font '{CUSTOM_FONT_FAMILY}'. Falling back to Arial.")
            self.font_large = font.Font(family='Arial', size=28, weight='bold')
            self.font_title = font.Font(family='Arial', size=40, weight='bold')
            self.font_medium = font.Font(family='Arial', size=18)
            self.font_button = font.Font(family='Arial', size=16, weight='bold')
            self.font_nav = font.Font(family='Arial', size=12, weight='bold')
            self.font_header = font.Font(family='Arial', size=18, weight='bold')
        
        master.geometry("800x600")
        master.minsize(400, 400)
        
        self.file_path = 'randomJokes.txt'
        self.current_joke = None
        self.jokes = self.load_jokes()

        # --- Frames for different "pages" using the new colors ---
        self.welcome_frame = tk.Frame(master, bg=COLOR_BACKGROUND)
        self.joke_frame = tk.Frame(master, bg=COLOR_BACKGROUND)

        # Emoji lists (for animation and persistence)
        self.emojis = []
        self.emoji_photos = [] # CRITICAL: Stores PhotoImage objects to prevent garbage collection
        self.emoji_image_paths = ['laughing_emoji_1.png', 'laughing_emoji_2.png', 'laughing_emoji_3.png']

        self.create_welcome_page()
        self.create_joke_page()

        self.show_frame(self.welcome_frame)
        
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Stops music and closes the application."""
        if self.music_enabled:
            pygame.mixer.music.stop()
        self.master.destroy()

    def play_background_music(self):
        """Starts playing the loaded background music in a loop."""
        if self.music_enabled:
            pygame.mixer.music.play(-1)
            print("Background music started.")

    def play_click(self):
        """Plays the click sound."""
        if self.sound_enabled:
            self.click_sound.play()

    def play_laugh(self):
        """Plays the laugh sound."""
        if self.sound_enabled:
            self.laugh_sound.play()
            
    def show_frame(self, frame):
        """Hides all frames and shows the selected frame."""
        self.welcome_frame.pack_forget()
        self.joke_frame.pack_forget()
        frame.pack(fill=tk.BOTH, expand=True)
        
        if frame == self.joke_frame:
            self.play_click()
            self.show_setup()
            # Start emoji animation when entering joke page
            self.start_emoji_animation()
        else:
            # Stop emoji animation when leaving joke page
            self.stop_emoji_animation()


    def create_welcome_page(self):
        """Configures the welcome page."""
        
        self.welcome_frame.config(bg=COLOR_BACKGROUND)
        
        header_placeholder = tk.Frame(self.welcome_frame, bg=COLOR_ACCENT, height=30)
        header_placeholder.pack(fill=tk.X)

        title = tk.Label(self.welcome_frame, text="Your Daily Dose\nof LOLs",
                             font=self.font_title, fg=COLOR_DARK_TEXT, bg=COLOR_BACKGROUND,
                             justify=tk.CENTER)
        title.pack(pady=(60, 30))

        description = tk.Label(self.welcome_frame, text="Kick start every day with\nside-splitting jokes.",
                                 font=self.font_medium, fg=COLOR_DARK_TEXT, bg=COLOR_BACKGROUND,
                                 justify=tk.CENTER, wraplength=500)
        description.pack(pady=20)

        cta = tk.Label(self.welcome_frame, text="Ready for a comedy break?",
                         font=self.font_medium, fg=COLOR_ACCENT, bg=COLOR_BACKGROUND,
                         justify=tk.CENTER, wraplength=500)
        cta.pack(pady=(20, 80))

        make_me_laugh_button = tk.Button(self.welcome_frame, text="MAKE ME LAUGH",
                                             command=lambda: self.show_frame(self.joke_frame),
                                             font=self.font_button, bg=COLOR_ACCENT, fg=COLOR_WHITE,
                                             relief=tk.FLAT, padx=30, pady=10, borderwidth=0)
        make_me_laugh_button.pack(pady=20)
        make_me_laugh_button.config(width=20)

    def create_joke_page(self):
        """Configures the joke display page."""
        
        self.joke_frame.config(bg=COLOR_BACKGROUND)

        header_frame = tk.Frame(self.joke_frame, bg=COLOR_ACCENT, height=50)
        header_frame.pack(fill=tk.X)
        
        header_title = tk.Label(header_frame, text="Alexa Tell Me A Joke",
                                 font=self.font_header, fg=COLOR_WHITE, bg=COLOR_ACCENT)
        header_title.pack(side=tk.LEFT, padx=15, pady=10)

        quit_button = tk.Button(header_frame, text="QUIT", command=self.on_closing,
                                 font=self.font_nav, fg=COLOR_WHITE, bg=COLOR_ACCENT,
                                 relief=tk.FLAT, padx=10)
        quit_button.pack(side=tk.RIGHT, padx=15, pady=10)

        # --- Main content area as a Canvas for emojis ---
        self.content_canvas = tk.Canvas(self.joke_frame, bg=COLOR_BACKGROUND, highlightthickness=0)
        self.content_canvas.pack(fill=tk.BOTH, expand=True)

        self.joke_text_label = tk.Label(self.content_canvas, text="",
                                         font=self.font_large, fg=COLOR_DARK_TEXT, bg=COLOR_BACKGROUND,
                                         wraplength=800, justify=tk.CENTER)
        self.joke_text_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        self.q_mark_canvas = tk.Canvas(self.content_canvas, width=120, height=120,
                                         bg=COLOR_BACKGROUND, highlightthickness=0)
        self.q_mark_canvas.create_oval(5, 5, 115, 115, fill=COLOR_ACCENT, outline=COLOR_ACCENT, width=4)
        self.q_mark_canvas.create_text(60, 60, text="?", font=(CUSTOM_FONT_FAMILY, 70, 'bold'), fill=COLOR_WHITE)
        self.q_mark_canvas.bind("<Button-1>", self.show_punchline_event)
        self.q_mark_canvas.config(cursor="hand2")
        self.q_mark_canvas.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

        nav_frame = tk.Frame(self.content_canvas, bg=COLOR_BACKGROUND)
        nav_frame.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        self.next_joke_button = tk.Button(nav_frame, text="NEXT JOKE", command=self.show_setup_with_click,
                                             font=self.font_nav, fg=COLOR_DARK_TEXT, bg=COLOR_WHITE,
                                             width=15, relief=tk.FLAT)
        self.next_joke_button.pack(padx=10)

    def setup_emojis(self):
        """Initializes emoji objects and places them on the canvas."""
        
        self.emojis = []
        # Clear existing PhotoImage references to allow creation of new ones
        self.emoji_photos = [] 
        
        canvas_width = self.content_canvas.winfo_width()
        canvas_height = self.content_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return 
            
        target_size = 50 # Desired max dimension for the emoji
            
        for path in self.emoji_image_paths:
            if os.path.exists(path):
                try:
                    # 1. Load the image
                    original_photo = tk.PhotoImage(file=path)
                    
                    # Calculate subsample factors for resizing
                    subsample_x = max(1, original_photo.width() // target_size)
                    subsample_y = max(1, original_photo.height() // target_size)
                    
                    # Resize the image using subsample
                    resized_image = original_photo.subsample(subsample_x, subsample_y)
                    # CRITICAL: Store reference to prevent garbage collection
                    self.emoji_photos.append(resized_image) 
                    
                    # 2. Set random position and speed
                    x = random.randint(target_size, canvas_width - target_size)
                    y = random.randint(target_size, canvas_height - target_size)
                    speed_x = random.choice([-2, -1, 1, 2])
                    speed_y = random.choice([-2, -1, 1, 2])
                    
                    # 3. Create the Emoji object
                    self.emojis.append(Emoji(self.content_canvas, resized_image, x, y, speed_x, speed_y))
                    
                except tk.TclError as e:
                    print(f"Error loading image {path}: {e}")
            else:
                print(f"Warning: Emoji image file not found: {path}")

    def animate_emojis(self):
        """Moves all emojis and schedules the next animation frame."""
        for emoji in self.emojis:
            emoji.move()
        self.animation_job = self.master.after(50, self.animate_emojis) # Update every 50ms

    def start_emoji_animation(self):
        """Starts the emoji animation if not already running."""
        # Setup emojis only when the canvas dimensions are available and they haven't been set up yet
        if not self.emojis:
            # We use after(100) to ensure the frame has rendered and has dimensions
            self.master.after(100, lambda: self._start_animation_after_setup())
        else:
            # If already set up, just restart the animation loop
            if hasattr(self, 'animation_job'):
                self.master.after_cancel(self.animation_job)
            self.animate_emojis()
            
    def _start_animation_after_setup(self):
        """Helper to ensure setup runs only after the canvas is fully drawn."""
        self.setup_emojis()
        if self.emojis:
            self.animate_emojis()

    def stop_emoji_animation(self):
        """Stops the emoji animation."""
        if hasattr(self, 'animation_job'):
            self.master.after_cancel(self.animation_job)
            del self.animation_job 
        
        # Clean up canvas items and objects
        for emoji in self.emojis:
            self.content_canvas.delete(emoji.id) 
        self.emojis = [] 
        self.emoji_photos = [] 


    def load_jokes(self):
        """Loads jokes from the file."""
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
        """Randomly selects a joke."""
        if self.jokes:
            self.current_joke = random.choice(self.jokes)
            return True
        return False
        
    def show_setup_with_click(self):
        """Wrapper to play click sound before showing the next joke setup."""
        self.play_click()
        self.show_setup()

    def show_setup(self):
        """Selects a new joke, displays the setup, and updates button states."""
        
        self.q_mark_canvas.place(relx=0.5, rely=0.65, anchor=tk.CENTER)
        
        self.q_mark_canvas.config(state=tk.NORMAL, cursor="hand2")
        self.q_mark_canvas.itemconfigure(1, fill=COLOR_ACCENT)
        
        if self.get_random_joke():
            setup = self.current_joke[0]
            self.joke_text_label.config(text=f"Q: {setup}?",
                                         font=self.font_large, fg=COLOR_DARK_TEXT)
        else:
            self.joke_text_label.config(text="No jokes available. Check the 'randomJokes.txt' file.",
                                         font=self.font_medium, fg=COLOR_DARK_TEXT)
            self.q_mark_canvas.place_forget()

    def show_punchline_event(self, event):
        """Event handler for clicking the question mark button (includes click sound)."""
        self.play_click()
        self.show_punchline()

    def show_punchline(self):
        """Plays laugh sound, displays the punchline and hides the question mark."""
        if self.current_joke:
            self.play_laugh()
            
            punchline = self.current_joke[1]
            
            full_text = self.joke_text_label.cget("text") + f"\n\nA: {punchline}"
            
            self.joke_text_label.config(text=full_text,
                                         font=self.font_large,
                                         fg=COLOR_ACCENT,
                                         justify=tk.CENTER)
            
            self.q_mark_canvas.place_forget()
            
            self.q_mark_canvas.config(state=tk.DISABLED, cursor="")


if __name__ == "__main__":
    root = tk.Tk()
    app = JokeApp(root)
    root.mainloop()