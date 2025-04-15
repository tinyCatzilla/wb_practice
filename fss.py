import random
import tkinter as tk
from collections import defaultdict
import os

def generate_substrings(word):
    """Generate all possible 3-letter substrings of a given word."""
    return {word[i:i+3] for i in range(len(word) - 2) if '-' not in word[i:i+3]}

def process_words(input_file):
    """Read words from input file and compute substring frequencies."""
    substring_counts = defaultdict(int)
    unique_words = set()

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip().lower()
            if word:
                unique_words.add(word)

    for word in unique_words:
        seen_substrings = set()
        for substring in generate_substrings(word):
            if substring not in seen_substrings:
                substring_counts[substring] += 1
                seen_substrings.add(substring)

    return unique_words, substring_counts

class GameApp:
    def __init__(self, root, unique_words, substrings):
        self.root = root
        self.unique_words = unique_words
        self.substrings = substrings
        self.skipped_prompts = []
        self.missed_prompts_file = 'missed_prompts.txt'
        self.missed_prompts = self.load_missed_prompts()
        self.solved_prompts = 0
        self.total_prompts = 0
        self.current_prompt = None

        self.root.title("Study Game")
        self.setup_ui()

    def setup_ui(self):


        """Set up the user interface."""
        self.prompt_label = tk.Label(self.root, text="Prompt: ", font=("Arial", 14))
        self.prompt_label.pack(pady=10)

        self.input_entry = tk.Entry(self.root, font=("Arial", 14))
        self.input_entry.pack(pady=10)

        self.error_label = tk.Label(self.root, text="", font=("Arial", 12), fg="red")
        self.error_label.pack(pady=5)

        self.skip_button = tk.Button(self.root, text="Skip", font=("Arial", 14), command=self.skip_prompt)
        self.skip_button.pack_forget()

        self.missed_button = tk.Button(self.root, text="Show Missed Prompts", font=("Arial", 14), command=self.show_missed_prompts)
        self.missed_button.pack(pady=10)

        self.solutions_listbox = tk.Listbox(self.root, font=("Arial", 12), width=40, height=5)
        self.solutions_listbox.pack(pady=10)

        self.tracker_label = tk.Label(self.root, text="Prompts Solved: 0/0 (0%)", font=("Arial", 12))
        self.tracker_label.pack(pady=10)

        self.min_label = tk.Label(self.root, text="Min solutions:", font=("Arial", 12))
        self.min_label.pack(pady=5)
        self.min_entry = tk.Entry(self.root, font=("Arial", 12))
        self.min_entry.insert(0, "1")
        self.min_entry.pack(pady=5)

        self.max_label = tk.Label(self.root, text="Max solutions:", font=("Arial", 12))
        self.max_label.pack(pady=5)
        self.max_entry = tk.Entry(self.root, font=("Arial", 12))
        self.max_entry.insert(0, "1000")
        self.max_entry.pack(pady=5)

        self.missed_only_var = tk.BooleanVar(value=False)
        self.missed_only_checkbox = tk.Checkbutton(self.root, text="Show Only Missed Prompts", font=("Arial", 12), variable=self.missed_only_var)
        self.missed_only_checkbox.pack(pady=5)

        self.input_entry.bind("<Return>", self.handle_user_input)
        self.root.bind("<space>", self.handle_spacebar)

        self.show_prompt()

    def load_missed_prompts(self):
        """Load missed prompts from the file."""
        if not os.path.exists(self.missed_prompts_file):
            return []

        with open(self.missed_prompts_file, 'r', encoding='utf-8') as file:
            return [line.strip().split(',')[0] for line in file.readlines()[1:]]

    def show_prompt(self):
        """Choose a random prompt that meets the min and max solutions criteria."""
        min_sols = self.get_min_solutions()
        max_sols = self.get_max_solutions()
        missed_only = self.missed_only_var.get()

        if missed_only:
            filtered_substrings = self.missed_prompts
        else:
            filtered_substrings = [s for s, count in self.substrings.items() if min_sols <= count <= max_sols]

        if filtered_substrings:
            self.current_prompt = random.choice(filtered_substrings)
            self.prompt_label.config(text=f"Prompt: {self.current_prompt} (Solutions: {self.substrings[self.current_prompt]})")
        else:
            self.error_label.config(text="No prompts match the specified range.")

    def get_min_solutions(self):
        """Get the minimum number of solutions from the input box."""
        try:
            return int(self.min_entry.get())
        except ValueError:
            return 0

    def get_max_solutions(self):
        """Get the maximum number of solutions from the input box."""
        try:
            return int(self.max_entry.get())
        except ValueError:
            return float('inf')

    def update_tracker(self):
        """Update the tracker label showing solved and total prompts with percentage."""
        percentage = (self.solved_prompts / self.total_prompts) * 100 if self.total_prompts > 0 else 0
        self.tracker_label.config(text=f"Prompts Solved: {self.solved_prompts}/{self.total_prompts} ({percentage:.2f}%)")

    def display_solutions(self, solutions):
        """Display solutions in the listbox."""
        self.solutions_listbox.delete(0, tk.END)
        for solution in solutions[:5]:
            self.solutions_listbox.insert(tk.END, solution)
        self.show_prompt()

    def handle_user_input(self, event):
        """Handle user input."""
        user_input = self.input_entry.get().strip().lower()
        self.input_entry.delete(0, tk.END)

        if user_input == "exit":
            self.root.quit()
        elif user_input in self.unique_words and self.current_prompt in user_input:
            solutions = [word for word in self.unique_words if self.current_prompt in word]
            random.shuffle(solutions)
            self.solved_prompts += 1
            self.total_prompts += 1
            self.update_tracker()
            self.display_solutions(solutions)
        else:
            self.error_label.config(text=f"Incorrect word: {user_input}")

    def skip_prompt(self):
        """Skip the current prompt and display solutions."""
        self.log_missed_prompt(self.current_prompt)
        self.skipped_prompts.append(self.current_prompt)
        solutions = [word for word in self.unique_words if self.current_prompt in word]
        self.total_prompts += 1
        self.update_tracker()
        random.shuffle(solutions)
        self.display_solutions(solutions)
        self.input_entry.delete(0, tk.END)
        self.error_label.config(text="")

    def log_missed_prompt(self, prompt):
        """Log the missed prompt to a file."""
        if not os.path.exists(self.missed_prompts_file):
            with open(self.missed_prompts_file, 'w', encoding='utf-8') as f:
                f.write("Prompt,Missed Count\n")

        with open(self.missed_prompts_file, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            prompt_found = False
            for i, line in enumerate(lines):
                if line.startswith(prompt):
                    count = int(line.strip().split(',')[1]) + 1
                    lines[i] = f"{prompt},{count}\n"
                    prompt_found = True
                    break
            if not prompt_found:
                lines.append(f"{prompt},1\n")
            f.seek(0)
            f.writelines(lines)

    def show_missed_prompts(self):
        """Show missed prompts in a new window."""
        missed_window = tk.Toplevel(self.root)
        missed_window.title("Missed Prompts")
        missed_listbox = tk.Listbox(missed_window, font=("Arial", 12), width=40, height=10)
        missed_listbox.pack(pady=10)

        for prompt in self.skipped_prompts:
            missed_listbox.insert(tk.END, prompt)

        missed_listbox.bind("<Double-1>", self.show_missed_prompt_solutions)

        close_button = tk.Button(missed_window, text="Close", font=("Arial", 14), command=missed_window.destroy)
        close_button.pack(pady=10)

    def show_missed_prompt_solutions(self, event):
        """Show the solutions for the selected missed prompt."""
        missed_listbox = event.widget
        selected_index = missed_listbox.curselection()

        if selected_index:
            selected_prompt = missed_listbox.get(selected_index[0])
            solutions = [word for word in self.unique_words if selected_prompt in word]
            random.shuffle(solutions)

            solutions_window = tk.Toplevel(self.root)
            solutions_window.title(f"Solutions for: {selected_prompt}")
            solutions_listbox = tk.Listbox(solutions_window, font=("Arial", 12), width=40, height=10)
            solutions_listbox.pack(pady=10)

            for solution in solutions:
                solutions_listbox.insert(tk.END, solution)

    def handle_spacebar(self, event):
        """Handle spacebar press to skip the prompt."""
        self.skip_prompt()
        return "break"

# Load data
input_filename = "dict.txt"
unique_words, substrings = process_words(input_filename)

# Set up the Tkinter window
root = tk.Tk()
app = GameApp(root, unique_words, substrings)
root.mainloop()