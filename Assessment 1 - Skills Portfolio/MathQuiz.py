import tkinter as tk
from tkinter import messagebox
import random
# --- NEW IMPORTS FOR IMAGE HANDLING ---
from PIL import Image, ImageTk 
# --------------------------------------

# --- Global Configuration ---
QUIZ_LENGTH = 10
SCORE_FIRST_ATTEMPT = 10
SCORE_SECOND_ATTEMPT = 5
QUESTION_TIME_LIMIT = 20 # Time limit in seconds

# Difficulty settings: (min_digits, max_digits)
DIFFICULTY_LEVELS = {
    "easy": (1, 1),      # Single digit (1 to 9)
    "moderate": (2, 2),  # Double digit (10 to 99)
    "advanced": (4, 4)   # Four digit (1000 to 9999)
}

# --- Font Definitions ---
LARGE_FONT = ('Arial', 24, 'bold')
MEDIUM_FONT = ('Arial', 18)
SMALL_FONT = ('Arial', 14)
TITLE_FONT = ('Arial', 36, 'bold')
TIMER_FONT = ('Courier', 20, 'bold')

# --- Core Quiz Functions ---
# ... (randomInt, decideOperation, isCorrect, calculate_grade functions remain unchanged)

def randomInt(difficulty):
    """
    Generates a random integer based on the selected difficulty.
    """
    min_digits, max_digits = DIFFICULTY_LEVELS[difficulty]
    
    min_val = 10**(min_digits - 1)
    max_val = (10**max_digits) - 1
    
    if min_digits == 1:
        min_val = 1 
        
    return random.randint(min_val, max_val)

def decideOperation():
    """
    Randomly decides between addition ('+') or subtraction ('-').
    """
    return random.choice(['+', '-'])

def isCorrect(user_answer, correct_answer):
    """
    Checks if the user's answer matches the correct answer.
    """
    try:
        return int(user_answer) == correct_answer
    except ValueError:
        return False

def calculate_grade(score):
    """
    Ranks the user based on their score out of 100.
    """
    if score > 90:
        return "A+ (Outstanding)"
    elif score > 80:
        return "A (Excellent)"
    elif score > 70:
        return "B (Good)"
    elif score > 60:
        return "C (Pass)"
    else:
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
        self.shared_data = {
            "score": 0,
            "question_num": 0,
            "current_difficulty": None
        }

        for F in (WelcomeFrame, DifficultyFrame, EasyGameFrame, ModerateGameFrame, AdvancedGameFrame, ResultsFrame):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomeFrame")

    def show_frame(self, page_name, difficulty=None):
        """Raises the desired frame to the top."""
        frame_key = page_name
        
        for f_key in ["EasyGameFrame", "ModerateGameFrame", "AdvancedGameFrame"]:
            if f_key in self.frames and hasattr(self.frames[f_key], 'cancel_timer'):
                self.frames[f_key].cancel_timer()

        if difficulty:
            self.shared_data["current_difficulty"] = difficulty
            self.shared_data["score"] = 0
            self.shared_data["question_num"] = 0
            
            if difficulty == "easy":
                frame_key = "EasyGameFrame"
            elif difficulty == "moderate":
                frame_key = "ModerateGameFrame"
            else: # advanced
                frame_key = "AdvancedGameFrame"
            
            frame = self.frames[frame_key]
            frame.setup_new_question()
            frame.tkraise()
            return
            
        frame = self.frames[frame_key]
        frame.tkraise()
        
        if page_name == "DifficultyFrame":
            self.frames[page_name].displayMenu()
        
        if page_name == "ResultsFrame":
            self.frames[page_name].displayResults()


# --- Base Frame for Back Button ---
class BaseQuizFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)
        self.grid_rowconfigure(5, weight=1)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

    def add_back_button(self, target_frame):
        """Adds a Back button to the frame."""
        tk.Button(self, text="⬅️ Back", command=lambda: self.controller.show_frame(target_frame), 
                  font=('Arial', 12), bg='#90A4AE', fg='white', width=10).grid(row=0, column=0, sticky="nw", padx=10, pady=10)

# --- Frame 1: Welcome Page ---

class WelcomeFrame(BaseQuizFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.logo_image = None
        self.logo_label = None

        # 1. Load the Image using Pillow (recommended for reliability)
        image_path = "classroom.gif"
        try:
            # Open the image file using PIL
            pil_image = Image.open(image_path)
            
            # OPTIONAL: Resize the image if needed:
            # pil_image = pil_image.resize((200, 200), Image.Resampling.LANCZOS)
            
            # Convert the PIL image to a format Tkinter can use
            self.logo_image = ImageTk.PhotoImage(pil_image)
            
        except FileNotFoundError:
            print(f"Error: Image file '{image_path}' not found. Check path and file name.")
            self.logo_image = None
        except Exception as e:
            # Handles issues like corrupted file or complex GIF features
            print(f"Error loading image via Pillow (check format): {e}")
            self.logo_image = None
            
        # 2. Display the Image using a Label (row=1, top-center)
        if self.logo_image:
            self.logo_label = tk.Label(self, image=self.logo_image, bg="white")
            self.logo_label.grid(row=1, column=1, pady=(50, 20), sticky="n")
        
        # Title (row=2, below image)
        tk.Label(self, text="🧠 Welcome to the Maths Quiz! 🔢", font=TITLE_FONT).grid(row=2, column=1, pady=20)

        # 'Play Now' Button (row=3, below title)
        tk.Button(self, text="▶️ Play Now", command=lambda: controller.show_frame("DifficultyFrame"), 
                  width=20, height=3, font=MEDIUM_FONT, bg='#4CAF50', fg='white').grid(row=3, column=1, pady=15)

        # 'Sound' Button (row=4, below 'Play Now')
        tk.Button(self, text="🔊 Sound (TBD)", command=lambda: messagebox.showinfo("Feature", "Sound functionality not yet implemented."), 
                  width=20, height=3, font=MEDIUM_FONT, bg='#2196F3', fg='white').grid(row=4, column=1, pady=15)
        
        # No back button on the Welcome screen

# --- Frame 2: Difficulty Selection ---

class DifficultyFrame(BaseQuizFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        self.add_back_button("WelcomeFrame")

        tk.Label(self, text="Select Difficulty Level:", font=LARGE_FONT).grid(row=1, column=1, pady=(40, 20))

        tk.Button(self, text="1. Easy (Single Digit)", command=lambda: controller.show_frame("EasyGameFrame", "easy"), 
                  width=25, height=2, font=MEDIUM_FONT, bg='#aaffaa').grid(row=2, column=1, pady=15)
                  
        tk.Button(self, text="2. Moderate (Double Digit)", command=lambda: controller.show_frame("ModerateGameFrame", "moderate"), 
                  width=25, height=2, font=MEDIUM_FONT, bg='#ffffaa').grid(row=3, column=1, pady=15)
                  
        tk.Button(self, text="3. Advanced (Four Digit)", command=lambda: controller.show_frame("AdvancedGameFrame", "advanced"), 
                  width=25, height=2, font=MEDIUM_FONT, bg='#ffaaaa').grid(row=4, column=1, pady=15)
        
    def displayMenu(self):
        messagebox.showinfo(
            "Instructions",
            f"You will be asked {QUIZ_LENGTH} arithmetic questions.\n\n"
            f"⚠️ **Timer:** You have {QUESTION_TIME_LIMIT} seconds per question!\n"
            f" - {SCORE_FIRST_ATTEMPT} points for the first correct attempt.\n"
            f" - {SCORE_SECOND_ATTEMPT} points for the second correct attempt.\n\n"
            "Good Luck!"
        )

# --- Base Game Frame (for frames 3, 4, 5) ---
# ... (BaseGameFrame and all other game/results frames remain unchanged)

class BaseGameFrame(BaseQuizFrame):
    def __init__(self, parent, controller, difficulty_key):
        super().__init__(parent, controller)
        self.difficulty = difficulty_key
        self.correct_answer = None
        self.attempt_count = 0
        self.timer_id = None
        self.time_left = QUESTION_TIME_LIMIT
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)
        self.grid_rowconfigure(5, weight=0)
        self.grid_rowconfigure(6, weight=0)
        self.grid_rowconfigure(7, weight=0)
        self.grid_rowconfigure(8, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        self.add_back_button("DifficultyFrame")
        
        self.timer_label = tk.Label(self, text=f"Time: {QUESTION_TIME_LIMIT}s", font=TIMER_FONT, fg='red')
        self.timer_label.grid(row=0, column=2, sticky="ne", padx=10, pady=10)
        
        self.score_label = tk.Label(self, text="Score: 0 | Q: 0/10", font=SMALL_FONT)
        self.score_label.grid(row=1, column=1, pady=(20, 10))
        
        self.difficulty_label = tk.Label(self, text=f"(Difficulty: {difficulty_key.upper()})", font=MEDIUM_FONT, fg='gray')
        self.difficulty_label.grid(row=2, column=1, pady=(0, 20))
        
        self.question_label = tk.Label(self, text="Loading question...", font=TITLE_FONT, fg='blue')
        self.question_label.grid(row=3, column=1, pady=20)
        
        self.answer_entry = tk.Entry(self, font=LARGE_FONT, justify='center', width=10)
        self.answer_entry.grid(row=4, column=1, pady=10)
        
        self.submit_button = tk.Button(self, text="Submit Answer", command=self.check_answer, 
                                        width=20, height=2, font=MEDIUM_FONT, bg='#FF9800', fg='white')
        self.submit_button.grid(row=5, column=1, pady=20)
        
        self.feedback_label = tk.Label(self, text="", font=MEDIUM_FONT)
        self.feedback_label.grid(row=6, column=1, pady=10)
        
        self.hint_label = tk.Label(self, text="", font=SMALL_FONT, fg='darkgreen', wraplength=400)
        self.hint_label.grid(row=7, column=1, pady=(5, 20))

    def start_timer(self):
        self.time_left = QUESTION_TIME_LIMIT
        self.timer_label.config(fg='red')
        self.update_timer()

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"Time: {self.time_left}s")
            self.timer_id = self.after(1000, self.update_timer)
        else:
            self.handle_timeout()

    def cancel_timer(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
            
    def handle_timeout(self):
        self.timer_label.config(text="TIME UP!", fg='red', bg='yellow')
        self.feedback_label.config(text=f"Time's up! The answer was {self.correct_answer}.", fg='red')
        messagebox.showerror("Time Out", f"Time is up! The correct answer was {self.correct_answer}. No points awarded.")
        
        self.submit_button.config(state=tk.DISABLED)
        self.after(1000, self.setup_new_question)

    def setup_new_question(self):
        self.cancel_timer()
        
        self.controller.shared_data["question_num"] += 1
        
        if self.controller.shared_data["question_num"] > QUIZ_LENGTH:
            self.controller.show_frame("ResultsFrame")
            return
            
        self.attempt_count = 0
        self.answer_entry.delete(0, tk.END)
        self.feedback_label.config(text="")
        self.hint_label.config(text="")
        self.timer_label.config(bg=self['bg'])
        self.submit_button.config(text="Submit Answer", state=tk.NORMAL)
        
        num1 = randomInt(self.difficulty)
        num2 = randomInt(self.difficulty)
        op = decideOperation()
        
        if op == '+':
            self.correct_answer = num1 + num2
        else:
            self.correct_answer = num1 - num2
        
        problem_text = f"{num1} {op} {num2} ="
        self.question_label.config(text=problem_text)
        
        self.score_label.config(text=f"Score: {self.controller.shared_data['score']} | Q: {self.controller.shared_data['question_num']}/{QUIZ_LENGTH}")
        
        self.start_timer()
        
    def generate_hint(self, num1, num2, op):
        if op == '+':
            return f"Hint: When adding, try starting from the largest number ({max(num1, num2)}) and count up."
        else:
            if self.correct_answer >= 0:
                return f"Hint: To find {num1} - {num2}, try counting up from {num2} to {num1}."
            else:
                return f"Hint: When the second number ({num2}) is larger than the first ({num1}), the answer will be negative."


    def check_answer(self):
        self.cancel_timer()
        user_input = self.answer_entry.get().strip()
        self.attempt_count += 1
        
        if isCorrect(user_input, self.correct_answer):
            self.feedback_label.config(text="✅ Correct!", fg='green')
            
            points = SCORE_FIRST_ATTEMPT if self.attempt_count == 1 else SCORE_SECOND_ATTEMPT
            messagebox.showinfo("Feedback", f"Correct! +{points} points.")
                
            self.controller.shared_data["score"] += points
            
            self.submit_button.config(state=tk.DISABLED)
            self.after(1000, self.setup_new_question)
            
        else:
            if self.attempt_count == 1:
                self.feedback_label.config(text="❌ Incorrect. Try again!", fg='red')
                self.answer_entry.delete(0, tk.END)
                self.submit_button.config(text="Submit Again (Last Chance)")
                
                question_text = self.question_label.cget("text")[:-2].split()
                hint = self.generate_hint(int(question_text[0]), int(question_text[2]), question_text[1])
                self.hint_label.config(text=hint)
                
                self.start_timer()
                
            else:
                self.feedback_label.config(text=f"❌ Incorrect. The answer was {self.correct_answer}.", fg='red')
                messagebox.showerror("Feedback", f"Incorrect. The correct answer was {self.correct_answer}. No points awarded for this question.")
                
                self.submit_button.config(state=tk.DISABLED)
                self.after(1000, self.setup_new_question)

# --- Frame 3, 4, 5: Difficulty Modes ---

class EasyGameFrame(BaseGameFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "easy")

class ModerateGameFrame(BaseGameFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "moderate")

class AdvancedGameFrame(BaseGameFrame):
    def __init__(self, parent, controller): 
        super().__init__(parent, controller, "advanced")

# --- Frame 6: Results Page ---

class ResultsFrame(BaseQuizFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        self.add_back_button("WelcomeFrame")
        
        tk.Label(self, text="🎉 Quiz Complete! 🎉", font=TITLE_FONT).grid(row=1, column=1, pady=40)
        
        self.score_label = tk.Label(self, text="", font=LARGE_FONT)
        self.score_label.grid(row=2, column=1, pady=10)
        
        self.grade_label = tk.Label(self, text="", font=('Arial', 28, 'italic'), fg='purple')
        self.grade_label.grid(row=3, column=1, pady=20)
        
        tk.Button(self, text="Play Again", command=lambda: controller.show_frame("DifficultyFrame"), 
                  width=20, height=2, font=MEDIUM_FONT, bg='#4CAF50', fg='white').grid(row=4, column=1, pady=15)
                  
        tk.Button(self, text="Exit", command=controller.quit, 
                  width=20, height=2, font=MEDIUM_FONT, bg='#F44336', fg='white').grid(row=5, column=1, pady=15)

    def displayResults(self):
        final_score = self.controller.shared_data["score"]
        possible_score = QUIZ_LENGTH * SCORE_FIRST_ATTEMPT
        grade = calculate_grade(final_score)
        
        self.score_label.config(text=f"Your final score: {final_score} / {possible_score}")
        self.grade_label.config(text=f"Your Rank: {grade}")

# --- Run the application ---

if __name__ == "__main__":
    app = MathQuizApp()
    app.mainloop()