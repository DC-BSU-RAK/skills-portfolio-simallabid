import tkinter as tk
from tkinter import messagebox
import random
import tkinter.font as tkFont

# --- Core Logic Functions ---
def randomInt(d):
    """Determines min/max values based on difficulty."""
    if d == 1: return random.randint(1, 9), random.randint(1, 9)
    elif d == 2: return random.randint(10, 99), random.randint(10, 99)
    elif d == 3: return random.randint(1000, 9999), random.randint(1000, 9999)
    return 0, 0
def decideOperation(): return random.choice(['+', '-'])
def isCorrect(ans, n1, n2, op):
    """Checks if the answer is correct."""
    try: ans = int(ans); return ans == (n1 + n2 if op == '+' else n1 - n2)
    except ValueError: return False
def displayResults(score):
    """Calculates rank based on score (out of 100)."""
    if score >= 90: return f"A+ (Excellent!)"
    elif score >= 80: return f"A (Great job!)"
    elif score >= 70: return f"B (Good effort)"
    else: return f"C (Keep practicing)"

# --- GUI Class ---
class MathQuizApp:
    def __init__(self, root):
        self.root = root; root.title("Mental Math Cards"); root.geometry("400x600")
        # Ensure the root window can resize
        root.resizable(True, True); root.configure(bg="#E6F9E6") # Light Green Theme
        
        self.score, self.q_count, self.difficulty, self.attempts = 0, 0, 0, 0
        self.right_count, self.wrong_count = 0, 0
        self.current_answer, self.timer_id, self.time_left = None, None, 0
        self.num1, self.num2, self.operation = None, None, None

        # Define custom fonts
        self.heading_font = tkFont.Font(family="Helvetica", size=30, weight="bold")
        self.text_font = tkFont.Font(family="Arial", size=18)
        self.button_font = tkFont.Font(family="Arial", size=20, weight="bold")
        self.responsive_keypad_font = tkFont.Font(family="Arial", size=18, weight="bold")
        self.number_font = ('Arial', 50, 'bold')
        self.feedback_font = tkFont.Font(family="Arial", size=100, weight="bold") # Font for the feedback cross/check

        # Setup frames and ensure the main grid cell expands to fill the window
        self.frames = {}; names = ["Welcome", "Instructions", "Menu", "Quiz"]
        for name in names:
            # All frames fill the single grid cell of the root window
            frame = tk.Frame(root, bg="#E6F9E6"); self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.root.grid_rowconfigure(0, weight=1); self.root.grid_columnconfigure(0, weight=1)

        self.answer_display = tk.StringVar(root, value="")
        self.create_welcome_page(); self.create_instructions_page()
        self.create_menu_page(); self.create_quiz_page()
        self.show_frame("Welcome")

    def show_frame(self, name): self.frames[name].tkraise()

    def create_welcome_page(self):
        frame = self.frames["Welcome"]
        
        # Configure grid for vertical centering
        frame.grid_rowconfigure(0, weight=1) # Top spacer
        frame.grid_rowconfigure(1, weight=0) # Content
        frame.grid_rowconfigure(2, weight=1) # Bottom spacer
        frame.grid_columnconfigure(0, weight=1)

        content_frame = tk.Frame(frame, bg="#E6F9E6")
        content_frame.grid(row=1, column=0, sticky="")
        
        tk.Label(content_frame, text="Welcome to\nMental Math Cards", font=self.heading_font, bg="#E6F9E6").pack(pady=(0, 50))
        tk.Button(content_frame, text="Start", font=self.button_font, command=lambda: self.show_frame("Instructions"), bg="#6B8E23", fg="white", relief="flat", padx=30, pady=10).pack(pady=20)

    def create_instructions_page(self):
        frame = self.frames["Instructions"]
        
        # Configure grid for responsive layout
        frame.grid_rowconfigure(0, weight=0) # Back button
        frame.grid_rowconfigure(1, weight=0) # Content
        frame.grid_rowconfigure(2, weight=1) # Spacer
        frame.grid_columnconfigure(0, weight=1)
        
        tk.Button(frame, text="<", font=('Arial', 24), command=lambda: self.show_frame("Welcome"), bg="#E6F9E6", bd=0).grid(row=0, column=0, sticky='nw', padx=10, pady=10) 

        content_frame = tk.Frame(frame, bg="#E6F9E6")
        content_frame.grid(row=1, column=0, sticky="ew", padx=20)

        tk.Label(content_frame, text="Instructions", font=self.heading_font, bg="#E6F9E6").pack(pady=(10, 40))
        instructions = ["1. Select a difficulty level.", "2. Answer 10 problems in 20 seconds each.", "3. 10/5 points for 1st/2nd correct attempt.", "4. Use the on-screen keypad to enter answers."]
        
        for text in instructions: 
            # Use justify="center" and fill="x" for clean, responsive text block
            tk.Label(content_frame, text=text, font=self.text_font, bg="#E6F9E6", justify="center", wraplength=450).pack(fill="x", padx=20, pady=5)
            
        tk.Button(content_frame, text="Next", font=self.button_font, command=lambda: self.show_frame("Menu"), bg="#7FFF7F", relief="solid", borderwidth=2, padx=40, pady=10).pack(pady=40)
    
    def create_menu_page(self):
        frame = self.frames["Menu"]
        
        # Configure grid for vertical centering and full width buttons
        frame.grid_rowconfigure(0, weight=0) # Back button
        frame.grid_rowconfigure(1, weight=1) # Top spacer
        frame.grid_rowconfigure(2, weight=0) # Content
        frame.grid_rowconfigure(3, weight=1) # Bottom spacer
        frame.grid_columnconfigure(0, weight=1)
        
        tk.Button(frame, text="<", font=('Arial', 24), command=lambda: self.show_frame("Instructions"), bg="#E6F9E6", bd=0).grid(row=0, column=0, sticky='nw', padx=10, pady=10) 

        menu_content = tk.Frame(frame, bg="#E6F9E6")
        menu_content.grid(row=2, column=0, sticky="ew", padx=20) # Center the content frame

        menu_content.grid_columnconfigure(0, weight=1) # Ensure buttons stretch
        
        tk.Label(menu_content, text="🔢 Difficulty Level", font=self.heading_font, bg="#E6F9E6").pack(pady=(0, 30))
        
        levels = [("1. Easy (1-digit)", 1), ("2. Moderate (2-digit)", 2), ("3. Advanced (4-digit)", 3)]
        
        for text, level in levels: 
            # Use pack here, but the container (menu_content) is centered and stretching
            tk.Button(menu_content, text=text, font=self.button_font, command=lambda l=level: self.start_quiz(l), 
                      bg="#FFC0CB", relief="raised", padx=20, pady=10).pack(pady=15, ipadx=20, fill='x')


    def create_quiz_page(self):
        frame = self.frames["Quiz"]
        
        # Configure layout for vertical responsiveness
        frame.grid_rowconfigure(0, weight=0) # Status bar
        frame.grid_rowconfigure(1, weight=0) # Problem area
        frame.grid_rowconfigure(2, weight=1) # Keypad (expands)
        frame.grid_columnconfigure(0, weight=1) # Center content horizontally
        
        # --- ROW 0: TOP STATUS BAR (Back, Score/Q, Timer) ---
        status_frame = tk.Frame(frame, bg="#E6F9E6"); 
        status_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)
        
        tk.Button(status_frame, text="<", font=('Arial', 24), command=self.return_to_menu_from_quiz, bg="#E6F9E6", bd=0).pack(side='left', padx=(0, 20))

        stats_frame = tk.Frame(status_frame, bg="#E6F9E6"); stats_frame.pack(side='right')
        tk.Label(stats_frame, text="RIGHT:", font=('Arial', 14, 'bold'), fg="green", bg="#E6F9E6").pack(side='left', padx=(5, 0))
        self.right_label = tk.Label(stats_frame, text="0", font=('Arial', 14, 'bold'), fg="green", bg="#E6F9E6"); self.right_label.pack(side='left')
        tk.Label(stats_frame, text="| WRONG:", font=('Arial', 14, 'bold'), fg="red", bg="#E6F9E6").pack(side='left', padx=(5, 0))
        self.wrong_label = tk.Label(stats_frame, text="0", font=('Arial', 14, 'bold'), fg="red", bg="#E6F9E6"); self.wrong_label.pack(side='left')
        self.timer_label = tk.Label(stats_frame, text="TIME: 20", font=('Arial', 14, 'bold'), fg="black", bg="#E6F9E6"); self.timer_label.pack(side='right', padx=(10, 0))
        
        # Score and Question count labels
        score_q_frame = tk.Frame(status_frame, bg="#E6F9E6"); score_q_frame.pack(side='left', padx=10)
        self.score_label = tk.Label(score_q_frame, text="Score: 0", font=('Arial', 22, 'bold'), bg="#E6F9E6"); self.score_label.pack(side='left')
        self.q_label = tk.Label(score_q_frame, font=('Arial', 18, 'bold'), bg="#E6F9E6"); self.q_label.pack(side='right', padx=(20, 0))

        # --- ROW 1: MATH PROBLEM DISPLAY (Stacked) ---
        problem_area = tk.Frame(frame, bg="#E6F9E6"); 
        # Grid placement: Centered horizontally, sticky 'n' to keep it close to the top of its row
        problem_area.grid(row=1, column=0, pady=10, sticky='n') 

        num_font = self.number_font

        self.num1_label = tk.Label(problem_area, text="", font=num_font, bg="#E6F9E6"); self.num1_label.pack(anchor='e', padx=20)
        
        op_frame = tk.Frame(problem_area, bg="#E6F9E6"); op_frame.pack(fill='x')
        self.op_label = tk.Label(op_frame, text="", font=num_font, bg="#E6F9E6"); self.op_label.pack(side='left')
        self.num2_label = tk.Label(op_frame, text="", font=num_font, bg="#E6F9E6"); self.num2_label.pack(side='right', padx=20)

        tk.Frame(problem_area, height=3, bg="black").pack(fill='x', pady=5)
        self.answer_label = tk.Label(problem_area, textvariable=self.answer_display, font=num_font, bg="#E6F9E6", width=8, anchor='e'); self.answer_label.pack(pady=10)
        
        # --- NEW: Visual Feedback Label (Hidden by default) ---
        self.feedback_label = tk.Label(problem_area, text="", font=self.feedback_font, bg="#E6F9E6")
        # Use place() to center it over the main problem area elements
        self.feedback_label.place(relx=0.5, rely=0.5, anchor='center')

        # --- ROW 2: KEYPAD (Responsive Section) ---
        keypad_frame = tk.Frame(frame, bg="#E6F9E6"); 
        # Grid placement: Sticky "nsew" to fill remaining space
        keypad_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'Clear', '0', 'Check']
        
        # Configure weights for responsive scaling
        for i in range(4): 
            keypad_frame.grid_rowconfigure(i, weight=1)
        for i in range(3): 
            keypad_frame.grid_columnconfigure(i, weight=1)

        for i, key in enumerate(keys):
            r, c = divmod(i, 3)
            
            if key.isdigit():
                cmd = lambda k=key: self.key_press(k); btn_bg = "white"; btn_fg = "black"
            elif key == 'Clear':
                cmd = self.clear_answer; btn_bg = "#808080"; btn_fg = "white"
            elif key == 'Check':
                cmd = self.handle_input; btn_bg = "#FF8C00"; btn_fg = "white"
            
            # Use sticky="nsew" to make the buttons fill the cells
            tk.Button(keypad_frame, text=key, font=self.responsive_keypad_font, command=cmd, 
                      bg=btn_bg, fg=btn_fg, relief="raised", bd=2).grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

    def show_feedback(self, symbol, color):
        """Displays a visual feedback symbol (e.g., '❌' or '✅') temporarily."""
        self.feedback_label.config(text=symbol, fg=color)
        self.feedback_label.lift() # Bring it to the front
        # Keep the feedback visible for 500 milliseconds (0.5 seconds)
        # Note: This timer only starts after a blocking messagebox (if present) is closed.
        self.root.after(500, self.hide_feedback)

    def hide_feedback(self):
        """Hides the visual feedback label."""
        self.feedback_label.config(text="")
        self.feedback_label.lower() # Push it back down


    def return_to_menu_from_quiz(self):
        if messagebox.askyesno("Quit Quiz", "Are you sure you want to quit the current quiz?"):
            if self.timer_id: self.root.after_cancel(self.timer_id)
            self.score = 0; self.q_count = 0; self.difficulty = 0
            self.right_count = 0; self.wrong_count = 0
            self.show_frame("Menu")

    def key_press(self, key):
        current = self.answer_display.get()
        # Maximum length adjusted to handle large numbers in advanced difficulty
        max_len = 5 if self.difficulty == 3 else 5
        if len(current) < max_len: self.answer_display.set(current + key)

    def clear_answer(self): self.answer_display.set("")

    def start_quiz(self, level):
        self.difficulty = level; self.score = 0; self.q_count = 0
        self.right_count = 0; self.wrong_count = 0
        self.show_frame("Quiz"); self.present_problem()

    def generate_problem(self):
        self.num1, self.num2 = randomInt(self.difficulty); self.operation = decideOperation()
        # Ensure non-negative result for subtraction (no negative key on keypad)
        if self.operation == '-' and self.num2 > self.num1:
            self.num1, self.num2 = self.num2, self.num1
        self.attempts = 0
        self.current_answer = self.num1 + self.num2 if self.operation == '+' else self.num1 - self.num2

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"TIME: {self.time_left}", fg="red" if self.time_left <= 5 else "black")
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            # Show the cross on timeout
            self.show_feedback('❌', 'red') 
            self.wrong_count += 1
            messagebox.showerror("Time's Up!", f"Out of time! Answer: {self.current_answer}.")
            self.present_problem()

    def present_problem(self):
        # Ensure the feedback cross is hidden when a new problem loads
        self.hide_feedback() 
        
        if self.timer_id: self.root.after_cancel(self.timer_id)
        if self.q_count >= 10: self.end_quiz(); return

        self.q_count += 1; self.generate_problem(); self.time_left = 20
        self.q_label.config(text=f"Question {self.q_count} of 10")
        self.num1_label.config(text=str(self.num1))
        self.op_label.config(text=self.operation)
        self.num2_label.config(text=str(self.num2))
        self.clear_answer()
        self.score_label.config(text=f"Score: {self.score}")
        self.right_label.config(text=str(self.right_count))
        self.wrong_label.config(text=str(self.wrong_count))
        self.update_timer()
        
    def handle_input(self):
        # Cancel the timer before processing input
        if self.timer_id: self.root.after_cancel(self.timer_id); self.timer_id = None
        user_input = self.answer_display.get()
        if not user_input: 
            messagebox.showerror("Error", "Enter an answer.")
            # Restart the timer if input was empty
            self.update_timer() 
            return
            
        if isCorrect(user_input, self.num1, self.num2, self.operation):
            points = 10 if self.attempts == 0 else 5; self.score += points
            self.right_count += 1
            # Show a green checkmark for correct answers
            self.show_feedback('✅', 'green') 
            messagebox.showinfo("Correct!", f"🎉 Correct! (+{points} pts)")
            self.present_problem()
        else:
            # Show the cross when the answer is incorrect
            self.show_feedback('❌', 'red') 
            self.attempts += 1
            if self.attempts == 1: 
                messagebox.showerror("Incorrect!", "❌ Incorrect. One more chance (+5 pts).")
                self.clear_answer()
                # Restart the timer for the second attempt
                self.update_timer()
            else: 
                self.wrong_count += 1
                messagebox.showerror("Wrong Again!", f"💔 Incorrect. Answer: {self.current_answer}.")
                self.present_problem()
                
    def end_quiz(self):
        if self.timer_id: self.root.after_cancel(self.timer_id)
        rank = displayResults(self.score)
        messagebox.showinfo("Quiz Finished!", f"🏆 Quiz Complete!\nScore: {self.score}/100.\nRank: {rank}")
        if messagebox.askyesno("Play Again?", "Play another?"): 
            self.score = 0; self.q_count = 0; self.difficulty = 0; self.right_count = 0; self.wrong_count = 0; self.show_frame("Menu")
        else: self.root.destroy()

# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MathQuizApp(root)
    root.mainloop()