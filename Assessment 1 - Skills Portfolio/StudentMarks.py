import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import scrolledtext
from tkinter import font as tkFont # Import font module for custom fonts

# --- Data Structure for Student Records (remains the same) ---
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
        """Determines the student's grade based on percentage."""
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
        # Enhanced formatting for better readability
        return (
            f"  Name: {self.name}\n"
            f"  Number: {self.student_number}\n"
            f"  Coursework: {self.get_coursework_total():<3} / 60\n"
            f"  Exam Mark: {self.exam_mark:<3} / 100\n"
            f"  Overall %: {self.get_percentage():<6.2f}%\n"
            f"  Grade: {self.get_grade()}\n"
            f"{'=' * 35}" # Separator for individual records
        )

# --- Data Loading Function (remains the same) ---
def load_student_data(filename='studentMarks.txt'):
    """
    Loads student data from the specified file into a list of Student objects.
    Returns: A tuple (list of Student objects, number of students) or (None, 0) on error.
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
        messagebox.showerror("File Error", f"The file '{filename}' was not found. Please ensure it is in the correct directory.")
        return None, 0
    except ValueError as e:
        messagebox.showerror("Data Error", f"Error processing data: {e}. Check the format of the first line.")
        return None, 0
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        return None, 0

# --- Tkinter Application Class ---
class StudentManagerApp:
    def __init__(self, master):
        self.master = master
        master.title("Student Manager Dashboard")
        master.geometry("700x700") # Set initial window size
        master.resizable(True, True) # Allow resizing

        # --- Color Palette ---
        self.primary_bg = "#2C3E50" # Dark Blue-Grey
        self.secondary_bg = "#34495E" # Slightly lighter Blue-Grey
        self.accent_color = "#1ABC9C" # Turquoise/Teal
        self.text_color = "#ECF0F1" # Light Grey
        self.highlight_color = "#3498DB" # Brighter Blue for emphasis
        self.output_bg = "#ECF0F1" # Very light grey for output area
        self.output_fg = "#2C3E50" # Dark text for output

        master.config(bg=self.primary_bg) # Set main window background

        # --- Custom Fonts ---
        self.title_font = tkFont.Font(family="Helvetica Neue", size=20, weight="bold")
        self.header_font = tkFont.Font(family="Helvetica Neue", size=14, weight="bold")
        self.body_font = tkFont.Font(family="Fira Code", size=11) # Monospace for output readability
        self.menu_font = tkFont.Font(family="Helvetica Neue", size=11)


        # Load data immediately upon starting the app
        self.students, self.num_students = load_student_data()
        
        if not self.students:
            messagebox.showerror("Initialization Error", "Could not load student data. Application will be limited.")
            self.students = []
            self.num_students = 0

        # --- GUI Setup ---
        # Title Label
        self.title_label = tk.Label(master, 
                                     text="Student Performance Manager", 
                                     font=self.title_font, 
                                     bg=self.primary_bg, 
                                     fg=self.accent_color)
        self.title_label.pack(pady=(20, 15)) # More vertical padding

        # Output Text Area (ScrolledText for multi-line output)
        self.output_area = scrolledtext.ScrolledText(master, 
                                                     width=70, 
                                                     height=20, 
                                                     wrap=tk.WORD, 
                                                     font=self.body_font,
                                                     bg=self.output_bg,
                                                     fg=self.output_fg,
                                                     padx=10,
                                                     pady=10,
                                                     bd=2, # Border for definition
                                                     relief=tk.FLAT) # Flat border
        self.output_area.pack(padx=20, pady=10, fill=tk.BOTH, expand=True) # Fill and expand
        self.output_area.insert(tk.END, f"Welcome to the Student Manager!\n\n")
        self.output_area.insert(tk.END, f"Successfully loaded {self.num_students} student records from 'studentMarks.txt'.\n")
        self.output_area.insert(tk.END, f"Please select an action from the 'Actions' menu above.")
        self.output_area.config(state=tk.DISABLED) # Make it read-only
        
        # --- Menu Bar Setup ---
        menubar = tk.Menu(master, bg=self.secondary_bg, fg=self.text_color, 
                          font=self.menu_font, relief=tk.FLAT)
        master.config(menu=menubar)

        action_menu = tk.Menu(menubar, tearoff=0, 
                             bg=self.secondary_bg, fg=self.text_color, 
                             activebackground=self.highlight_color, 
                             activeforeground="white", font=self.menu_font,
                             relief=tk.FLAT, bd=0) # Flat and no border for menu

        menubar.add_cascade(label="Actions", menu=action_menu, 
                            activebackground=self.highlight_color, 
                            activeforeground="white") # Highlight main menu item

        action_menu.add_command(label="1. View All Student Records", command=self.view_all_records)
        action_menu.add_command(label="2. View Individual Student Record", command=self.view_individual_record)
        action_menu.add_separator(background=self.primary_bg) # Separator with background
        action_menu.add_command(label="3. Show Student with Highest Total Score", command=self.show_highest_score)
        action_menu.add_command(label="4. Show Student with Lowest Total Score", command=self.show_lowest_score)
        action_menu.add_separator(background=self.primary_bg)
        action_menu.add_command(label="Exit Application", command=master.quit) # More descriptive exit label

        # --- Status Bar (optional but good for aesthetics) ---
        self.status_bar = tk.Label(master, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                    bg=self.secondary_bg, fg=self.text_color, font=('Helvetica Neue', 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _clear_output(self, title):
        """Clears the output area and prints a title with enhanced styling."""
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete(1.0, tk.END)
        
        # Title for the output area
        self.output_area.insert(tk.END, f"{'='*10} {title.upper()} {'='*10}\n\n", "header_style") # Use a tag for styling
        self.output_area.tag_config("header_style", font=self.header_font, foreground=self.accent_color)
        
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
            f"  Number of Students: {self.num_students}\n"
            f"  Average Percentage: {average_percentage:.2f}%\n"
            f"{'=' * 35}"
        )
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, summary, "summary_style")
        self.output_area.tag_config("summary_style", font=self.header_font, foreground=self.highlight_color)
        self.output_area.config(state=tk.DISABLED)

    # --- Menu Item 1: View all student records ---
    def view_all_records(self):
        """Displays all student records and the class summary."""
        if not self.students:
            messagebox.showinfo("Info", "No student data available to display.")
            self.status_bar.config(text="Status: No data loaded.")
            return

        self._clear_output("All Student Records")
        self.output_area.config(state=tk.NORMAL) # Enable writing

        for student in self.students:
            self.output_area.insert(tk.END, student.get_formatted_record() + "\n\n") # Added extra newlines for spacing
        
        self._display_summary()
        self.output_area.config(state=tk.DISABLED) # Disable writing again
        self.status_bar.config(text="Status: Displayed all student records.")

    # --- Menu Item 2: View individual student record ---
    def view_individual_record(self):
        """Prompts for student number/name and displays the matching record."""
        if not self.students:
            messagebox.showinfo("Info", "No student data available.")
            self.status_bar.config(text="Status: No data loaded.")
            return

        # Simpledialog can't be styled much, but will inherit system theme or Tkinter's basic colors.
        search_term = simpledialog.askstring(
            "Search Student", 
            "Enter Student Number (e.g., 8439) or Student Name:", 
            parent=self.master
        )

        if search_term is None or search_term.strip() == "":
            self.status_bar.config(text="Status: Individual search cancelled.")
            return # User cancelled or entered nothing

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
            self.output_area.tag_config("error_message", foreground="red", font=self.body_font)
            self.status_bar.config(text=f"Status: No record found for '{search_term}'.")
        
        self.output_area.config(state=tk.DISABLED)

    # --- Menu Item 3: Show student with highest total score ---
    def show_highest_score(self):
        """Finds and displays the student with the highest total score."""
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

    # --- Menu Item 4: Show student with lowest total score ---
    def show_lowest_score(self):
        """Finds and displays the student with the lowest total score."""
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