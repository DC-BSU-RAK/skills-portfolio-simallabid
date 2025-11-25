import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import scrolledtext
from tkinter import font as tkFont
from functools import cmp_to_key

#Attempt to import Pygame for audio, handling potential import errors
try:
    import pygame
    pygame_available = True
except ImportError:
    pygame_available = False
    print("Warning: Pygame not installed. Audio features will be disabled.")


#Data Structure for Student Records
class Student:
    """Represents a single student's record and calculated results."""
    def __init__(self, student_number, name, course1, course2, course3, exam_mark):
        self.student_number = str(student_number)
        self.name = name
        #Coursework marks (C1, C2, C3) and Exam mark are stored here.
        self.course1 = int(course1)
        self.course2 = int(course2)
        self.course3 = int(course3)
        self.exam_mark = int(exam_mark)

    def get_coursework_total(self):
        """Calculates the total coursework mark (max 60)."""
        return self.course1 + self.course2 + self.course3

    def get_overall_total(self):
        """Calculates the overall total mark (max 160 = 60 CW + 100 Exam)."""
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
        
    def to_file_format(self):
        """Returns the record in the comma-separated format used in the file."""
        return f"{self.student_number}, {self.name}, {self.course1}, {self.course2}, {self.course3}, {self.exam_mark}"

#Data Loading Function
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
            #The first line is expected to be the total number of students
            num_students = int(lines[0].strip())
            for line in lines[1:]:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) == 6:
                    student_number = parts[0]
                    name = parts[1]
                    try:
                        # Convert marks to integers
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
        messagebox.showerror("File Error", f"The file '{filename}' was not found. Creating empty file structure.")
        #Create an empty file structure if not found
        try:
            with open(filename, 'w') as file:
                file.write("0\n")
            return [], 0
        except Exception as e:
            messagebox.showerror("File Creation Error", f"Could not create file '{filename}': {e}")
            return None, 0
    except ValueError as e:
        messagebox.showerror("Data Error", f"Error processing data: {e}. Check the file format.")
        return None, 0
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        return None, 0

#Tkinter Application Class
class StudentManagerApp:
    
    #Data Persistence Method
    def save_student_data(self, filename='studentMarks.txt'):
        """Writes the current list of student records back to the file."""
        try:
            with open(filename, 'w') as file:
                #Write the total number of students first
                file.write(f"{len(self.students)}\n")
                #Write each student record in the correct comma-separated format
                for student in self.students:
                    file.write(f"{student.to_file_format()}\n")
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save data to file: {e}")
            return False

    #Initialization
    def __init__(self, master):
        self.master = master
        master.title("Student Manager Dashboard")
        master.geometry("1000x800") #Increased size for new buttons
        master.resizable(True, True)

        #Color Palette
        self.primary_bg = "#2C3E50"      
        self.action_panel_bg = "#34495E" 
        self.accent_color = "#1ABC9C"    
        self.view_button_color = "#3498DB" #Bright Blue for View/Search/Sort
        self.modify_button_color = "#F39C12" #Orange/Yellow for Add/Update/Delete
        self.highlight_color = "#E74C3C" #Bright Red 
        self.text_color = "#ECF0F1"      
        self.output_bg = "#ECF0F1"       
        self.output_fg = "#2C3E50"       

        master.config(bg=self.primary_bg)

        #Custom Fonts
        self.title_font = tkFont.Font(family="Helvetica Neue", size=22, weight="bold")
        self.header_font = tkFont.Font(family="Helvetica Neue", size=16, weight="bold")
        self.button_font = tkFont.Font(family="Helvetica Neue", size=12, weight="bold") 
        self.body_font = tkFont.Font(family="Fira Code", size=11)
        
        #Audio Setup (Pygame Mixer)
        self.is_playing_audio = False
        self.click_sound = None 
        if pygame_available:
            try:
                pygame.mixer.init(44100, -16, 2, 2048)
                pygame.mixer.music.load('studentbg.mp3')
                pygame.mixer.music.play(-1) 
                self.click_sound = pygame.mixer.Sound('studentclick.mp3')
                self.is_playing_audio = True
                print("Background music started.")
            except pygame.error as e:
                print(f"Pygame audio error: {e}")
                messagebox.showwarning("Audio Warning", "Could not start audio. Check MP3 files.")
                self.is_playing_audio = False
        
        master.protocol("WM_DELETE_WINDOW", self.on_closing)
        if self.is_playing_audio and self.click_sound:
            master.bind('<Button-1>', self.play_click_sound) 

        #Load data
        self.students, self.num_students = load_student_data()
        if not self.students:
            self.students = []
            self.num_students = 0

        #GUI Layout (Grid System)
        
        #Title Bar
        title_frame = tk.Frame(master, bg=self.primary_bg)
        title_frame.pack(side=tk.TOP, fill=tk.X)
        self.title_label = tk.Label(title_frame, text="📊 Student Performance Dashboard", 
                                    font=self.title_font, bg=self.primary_bg, 
                                    fg=self.accent_color, pady=15)
        self.title_label.pack()

        #Main Content Frame (Uses Grid)
        content_frame = tk.Frame(master, bg=self.primary_bg)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        #Configure columns: Column 0 (Actions) is fixed width, Column 1 (Output) expands
        content_frame.grid_columnconfigure(0, weight=0) 
        content_frame.grid_columnconfigure(1, weight=1) 
        content_frame.grid_rowconfigure(0, weight=1)

        #Action Panel (Column 0)
        self.action_frame = tk.Frame(content_frame, 
                                     bg=self.action_panel_bg, padx=15, pady=15,
                                     relief=tk.RAISED, bd=3)
        #Place action frame on the left side
        self.action_frame.grid(row=0, column=0, sticky="nswe", padx=(0, 15))

        self.action_header = tk.Label(self.action_frame, text="Action Center ⬇️", 
                                     font=self.header_font, fg=self.highlight_color, 
                                     bg=self.action_panel_bg, pady=10)
        self.action_header.pack(fill=tk.X)
        
        #Helper function to create consistently styled buttons
        def create_action_button(text, command, color):
            return tk.Button(self.action_frame,
                             text=text,
                             command=command,
                             font=self.button_font,
                             bg=color,
                             fg=self.primary_bg, 
                             activebackground=self.highlight_color,
                             activeforeground="white",
                             relief=tk.FLAT, 
                             bd=0,
                             padx=10, pady=10)

        #VIEW/SEARCH/SORT Actions (Blue)
        self.btn_view_all = create_action_button("1. View All Records", self.view_all_records, self.view_button_color)
        self.btn_view_all.pack(fill=tk.X, pady=(5, 5))
        
        self.btn_view_individual = create_action_button("2. Search Student", self.view_individual_record, self.view_button_color)
        self.btn_view_individual.pack(fill=tk.X, pady=5)
        
        self.btn_highest = create_action_button("3. Show Highest Score 🏆", self.show_highest_score, self.view_button_color)
        self.btn_highest.pack(fill=tk.X, pady=5)
        
        self.btn_lowest = create_action_button("4. Show Lowest Score 📉", self.show_lowest_score, self.view_button_color)
        self.btn_lowest.pack(fill=tk.X, pady=5)
        
        #Sort Student Records
        self.btn_sort = create_action_button("5. Sort Student Records 🔄", self.sort_student_records, self.view_button_color)
        self.btn_sort.pack(fill=tk.X, pady=5)

        tk.Frame(self.action_frame, height=2, bg=self.primary_bg).pack(fill=tk.X, pady=10) # Separator

        #Modification Actions (Orange/Yellow)
        #Add New Student
        self.btn_add = create_action_button("6. Add New Student ➕", self.add_student_record, self.modify_button_color)
        self.btn_add.pack(fill=tk.X, pady=5)

        #Update Student Record
        self.btn_update = create_action_button("7. Update Student Record ✏️", self.update_student_record, self.modify_button_color)
        self.btn_update.pack(fill=tk.X, pady=5)
        
        #Delete Student Record
        self.btn_delete = create_action_button("8. Delete Student Record 🗑️", self.delete_student_record, self.modify_button_color)
        self.btn_delete.pack(fill=tk.X, pady=5)

        tk.Frame(self.action_frame, height=2, bg=self.primary_bg).pack(fill=tk.X, pady=10) # Separator
        
        self.btn_exit = create_action_button("Exit Application ❌", self.on_closing, self.highlight_color)
        self.btn_exit.config(fg="white") 
        self.btn_exit.pack(fill=tk.X, pady=(20, 5), side=tk.BOTTOM)
        
        #Output Display Area (Column 1)
        self.output_area = scrolledtext.ScrolledText(content_frame, 
                                                     width=50, height=30, wrap=tk.WORD, 
                                                     font=self.body_font, bg=self.output_bg,
                                                     fg=self.output_fg, padx=15, pady=15,
                                                     bd=5, relief=tk.SUNKEN)
        #Place output area on the right side
        self.output_area.grid(row=0, column=1, sticky="nswe")
        
        #Initial Welcome Message
        self.output_area.insert(tk.END, f"Welcome to the Student Manager!\n\n")
        self.output_area.insert(tk.END, f"Loaded {self.num_students} student records.\n")
        self.output_area.insert(tk.END, f"Use the **Action Center** on the left to manage records.\n")
        self.output_area.config(state=tk.DISABLED)
        
        #Status Bar
        self.status_bar = tk.Label(master, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                   bg=self.action_panel_bg, fg=self.text_color, font=('Helvetica Neue', 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    #Graceful Exit Handler (Stops audio)
    def on_closing(self):
        """Stops background music and destroys the window."""
        if self.is_playing_audio:
            pygame.mixer.music.stop()
        self.master.destroy()

    #Mouse Click Sound Player
    def play_click_sound(self, event):
        """Plays the click sound effect when the mouse button is pressed."""
        if self.click_sound:
            if event.widget != self.output_area:
                self.click_sound.play()

    #Helper Methods
    def _clear_output(self, title):
        """Clears the output area and prints a title with enhanced styling."""
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete(1.0, tk.END)
        
        self.output_area.insert(tk.END, f"{'='*10} {title.upper()} {'='*10}\n\n", "header_style")
        self.output_area.tag_config("header_style", font=self.header_font, foreground=self.highlight_color)
        
        self.output_area.config(state=tk.DISABLED)
        self.status_bar.config(text=f"Action: {title}")
    
    def _find_student(self, search_term):
        """Helper to find a student by exact number or name prefix."""
        found_students = []
        is_exact_number_match = False
        
        #Check for Exact Student Number Match (Takes priority)
        for student in self.students:
            if student.student_number.lower() == search_term:
                return [student] 
        
        #If no exact number match, perform Alphabetic/Prefix search
        for student in self.students:
            if student.name.lower().startswith(search_term):
                found_students.append(student)

        #Sort matches alphabetically by name if multiple results exist
        if len(found_students) > 1:
            found_students.sort(key=lambda s: s.name.lower())
            
        return found_students


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

    #View/SEARCH Actions
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
            "Enter Student Number (e.g., 8439) or Student Name prefix (e.g., 'J'):", 
            parent=self.master
        )

        if search_term is None or search_term.strip() == "":
            self.status_bar.config(text="Status: Individual search cancelled.")
            return

        search_term = search_term.strip().lower()
        found_students = self._find_student(search_term)

        self._clear_output(f"Individual Student Record Search: '{search_term}'")
        self.output_area.config(state=tk.NORMAL)
        
        if found_students:
            self.output_area.insert(tk.END, f"--- {len(found_students)} Match(es) Found ---\n\n", "match_header")
            self.output_area.tag_config("match_header", font=self.header_font, foreground=self.accent_color)
            
            for student in found_students:
                self.output_area.insert(tk.END, student.get_formatted_record() + "\n\n")

            self.status_bar.config(text=f"Status: Found {len(found_students)} record(s) for '{search_term}'.")
        else:
            self.output_area.insert(tk.END, "No student found matching that Number or Name prefix.", "error_message")
            self.output_area.tag_config("error_message", foreground=self.highlight_color, font=self.body_font)
            self.status_bar.config(text=f"Status: No record found for '{search_term}'.")
        
        self.output_area.config(state=tk.DISABLED)

    def show_highest_score(self):
        if not self.students:
            messagebox.showinfo("Info", "No student data available.")
            self.status_bar.config(text="Status: No data loaded.")
            return

        #Uses the max() function and a lambda key to find the student object 
        #with the highest value returned by get_overall_total().
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

        #Uses the min() function and a lambda key to find the student object 
        #with the lowest value returned by get_overall_total().
        lowest_scorer = min(self.students, key=lambda s: s.get_overall_total())

        self._clear_output("Student with Lowest Overall Score")
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, lowest_scorer.get_formatted_record())
        self.output_area.config(state=tk.DISABLED)
        self.status_bar.config(text=f"Status: Displayed lowest scorer: {lowest_scorer.name}.")
        
    #Sort student records
    def sort_student_records(self):
        if not self.students:
            messagebox.showinfo("Info", "No student data available to sort.")
            return

        #Simple Dialog to choose sort key
        key_options = "Name (N), Total Score (T), Percentage (P)"
        key_input = simpledialog.askstring("Sort Records", 
                                           f"Sort by? ({key_options})",
                                           parent=self.master).strip().upper()
        
        if not key_input:
            self.status_bar.config(text="Status: Sort cancelled.")
            return

        #Simple Dialog to choose sort order
        order_input = simpledialog.askstring("Sort Records", 
                                             "Order? (Ascending=A / Descending=D)",
                                             parent=self.master).strip().upper()

        reverse = (order_input == 'D')
        sort_key = None
        sort_title = ""

        if key_input == 'N':
            sort_key = lambda s: s.name.lower()
            sort_title = "Alphabetical Order by Name"
        elif key_input == 'T':
            sort_key = lambda s: s.get_overall_total()
            sort_title = "Overall Total Score"
        elif key_input == 'P':
            sort_key = lambda s: s.get_percentage()
            sort_title = "Overall Percentage"
        else:
            messagebox.showerror("Error", "Invalid sort key selected.")
            self.status_bar.config(text="Status: Sort failed (Invalid key).")
            return

        #Perform the sort
        self.students.sort(key=sort_key, reverse=reverse)
        
        self._clear_output(f"Sorted Records by {sort_title} ({'Descending' if reverse else 'Ascending'})")
        self.output_area.config(state=tk.NORMAL)
        
        for student in self.students:
            self.output_area.insert(tk.END, student.get_formatted_record() + "\n\n")
        
        self._display_summary()
        self.output_area.config(state=tk.DISABLED)
        self.status_bar.config(text=f"Status: Records sorted by {sort_title}.")

    #Add a student record
    def add_student_record(self):
        #Helper for input validation and conversion to int
        def get_int_input(prompt, max_val=None):
            while True:
                value_str = simpledialog.askstring("Input", prompt, parent=self.master)
                if value_str is None: return None #Cancelled
                try:
                    value = int(value_str.strip())
                    if max_val is not None and value > max_val:
                        messagebox.showwarning("Warning", f"Value cannot exceed {max_val}.")
                        continue
                    if value < 0:
                        messagebox.showwarning("Warning", "Value cannot be negative.")
                        continue
                    return value
                except ValueError:
                    messagebox.showwarning("Warning", "Invalid input. Please enter a whole number.")
        
        #Get student number and check for duplicates
        while True:
            s_num = simpledialog.askstring("Input", "Enter Student Number (must be unique):", parent=self.master)
            if s_num is None: return 
            s_num = s_num.strip()
            
            #Check for duplicates
            if any(s.student_number == s_num for s in self.students):
                messagebox.showwarning("Warning", "Student Number already exists. Please enter a unique number.")
            else:
                break
        
        #Get name
        name = simpledialog.askstring("Input", "Enter Student Name:", parent=self.master)
        if name is None: return 
        name = name.strip()

        #Get coursework marks (max 20 each)
        c1 = get_int_input("Enter Course 1 Mark (max 20):", 20)
        if c1 is None: return
        c2 = get_int_input("Enter Course 2 Mark (max 20):", 20)
        if c2 is None: return
        c3 = get_int_input("Enter Course 3 Mark (max 20):", 20)
        if c3 is None: return

        #Get exam mark (max 100)
        exam = get_int_input("Enter Exam Mark (max 100):", 100)
        if exam is None: return

        #Create and add new student
        new_student = Student(s_num, name, c1, c2, c3, exam)
        self.students.append(new_student)
        self.num_students = len(self.students) # Update the count

        #Save and display result
        if self.save_student_data():
            self._clear_output("Student Record Added")
            self.output_area.config(state=tk.NORMAL)
            self.output_area.insert(tk.END, f"Successfully added new student record:\n\n")
            self.output_area.insert(tk.END, new_student.get_formatted_record())
            self.output_area.config(state=tk.DISABLED)
            self.status_bar.config(text=f"Status: Added student '{name}'. Data saved.")
        else:
            #If save fails, remove the student to maintain consistency
            self.students.remove(new_student) 
            self.num_students = len(self.students)
            self.status_bar.config(text="Status: Add failed (Save error).")


    #Delete a student record
    def delete_student_record(self):
        if not self.students:
            messagebox.showinfo("Info", "No student data to delete.")
            return

        search_term = simpledialog.askstring("Delete Record", 
                                             "Enter Student Number or Name to delete:", 
                                             parent=self.master)
        if search_term is None or search_term.strip() == "":
            self.status_bar.config(text="Status: Delete cancelled.")
            return

        search_term = search_term.strip().lower()
        found_students = self._find_student(search_term)

        if not found_students:
            messagebox.showwarning("Warning", f"No student found matching '{search_term}'.")
            self.status_bar.config(text="Status: Delete failed (Student not found).")
            return

        #If multiple students match the name prefix, we must require a specific Student Number
        if len(found_students) > 1:
            display_list = "\n".join([f"- {s.name} (Num: {s.student_number})" for s in found_students])
            messagebox.showwarning("Ambiguous Search", 
                                   f"Multiple students match '{search_term}':\n{display_list}\nPlease use the exact Student Number to delete.")
            self.status_bar.config(text="Status: Delete failed (Ambiguous match).")
            return
        
        #Only one student found (or exact number match)
        student_to_delete = found_students[0]

        #Confirmation step
        confirmation = messagebox.askyesno("Confirm Deletion", 
                                           f"Are you sure you want to permanently delete the record for {student_to_delete.name} (Num: {student_to_delete.student_number})?",
                                           parent=self.master)

        if confirmation:
            self.students.remove(student_to_delete)
            self.num_students = len(self.students)

            if self.save_student_data():
                self._clear_output("Student Record Deleted")
                self.output_area.config(state=tk.NORMAL)
                self.output_area.insert(tk.END, f"Successfully deleted record for: {student_to_delete.name} (Num: {student_to_delete.student_number})")
                self.output_area.config(state=tk.DISABLED)
                self.status_bar.config(text=f"Status: Deleted student '{student_to_delete.name}'. Data saved.")
            else:
                #Critical Error: Data deletion was successful in memory but failed to save. 
                #Reverting the deletion is complex, so we just inform the user and leave the list in memory.
                messagebox.showerror("Critical Error", "Failed to save deletion to file. Data in memory may not match file.")
                self.status_bar.config(text="Status: Delete failed (Save error).")


    #Update a student's record
    def update_student_record(self):
        if not self.students:
            messagebox.showinfo("Info", "No student data to update.")
            return

        search_term = simpledialog.askstring("Update Record", 
                                             "Enter Student Number or Name prefix to update:", 
                                             parent=self.master)
        if search_term is None or search_term.strip() == "":
            self.status_bar.config(text="Status: Update cancelled.")
            return

        search_term = search_term.strip().lower()
        found_students = self._find_student(search_term)

        if not found_students:
            messagebox.showwarning("Warning", f"No student found matching '{search_term}'.")
            self.status_bar.config(text="Status: Update failed (Student not found).")
            return

        #If multiple students match, require specific Student Number
        if len(found_students) > 1:
            display_list = "\n".join([f"- {s.name} (Num: {s.student_number})" for s in found_students])
            messagebox.showwarning("Ambiguous Search", 
                                   f"Multiple students match '{search_term}':\n{display_list}\nPlease use the exact Student Number to update.")
            self.status_bar.config(text="Status: Update failed (Ambiguous match).")
            return
        
        #Single student found
        student_to_update = found_students[0]

        #Helper for input validation and conversion to int for marks
        def get_mark_update(prompt, current_val, max_val):
            new_val_str = simpledialog.askstring("Update Mark", 
                                                 f"{prompt} (Current: {current_val}, Max: {max_val})",
                                                 parent=self.master)
            if new_val_str is None or new_val_str.strip() == "":
                return current_val # No change
            
            try:
                value = int(new_val_str.strip())
                if 0 <= value <= max_val:
                    return value
                else:
                    messagebox.showwarning("Warning", f"Value must be between 0 and {max_val}.")
                    return None #Signal invalid input
            except ValueError:
                messagebox.showwarning("Warning", "Invalid input. Please enter a whole number.")
                return None #Signal invalid input

        #Sub-menu for field selection (using simpledialog as a makeshift menu)
        update_choice = simpledialog.askstring("Update Field", 
                                                f"Updating: {student_to_update.name} (Num: {student_to_update.student_number})\n\n"
                                                "Which field to update?\n"
                                                "N: Name\n"
                                                "C1: Course 1 Mark\n"
                                                "C2: Course 2 Mark\n"
                                                "C3: Course 3 Mark\n"
                                                "E: Exam Mark",
                                                parent=self.master).strip().upper()

        updated = False
        
        if update_choice == 'N':
            new_name = simpledialog.askstring("Update Name", f"Enter new name for {student_to_update.name}:", parent=self.master)
            if new_name and new_name.strip():
                student_to_update.name = new_name.strip()
                updated = True
        elif update_choice == 'C1':
            new_c1 = get_mark_update("Enter new Course 1 Mark", student_to_update.course1, 20)
            if new_c1 is not None:
                student_to_update.course1 = new_c1
                updated = True
        elif update_choice == 'C2':
            new_c2 = get_mark_update("Enter new Course 2 Mark", student_to_update.course2, 20)
            if new_c2 is not None:
                student_to_update.course2 = new_c2
                updated = True
        elif update_choice == 'C3':
            new_c3 = get_mark_update("Enter new Course 3 Mark", student_to_update.course3, 20)
            if new_c3 is not None:
                student_to_update.course3 = new_c3
                updated = True
        elif update_choice == 'E':
            new_exam = get_mark_update("Enter new Exam Mark", student_to_update.exam_mark, 100)
            if new_exam is not None:
                student_to_update.exam_mark = new_exam
                updated = True
        else:
            messagebox.showwarning("Warning", "Invalid update choice.")
            self.status_bar.config(text="Status: Update failed (Invalid choice).")
            return
            
        if updated:
            if self.save_student_data():
                self._clear_output("Student Record Updated")
                self.output_area.config(state=tk.NORMAL)
                self.output_area.insert(tk.END, f"Successfully updated record for: {student_to_update.name}\n\n")
                self.output_area.insert(tk.END, student_to_update.get_formatted_record())
                self.output_area.config(state=tk.DISABLED)
                self.status_bar.config(text=f"Status: Updated student '{student_to_update.name}'. Data saved.")
            else:
                self.status_bar.config(text="Status: Update failed (Save error).")
        else:
            self.status_bar.config(text="Status: No changes made or input was invalid.")


#Main execution block
if __name__ == '__main__':
    root = tk.Tk()
    app = StudentManagerApp(root)
    root.mainloop()

    #Quit pygame mixer after Tkinter window closes
    if pygame_available:
        try:
            pygame.quit()
        except Exception:
            pass #Ignore if mixer wasn't initialized