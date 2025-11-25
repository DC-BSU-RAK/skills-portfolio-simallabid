import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import scrolledtext
from tkinter import font as tkFont

# Attempt to import Pygame for audio, handling potential import errors
try:
    import pygame
    pygame_available = True
except ImportError:
    pygame_available = False
    print("Warning: Pygame not installed. Audio features will be disabled.")


# --- Data Structure for Student Records ---
class Student:
    """Represents a single student's record and calculated results."""
    def __init__(self, student_number, name, course1, course2, course3, exam_mark):
        self.student_number = student_number
        self.name = name
        self.course1 = course1
        self.course2 = course2
        self.course3 = course3
        self.exam_mark = exam_mark

    def get_coursework_total(self):
        """Calculates the total coursework mark (max 60)."""
        return self.course1 + self.course2 + self.course3

    def get_overall_total(self):
        """Calculates the overall total mark (max 160)."""
        return self.get_coursework_total() + self.exam_mark

    def get_percentage(self):
        """Calculates the overall percentage based on 160 total marks."""
        return (self.get_overall_total() / 160) * 100

    def get_grade(self):
        """Determines the student's grade based on percentage (as per specs)."""
        percent = self.get_percentage()
        if percent >= 70:
            return 'A'
        elif percent >= 60:
            return 'B'
        elif percent >= 50:
            return 'C'
        elif percent >= 40:
            return 'D'
        else:
            return 'F'

    def get_formatted_record(self):
        """Returns a string with the full formatted record for display."""
        return (
            f"  Name: {self.name}\n"
            f"  Number: {self.student_number}\n"
            f"  Total Coursework: {self.get_coursework_total():<3} / 60\n"
            f"  Exam Mark: {self.exam_mark:<3} / 100\n"
            f"  Overall Percentage: {self.get_percentage():<6.2f}%\n"
            f"  Student Grade: {self.get_grade()}\n"
            f"{'=' * 35}"
        )

# --- Data Loading Function ---
def load_student_data(filename='studentMarks.txt'):
    """
    Loads student data from the specified file into a list of Student objects.
    """
    student_list = []
    num_students = 0
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            if not lines:
                raise ValueError("File is empty.")
            num_students = int(lines[0].strip())
            for line in lines[1:]:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) == 6:
                    student_number = parts[0]
                    name = parts[1]
                    try:
                        course1 = int(parts[2])
                        course2 = int(parts[3])
                        course3 = int(parts[4])
                        exam_mark = int(parts[5])
                        student_list.append(Student(student_number, name, course1, course2, course3, exam_mark))
                    except ValueError:
                        print(f"Skipping line due to invalid mark data: {line.strip()}")
                else:
                    print(f"Skipping line due to incorrect format: {line.strip()}")
        if len(student_list) != num_students:
              print(f"Warning: Expected {num_students} students, but loaded {len(student_list)}.")
        return student_list, len(student_list)
    except FileNotFoundError:
        messagebox.showerror("File Error", f"The file '{filename}' was not found.")
        return None, 0
    except ValueError as e:
        messagebox.showerror("Data Error", f"Error processing data: {e}. Check the file format.")
        return None, 0
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        return None, 0

# --- Tkinter Application Class ---
class StudentManagerApp:
    def __init__(self, master):
        self.master = master
        master.title("Student Manager Dashboard")
        master.geometry("850x750") 
        master.resizable(True, True)

        # --- Color Palette ---
        self.primary_bg = "#2C3E50"      # Dark Blue-Grey (Main window)
        self.action_panel_bg = "#34495E" # Lighter Blue-Grey (Action frame background)
        self.accent_color = "#1ABC9C"    # Turquoise/Teal (Title)
        self.button_color = "#3498DB"    # Bright Blue (Primary action buttons) 
        self.highlight_color = "#E74C3C" # Bright Red (Exit/Headers/Alerts)
        self.text_color = "#ECF0F1"      # Light Grey (All text)
        self.output_bg = "#ECF0F1"       # Very light grey (Output area background)
        self.output_fg = "#2C3E50"       # Dark text for output

        master.config(bg=self.primary_bg)

        # --- Custom Fonts ---
        self.title_font = tkFont.Font(family="Helvetica Neue", size=22, weight="bold")
        self.header_font = tkFont.Font(family="Helvetica Neue", size=16, weight="bold")
        self.button_font = tkFont.Font(family="Helvetica Neue", size=12, weight="bold") 
        self.body_font = tkFont.Font(family="Fira Code", size=11)
        
        # --- Audio Setup (Pygame Mixer) ---
        self.is_playing_audio = False
        self.click_sound = None # Initialize click sound variable
        if pygame_available:
            try:
                # Initialize mixer with recommended settings
                pygame.mixer.init(44100, -16, 2, 2048)
                
                # Load background music
                pygame.mixer.music.load('studentbg.mp3')
                pygame.mixer.music.play(-1) # Play indefinitely
                
                # Load click sound
                self.click_sound = pygame.mixer.Sound('studentclick.mp3')

                self.is_playing_audio = True
                print("Background music started.")
            except pygame.error as e:
                print(f"Pygame audio error (file missing or mixer failed): {e}")
                # Updated warning message to include both files
                messagebox.showwarning("Audio Warning", "Could not start background music or load sound effects. Ensure 'studentbg.mp3' and 'studentclick.mp3' are in the application directory.")
                self.is_playing_audio = False
        
        # --- Set up protocol handler for graceful exit (stops music) ---
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- Bind mouse click for sound effect ---
        if self.is_playing_audio and self.click_sound:
            # <Button-1> binds to the left mouse button click
            master.bind('<Button-1>', self.play_click_sound) 

        # Load data
        self.students, self.num_students = load_student_data()
        
        if not self.students:
            messagebox.showerror("Initialization Error", "Could not load student data.")
            self.students = []
            self.num_students = 0

        # --- GUI Layout (Grid System) ---
        
        # 1. Title Bar
        title_frame = tk.Frame(master, bg=self.primary_bg)
        title_frame.pack(side=tk.TOP, fill=tk.X)

        self.title_label = tk.Label(title_frame, 
                                    text="📊 Student Performance Dashboard", 
                                    font=self.title_font, 
                                    bg=self.primary_bg, 
                                    fg=self.accent_color,
                                    pady=15)
        self.title_label.pack()

        # 2. Main Content Frame (Uses Grid)
        content_frame = tk.Frame(master, bg=self.primary_bg)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        content_frame.grid_columnconfigure(0, weight=0) # Action Panel fixed width
        content_frame.grid_columnconfigure(1, weight=1) # Output Area expands
        content_frame.grid_rowconfigure(0, weight=1)

        # --- Action Panel (Column 0) ---
        self.action_frame = tk.Frame(content_frame, 
                                     bg=self.action_panel_bg, 
                                     padx=15, 
                                     pady=15,
                                     relief=tk.RAISED, 
                                     bd=3)
        self.action_frame.grid(row=0, column=0, sticky="nswe", padx=(0, 15))

        self.action_header = tk.Label(self.action_frame, 
                                     text="Action Center ⬇️", 
                                     font=self.header_font, 
                                     fg=self.highlight_color, 
                                     bg=self.action_panel_bg,
                                     pady=10)
        self.action_header.pack(fill=tk.X)
        
        # Function to create standardized, styled buttons
        def create_action_button(text, command):
            return tk.Button(self.action_frame,
                             text=text,
                             command=command,
                             font=self.button_font,
                             bg=self.button_color, # Use Bright Blue
                             fg=self.primary_bg, 
                             activebackground=self.highlight_color,
                             activeforeground="white",
                             relief=tk.FLAT,
                             bd=0,
                             padx=10, pady=10)

        # Create Buttons 
        self.btn_view_all = create_action_button("1. View All Records", self.view_all_records)
        self.btn_view_all.pack(fill=tk.X, pady=(5, 5))
        
        self.btn_view_individual = create_action_button("2. Search Student", self.view_individual_record)
        self.btn_view_individual.pack(fill=tk.X, pady=5)
        
        tk.Frame(self.action_frame, height=2, bg=self.primary_bg).pack(fill=tk.X, pady=10) # Separator
        
        self.btn_highest = create_action_button("3. Show Highest Score 🏆", self.show_highest_score)
        self.btn_highest.pack(fill=tk.X, pady=5)
        
        self.btn_lowest = create_action_button("4. Show Lowest Score 📉", self.show_lowest_score)
        self.btn_lowest.pack(fill=tk.X, pady=5)
        
        tk.Frame(self.action_frame, height=2, bg=self.primary_bg).pack(fill=tk.X, pady=10) # Separator
        
        self.btn_exit = create_action_button("Exit Application ❌", self.on_closing)
        self.btn_exit.config(bg=self.highlight_color, fg="white") # Use red highlight for exit
        self.btn_exit.pack(fill=tk.X, pady=(20, 5), side=tk.BOTTOM)
        
        # --- Output Display Area (Column 1) ---
        self.output_area = scrolledtext.ScrolledText(content_frame, 
                                                     width=50, 
                                                     height=30, 
                                                     wrap=tk.WORD, 
                                                     font=self.body_font,
                                                     bg=self.output_bg,
                                                     fg=self.output_fg,
                                                     padx=15,
                                                     pady=15,
                                                     bd=5, 
                                                     relief=tk.SUNKEN)
        self.output_area.grid(row=0, column=1, sticky="nswe")
        
        # Initial Welcome Message
        self.output_area.insert(tk.END, f"Welcome to the Student Manager!\n\n")
        self.output_area.insert(tk.END, f"Successfully loaded {self.num_students} student records.\n")
        self.output_area.insert(tk.END, f"Please use the **Action Center** on the left to begin.\n")
        self.output_area.config(state=tk.DISABLED)
        
        # --- Status Bar ---
        self.status_bar = tk.Label(master, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                   bg=self.action_panel_bg, fg=self.text_color, font=('Helvetica Neue', 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # --- Graceful Exit Handler (Stops audio) ---
    def on_closing(self):
        """Stops background music and destroys the window."""
        if self.is_playing_audio:
            pygame.mixer.music.stop()
        self.master.destroy()

    # --- New: Mouse Click Sound Player ---
    def play_click_sound(self, event):
        """Plays the click sound effect when the mouse button is pressed."""
        if self.click_sound:
            # Check if the click event originated from the output text area
            # We skip clicks on the output area to avoid noise when scrolling/selecting text.
            if event.widget != self.output_area:
                self.click_sound.play()

    # --- Helper Methods ---
    def _clear_output(self, title):
        """Clears the output area and prints a title with enhanced styling."""
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete(1.0, tk.END)
        
        self.output_area.insert(tk.END, f"{'='*10} {title.upper()} {'='*10}\n\n", "header_style")
        self.output_area.tag_config("header_style", font=self.header_font, foreground=self.highlight_color)
        
        self.output_area.config(state=tk.DISABLED)
        self.status_bar.config(text=f"Action: {title}")


    def _display_summary(self):
        """Calculates and displays the summary information with enhanced styling."""
        if not self.students:
            return

        total_percentage_sum = sum(s.get_percentage() for s in self.students)
        average_percentage = total_percentage_sum / self.num_students

        summary = (
            f"\n\n{'=' * 10} CLASS SUMMARY {'=' * 10}\n"
            f"  Number of Students: {self.num_students}\n"
            f"  Average Percentage: {average_percentage:.2f}%\n"
            f"{'=' * 35}"
        )
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, summary, "summary_style")
        self.output_area.tag_config("summary_style", font=self.header_font, foreground=self.accent_color)
        self.output_area.config(state=tk.DISABLED)

    # --- Action Methods ---
    def view_all_records(self):
        if not self.students:
            messagebox.showinfo("Info", "No student data available to display.")
            self.status_bar.config(text="Status: No data loaded.")
            return

        self._clear_output("All Student Records")
        self.output_area.config(state=tk.NORMAL)

        for student in self.students:
            self.output_area.insert(tk.END, student.get_formatted_record() + "\n\n")
        
        self._display_summary()
        self.output_area.config(state=tk.DISABLED)
        self.status_bar.config(text="Status: Displayed all student records.")

    def view_individual_record(self):
        if not self.students:
            messagebox.showinfo("Info", "No student data available.")
            self.status_bar.config(text="Status: No data loaded.")
            return

        search_term = simpledialog.askstring(
            "Search Student", 
            "Enter Student Number (e.g., 8439) or Student Name:", 
            parent=self.master
        )

        if search_term is None or search_term.strip() == "":
            self.status_bar.config(text="Status: Individual search cancelled.")
            return

        search_term = search_term.strip()
        found_student = None

        for student in self.students:
            if student.student_number == search_term:
                found_student = student
                break
            if search_term.lower() in student.name.lower():
                found_student = student
                break

        self._clear_output(f"Individual Student Record Search: '{search_term}'")
        self.output_area.config(state=tk.NORMAL)
        
        if found_student:
            self.output_area.insert(tk.END, "--- Match Found ---\n\n", "match_header")
            self.output_area.tag_config("match_header", font=self.header_font, foreground=self.accent_color)
            self.output_area.insert(tk.END, found_student.get_formatted_record())
            self.status_bar.config(text=f"Status: Found record for '{search_term}'.")
        else:
            self.output_area.insert(tk.END, "No student found with that Number or Name.", "error_message")
            self.output_area.tag_config("error_message", foreground=self.highlight_color, font=self.body_font)
            self.status_bar.config(text=f"Status: No record found for '{search_term}'.")
        
        self.output_area.config(state=tk.DISABLED)

    def show_highest_score(self):
        if not self.students:
            messagebox.showinfo("Info", "No student data available.")
            self.status_bar.config(text="Status: No data loaded.")
            return

        highest_scorer = max(self.students, key=lambda s: s.get_overall_total())

        self._clear_output("Student with Highest Overall Score")
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, highest_scorer.get_formatted_record())
        self.output_area.config(state=tk.DISABLED)
        self.status_bar.config(text=f"Status: Displayed highest scorer: {highest_scorer.name}.")

    def show_lowest_score(self):
        if not self.students:
            messagebox.showinfo("Info", "No student data available.")
            self.status_bar.config(text="Status: No data loaded.")
            return

        lowest_scorer = min(self.students, key=lambda s: s.get_overall_total())

        self._clear_output("Student with Lowest Overall Score")
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, lowest_scorer.get_formatted_record())
        self.output_area.config(state=tk.DISABLED)
        self.status_bar.config(text=f"Status: Displayed lowest scorer: {lowest_scorer.name}.")

# --- Main execution block ---
if __name__ == '__main__':
    root = tk.Tk()
    app = StudentManagerApp(root)
    root.mainloop()

    # Quit pygame mixer after Tkinter window closes
    if pygame_available:
        try:
            pygame.quit()
        except Exception:
            pass # Ignore if mixer wasn't initialized