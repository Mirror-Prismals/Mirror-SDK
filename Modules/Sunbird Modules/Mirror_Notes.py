import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import json
import os
from openai import OpenAI

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notes App with GPT-4")
        self.root.geometry("1200x800")

        # Prompt for API Key
        self.api_key = simpledialog.askstring("API Key", "Enter your OpenAI API Key:", show='*')
        self.client = OpenAI(api_key=self.api_key)

        # Frame for note input and list
        self.note_frame = tk.Frame(root)
        self.note_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Note input
        self.note_title_label = tk.Label(self.note_frame, text="Note Title")
        self.note_title_label.pack()
        self.note_title_entry = tk.Entry(self.note_frame, width=100)
        self.note_title_entry.pack()

        self.note_content_label = tk.Label(self.note_frame, text="Note Content")
        self.note_content_label.pack()
        self.note_content_text = scrolledtext.ScrolledText(self.note_frame, wrap=tk.WORD, width=100, height=20)
        self.note_content_text.pack()

        self.save_note_button = tk.Button(self.note_frame, text="Save Note", command=self.save_note)
        self.save_note_button.pack()

        # Note list
        self.notes_list_label = tk.Label(self.note_frame, text="Saved Notes")
        self.notes_list_label.pack()
        self.notes_listbox = tk.Listbox(self.note_frame, width=100, height=10)
        self.notes_listbox.pack()
        self.notes_listbox.bind('<<ListboxSelect>>', self.display_note)

        # Frame for GPT interaction
        self.gpt_frame = tk.Frame(root)
        self.gpt_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.gpt_input_label = tk.Label(self.gpt_frame, text="Ask GPT-4")
        self.gpt_input_label.pack()
        self.gpt_input_text = tk.Entry(self.gpt_frame, width=100)
        self.gpt_input_text.pack()

        self.gpt_response_label = tk.Label(self.gpt_frame, text="GPT-4 Response")
        self.gpt_response_label.pack()
        self.gpt_response_text = scrolledtext.ScrolledText(self.gpt_frame, wrap=tk.WORD, width=100, height=20)
        self.gpt_response_text.pack()
        
        self.ask_gpt_button = tk.Button(self.gpt_frame, text="Ask GPT-4", command=self.ask_gpt)
        self.ask_gpt_button.pack()

        self.notes = []
        self.load_notes()

    def generate_response(self, prompt):
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o",
        )
        return chat_completion.choices[0].message.content.strip()

    def save_note(self):
        title = self.note_title_entry.get()
        content = self.note_content_text.get('1.0', tk.END).strip()
        if title and content:
            note = {"title": title, "content": content}
            self.notes.append(note)
            self.save_notes()
            self.note_title_entry.delete(0, tk.END)
            self.note_content_text.delete('1.0', tk.END)
            self.update_notes_list()
        else:
            messagebox.showwarning("Input Error", "Both title and content are required!")

    def display_note(self, event):
        selected_index = self.notes_listbox.curselection()
        if selected_index:
            note = self.notes[selected_index[0]]
            self.note_title_entry.delete(0, tk.END)
            self.note_title_entry.insert(tk.END, note["title"])
            self.note_content_text.delete('1.0', tk.END)
            self.note_content_text.insert(tk.END, note["content"])

    def ask_gpt(self):
        prompt = self.gpt_input_text.get()
        if prompt:
            # Include the titles of all notes
            all_titles = "\n".join([note["title"] for note in self.notes])

            # Get the current note title and content
            current_note_title = self.note_title_entry.get()
            current_note_content = self.note_content_text.get('1.0', tk.END).strip()

            # Create a comprehensive prompt
            full_prompt = (
                f"Titles of all notes:\n{all_titles}\n\n"
                f"Current note title: {current_note_title}\n"
                f"Current note content: {current_note_content}\n\n"
                f"User's question: {prompt}"
            )

            response = self.generate_response(full_prompt)
            self.gpt_response_text.delete('1.0', tk.END)
            self.gpt_response_text.insert(tk.END, response)
        else:
            messagebox.showwarning("Input Error", "Prompt is required!")

    def save_notes(self):
        with open("notes.json", "w") as f:
            json.dump(self.notes, f)

    def load_notes(self):
        try:
            with open("notes.json", "r") as f:
                self.notes = json.load(f)
            self.update_notes_list()
        except FileNotFoundError:
            self.notes = []

    def update_notes_list(self):
        self.notes_listbox.delete(0, tk.END)
        for note in self.notes:
            self.notes_listbox.insert(tk.END, note["title"])

if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()
