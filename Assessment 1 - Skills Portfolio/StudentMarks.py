import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import scrolledtext

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
        return (
            f"Student Name: {self.name}\n"
            f"Student Number: {self.student_number}\n"
            f"Total Coursework Mark: {self.get_coursework_total()} / 60\n"
            f"Exam Mark: {self.exam_mark} / 100\n"
            f"Overall Percentage: {self.get_percentage():.2f}%\n"
            f"Student Grade: {self.get_grade()}\n"
            f"{'-' * 30}"
        )

# --- Data Loading Function ---
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

            # The first line is the number of students
            num_students = int(lines[0].strip())

            # Subsequent lines are student records
            for line in lines[1:]:
                # Example: 8439,Jake Hobbs,10,11,10,43
                parts = [p.strip() for p in line.split(',')]
                if len(parts) == 6:
                    student_number = parts[0]
                    name = parts[1]
                    # Marks are converted to integers
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

        # Basic check to ensure loaded data matches the count in the file
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
        master.title("Student Manager")

        # Load data immediately upon starting the app
        self.students, self.num_students = load_student_data()
        
        if not self.students:
            # If data loading fails, disable functionality and display an error
            messagebox.showerror("Initialization Error", "Could not load student data. Application will be limited.")
            self.students = []
            self.num_students = 0

        # --- GUI Setup ---
        self.label = tk.Label(master, text="Student Manager Application", font=('Arial', 14, 'bold'))
        self.label.pack(pady=10)
        
        # Output Text Area (ScrolledText for multi-line output)
        self.output_area = scrolledtext.ScrolledText(master, width=80, height=25, wrap=tk.WORD, font=('Courier', 10))
        self.output_area.pack(padx=10, pady=5)
        self.output_area.insert(tk.END, f"Loaded {self.num_students} student records from 'studentMarks.txt'.\nSelect an option from the menu above.")
        self.output_area.config(state=tk.DISABLED) # Make it read-only
        
        # --- Menu Bar Setup ---
        menubar = tk.Menu(master)
        master.config(menu=menubar)

        action_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Actions", menu=action_menu)
        action_menu.add_command(label="1. View All Student Records", command=self.view_all_records)
        action_menu.add_command(label="2. View Individual Student Record", command=self.view_individual_record)
        action_menu.add_separator()
        action_menu.add_command(label="3. Show Highest Total Score", command=self.show_highest_score)
        action_menu.add_command(label="4. Show Lowest Total Score", command=self.show_lowest_score)
        action_menu.add_separator()
        action_menu.add_command(label="Exit", command=master.quit)

    def _clear_output(self, title):
        """Clears the output area and prints a title."""
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete(1.0, tk.END)
        self.output_area.insert(tk.END, f"*** {title} ***\n\n")

    def _display_summary(self):
        """Calculates and displays the summary information."""
        if not self.students:
            return

        total_percentage_sum = sum(s.get_percentage() for s in self.students)
        average_percentage = total_percentage_sum / self.num_students

        summary = (
            f"\n{'-' * 30}\n"
            f"*** CLASS SUMMARY ***\n"
            f"Number of Students: {self.num_students}\n"
            f"Average Percentage Mark: {average_percentage:.2f}%\n"
            f"{'-' * 30}"
        )
        self.output_area.insert(tk.END, summary)
        self.output_area.config(state=tk.DISABLED)

    # --- Menu Item 1: View all student records ---
    def view_all_records(self):
        """Displays all student records and the class summary."""
        if not self.students:
            messagebox.showinfo("Info", "No student data available to display.")
            return

        self._clear_output("All Student Records")

        for student in self.students:
            self.output_area.insert(tk.END, student.get_formatted_record() + "\n")
        
        self._display_summary()

    # --- Menu Item 2: View individual student record ---
    def view_individual_record(self):
        """Prompts for student number/name and displays the matching record."""
        if not self.students:
            messagebox.showinfo("Info", "No student data available.")
            return

        # Use simpledialog to get user input for student identification
        search_term = simpledialog.askstring(
            "Search Student", 
            "Enter Student Number (e.g., 8439) or Student Name (e.g., Jake Hobbs):", 
            parent=self.master
        )

        if search_term is None or search_term == "":
            return # User cancelled or entered nothing

        search_term = search_term.strip()
        found_student = None

        # Search by Student Number (exact match) or Name (case-insensitive partial/full match)
        for student in self.students:
            if student.student_number == search_term:
                found_student = student
                break
            # Check for name match
            if search_term.lower() in student.name.lower():
                found_student = student
                # For simplicity, we take the first name match, though student number is better.
                # In a real app, you'd handle multiple matches.
                break

        self._clear_output(f"Individual Student Record Search: '{search_term}'")
        
        if found_student:
            self.output_area.insert(tk.END, "--- Match Found ---\n")
            self.output_area.insert(tk.END, found_student.get_formatted_record())
        else:
            self.output_area.insert(tk.END, "No student found with that Number or Name.")
        
        self.output_area.config(state=tk.DISABLED)

    # --- Menu Item 3: Show student with highest total score ---
    def show_highest_score(self):
        """Finds and displays the student with the highest total score."""
        if not self.students:
            messagebox.showinfo("Info", "No student data available.")
            return

        # Find the student with the maximum overall total mark
        highest_scorer = max(self.students, key=lambda s: s.get_overall_total())

        self._clear_output("Student with Highest Overall Score")
        self.output_area.insert(tk.END, highest_scorer.get_formatted_record())
        self.output_area.config(state=tk.DISABLED)

    # --- Menu Item 4: Show student with lowest total score ---
    def show_lowest_score(self):
        """Finds and displays the student with the lowest total score."""
        if not self.students:
            messagebox.showinfo("Info", "No student data available.")
            return

        # Find the student with the minimum overall total mark
        lowest_scorer = min(self.students, key=lambda s: s.get_overall_total())

        self._clear_output("Student with Lowest Overall Score")
        self.output_area.insert(tk.END, lowest_scorer.get_formatted_record())
        self.output_area.config(state=tk.DISABLED)

# --- Main execution block ---
if __name__ == '__main__':
    root = tk.Tk()
    app = StudentManagerApp(root)
    root.mainloop()