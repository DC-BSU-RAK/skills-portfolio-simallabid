import tkinter as tk
from tkinter import messagebox
import random
import tkinter.font as tkFont
import pygame # Import pygame for audio playback
import math # Import math equations used in the background

#Global Constants for Animation
#This code portion was written with the help of an AI assistant
EQUATIONS_DATA = [
    ("E = mc²", 35, "#8B0000"),
    ("lim(x->0) (sin(x)/x) = 1", 20, "#191970"),
    ("Σ n(n+1)/2", 40, "#4B0082"),
    ("A = πr²", 30, "#228B22"),
    ("φ ≈ 1.618", 25, "#CC5500"),
    ("V = 4/3 πr³", 30, "#004D00"),
    ("d/dx(x³) = 3x²", 20, "#800080"),
    ("F = ma", 35, "#FF4500"),
    ("C = 2πr", 25, "#008B8B"),
    ("cos²θ + sin²θ = 1", 22, "#DAA520"),
]

#Core Logic Functions
#Determines min/max values based on difficulty (1-digit, 2-digit, 4-digit)
def randomInt(d):
    if d == 1: return random.randint(1, 9), random.randint(1, 9)
    if d == 2: return random.randint(10, 99), random.randint(10, 99)
    if d == 3: return random.randint(1000, 9999), random.randint(1000, 9999)
    return 0, 0
def decideOperation(): return random.choice(['+', '-'])

#Checks if the answer is correct
def isCorrect(ans, n1, n2, op):
    try: return int(ans) == (n1 + n2 if op == '+' else n1 - n2)
    except ValueError: return False

#Calculates rank based on score (out of 100)
def displayResults(s):
    if s >= 90: return "A+ (Excellent!)"
    if s >= 80: return "A (Great job!)"
    if s >= 70: return "B (Good effort)"
    return "C (Keep practicing)"

#GUI Class
class MathQuizApp:
    def __init__(self, root):
        self.root = root; root.title("Mental Math Cards"); root.geometry("400x600")
        root.resizable(True, True); root.configure(bg="#E6F9E6")
        
        #Init states
        self.score, self.q_count, self.difficulty, self.attempts = 0, 0, 0, 0
        self.r_count, self.w_count = 0, 0 
        self.ans_val, self.timer_id, self.time_left = None, None, 0
        self.n1, self.n2, self.op = None, None, None
        
        #Animation States
        self.active_frame_name = "Welcome" #Tracks the current frame with animation
        self.floating_elements = [] #Holds the currently animated elements
        self.canvases = {} #Dictionary to store canvas references for animated frames
        self.center_windows = {} #Dictionary to store center window IDs
        self.animation_id = None
        
        #Audio Variables
        #sounds were added after learning from multiple videos on youtube.
        self.click_sound = None 
        self.correct_sound = None 
        self.wrong_sound = None 
        self.fx_channel = None 
        self.timer_sound = None 
        self.timer_channel = None

        #Initializing Pygame Mixer, load music, and load sound effects
        self.init_audio()
        
        #Defining the font
        font_name = "pigment DEMO"

        self.h_font = tkFont.Font(family=font_name, size=30, weight="bold")
        self.t_font = tkFont.Font(family=font_name, size=18)
        self.b_font = tkFont.Font(family=font_name, size=20, weight="bold")
        self.k_font = tkFont.Font(family=font_name, size=18, weight="bold")
        self.n_font = (font_name, 50, 'bold') 
        self.f_font = tkFont.Font(family=font_name, size=100, weight="bold")

        #Setup frames
        self.frames = {}; names = ["Welcome", "Instructions", "Menu", "Quiz"]
        for name in names:
            frame = tk.Frame(root, bg="#E6F9E6"); self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        root.grid_rowconfigure(0, weight=1); root.grid_columnconfigure(0, weight=1)

        self.ans_disp = tk.StringVar(root, value="")
        self.create_welcome_page(); self.create_instructions_page()
        self.create_menu_page(); self.create_quiz_page()
        self.show_frame("Welcome")

        #Bind closing event to stop music cleanly
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)


    #Animation Helper Methods
    #Creates the floating elements on a given canvas and returns their animation state.
    def _create_floating_elements(self, canvas):
        elements = []
        font_family = self.n_font[0]
        
        #Get current canvas dimensions for initial placement
        canvas.update_idletasks() #Ensure the dimensions are up to date
        w = max(400, canvas.winfo_width())
        h = max(600, canvas.winfo_height())
        
        for text, size, color in EQUATIONS_DATA:
            font = tkFont.Font(family=font_family, size=size, weight="bold")
            
            # Initializing random position, constrained slightly inside the canvas
            x = random.randint(50, w - 50)
            y = random.randint(50, h - 50)
            
            element_id = canvas.create_text(x, y, text=text, font=font, fill=color, anchor='center')
            
            # Generate random small velocity (dx, dy)
            dx = random.choice([-1, 1]) * random.uniform(0.5, 1.5)
            dy = random.choice([-1, 1]) * random.uniform(0.5, 1.5)
            
            elements.append({
                'id': element_id,
                'dx': dx,
                'dy': dy,
            })
        return elements


    #Recenter the main content frame when the canvas size changes
    def recenter_content(self, event, frame_name):
        canvas = self.canvases.get(frame_name)
        center_window_id = self.center_windows.get(frame_name)
        if canvas and center_window_id:
            w = event.width
            h = event.height
            canvas.coords(center_window_id, w / 2, h / 2)

    #Moves the floating equations and handles boundary collision.
    def animate_equations(self):        
        # Use the canvas associated with the currently animated frame
        canvas = self.canvases.get(self.active_frame_name) 

        if not canvas or not self.floating_elements:
            #If the frame has switched or elements are cleared, stop the loop.
            if self.animation_id:
                self.root.after_cancel(self.animation_id)
                self.animation_id = None
            return

        w = canvas.winfo_width()
        h = canvas.winfo_height()

        if w == 0 or h == 0:
            self.animation_id = self.root.after(50, self.animate_equations)
            return

        for element in self.floating_elements:
            try:
                x, y = canvas.coords(element['id'])
                
                #Safety check: if coords failed, skip this element
                if not x or not y: continue
                
                new_x = x + element['dx']
                new_y = y + element['dy']
                text_margin = 20
                
                #Boundary Check and Bounce
                if new_x < text_margin or new_x > w - text_margin:
                    element['dx'] *= -1
                    new_x = x + element['dx']
                    
                if new_y < text_margin or new_y > h - text_margin:
                    element['dy'] *= -1
                    new_y = y + element['dy']
                    
                canvas.coords(element['id'], new_x, new_y)
            except Exception:
                #Catch exception if element ID becomes invalid during a quick close/switch
                pass

        #Re-schedule the animation
        self.animation_id = self.root.after(50, self.animate_equations) 
    #End Animation Helper Methods


    #Audio Handlers
    def play_click_sound(self):
        if self.click_sound and self.fx_channel:
            self.fx_channel.play(self.click_sound)

    def play_correct_sound(self):
        if self.correct_sound and self.fx_channel:
            self.fx_channel.play(self.correct_sound)

    def play_wrong_sound(self):
        if self.wrong_sound and self.fx_channel:
            self.fx_channel.play(self.wrong_sound)
    
    def play_timer_sound(self):
        if self.timer_sound and self.timer_channel:
            self.timer_channel.play(self.timer_sound, loops=-1) 

    def stop_timer_sound(self):
        if self.timer_channel and self.timer_channel.get_busy():
            self.timer_channel.stop()

    #Initializes pygame mixer and loads all audio effects
    def init_audio(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.music.load('bg.mp3')
            pygame.mixer.music.play(-1) 
            pygame.mixer.music.set_volume(0.5) 
            
            self.click_sound = pygame.mixer.Sound('click.mp3')
            self.correct_sound = pygame.mixer.Sound('correct.mp3')
            self.wrong_sound = pygame.mixer.Sound('wrong.mp3')
            self.timer_sound = pygame.mixer.Sound('timer.mp3') 
            
            self.click_sound.set_volume(1.0)
            self.correct_sound.set_volume(1.0)
            self.wrong_sound.set_volume(1.0)
            self.timer_sound.set_volume(0.8)

            self.fx_channel = pygame.mixer.Channel(0)
            self.timer_channel = pygame.mixer.Channel(1)
            
        except pygame.error as e:
            print(f"Could not load audio file or initialize mixer: {e}. Check file names and location.")

    #Stops all sounds, stops animation, and destroys the window upon closing.
    def on_closing(self):
        self.stop_timer_sound() 
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        
        #Clean up floating elements on all canvases
        for element in self.floating_elements:
             try: element['canvas'].delete(element['id'])
             except: pass
        self.floating_elements = []


        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        self.root.destroy()
    #End Audio Handlers


    def show_frame(self, name): 
        self.play_click_sound() 
        self.frames[name].tkraise()
        
        animated_frames = ["Welcome", "Instructions", "Menu"]
        
        if name in animated_frames:
            #Stops existing animation loop if running
            if self.animation_id:
                self.root.after_cancel(self.animation_id)
                self.animation_id = None
                
            #Deletes old floating elements from the old canvas
            if self.floating_elements:
                canvas_to_delete_from = self.canvases.get(self.active_frame_name)
                if canvas_to_delete_from:
                    for element in self.floating_elements:
                        canvas_to_delete_from.delete(element['id'])
            self.floating_elements = []
            
            #Creates new elements on the active canvas
            canvas = self.canvases.get(name)
            if canvas:
                # Store the active canvas name
                self.active_frame_name = name 
                # Re-create and store the floating elements for the current canvas
                self.floating_elements = self._create_floating_elements(canvas)
                
            #Starts new animation loop
            if self.floating_elements:
                self.animation_id = self.root.after(50, self.animate_equations)
                
        else: #Quiz frame
            if self.animation_id:
                self.root.after_cancel(self.animation_id)
                self.animation_id = None
            #Clear elements from memory
            if self.floating_elements:
                canvas_to_delete_from = self.canvases.get(self.active_frame_name)
                if canvas_to_delete_from:
                    for element in self.floating_elements:
                        canvas_to_delete_from.delete(element['id'])
            self.floating_elements = []


    def _setup_animated_frame_base(self, frame_name, next_frame_name=None, back_frame_name=None):
        #Sets up the canvas and content structure for Welcome/Instructions/Menu
        frame = self.frames[frame_name]
        # Frame layout must only contain the canvas
        frame.grid_rowconfigure(0, weight=1); frame.grid_columnconfigure(0, weight=1)
        
        #Creates a full-size Canvas for floating elements
        canvas = tk.Canvas(frame, bg="#E6F9E6", highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        self.canvases[frame_name] = canvas
        
        #Creates the main content frame and place it in the center of the canvas
        content = tk.Frame(canvas, bg="#E6F9E6")
        self.center_windows[frame_name] = canvas.create_window(
            200, 300, 
            window=content, anchor="center"
        )
        
        #Bind resize event to re-center the content
        canvas.bind("<Configure>", lambda event, name=frame_name: self.recenter_content(event, name))
        
        if back_frame_name:
            font_name = self.n_font[0]
            tk.Button(content, text="<", font=(font_name, 24), command=lambda: self.show_frame(back_frame_name), 
                      bg="#E6F9E6", bd=0, activebackground="#E6F9E6", padx=10).pack(pady=(0, 20), anchor='nw')
        
        return content


    def create_welcome_page(self):
        content = self._setup_animated_frame_base("Welcome", next_frame_name="Instructions")
        
        #Main content labels and button
        title_text = "🧠 Mental Math Cards ➕➖"
        tk.Label(content, text=title_text, font=self.h_font, bg="#E6F9E6", fg="#004D00").pack(pady=(0, 20))
        
        tk.Label(content, text="Sharpen Your Mind, One Equation at a Time.", 
                  font=self.t_font, bg="#E6F9E6", fg="#333333").pack(pady=(0, 30))

        tk.Button(content, text="START QUIZ", font=self.b_font, command=lambda: self.show_frame("Instructions"), 
                  bg="#6B8E23", fg="white", relief="raised", padx=40, pady=15, bd=4, 
                  activebackground="#8FBC8F", activeforeground="white").pack(pady=20)


    def create_instructions_page(self):
        content = self._setup_animated_frame_base("Instructions", next_frame_name="Menu", back_frame_name="Welcome")
        tk.Label(content, text="Instructions", font=self.h_font, bg="#E6F9E6").pack(pady=(10, 40))
        instr = ["1. Select a difficulty level.", "2. Answer 10 problems in 20 seconds each.", "3. 10/5 points for 1st/2nd correct attempt.", "4. Use the on-screen keypad to enter answers."]
        for text in instr: 
            tk.Label(content, text=text, font=self.t_font, bg="#E6F9E6", justify="center", wraplength=450).pack(fill="x", padx=20, pady=5)
            
        tk.Button(content, text="Next", font=self.b_font, command=lambda: self.show_frame("Menu"), bg="#7FFF7F", relief="solid", borderwidth=2, padx=40, pady=10).pack(pady=(40, 20))


    def create_menu_page(self):
        content = self._setup_animated_frame_base("Menu", next_frame_name="Quiz", back_frame_name="Instructions")
                
        tk.Label(content, text="🔢 Difficulty Level", font=self.h_font, bg="#E6F9E6").pack(pady=(0, 30))
        levels = [("1. Easy (1-digit)", 1), ("2. Moderate (2-digit)", 2), ("3. Advanced (4-digit)", 3)]
        for text, level in levels: 
            tk.Button(content, text=text, font=self.b_font, command=lambda l=level: self.start_quiz(l), 
                      bg="#FFC0CB", relief="raised", padx=20, pady=10).pack(pady=15, ipadx=20, fill='x')

    def create_quiz_page(self):
        font_name = self.n_font[0]
        frame = self.frames["Quiz"]
        frame.grid_rowconfigure(2, weight=1); frame.grid_columnconfigure(0, weight=1)
        
        #TOP STATUS BAR (No canvas, static frame structure)
        s_frame = tk.Frame(frame, bg="#E6F9E6"); s_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)
        
        tk.Button(s_frame, text="<", font=(font_name, 24), command=self.quit_quiz, bg="#E6F9E6", bd=0).pack(side='left', padx=(0, 20))
        st_frame = tk.Frame(s_frame, bg="#E6F9E6"); st_frame.pack(side='right')
        sc_q_frame = tk.Frame(s_frame, bg="#E6F9E6"); sc_q_frame.pack(side='left', padx=10)

        tk.Label(st_frame, text="RIGHT:", font=(font_name, 14, 'bold'), fg="green", bg="#E6F9E6").pack(side='left', padx=(5, 0))
        self.r_label = tk.Label(st_frame, text="0", font=(font_name, 14, 'bold'), fg="green", bg="#E6F9E6"); self.r_label.pack(side='left')
        tk.Label(st_frame, text="| WRONG:", font=(font_name, 14, 'bold'), fg="red", bg="#E6F9E6").pack(side='left', padx=(5, 0))
        self.w_label = tk.Label(st_frame, text="0", font=(font_name, 14, 'bold'), fg="red", bg="#E6F9E6"); self.w_label.pack(side='left')
        self.t_label = tk.Label(st_frame, text="TIME: 20", font=(font_name, 14, 'bold'), fg="black", bg="#E6F9E6"); self.t_label.pack(side='right', padx=(10, 0))
        
        self.s_label = tk.Label(sc_q_frame, text="Score: 0", font=(font_name, 22, 'bold'), bg="#E6F9E6"); self.s_label.pack(side='left')
        self.q_label = tk.Label(sc_q_frame, font=(font_name, 18, 'bold'), bg="#E6F9E6"); self.q_label.pack(side='right', padx=(20, 0))

        #MATH PROBLEM DISPLAY 
        p_area = tk.Frame(frame, bg="#E6F9E6"); p_area.grid(row=1, column=0, pady=10, sticky='n') 
        self.n1_label = tk.Label(p_area, text="", font=self.n_font, bg="#E6F9E6"); self.n1_label.pack(anchor='e', padx=20)
        op_frame = tk.Frame(p_area, bg="#E6F9E6"); op_frame.pack(fill='x')
        self.op_label = tk.Label(op_frame, text="", font=self.n_font, bg="#E6F9E6"); self.op_label.pack(side='left')
        self.n2_label = tk.Label(op_frame, text="", font=self.n_font, bg="#E6F9E6"); self.n2_label.pack(side='right', padx=20)
        tk.Frame(p_area, height=3, bg="black").pack(fill='x', pady=5)
        self.ans_label = tk.Label(p_area, textvariable=self.ans_disp, font=self.n_font, bg="#E6F9E6", width=8, anchor='e'); self.ans_label.pack(pady=10)
        
        self.f_label = tk.Label(p_area, text="", font=self.f_font, bg="#E6F9E6")
        self.f_label.place(relx=0.5, rely=0.5, anchor='center')

        #Keypad
        #The inspiration was taken from an app and I took assistance from AI to create this.
        k_frame = tk.Frame(frame, bg="#E6F9E6"); k_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'Clear', '0', 'Check']
        for i in range(4): k_frame.grid_rowconfigure(i, weight=1)
        for i in range(3): k_frame.grid_columnconfigure(i, weight=1)
        
        for i, key in enumerate(keys):
            r, c = divmod(i, 3)
            #All keypad commands include the click sound call
            if key.isdigit(): cmd = lambda k=key: (self.play_click_sound(), self.key_press(k)); bg, fg = "white", "black"
            elif key == 'Clear': cmd = lambda: (self.play_click_sound(), self.clear_answer()); bg, fg = "#808080", "white"
            elif key == 'Check': cmd = lambda: (self.play_click_sound(), self.handle_input()); bg, fg = "#FF8C00", "white"
            tk.Button(k_frame, text=key, font=self.k_font, command=cmd, 
                      bg=bg, fg=fg, relief="raised", bd=2).grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

    def show_feedback(self, symbol, color):
        #Displays a visual feedback symbol temporarily
        self.f_label.config(text=symbol, fg=color); self.f_label.lift()
        self.root.after(500, self.hide_feedback)

    def hide_feedback(self):
        #Hides the visual feedback label
        self.f_label.config(text=""); self.f_label.lower()

    def quit_quiz(self):
        self.play_click_sound() #Play sound on quit attempt
        if messagebox.askyesno("Quit Quiz", "Are you sure you want to quit the current quiz?"):
            self.end_timer()
            self.stop_timer_sound() #Stop timer sound on quit
            self.score, self.q_count, self.difficulty, self.r_count, self.w_count = 0, 0, 0, 0, 0
            self.show_frame("Menu")

    def key_press(self, key):
        current = self.ans_disp.get()
        if len(current) < 5: self.ans_disp.set(current + key)

    def clear_answer(self): self.ans_disp.set("")

    def start_quiz(self, level):
        self.play_click_sound() #Play sound when starting quiz
        self.difficulty = level; self.score, self.q_count = 0, 0
        self.r_count, self.w_count = 0, 0
        self.show_frame("Quiz"); self.present_problem()
    
    def end_timer(self):
        if self.timer_id: self.root.after_cancel(self.timer_id); self.timer_id = None

    def generate_problem(self):
        self.n1, self.n2 = randomInt(self.difficulty); self.op = decideOperation()
        if self.op == '-' and self.n2 > self.n1: self.n1, self.n2 = self.n2, self.n1
        self.attempts = 0
        self.ans_val = self.n1 + self.n2 if self.op == '+' else self.n1 - self.n2

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.t_label.config(text=f"TIME: {self.time_left}", fg="red" if self.time_left <= 5 else "black")
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            #Time's Up is treated as a wrong answer
            self.stop_timer_sound() #Stop the timer sound
            self.play_wrong_sound() 
            self.show_feedback('❌', 'red'); self.w_count += 1
            messagebox.showerror("Time's Up!", f"Out of time! Answer: {self.ans_val}.")
            self.present_problem()

    def present_problem(self):
        self.hide_feedback()
        self.end_timer()
        if self.q_count >= 10: 
            self.stop_timer_sound() #Stops the timer sound when quiz ends
            self.end_quiz(); 
            return

        self.q_count += 1; self.generate_problem(); self.time_left = 20 #The timer in the quiz
        self.q_label.config(text=f"Question {self.q_count} of 10")
        self.n1_label.config(text=str(self.n1))
        self.op_label.config(text=self.op)
        self.n2_label.config(text=str(self.n2))
        self.clear_answer()
        self.s_label.config(text=f"Score: {self.score}")
        self.r_label.config(text=str(self.r_count)); self.w_label.config(text=str(self.w_count))
        
        #Starts the timer sound for the new problem
        self.play_timer_sound() 
        self.update_timer()
        
    def handle_input(self):
        self.end_timer()
        user_input = self.ans_disp.get()
        if not user_input: 
            messagebox.showerror("Error", "Enter an answer."); self.update_timer() 
            return
            
        if isCorrect(user_input, self.n1, self.n2, self.op):
            self.stop_timer_sound() # Stops the timer sound on correct answer
            self.play_correct_sound() 
            points = 10 if self.attempts == 0 else 5; self.score += points
            self.r_count += 1
            self.show_feedback('✅', 'green')
            messagebox.showinfo("Correct!", f"🎉 Correct! (+{points} pts)")
            self.present_problem() #This will call play_timer_sound() for the next question
        else:
            #Timer sound continues on wrong answer
            self.play_wrong_sound() 
            self.show_feedback('❌', 'red')
            self.attempts += 1
            if self.attempts == 1: 
                messagebox.showerror("Incorrect!", "❌ Incorrect. One more chance (+5 pts).")
                self.clear_answer(); self.update_timer()
            else: 
                self.stop_timer_sound() #Stop sound before moving to next question (after the 2nd wrong attempt)
                self.w_count += 1
                messagebox.showerror("Wrong Again!", f"💔 Incorrect. Answer: {self.ans_val}.")
                self.present_problem()
                
    def end_quiz(self):
        self.end_timer()
        self.stop_timer_sound() #Stops timer sound at the end of the quiz
        rank = displayResults(self.score)
        if messagebox.askyesno("Quiz Finished!", f"🏆 Quiz Complete!\nScore: {self.score}/100.\nRank: {rank}\n\nPlay another?"): 
            self.score, self.q_count, self.difficulty, self.r_count, self.w_count = 0, 0, 0, 0, 0
            self.show_frame("Menu")
        else: self.on_closing() 

#The Main Execution
if __name__ == "__main__":
    root = tk.Tk()
    app = MathQuizApp(root)
    root.mainloop()