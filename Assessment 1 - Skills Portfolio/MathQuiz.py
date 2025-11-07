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
        root.resizable(True, True); root.configure(bg="#E6F9E6") # Light Green Theme
        
        self.score, self.q_count, self.difficulty, self.attempts = 0, 0, 0, 0
        self.right_count, self.wrong_count = 0, 0
        self.current_answer, self.timer_id, self.time_left = None, None, 0
        self.num1, self.num2, self.operation = None, None, None

        self.heading_font = tkFont.Font(family="Helvetica", size=30, weight="bold")
        self.text_font = tkFont.Font(family="Arial", size=18)
        self.button_font = tkFont.Font(family="Arial", size=20, weight="bold")

        self.frames = {}; names = ["Welcome", "Instructions", "Menu", "Quiz"]
        for name in names:
            frame = tk.Frame(root, bg="#E6F9E6"); self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        root.grid_rowconfigure(0, weight=1); root.grid_columnconfigure(0, weight=1)

        self.answer_display = tk.StringVar(root, value="")
        self.create_welcome_page(); self.create_instructions_page()
        self.create_menu_page(); self.create_quiz_page()
        self.show_frame("Welcome")

    def show_frame(self, name): self.frames[name].tkraise()

    def create_welcome_page(self):
        frame = self.frames["Welcome"]
        tk.Label(frame, text="Welcome to\nMental Math Cards", font=self.heading_font, bg="#E6F9E6").pack(pady=(150, 50))
        tk.Button(frame, text="Start", font=self.button_font, command=lambda: self.show_frame("Instructions"), bg="#6B8E23", fg="white", relief="flat", padx=30, pady=10).pack(pady=20)

    def create_instructions_page(self):
        frame = self.frames["Instructions"]
        tk.Button(frame, text="<", font=('Arial', 24), command=lambda: self.show_frame("Welcome"), bg="#E6F9E6", bd=0).pack(anchor='nw', padx=10, pady=10) 
        tk.Label(frame, text="Instructions", font=self.heading_font, bg="#E6F9E6").pack(pady=(10, 40))
        instructions = ["1. Select a difficulty level.", "2. Answer 10 problems in 20 seconds each.", "3. 10/5 points for 1st/2nd correct attempt.", "4. Use the on-screen keypad to enter answers."]
        for text in instructions: tk.Label(frame, text=text, font=self.text_font, bg="#E6F9E6", justify="left", wraplength=350).pack(fill="x", padx=40, pady=5)
        tk.Button(frame, text="Next", font=self.button_font, command=lambda: self.show_frame("Menu"), bg="#7FFF7F", relief="solid", borderwidth=2, padx=40, pady=10).pack(pady=40)
    
    def create_menu_page(self):
        frame = self.frames["Menu"]
        tk.Button(frame, text="<", font=('Arial', 24), command=lambda: self.show_frame("Instructions"), bg="#E6F9E6", bd=0).pack(anchor='nw', padx=10, pady=10) 
        tk.Label(frame, text="🔢 Difficulty Level", font=self.heading_font, bg="#E6F9E6").pack(pady=(10, 30))
        levels = [("1. Easy (1-digit)", 1), ("2. Moderate (2-digit)", 2), ("3. Advanced (4-digit)", 3)]
        for text, level in levels: tk.Button(frame, text=text, font=self.button_font, command=lambda l=level: self.start_quiz(l), bg="#FFC0CB", relief="raised", padx=20, pady=10).pack(pady=15, ipadx=20)

    def create_quiz_page(self):
        frame = self.frames["Quiz"]
        
        # --- TOP STATUS BAR ---
        status_frame = tk.Frame(frame, bg="#E6F9E6"); status_frame.pack(fill='x', padx=10, pady=5)
        tk.Button(status_frame, text="<", font=('Arial', 24), command=self.return_to_menu_from_quiz, bg="#E6F9E6", bd=0).pack(side='left', padx=(0, 20))

        stats_frame = tk.Frame(status_frame, bg="#E6F9E6"); stats_frame.pack(side='right')
        tk.Label(stats_frame, text="RIGHT:", font=('Arial', 14, 'bold'), fg="green", bg="#E6F9E6").pack(side='left', padx=(5, 0))
        self.right_label = tk.Label(stats_frame, text="0", font=('Arial', 14, 'bold'), fg="green", bg="#E6F9E6"); self.right_label.pack(side='left')
        tk.Label(stats_frame, text="| WRONG:", font=('Arial', 14, 'bold'), fg="red", bg="#E6F9E6").pack(side='left', padx=(5, 0))
        self.wrong_label = tk.Label(stats_frame, text="0", font=('Arial', 14, 'bold'), fg="red", bg="#E6F9E6"); self.wrong_label.pack(side='left')
        self.timer_label = tk.Label(stats_frame, text="TIME: 20", font=('Arial', 14, 'bold'), fg="black", bg="#E6F9E6"); self.timer_label.pack(side='right', padx=(10, 0))
        
        self.score_label = tk.Label(frame, text="Score: 0", font=('Arial', 22, 'bold'), bg="#E6F9E6"); self.score_label.pack(pady=(0, 20), anchor='w', padx=20)
        self.q_label = tk.Label(frame, font=('Arial', 18, 'bold'), bg="#E6F9E6"); self.q_label.pack(pady=(0, 5))

        # --- MATH PROBLEM DISPLAY (Stacked) ---
        problem_area = tk.Frame(frame, bg="#E6F9E6"); problem_area.pack(pady=10)
        self.num1_label = tk.Label(problem_area, text="", font=('Arial', 72, 'bold'), bg="#E6F9E6"); self.num1_label.pack(anchor='e', padx=20)
        
        op_frame = tk.Frame(problem_area, bg="#E6F9E6"); op_frame.pack(fill='x')
        self.op_label = tk.Label(op_frame, text="", font=('Arial', 72, 'bold'), bg="#E6F9E6"); self.op_label.pack(side='left')
        self.num2_label = tk.Label(op_frame, text="", font=('Arial', 72, 'bold'), bg="#E6F9E6"); self.num2_label.pack(side='right', padx=20)

        tk.Frame(problem_area, height=3, bg="black").pack(fill='x', pady=5)
        self.answer_label = tk.Label(problem_area, textvariable=self.answer_display, font=('Arial', 72, 'bold'), bg="#E6F9E6", width=5); self.answer_label.pack(pady=10)

        # --- KEYPAD ---
        keypad_frame = tk.Frame(frame, bg="#E6F9E6"); keypad_frame.pack(pady=10)
        keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'Clear', '0', 'Check']
        for i, key in enumerate(keys):
            r, c = divmod(i, 3)
            if key.isdigit():
                cmd = lambda k=key: self.key_press(k); btn_bg = "white"
            elif key == 'Clear':
                cmd = self.clear_answer; btn_bg = "#808080"
            elif key == 'Check':
                cmd = self.handle_input; btn_bg = "#FF8C00"
            
            tk.Button(keypad_frame, text=key, font=('Arial', 20, 'bold'), command=cmd, width=4, height=1, bg=btn_bg, fg="white" if key in ['Clear', 'Check'] else "black", relief="raised", bd=2).grid(row=r, column=c, padx=5, pady=5)


    def return_to_menu_from_quiz(self):
        if messagebox.askyesno("Quit Quiz", "Are you sure you want to quit the current quiz?"):
            if self.timer_id: self.root.after_cancel(self.timer_id)
            self.score = 0; self.q_count = 0; self.difficulty = 0
            self.right_count = 0; self.wrong_count = 0
            self.show_frame("Menu")

    def key_press(self, key):
        current = self.answer_display.get()
        max_len = 5 if self.difficulty == 3 else 3
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
            self.wrong_count += 1
            messagebox.showerror("Time's Up!", f"Out of time! Answer: {self.current_answer}.")
            self.present_problem()

    def present_problem(self):
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
        if self.timer_id: self.root.after_cancel(self.timer_id); self.timer_id = None
        user_input = self.answer_display.get()
        if not user_input: messagebox.showerror("Error", "Enter an answer."); self.update_timer(); return
            
        if isCorrect(user_input, self.num1, self.num2, self.operation):
            points = 10 if self.attempts == 0 else 5; self.score += points
            self.right_count += 1
            messagebox.showinfo("Correct!", f"🎉 Correct! (+{points} pts)")
            self.present_problem()
        else:
            self.attempts += 1
            if self.attempts == 1: 
                messagebox.showerror("Incorrect!", "❌ Incorrect. One more chance (+5 pts)."); self.clear_answer(); self.update_timer()
            else: 
                self.wrong_count += 1
                messagebox.showerror("Wrong Again!", f"💔 Incorrect. Answer: {self.current_answer}."); self.present_problem()
                
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