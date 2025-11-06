import tkinter as tk
from tkinter import messagebox
import random

# --- Global Configuration ---
QUIZ_LENGTH = 10
SCORE_FIRST_ATTEMPT = 10
SCORE_SECOND_ATTEMPT = 5
QUESTION_TIME_LIMIT = 20

# Difficulty settings: (min_digits, max_digits)
DIFFICULTY_LEVELS = {
    "easy": (1, 1),      # Single digit (1 to 9)
    "moderate": (2, 2),  # Double digit (10 to 99)
    "advanced": (4, 4)   # Four digit (1000 to 9999)
}

# --- Font Definitions ---
LARGE_FONT = ('Arial', 24, 'bold')
MEDIUM_FONT = ('Arial', 18)
TITLE_FONT = ('Arial', 36, 'bold')
TIMER_FONT = ('Courier', 20, 'bold')

# --- Core Quiz Functions ---
def randomInt(difficulty):
    min_digits, max_digits = DIFFICULTY_LEVELS[difficulty]
    min_val = 10**(min_digits - 1)
    max_val = (10**max_digits) - 1
    if min_digits == 1: min_val = 1
    return random.randint(min_val, max_val)

def decideOperation():
    return random.choice(['+', '-'])

def isCorrect(user_answer, correct_answer):
    try: return int(user_answer) == correct_answer
    except ValueError: return False

def calculate_grade(score):
    if score > 90: return "A+ (Outstanding)"
    if score > 80: return "A (Excellent)"
    if score > 70: return "B (Good)"
    if score > 60: return "C (Pass)"
    return "F (Needs Practice)"

# --- Tkinter Application Class ---
class MathQuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Arithmetic Maths Quiz")
        self.geometry("800x800")
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.shared_data = {"score": 0, "question_num": 0, "current_difficulty": None}
        
        for F in (WelcomeFrame, DifficultyFrame, GameFrame, ResultsFrame):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomeFrame")

    def show_frame(self, page_name, difficulty=None):
        if hasattr(self.frames.get("GameFrame"), 'cancel_timer'):
            self.frames["GameFrame"].cancel_timer()

        frame = self.frames[page_name]
        
        if difficulty:
            self.shared_data["current_difficulty"] = difficulty
            self.shared_data["score"] = 0
            self.shared_data["question_num"] = 0
            self.frames["GameFrame"].setup_new_question()
            frame = self.frames["GameFrame"]
        elif page_name == "ResultsFrame":
            frame.displayResults()
        elif page_name == "DifficultyFrame":
            frame.displayMenu()
            
        frame.tkraise()

# --- Base Frame for Back Button ---
class BaseQuizFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.grid_rowconfigure((0, 8), weight=1)
        self.grid_columnconfigure((0, 2), weight=1)

    def add_back_button(self, target_frame):
        tk.Button(self, text="⬅️ Back", command=lambda: self.controller.show_frame(target_frame), 
                  font=('Arial', 12), bg='#90A4AE', fg='white', width=10).grid(row=0, column=0, sticky="nw", padx=10, pady=10)

# --- Frame 1: Welcome Page ---
class WelcomeFrame(BaseQuizFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        tk.Label(self, text="🧠 Welcome to the Maths Quiz! 🔢", font=TITLE_FONT).grid(row=2, column=1, pady=(150, 40))
        tk.Button(self, text="▶️ Play Now", command=lambda: controller.show_frame("DifficultyFrame"), 
                  width=20, height=3, font=MEDIUM_FONT, bg='#4CAF50', fg='white').grid(row=3, column=1, pady=15)
        tk.Button(self, text="🔊 Sound (TBD)", command=lambda: messagebox.showinfo("Feature", "Sound functionality not yet implemented."), 
                  width=20, height=3, font=MEDIUM_FONT, bg='#2196F3', fg='white').grid(row=4, column=1, pady=15)

# --- Frame 2: Difficulty Selection ---
class DifficultyFrame(BaseQuizFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.add_back_button("WelcomeFrame")
        tk.Label(self, text="Select Difficulty Level:", font=LARGE_FONT).grid(row=1, column=1, pady=(100, 20))
        tk.Button(self, text="1. Easy (Single Digit)", command=lambda: controller.show_frame("GameFrame", "easy"), 
                  width=25, height=2, font=MEDIUM_FONT, bg='#aaffaa').grid(row=2, column=1, pady=15)
        tk.Button(self, text="2. Moderate (Double Digit)", command=lambda: controller.show_frame("GameFrame", "moderate"), 
                  width=25, height=2, font=MEDIUM_FONT, bg='#ffffaa').grid(row=3, column=1, pady=15)
        tk.Button(self, text="3. Advanced (Four Digit)", command=lambda: controller.show_frame("GameFrame", "advanced"), 
                  width=25, height=2, font=MEDIUM_FONT, bg='#ffaaaa').grid(row=4, column=1, pady=15)
    
    def displayMenu(self):
        messagebox.showinfo("Instructions", f"You will be asked {QUIZ_LENGTH} questions.\n\n"
                            f"Time: {QUESTION_TIME_LIMIT} seconds per question!\n"
                            f" - {SCORE_FIRST_ATTEMPT} pts (1st try)\n"
                            f" - {SCORE_SECOND_ATTEMPT} pts (2nd try)")

# --- Frame 3: Game Frame (Consolidated Logic) ---
class GameFrame(BaseQuizFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.correct_answer, self.attempt_count, self.timer_id = None, 0, None
        self.time_left = QUESTION_TIME_LIMIT
        self.add_back_button("DifficultyFrame")
        
        self.timer_label = tk.Label(self, text="", font=TIMER_FONT, fg='red')
        self.timer_label.grid(row=0, column=2, sticky="ne", padx=10, pady=10)
        self.score_label = tk.Label(self, text="", font=('Arial', 14))
        self.score_label.grid(row=1, column=1, pady=(20, 10))
        self.difficulty_label = tk.Label(self, text="", font=MEDIUM_FONT, fg='gray')
        self.difficulty_label.grid(row=2, column=1, pady=(0, 20))
        self.question_label = tk.Label(self, text="", font=TITLE_FONT, fg='blue')
        self.question_label.grid(row=3, column=1, pady=20)
        self.answer_entry = tk.Entry(self, font=LARGE_FONT, justify='center', width=10)
        self.answer_entry.grid(row=4, column=1, pady=10)
        self.submit_button = tk.Button(self, text="Submit Answer", command=self.check_answer, width=20, height=2, font=MEDIUM_FONT, bg='#FF9800', fg='white')
        self.submit_button.grid(row=5, column=1, pady=20)
        self.feedback_label = tk.Label(self, text="", font=MEDIUM_FONT)
        self.feedback_label.grid(row=6, column=1, pady=10)
        self.hint_label = tk.Label(self, text="", font=('Arial', 14), fg='darkgreen', wraplength=400)
        self.hint_label.grid(row=7, column=1, pady=(5, 20))

    def start_timer(self):
        self.time_left = QUESTION_TIME_LIMIT
        self.timer_label.config(fg='red', text=f"Time: {QUESTION_TIME_LIMIT}s")
        self.update_timer()

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"Time: {self.time_left}s")
            self.timer_id = self.after(1000, self.update_timer)
        else: self.handle_timeout()

    def cancel_timer(self):
        if self.timer_id: self.after_cancel(self.timer_id); self.timer_id = None
            
    def handle_timeout(self):
        self.timer_label.config(text="TIME UP!", bg='yellow')
        messagebox.showerror("Time Out", f"Time is up! The correct answer was {self.correct_answer}.")
        self.submit_button.config(state=tk.DISABLED)
        self.after(1000, self.setup_new_question)

    def generate_hint(self, n1, n2, op):
        if op == '+': return f"Hint: Try starting from {max(n1, n2)} and counting up."
        if self.correct_answer >= 0: return f"Hint: To find {n1} - {n2}, try counting up from {n2} to {n1}."
        return f"Hint: When {n2} is larger than {n1}, the answer will be negative."

    def check_answer(self):
        self.cancel_timer()
        user_input = self.answer_entry.get().strip()
        self.attempt_count += 1
        
        if isCorrect(user_input, self.correct_answer):
            points = SCORE_FIRST_ATTEMPT if self.attempt_count == 1 else SCORE_SECOND_ATTEMPT
            self.controller.shared_data["score"] += points
            messagebox.showinfo("Feedback", f"Correct! +{points} points.")
            self.submit_button.config(state=tk.DISABLED)
            self.after(1000, self.setup_new_question)
        else:
            if self.attempt_count == 1:
                self.feedback_label.config(text="❌ Incorrect. Try again!", fg='red')
                self.answer_entry.delete(0, tk.END)
                self.submit_button.config(text="Submit Again (Last Chance)")
                
                q_parts = self.question_label.cget("text")[:-2].split()
                self.hint_label.config(text=self.generate_hint(int(q_parts[0]), int(q_parts[2]), q_parts[1]))
                self.start_timer()
            else:
                messagebox.showerror("Feedback", f"Incorrect. The correct answer was {self.correct_answer}.")
                self.submit_button.config(state=tk.DISABLED)
                self.after(1000, self.setup_new_question)

    def setup_new_question(self):
        self.cancel_timer()
        self.controller.shared_data["question_num"] += 1
        if self.controller.shared_data["question_num"] > QUIZ_LENGTH:
            self.controller.show_frame("ResultsFrame"); return
            
        self.attempt_count = 0
        self.answer_entry.delete(0, tk.END)
        self.feedback_label.config(text="", fg='black'); self.hint_label.config(text="")
        self.timer_label.config(bg=self['bg']); self.submit_button.config(text="Submit Answer", state=tk.NORMAL)
        
        difficulty = self.controller.shared_data["current_difficulty"]
        num1, num2, op = randomInt(difficulty), randomInt(difficulty), decideOperation()
        self.correct_answer = num1 + num2 if op == '+' else num1 - num2
        
        self.question_label.config(text=f"{num1} {op} {num2} =")
        self.score_label.config(text=f"Score: {self.controller.shared_data['score']} | Q: {self.controller.shared_data['question_num']}/{QUIZ_LENGTH}")
        self.difficulty_label.config(text=f"(Difficulty: {difficulty.upper()})")
        self.start_timer()

# --- Frame 4: Results Page ---
class ResultsFrame(BaseQuizFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.add_back_button("WelcomeFrame")
        tk.Label(self, text="🎉 Quiz Complete! 🎉", font=TITLE_FONT).grid(row=1, column=1, pady=40)
        self.score_label = tk.Label(self, text="", font=LARGE_FONT); self.score_label.grid(row=2, column=1, pady=10)
        self.grade_label = tk.Label(self, text="", font=('Arial', 28, 'italic'), fg='purple'); self.grade_label.grid(row=3, column=1, pady=20)
        tk.Button(self, text="Play Again", command=lambda: controller.show_frame("DifficultyFrame"), width=20, height=2, font=MEDIUM_FONT, bg='#4CAF50', fg='white').grid(row=4, column=1, pady=15)
        tk.Button(self, text="Exit", command=controller.quit, width=20, height=2, font=MEDIUM_FONT, bg='#F44336', fg='white').grid(row=5, column=1, pady=15)

    def displayResults(self):
        final_score = self.controller.shared_data["score"]
        possible_score = QUIZ_LENGTH * SCORE_FIRST_ATTEMPT
        self.score_label.config(text=f"Your final score: {final_score} / {possible_score}")
        self.grade_label.config(text=f"Your Rank: {calculate_grade(final_score)}")

if __name__ == "__main__":
    app = MathQuizApp()
    app.mainloop()