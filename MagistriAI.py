import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

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

        # Add student to seating plan
        add_student_to_seating_plan(name, 50, len(student_labels) * 40)

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

# Chatbot Logic
def chatbot_response():
    query = chat_input.get("1.0", tk.END).strip().lower()

    if "learning styles" in query:
        response = "Learning styles refer to the ways individuals prefer to approach learning. The three main learning styles are:\n\n1. Visual: Prefer visual aids and diagrams.\n2. Auditory: Learn best through listening and discussion.\n3. Kinesthetic: Require hands-on activities and movement."
    elif "work well" in query:
        response = "Different individuals work well with different learning styles. It's essential to identify your preferred learning style and explore study methods that align with it. For example, if you're a visual learner, using mind maps and diagrams may be effective."
    else:
        response = "I'm sorry, I couldn't understand the question. Please ask about learning styles or how different learning styles work well."

    # Display the response in the chatbot_output Text widget
    chatbot_output.config(state=tk.NORMAL)
    chatbot_output.insert(tk.END, f"\nUser: {query}\nChatbot: {response}\n\n")
    chatbot_output.config(state=tk.DISABLED)

# GUI
root = tk.Tk()
root.title("Student Compatibility Finder")

# Set a nicer font
nice_font = ("Arial", 12)

# Create a Canvas to make the whole program scrollable
canvas = tk.Canvas(root)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add a scrollbar to the Canvas
scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.configure(yscrollcommand=scrollbar.set)

# Create a Frame inside the Canvas
frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame, anchor=tk.NW)

# Add the widgets to the Frame
# Labels
tk.Label(frame, text="Name:", bg='white', font=nice_font).grid(row=0, column=0, padx=5, pady=5)
tk.Label(frame, text="Math:", bg='white', font=nice_font).grid(row=1, column=0, padx=5, pady=5)
tk.Label(frame, text="Science:", bg='white', font=nice_font).grid(row=2, column=0, padx=5, pady=5)
tk.Label(frame, text="English:", bg='white', font=nice_font).grid(row=3, column=0, padx=5, pady=5)
tk.Label(frame, text="Learning Style:", bg='white', font=nice_font).grid(row=4, column=0, padx=5, pady=5)

# Entries
name_entry = tk.Entry(frame, font=nice_font)
name_entry.grid(row=0, column=1, padx=5, pady=5)
math_entry = tk.Entry(frame, font=nice_font)
math_entry.grid(row=1, column=1, padx=5, pady=5)
science_entry = tk.Entry(frame, font=nice_font)
science_entry.grid(row=2, column=1, padx=5, pady=5)
english_entry = tk.Entry(frame, font=nice_font)
english_entry.grid(row=3, column=1, padx=5, pady=5)

# Learning style dropdown
learning_styles = ["Visual", "Auditory", "Kinesthetic"]
learning_style_var = tk.StringVar(frame)
learning_style_var.set(learning_styles[0])
learning_style_dropdown = ttk.Combobox(frame, textvariable=learning_style_var, values=learning_styles, font=nice_font)
learning_style_dropdown.grid(row=4, column=1, padx=5, pady=5)
learning_style_dropdown.config(background='#aedbf2')  # Set pastel blue background

# Add student button
add_button = tk.Button(frame, text="Add Student", command=add_student, font=nice_font, bg='#aedbf2')  # Set pastel blue background
add_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="we")

# Dropdown for selecting students
selected_student_var = tk.StringVar(frame)
select_student_dropdown = tk.OptionMenu(frame, selected_student_var, "Select a student")
select_student_dropdown.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="we")
select_student_dropdown.config(background='#aedbf2')  # Set pastel blue background

# Button to show compatible students
show_compatible_button = tk.Button(frame, text="Show Compatible Students", command=show_compatible_students, font=nice_font, bg='#aedbf2')  # Set pastel blue background
show_compatible_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="we")

# Add compatible_students_text widget for displaying compatible students
compatible_students_text = tk.Text(frame, height=10, width=50, font=nice_font, wrap='word')
compatible_students_text.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

# Add text colors
compatible_students_text.tag_configure("red", foreground="red")
compatible_students_text.tag_configure("orange", foreground="orange")
compatible_students_text.tag_configure("green", foreground="green")

# Notebook for tabs
notebook = ttk.Notebook(frame)
notebook.grid(row=9, column=0, columnspan=2, pady=10, sticky="we")

# Seating Plan Tab
seating_plan_tab = ttk.Frame(notebook)
notebook.add(seating_plan_tab, text="Seating Plan")

# Use ttk.Style to set the background color for Seating Plan Tab
seating_plan_style = ttk.Style()
seating_plan_style.configure("SeatingPlan.TFrame", background='white')
seating_plan_tab.configure(style="SeatingPlan.TFrame")

# Seating Plan Logic
seating_plan_label = tk.Label(seating_plan_tab, text="Drag and drop students to create a seating plan:", bg='white', font=nice_font)
seating_plan_label.pack(pady=10)

# Canvas for seating plan
seating_plan_canvas = tk.Canvas(seating_plan_tab, bg="white", width=500, height=300)
seating_plan_canvas.pack(expand=tk.YES, fill=tk.BOTH)

# Add a scrollbar to the seating plan canvas
seating_plan_scrollbar = ttk.Scrollbar(seating_plan_tab, orient=tk.VERTICAL, command=seating_plan_canvas.yview)
seating_plan_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
seating_plan_canvas.configure(yscrollcommand=seating_plan_scrollbar.set)

# Frame inside the seating plan canvas
seating_plan_frame = tk.Frame(seating_plan_canvas, bg="white")
seating_plan_canvas.create_window((0, 0), window=seating_plan_frame, anchor=tk.NW)

# List to store student labels for easy reference
student_labels = []

def add_student_to_seating_plan(student_name, x, y):
    label = tk.Label(seating_plan_frame, text=student_name, bg="lightblue", padx=10, pady=5, borderwidth=2, relief="ridge", font=nice_font)
    label.bind("<Button-1>", lambda event, label=label: on_drag_start(event, label))
    label.pack()
    label.place(x=x, y=y)
    student_labels.append(label)

# Implement your seating plan logic here
# For example:
add_student_to_seating_plan("Student 1", 50, 50)
add_student_to_seating_plan("Student 2", 150, 50)
add_student_to_seating_plan("Student 3", 250, 50)

# Function to handle dragging of student labels
def on_drag_start(event, label):
    label._drag_data = {'x': event.x, 'y': event.y, 'item': label}
    label.bind('<B1-Motion>', lambda event, label=label: on_drag_motion(event, label))

def on_drag_motion(event, label):
    delta_x = event.x - label._drag_data['x']
    delta_y = event.y - label._drag_data['y']
    x = label.winfo_x() + delta_x
    y = label.winfo_y() + delta_y
    label.place(x=x, y=y)
    label._drag_data['x'] = event.x
    label._drag_data['y'] = event.y

# Learning Style Breakdown Tab
breakdown_tab = ttk.Frame(notebook)
notebook.add(breakdown_tab, text="Learning Style Breakdown")

# Use a Canvas widget to set the background color
canvas_breakdown = tk.Canvas(breakdown_tab, bg="white", width=500, height=300)
canvas_breakdown.pack(expand=tk.YES, fill=tk.BOTH)

# Learning Style Breakdown Logic
def show_learning_style_breakdown(learning_style):
    learning_style_requirements = {
        "Visual": "Prefer visual aids and diagrams.",
        "Auditory": "Learn best through listening and discussion.",
        "Kinesthetic": "Require hands-on activities and movement."
    }

    breakdown_text.delete(1.0, tk.END)  # Clear previous content
    breakdown_text.insert(tk.END, learning_style_requirements[learning_style])

# Text widget for displaying breakdown
breakdown_text = tk.Text(canvas_breakdown, bg="white", font=nice_font, wrap=tk.WORD)
breakdown_text.pack(expand=tk.YES, fill=tk.BOTH)

# Buttons to show learning style breakdown
visual_button = tk.Button(breakdown_tab, text="Visual", command=lambda: show_learning_style_breakdown("Visual"), font=nice_font, bg='#aedbf2')  # Set pastel blue background
visual_button.pack(side=tk.LEFT, padx=10, pady=5)

auditory_button = tk.Button(breakdown_tab, text="Auditory", command=lambda: show_learning_style_breakdown("Auditory"), font=nice_font, bg='#aedbf2')  # Set pastel blue background
auditory_button.pack(side=tk.LEFT, padx=10, pady=5)

kinesthetic_button = tk.Button(breakdown_tab, text="Kinesthetic", command=lambda: show_learning_style_breakdown("Kinesthetic"), font=nice_font, bg='#aedbf2')  # Set pastel blue background
kinesthetic_button.pack(side=tk.LEFT, padx=10, pady=5)

# Chatbot Tab
chatbot_tab = ttk.Frame(notebook)
notebook.add(chatbot_tab, text="Chatbot")

# Chatbot Logic
chat_input_label = tk.Label(chatbot_tab, text="Ask the chatbot about learning styles:", bg='white', font=nice_font)
chat_input_label.pack(pady=10)

chat_input = tk.Text(chatbot_tab, height=3, width=50, font=nice_font, wrap=tk.WORD)
chat_input.pack(pady=10)

chatbot_output = tk.Text(chatbot_tab, height=20, width=50, font=nice_font, wrap=tk.WORD, state=tk.DISABLED)
chatbot_output.pack(pady=10)

chat_button = tk.Button(chatbot_tab, text="Ask Chatbot", command=chatbot_response, font=nice_font, bg='#aedbf2')  # Set pastel blue background
chat_button.pack(pady=10)

# Run the GUI
root.mainloop()
