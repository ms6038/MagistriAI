import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import numpy as np

# Initialize students data (now with a DataFrame for ML processing)
students_df = pd.DataFrame(columns=['Name', 'Math', 'Science', 'English', 'LearningStyle'])

def add_student():
    try:
        name = name_entry.get()
        math_score = float(math_entry.get())
        science_score = float(science_entry.get())
        english_score = float(english_entry.get())
        learning_style = learning_style_var.get()

        # Basic validation
        if not name:
            raise ValueError("Name cannot be empty.")

        # Add student to DataFrame
        global students_df
        new_student = pd.DataFrame({
            'Name': [name],
            'Math': [math_score],
            'Science': [science_score],
            'English': [english_score],
            'LearningStyle': [learning_style]
        })
        students_df = pd.concat([students_df, new_student], ignore_index=True)

        # Update dropdown for selecting students
        update_student_selection()

        messagebox.showinfo("Success", f"Added {name} successfully.")

        # Clear inputs
        clear_entries()

    except ValueError as e:
        messagebox.showerror("Error", str(e))

def clear_entries():
    name_entry.delete(0, tk.END)
    math_entry.delete(0, tk.END)
    science_entry.delete(0, tk.END)
    english_entry.delete(0, tk.END)
    learning_style_var.set(learning_styles[0])

def update_student_selection():
    select_student_dropdown['menu'].delete(0, 'end')
    for student in students_df['Name']:
        select_student_dropdown['menu'].add_command(label=student, command=tk._setit(selected_student_var, student))
    selected_student_var.set('Select a student')

def calculate_compatibility(selected_student_scores, selected_student_learning_style, candidate_scores, candidate_learning_styles):
    # Normalize scores
    selected_student_scores_normalized = selected_student_scores / np.linalg.norm(selected_student_scores)
    candidate_scores_normalized = candidate_scores / np.linalg.norm(candidate_scores, axis=1)[:, np.newaxis]

    # Train a machine learning model (Random Forest Regressor)
    model = RandomForestRegressor()
    model.fit(candidate_scores_normalized, candidate_scores_normalized)

    # Predict scores for the selected student using the model
    predicted_scores_normalized = model.predict(selected_student_scores_normalized.reshape(1, -1))

    # Calculate compatibility percentages for all students based on similarity of predicted and actual scores
    similarities = 1 - np.linalg.norm(predicted_scores_normalized - candidate_scores_normalized, axis=1)
    compatibility_percentages = similarities * 100

    # Set negative compatibility percentages to 0
    compatibility_percentages = np.maximum(compatibility_percentages, 0)

    # Define color thresholds
    red_threshold = 35
    orange_threshold = 70

    # Apply color-coding based on compatibility percentages
    color_codes = []
    for percentage in compatibility_percentages:
        if percentage < red_threshold:
            color_codes.append("red")
        elif percentage < orange_threshold:
            color_codes.append("orange")
        else:
            color_codes.append("green")

    return compatibility_percentages, color_codes

def show_compatible_students():
    if len(students_df) < 2:
        messagebox.showinfo("Info", "Not enough students to find matches.")
        return

    selected_student_name = selected_student_var.get()
    if selected_student_name == 'Select a student':
        messagebox.showerror("Error", "Please select a student.")
        return

    # Extract the selected student's scores and learning style
    selected_student = students_df.loc[students_df['Name'] == selected_student_name]
    selected_student_scores = selected_student[['Math', 'Science', 'English']].values[0]
    selected_student_learning_style = selected_student['LearningStyle'].values[0]

    # Get names, compatibility percentages, and color codes of all students
    all_students = students_df.copy()
    all_students.drop(selected_student.index, inplace=True)  # Remove the selected student from the list
    all_students.reset_index(drop=True, inplace=True)
    all_students_scores = all_students[['Math', 'Science', 'English']].values
    all_students_learning_styles = all_students['LearningStyle'].values
    compatibility_percentages, color_codes = calculate_compatibility(selected_student_scores, selected_student_learning_style, all_students_scores, all_students_learning_styles)

    # Clear previous content in the text widget
    compatible_students_text.delete(1.0, tk.END)

    # Show compatible students with colored text
    for index, row in all_students.iterrows():
        student_name = row['Name']
        compatibility_percentage = compatibility_percentages[index]
        color = color_codes[index]
        formatted_percentage = "{:.1f}".format(compatibility_percentage)
        compatible_students_info = f"{student_name}: {formatted_percentage}%\n"
        # Change text color based on compatibility percentage
        compatible_students_text.insert(tk.END, compatible_students_info, color)

    messagebox.showinfo("Compatible Students", "Compatible Students displayed below.")

# GUI
root = tk.Tk()
root.title("Student Compatibility Finder")

# Labels
tk.Label(root, text="Name:").grid(row=0, column=0, padx=5, pady=5)
tk.Label(root, text="Math:").grid(row=1, column=0, padx=5, pady=5)
tk.Label(root, text="Science:").grid(row=2, column=0, padx=5, pady=5)
tk.Label(root, text="English:").grid(row=3, column=0, padx=5, pady=5)
tk.Label(root, text="Learning Style:").grid(row=4, column=0, padx=5, pady=5)

# Entries
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1, padx=5, pady=5)
math_entry = tk.Entry(root)
math_entry.grid(row=1, column=1, padx=5, pady=5)
science_entry = tk.Entry(root)
science_entry.grid(row=2, column=1, padx=5, pady=5)
english_entry = tk.Entry(root)
english_entry.grid(row=3, column=1, padx=5, pady=5)

# Learning style dropdown
learning_styles = ["Visual", "Auditory", "Kinesthetic"]
learning_style_var = tk.StringVar(root)
learning_style_var.set(learning_styles[0])
learning_style_dropdown = ttk.Combobox(root, textvariable=learning_style_var, values=learning_styles)
learning_style_dropdown.grid(row=4, column=1, padx=5, pady=5)

# Add student button
add_button = tk.Button(root, text="Add Student", command=add_student)
add_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="we")

# Dropdown for selecting students
selected_student_var = tk.StringVar(root)
select_student_dropdown = tk.OptionMenu(root, selected_student_var, "Select a student")
select_student_dropdown.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="we")

# Button to show compatible students
show_compatible_button = tk.Button(root, text="Show Compatible Students", command=show_compatible_students)
show_compatible_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="we")

# Add compatible_students_text widget for displaying compatible students
compatible_students_text = tk.Text(root, height=10, width=50)
compatible_students_text.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

# Add text colors
compatible_students_text.tag_configure("red", foreground="red")
compatible_students_text.tag_configure("orange", foreground="orange")
compatible_students_text.tag_configure("green", foreground="green")

# Notebook for tabs
notebook = ttk.Notebook(root)
notebook.grid(row=9, column=0, columnspan=2, pady=10, sticky="we")

# Seating Plan Tab
seating_plan_tab = ttk.Frame(notebook)
notebook.add(seating_plan_tab, text="Seating Plan")

# Seating Plan Logic
seating_plan_label = tk.Label(seating_plan_tab, text="Drag and drop students to create a seating plan:")
seating_plan_label.pack(pady=10)

# Canvas for seating plan
canvas = tk.Canvas(seating_plan_tab, bg="white", height=300, width=500)
canvas.pack(pady=10)

# List to store student labels for easy reference
student_labels = []

def add_student_to_seating_plan(student_name, x, y):
    label = tk.Label(canvas, text=student_name, bg="lightblue", padx=10, pady=5, borderwidth=2, relief="ridge")
    label.bind("<Button-1>", lambda event, label=label: on_drag_start(event, label))
    label.pack()
    label.place(x=x, y=y)
    student_labels.append(label)

add_student_to_seating_plan("Student 1", 50, 50)
add_student_to_seating_plan("Student 2", 150, 50)
add_student_to_seating_plan("Student 3", 250, 50)

# Learning Style Breakdown Tab
breakdown_tab = ttk.Frame(notebook)
notebook.add(breakdown_tab, text="Learning Style Breakdown")

# Learning Style Breakdown Logic
learning_style_breakdown_label = tk.Label(breakdown_tab, text="Learning Style Breakdown:")
learning_style_breakdown_label.pack(pady=10)

def show_learning_style_breakdown():
    learning_style_requirements = {
        "Visual": "Prefer visual aids and diagrams.",
        "Auditory": "Learn best through listening and discussion.",
        "Kinesthetic": "Require hands-on activities and movement."
    }

    breakdown_text.delete(1.0, tk.END)  # Clear previous content
    for style, requirement in learning_style_requirements.items():
        breakdown_text.insert(tk.END, f"{style}: {requirement}\n\n")

# Text widget for displaying breakdown
breakdown_text = tk.Text(breakdown_tab, height=10, width=50)
breakdown_text.pack(pady=10)

# Button to show learning style breakdown
show_learning_style_breakdown_button = tk.Button(breakdown_tab, text="Show Learning Style Breakdown", command=show_learning_style_breakdown)
show_learning_style_breakdown_button.pack(pady=10)
# Seating Plan Tab
seating_plan_tab = ttk.Frame(notebook)
notebook.add(seating_plan_tab, text="Seating Plan")

# Seating Plan Logic
seating_plan_label = tk.Label(seating_plan_tab, text="Drag and drop students to create a seating plan:")
seating_plan_label.pack(pady=10)

# Canvas for seating plan
canvas = tk.Canvas(seating_plan_tab, bg="white", height=300, width=500)
canvas.pack(pady=10)

# List to store student labels for easy reference
student_labels = []

def add_student_to_seating_plan(student_name, x, y):
    label = tk.Label(canvas, text=student_name, bg="lightblue", padx=10, pady=5, borderwidth=2, relief="ridge")
    label.bind("<Button-1>", lambda event, label=label: on_drag_start(event, label))
    label.pack()
    label.place(x=x, y=y)
    student_labels.append(label)

add_student_to_seating_plan("Student 1", 50, 50)
add_student_to_seating_plan("Student 2", 150, 50)
add_student_to_seating_plan("Student 3", 250, 50)

# Learning Style Breakdown Tab
breakdown_tab = ttk.Frame(notebook)
notebook.add(breakdown_tab, text="Learning Style Breakdown")

# Learning Style Breakdown Logic
learning_style_breakdown_label = tk.Label(breakdown_tab, text="Learning Style Breakdown:")
learning_style_breakdown_label.pack(pady=10)

def show_learning_style_breakdown():
    learning_style_requirements = {
        "Visual": "Prefer visual aids and diagrams.",
        "Auditory": "Learn best through listening and discussion.",
        "Kinesthetic": "Require hands-on activities and movement."
    }

    breakdown_text.delete(1.0, tk.END)  # Clear previous content
    for style, requirement in learning_style_requirements.items():
        breakdown_text.insert(tk.END, f"{style}: {requirement}\n\n")

# Text widget for displaying breakdown
breakdown_text = tk.Text(breakdown_tab, height=10, width=50)
breakdown_text.pack(pady=10)

# Button to show learning style breakdown
show_learning_style_breakdown_button = tk.Button(breakdown_tab, text="Show Learning Style Breakdown", command=show_learning_style_breakdown)
show_learning_style_breakdown_button.pack(pady=10)


# Run the main loop
root.mainloop()
