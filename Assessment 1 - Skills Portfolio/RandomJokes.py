import tkinter as tk
from tkinter import messagebox
import random
import os

# --- JOKE DATA PROVIDED BY THE USER ---
USER_JOKES = [
    "Why did the chicken cross the road?To get to the other side.",
    "What happens if you boil a clown?You get a laughing stock.",
    "Why did the car get a flat tire?Because there was a fork in the road!",
    "How did the hipster burn his mouth?He ate his pizza before it was cool.",
    "What did the janitor say when he jumped out of the closet?SUPPLIES!!!!",
    "Have you heard about the band 1023MB?It's probably because they haven't got a gig yet…",
    "Why does the golfer wear two pants?Because he's afraid he might get a \"Hole-in-one.\"",
    "Why should you wear glasses to maths class?Because it helps with division.",
    "Why does it take pirates so long to learn the alphabet?Because they could spend years at C.",
    "Why did the woman go on the date with the mushroom?Because he was a fun-ghi.",
    "Why do bananas never get lonely?Because they hang out in bunches.",
    "What did the buffalo say when his kid went to college?Bison.",
    "Why shouldn't you tell secrets in a cornfield?Too many ears.",
    "What do you call someone who doesn't like carbs?Lack-Toast Intolerant.",
    "Why did the can crusher quit his job?Because it was soda pressing.",
    "Why did the birthday boy wrap himself in paper?He wanted to live in the present.",
    "What does a house wear?A dress.",
    "Why couldn't the toilet paper cross the road?Because it got stuck in a crack.",
    "Why didn't the bike want to go anywhere?Because it was two-tired!",
    "Want to hear a pizza joke?Nahhh, it's too cheesy!",
    "Why are chemists great at solving problems?Because they have all of the solutions!",
    "Why is it impossible to starve in the desert?Because of all the sand which is there!",
    "What did the cheese say when it looked in the mirror?Halloumi!",
    "Why did the developer go broke?Because he used up all his cache.",
    "Did you know that ants are the only animals that don't get sick?It's true! It's because they have little antibodies.",
    "Why did the donut go to the dentist?To get a filling.",
    "What do you call a bear with no teeth?A gummy bear!",
    "What does a vegan zombie like to eat?Graaains.",
    "What do you call a dinosaur with only one eye?A Do-you-think-he-saw-us!",
    "Why should you never fall in love with a tennis player?Because to them... love means NOTHING!",
    "What did the full glass say to the empty glass?You look drunk.",
    "What's a potato's favorite form of transportation?The gravy train",
    "What did one ocean say to the other?Nothing, they just waved.",
    "What did the right eye say to the left eye?Honestly, between you and me something smells.",
    "What do you call a dog that's been run over by a steamroller?Spot!",
    "What's the difference between a hippo and a zippo?One's pretty heavy and the other's a little lighter",
    "Why don't scientists trust Atoms?They make up everything."
]
# ----------------------------------------


class JokeApp:
    def __init__(self, master):
        self.master = master
        master.title("Daily Dose of LOLs")
        
        # --- CHANGES MADE HERE TO ALLOW RESIZING/MAXIMIZING ---
        # Removed: master.geometry("375x667")
        # Removed: master.resizable(False, False)
        # Optional: Set a starting size
        master.geometry("800x600") 
        master.minsize(400, 400) # Set a minimum resize limit
        # -----------------------------------------------------

        self.file_path = 'randomJokes.txt'
        self.current_joke = None
        self.jokes = self.load_jokes()

        # --- Frames for different "pages" ---
        self.welcome_frame = tk.Frame(master, bg="#212121") # Dark Grey (Close to Image 3)
        self.joke_frame = tk.Frame(master, bg="#2196F3")   # Bright Blue (Close to Image 1 & 2)

        self.create_welcome_page()
        self.create_joke_page()

        self.show_frame(self.welcome_frame) # Start with the welcome page

    def show_frame(self, frame):
        """Hides all frames and shows the selected frame."""
        self.welcome_frame.pack_forget()
        self.joke_frame.pack_forget()
        frame.pack(fill=tk.BOTH, expand=True)
        
        if frame == self.joke_frame:
            self.show_setup() # Automatically load a new joke when entering joke page

    def create_welcome_page(self):
        """Configures the welcome page."""
        welcome_bg_color = "#212121"
        text_color = "white"
        
        self.welcome_frame.config(bg=welcome_bg_color)
        
        # Header (Top part is darker/placeholder)
        header_placeholder = tk.Frame(self.welcome_frame, bg="#1a1a1a", height=30)
        header_placeholder.pack(fill=tk.X)

        # Title
        title = tk.Label(self.welcome_frame, text="Your Daily Dose\nof LOLs", 
                         font=('Arial', 28, 'bold'), fg=text_color, bg=welcome_bg_color,
                         justify=tk.CENTER)
        title.pack(pady=(60, 30))

        # Description
        description = tk.Label(self.welcome_frame, text="Kick start every day with\nside-splitting jokes.",
                               font=('Arial', 18), fg="#BDBDBD", bg=welcome_bg_color,
                               justify=tk.CENTER, wraplength=500) # Adjusted wraplength for larger screen
        description.pack(pady=20)

        # Call to action
        cta = tk.Label(self.welcome_frame, text="Ready for a comedy break?",
                       font=('Arial', 18), fg=text_color, bg=welcome_bg_color,
                       justify=tk.CENTER, wraplength=500) # Adjusted wraplength for larger screen
        cta.pack(pady=(20, 80))

        # MAKE ME LAUGH Button
        make_me_laugh_button = tk.Button(self.welcome_frame, text="MAKE ME LAUGH", 
                                         command=lambda: self.show_frame(self.joke_frame),
                                         font=('Arial', 16, 'bold'), bg="white", fg="#212121",
                                         relief=tk.FLAT, padx=30, pady=10, borderwidth=0)
        make_me_laugh_button.pack(pady=20)
        make_me_laugh_button.config(width=20) 

    def create_joke_page(self):
        """Configures the joke display page."""
        
        joke_bg_color = "#2196F3" # Bright blue
        text_color = "white"
        
        self.joke_frame.config(bg=joke_bg_color)

        # --- Header (Red Bar) ---
        header_frame = tk.Frame(self.joke_frame, bg="#F44336", height=50) # Red header
        header_frame.pack(fill=tk.X)
        
        # Header title
        header_title = tk.Label(header_frame, text="Alexa Tell Me A Joke", 
                                font=('Arial', 18, 'bold'), fg=text_color, bg="#F44336")
        header_title.pack(side=tk.LEFT, padx=15, pady=10)

        # Quit button
        menu_button = tk.Button(header_frame, text="QUIT", command=self.master.quit,
                                font=('Arial', 10, 'bold'), fg=text_color, bg="#F44336",
                                relief=tk.FLAT, padx=10)
        menu_button.pack(side=tk.RIGHT, padx=15, pady=10)

        # --- Joke Display ---
        self.joke_text_label = tk.Label(self.joke_frame, text="", 
                                        font=('Arial', 24, 'bold'), fg=text_color, bg=joke_bg_color,
                                        wraplength=800, justify=tk.CENTER) # Increased wraplength
        self.joke_text_label.pack(pady=(50, 40), padx=20)

        # --- Question Mark Button (Show Punchline) ---
        # Canvas used to create the large circular button structure
        self.q_mark_canvas = tk.Canvas(self.joke_frame, width=120, height=120, 
                                       bg=joke_bg_color, highlightthickness=0)
        self.q_mark_canvas.pack(pady=20, expand=True) # Use expand=True to vertically center
        
        # Draw the Orange circle
        self.q_mark_canvas.create_oval(5, 5, 115, 115, fill="#FF9800", outline="#E65100", width=4)
        # Add the question mark text
        self.q_mark_canvas.create_text(60, 60, text="?", font=('Arial', 70, 'bold'), fill="white")
        self.q_mark_canvas.bind("<Button-1>", self.show_punchline_event) 
        self.q_mark_canvas.config(cursor="hand2")

        # --- Navigation Buttons ---
        nav_frame = tk.Frame(self.joke_frame, bg=joke_bg_color)
        nav_frame.pack(side=tk.BOTTOM, pady=30)

        # Previous/Next buttons placed in the button frame for layout
        
        # Prev Joke button (Left Arrow)
        self.prev_joke_button = tk.Button(nav_frame, text="PREV", command=self.show_setup, 
                                        font=('Arial', 12, 'bold'), fg="#2196F3", bg="white",
                                        width=8, relief=tk.FLAT)
        self.prev_joke_button.pack(side=tk.LEFT, padx=10)

        # Next Joke button (Right Arrow)
        self.next_joke_button = tk.Button(nav_frame, text="NEXT", command=self.show_setup,
                                        font=('Arial', 12, 'bold'), fg="#2196F3", bg="white",
                                        width=8, relief=tk.FLAT)
        self.next_joke_button.pack(side=tk.RIGHT, padx=10)

    def load_jokes(self):
        """Loads jokes from the file."""
        try:
            # Check if the file exists and create it if necessary
            if not os.path.exists(self.file_path):
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    for joke in USER_JOKES:
                        f.write(joke + '\n')
            
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
                return []
                
            return jokes_list
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading jokes: {e}")
            return []

    def get_random_joke(self):
        """Randomly selects a joke."""
        if self.jokes:
            self.current_joke = random.choice(self.jokes)
            return True
        return False

    def show_setup(self):
        """Selects a new joke, displays the setup, and updates button states."""
        
        # Reset canvas state (re-enable click and set color to initial orange)
        self.q_mark_canvas.config(state=tk.NORMAL, cursor="hand2")
        self.q_mark_canvas.itemconfigure(1, fill="#FF9800")
        
        if self.get_random_joke():
            setup = self.current_joke[0]
            # Reset color to white for setup
            self.joke_text_label.config(text=f"Q: {setup}?", font=('Arial', 24, 'bold'), fg="white") 
        else:
            self.joke_text_label.config(text="No jokes available. Check the file.", 
                                        font=('Arial', 18), fg="white")
            self.q_mark_canvas.config(state=tk.DISABLED, cursor="")

    def show_punchline_event(self, event):
        """Event handler for clicking the question mark button."""
        self.show_punchline()

    def show_punchline(self):
        """Displays the punchline."""
        if self.current_joke:
            punchline = self.current_joke[1]
            
            # Append punchline, changing the text color to yellow (mimics image)
            full_text = self.joke_text_label.cget("text") + f"\n\nA: {punchline}"
            self.joke_text_label.config(text=full_text, font=('Arial', 24, 'bold'), fg="#FFEB3B") # Yellow
            
            # Disable the punchline functionality
            self.q_mark_canvas.config(state=tk.DISABLED, cursor="") 
            self.q_mark_canvas.itemconfigure(1, fill="#FFC107") # Change circle color to indicate used


if __name__ == "__main__":
    
    # This block ensures the randomJokes.txt file exists with the user's data
    try:
        if not os.path.exists('randomJokes.txt'):
            print("Creating 'randomJokes.txt' with user-provided jokes.")
        else:
            print("Updating 'randomJokes.txt' with user-provided jokes.")
            
        with open('randomJokes.txt', 'w', encoding='utf-8') as f:
            for joke_line in USER_JOKES:
                f.write(joke_line + '\n')
        print("File 'randomJokes.txt' is ready.")
    except Exception as e:
        print(f"Error managing 'randomJokes.txt': {e}")

    root = tk.Tk()
    app = JokeApp(root)
    root.mainloop()