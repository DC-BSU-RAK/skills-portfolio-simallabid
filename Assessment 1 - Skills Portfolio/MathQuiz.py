import tkinter as tk
from tkinter import messagebox
import random
import tkinter.font as tkFont

# --- Core Logic Functions ---
def randomInt(d):
    """Determines min/max values based on difficulty (1-digit, 2-digit, 4-digit)."""
    if d == 1: return random.randint(1, 9), random.randint(1, 9)
    if d == 2: return random.randint(10, 99), random.randint(10, 99)
    if d == 3: return random.randint(1000, 9999), random.randint(1000, 9999)
    return 0, 0
def decideOperation(): return random.choice(['+', '-'])
def isCorrect(ans, n1, n2, op):
    """Checks if the answer is correct."""
    try: return int(ans) == (n1 + n2 if op == '+' else n1 - n2)
    except ValueError: return False
def displayResults(s):
    """Calculates rank based on score (out of 100)."""
    if s >= 90: return "A+ (Excellent!)"
    if s >= 80: return "A (Great job!)"
    if s >= 70: return "B (Good effort)"
    return "C (Keep practicing)"

# --- GUI Class ---
class MathQuizApp:
    def __init__(self, root):
        self.root = root; root.title("Mental Math Cards"); root.geometry("400x600")
        root.resizable(True, True); root.configure(bg="#E6F9E6")
        
        # Init state (Shortened variable names)
        self.score, self.q_count, self.difficulty, self.attempts = 0, 0, 0, 0
        self.r_count, self.w_count = 0, 0 
        self.ans_val, self.timer_id, self.time_left = None, None, 0
        self.n1, self.n2, self.op = None, None, None

        # Define fonts
        self.h_font = tkFont.Font(family="Helvetica", size=30, weight="bold")
        self.t_font = tkFont.Font(family="Arial", size=18)
        self.b_font = tkFont.Font(family="Arial", size=20, weight="bold")
        self.k_font = tkFont.Font(family="Arial", size=18, weight="bold")
        self.n_font = ('Arial', 50, 'bold')
        self.f_font = tkFont.Font(family="Arial", size=100, weight="bold")

        # Setup frames
        self.frames = {}; names = ["Welcome", "Instructions", "Menu", "Quiz"]
        for name in names:
            frame = tk.Frame(root, bg="#E6F9E6"); self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        root.grid_rowconfigure(0, weight=1); root.grid_columnconfigure(0, weight=1)

        self.ans_disp = tk.StringVar(root, value="")
        self.create_welcome_page(); self.create_instructions_page()
        self.create_menu_page(); self.create_quiz_page()
        self.show_frame("Welcome")

    def show_frame(self, name): self.frames[name].tkraise()
    def end_timer(self):
        if self.timer_id: self.root.after_cancel(self.timer_id); self.timer_id = None
        
    def create_welcome_page(self):
        frame = self.frames["Welcome"]
        frame.grid_rowconfigure((0, 2), weight=1); frame.grid_columnconfigure(0, weight=1)
        content = tk.Frame(frame, bg="#E6F9E6"); content.grid(row=1, column=0)
        tk.Label(content, text="Welcome to\nMental Math Cards", font=self.h_font, bg="#E6F9E6").pack(pady=(0, 50))
        tk.Button(content, text="Start", font=self.b_font, command=lambda: self.show_frame("Instructions"), bg="#6B8E23", fg="white", relief="flat", padx=30, pady=10).pack(pady=20)

    def create_instructions_page(self):
        frame = self.frames["Instructions"]
        frame.grid_rowconfigure(2, weight=1); frame.grid_columnconfigure(0, weight=1)
        tk.Button(frame, text="<", font=('Arial', 24), command=lambda: self.show_frame("Welcome"), bg="#E6F9E6", bd=0).grid(row=0, column=0, sticky='nw', padx=10, pady=10) 
        content = tk.Frame(frame, bg="#E6F9E6"); content.grid(row=1, column=0, sticky="ew", padx=20)
        tk.Label(content, text="Instructions", font=self.h_font, bg="#E6F9E6").pack(pady=(10, 40))
        instr = ["1. Select a difficulty level.", "2. Answer 10 problems in 20 seconds each.", "3. 10/5 points for 1st/2nd correct attempt.", "4. Use the on-screen keypad to enter answers."]
        for text in instr: tk.Label(content, text=text, font=self.t_font, bg="#E6F9E6", justify="center", wraplength=450).pack(fill="x", padx=20, pady=5)
        tk.Button(content, text="Next", font=self.b_font, command=lambda: self.show_frame("Menu"), bg="#7FFF7F", relief="solid", borderwidth=2, padx=40, pady=10).pack(pady=40)
    
    def create_menu_page(self):
        frame = self.frames["Menu"]
        frame.grid_rowconfigure((1, 3), weight=1); frame.grid_columnconfigure(0, weight=1)
        tk.Button(frame, text="<", font=('Arial', 24), command=lambda: self.show_frame("Instructions"), bg="#E6F9E6", bd=0).grid(row=0, column=0, sticky='nw', padx=10, pady=10) 
        content = tk.Frame(frame, bg="#E6F9E6"); content.grid(row=2, column=0, sticky="ew", padx=20)
        content.grid_columnconfigure(0, weight=1)
        tk.Label(content, text="🔢 Difficulty Level", font=self.h_font, bg="#E6F9E6").pack(pady=(0, 30))
        levels = [("1. Easy (1-digit)", 1), ("2. Moderate (2-digit)", 2), ("3. Advanced (4-digit)", 3)]
        for text, level in levels: 
            tk.Button(content, text=text, font=self.b_font, command=lambda l=level: self.start_quiz(l), 
                      bg="#FFC0CB", relief="raised", padx=20, pady=10).pack(pady=15, ipadx=20, fill='x')

    def create_quiz_page(self):
        frame = self.frames["Quiz"]
        frame.grid_rowconfigure(2, weight=1); frame.grid_columnconfigure(0, weight=1)
        
        # ROW 0: TOP STATUS BAR
        s_frame = tk.Frame(frame, bg="#E6F9E6"); s_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)
        tk.Button(s_frame, text="<", font=('Arial', 24), command=self.quit_quiz, bg="#E6F9E6", bd=0).pack(side='left', padx=(0, 20))
        st_frame = tk.Frame(s_frame, bg="#E6F9E6"); st_frame.pack(side='right')
        sc_q_frame = tk.Frame(s_frame, bg="#E6F9E6"); sc_q_frame.pack(side='left', padx=10)

        tk.Label(st_frame, text="RIGHT:", font=('Arial', 14, 'bold'), fg="green", bg="#E6F9E6").pack(side='left', padx=(5, 0))
        self.r_label = tk.Label(st_frame, text="0", font=('Arial', 14, 'bold'), fg="green", bg="#E6F9E6"); self.r_label.pack(side='left')
        tk.Label(st_frame, text="| WRONG:", font=('Arial', 14, 'bold'), fg="red", bg="#E6F9E6").pack(side='left', padx=(5, 0))
        self.w_label = tk.Label(st_frame, text="0", font=('Arial', 14, 'bold'), fg="red", bg="#E6F9E6"); self.w_label.pack(side='left')
        self.t_label = tk.Label(st_frame, text="TIME: 20", font=('Arial', 14, 'bold'), fg="black", bg="#E6F9E6"); self.t_label.pack(side='right', padx=(10, 0))
        
        self.s_label = tk.Label(sc_q_frame, text="Score: 0", font=('Arial', 22, 'bold'), bg="#E6F9E6"); self.s_label.pack(side='left')
        self.q_label = tk.Label(sc_q_frame, font=('Arial', 18, 'bold'), bg="#E6F9E6"); self.q_label.pack(side='right', padx=(20, 0))

        # ROW 1: MATH PROBLEM DISPLAY
        p_area = tk.Frame(frame, bg="#E6F9E6"); p_area.grid(row=1, column=0, pady=10, sticky='n') 
        self.n1_label = tk.Label(p_area, text="", font=self.n_font, bg="#E6F9E6"); self.n1_label.pack(anchor='e', padx=20)
        op_frame = tk.Frame(p_area, bg="#E6F9E6"); op_frame.pack(fill='x')
        self.op_label = tk.Label(op_frame, text="", font=self.n_font, bg="#E6F9E6"); self.op_label.pack(side='left')
        self.n2_label = tk.Label(op_frame, text="", font=self.n_font, bg="#E6F9E6"); self.n2_label.pack(side='right', padx=20)
        tk.Frame(p_area, height=3, bg="black").pack(fill='x', pady=5)
        self.ans_label = tk.Label(p_area, textvariable=self.ans_disp, font=self.n_font, bg="#E6F9E6", width=8, anchor='e'); self.ans_label.pack(pady=10)
        
        self.f_label = tk.Label(p_area, text="", font=self.f_font, bg="#E6F9E6")
        self.f_label.place(relx=0.5, rely=0.5, anchor='center')

        # ROW 2: KEYPAD
        k_frame = tk.Frame(frame, bg="#E6F9E6"); k_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'Clear', '0', 'Check']
        for i in range(4): k_frame.grid_rowconfigure(i, weight=1)
        for i in range(3): k_frame.grid_columnconfigure(i, weight=1)
        
        for i, key in enumerate(keys):
            r, c = divmod(i, 3)
            if key.isdigit(): cmd = lambda k=key: self.key_press(k); bg, fg = "white", "black"
            elif key == 'Clear': cmd = self.clear_answer; bg, fg = "#808080", "white"
            elif key == 'Check': cmd = self.handle_input; bg, fg = "#FF8C00", "white"
            tk.Button(k_frame, text=key, font=self.k_font, command=cmd, 
                      bg=bg, fg=fg, relief="raised", bd=2).grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

    def show_feedback(self, symbol, color):
        """Displays a visual feedback symbol temporarily."""
        self.f_label.config(text=symbol, fg=color); self.f_label.lift()
        self.root.after(500, self.hide_feedback)

    def hide_feedback(self):
        """Hides the visual feedback label."""
        self.f_label.config(text=""); self.f_label.lower()

    def quit_quiz(self):
        if messagebox.askyesno("Quit Quiz", "Are you sure you want to quit the current quiz?"):
            self.end_timer()
            self.score, self.q_count, self.difficulty, self.r_count, self.w_count = 0, 0, 0, 0, 0
            self.show_frame("Menu")

    def key_press(self, key):
        current = self.ans_disp.get()
        if len(current) < 5: self.ans_disp.set(current + key)

    def clear_answer(self): self.ans_disp.set("")

    def start_quiz(self, level):
        self.difficulty = level; self.score, self.q_count = 0, 0
        self.r_count, self.w_count = 0, 0
        self.show_frame("Quiz"); self.present_problem()

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
            self.show_feedback('❌', 'red'); self.w_count += 1
            messagebox.showerror("Time's Up!", f"Out of time! Answer: {self.ans_val}.")
            self.present_problem()

    def present_problem(self):
        self.hide_feedback()
        self.end_timer()
        if self.q_count >= 10: self.end_quiz(); return

        self.q_count += 1; self.generate_problem(); self.time_left = 20
        self.q_label.config(text=f"Question {self.q_count} of 10")
        self.n1_label.config(text=str(self.n1))
        self.op_label.config(text=self.op)
        self.n2_label.config(text=str(self.n2))
        self.clear_answer()
        self.s_label.config(text=f"Score: {self.score}")
        self.r_label.config(text=str(self.r_count)); self.w_label.config(text=str(self.w_count))
        self.update_timer()
        
    def handle_input(self):
        self.end_timer()
        user_input = self.ans_disp.get()
        if not user_input: 
            messagebox.showerror("Error", "Enter an answer."); self.update_timer() 
            return
            
        if isCorrect(user_input, self.n1, self.n2, self.op):
            points = 10 if self.attempts == 0 else 5; self.score += points
            self.r_count += 1
            self.show_feedback('✅', 'green')
            messagebox.showinfo("Correct!", f"🎉 Correct! (+{points} pts)")
            self.present_problem()
        else:
            self.show_feedback('❌', 'red')
            self.attempts += 1
            if self.attempts == 1: 
                messagebox.showerror("Incorrect!", "❌ Incorrect. One more chance (+5 pts).")
                self.clear_answer(); self.update_timer()
            else: 
                self.w_count += 1
                messagebox.showerror("Wrong Again!", f"💔 Incorrect. Answer: {self.ans_val}.")
                self.present_problem()
                
    def end_quiz(self):
        self.end_timer()
        rank = displayResults(self.score)
        if messagebox.askyesno("Quiz Finished!", f"🏆 Quiz Complete!\nScore: {self.score}/100.\nRank: {rank}\n\nPlay another?"): 
            self.score, self.q_count, self.difficulty, self.r_count, self.w_count = 0, 0, 0, 0, 0
            self.show_frame("Menu")
        else: self.root.destroy()

# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MathQuizApp(root)
    root.mainloop()