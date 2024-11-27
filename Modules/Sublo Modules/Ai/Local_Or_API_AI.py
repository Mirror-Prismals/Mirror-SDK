import os
import openai
import json
import tkinter as tk
from tkinter import simpledialog, scrolledtext, ttk
import pyttsx3
import random
import math

# Define the hex_to_rgb function
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    return tuple(int(hex_color[i:i+lv//3], 16) for i in range(0, lv, lv//3))

def generate_random_hex_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

class Character:
    def __init__(self, name, tagline, description, greeting, definition):
        self.name = name
        self.tagline = tagline
        self.description = description
        self.greeting = greeting
        self.definition = definition

def generate_response(prompt):
    # Create a chat completion
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompt
    )
    return response.choices[0].message.content.strip()

class CharacterApp:
    def __init__(self, root):
        self.root = root
        self.root.title('''"Buscar ‘Mí’ con tilde y ‘mi’ sin tilde Meek Impressor o Compassor{]}"Mira: Lolsiento.''')

        # Ask for OpenAI API key
        self.api_key = simpledialog.askstring("OpenAI API Key", "Please enter your OpenAI API key:", show='*')
        if self.api_key is None or self.api_key.strip() == "":
            self.switch_to_markov_chain()
            return
        
        os.environ["OPENAI_API_KEY"] = self.api_key

        # Configure OpenAI client
        global client
        client = openai.Client(api_key=self.api_key)
        
        # Configure text-to-speech engine
        self.tts_engine = pyttsx3.init()
        
        # Set goofy voice effect
        self.tts_engine.setProperty('rate', 200)  # Speed up the voice
        self.tts_engine.setProperty('volume', 1)  # Volume level 0-1
        voices = self.tts_engine.getProperty('voices')
        self.tts_engine.setProperty('voice', voices[1].id)  # Choose a voice with a higher pitch

        # Initialize and set the background color
        self.set_random_colors()
        
        # Tabs
        self.tabControl = ttk.Notebook(root)
        self.tab1 = ttk.Frame(self.tabControl, style="TFrame")
        self.tab2 = ttk.Frame(self.tabControl, style="TFrame")
        self.tabControl.add(self.tab1, text='Character')
        self.tabControl.add(self.tab2, text='Character List')
        self.tabControl.pack(expand=1, fill="both")
        
        style = ttk.Style()
        style.configure("TFrame", background=self.hex_color)
        style.configure("TLabel", background=self.hex_color)
        style.configure("TButton", background=self.hex_color)
        
        # Character input fields
        self.name_label = ttk.Label(self.tab1, text="Name")
        self.name_label.pack()
        self.name_entry = tk.Entry(self.tab1, bg=self.hex_color)
        self.name_entry.pack()
        
        self.tagline_label = ttk.Label(self.tab1, text="Tagline")
        self.tagline_label.pack()
        self.tagline_entry = tk.Entry(self.tab1, bg=self.hex_color)
        self.tagline_entry.pack()
        
        self.description_label = ttk.Label(self.tab1, text="Description")
        self.description_label.pack()
        self.description_entry = tk.Entry(self.tab1, bg=self.hex_color)
        self.description_entry.pack()
        
        self.greeting_label = ttk.Label(self.tab1, text="Greeting")
        self.greeting_label.pack()
        self.greeting_entry = tk.Entry(self.tab1, bg=self.hex_color)
        self.greeting_entry.pack()
        
        self.definition_label = ttk.Label(self.tab1, text="Definition")
        self.definition_label.pack()
        self.definition_text = scrolledtext.ScrolledText(self.tab1, wrap=tk.WORD, width=50, height=10, bg=self.hex_color)
        self.definition_text.pack()
        
        self.edit_button = tk.Button(self.tab1, text="Edit", command=self.edit_character, bg=self.hex_color)
        self.edit_button.pack()
        
        self.save_button = tk.Button(self.tab1, text="Save", command=self.save_character, bg=self.hex_color)
        self.save_button.pack()
        
        self.load_button = tk.Button(self.tab2, text="Load", command=self.load_character, bg=self.hex_color)
        self.load_button.pack()
        
        self.character_listbox = tk.Listbox(self.tab2, width=50, height=10, bg=self.hex_color)
        self.character_listbox.pack()
        
        self.chat_log = scrolledtext.ScrolledText(self.tab1, wrap=tk.WORD, width=50, height=10, bg=self.hex_color)
        self.chat_log.pack()
        
        self.message_label = ttk.Label(self.tab1, text="Your Message")
        self.message_label.pack()
        self.message_entry = tk.Entry(self.tab1, bg=self.hex_color)
        self.message_entry.pack()
        
        self.send_button = tk.Button(self.tab1, text="Send", command=self.send_message, bg=self.hex_color)
        self.send_button.pack()
        
        # Character list
        self.character_list = []
        self.selected_character = None
        
        # Load characters from files
        self.load_characters_from_files()

        # Bind close event to save characters
        root.protocol("WM_DELETE_WINDOW", self.save_characters_on_close)

        # Start the color randomizer
        self.randomize_colors()

    def set_random_colors(self):
        self.hex_color = generate_random_hex_color()
        self.rgb_color = hex_to_rgb(self.hex_color)
        self.root.configure(bg=self.hex_color)

    def randomize_colors(self):
        self.set_random_colors()
        self.root.after(5000, self.randomize_colors)  # Change colors every 5 seconds

    def create_character(self):
        name = self.name_entry.get()
        tagline = self.tagline_entry.get()
        description = self.description_entry.get()
        greeting = self.greeting_entry.get()
        definition = self.definition_text.get("1.0", tk.END)
        
        character = Character(name, tagline, description, greeting, definition)
        self.character_list.append(character)
        self.update_character_listbox()
        self.clear_character_input_fields()
        
    def edit_character(self):
        if self.selected_character:
            # Clear input fields
            self.clear_character_input_fields()
            # Populate input fields with selected character's details
            self.name_entry.insert(0, self.selected_character.name)
            self.tagline_entry.insert(0, self.selected_character.tagline)
            self.description_entry.insert(0, self.selected_character.description)
            self.greeting_entry.insert(0, self.selected_character.greeting)
            self.definition_text.insert(tk.END, self.selected_character.definition)
        else:
            self.chat_log.insert(tk.END, "Please select a character to edit.\n")
        
    def save_character(self):
        if not self.selected_character:
            self.create_character()
            self.chat_log.insert(tk.END, "Character saved.\n")
        else:
            self.chat_log.insert(tk.END, "Character updated.\n")
            self.selected_character.name = self.name_entry.get()
            self.selected_character.tagline = self.tagline_entry.get()
            self.selected_character.description = self.description_entry.get()
            self.selected_character.greeting = self.greeting_entry.get()
            self.selected_character.definition = self.definition_text.get("1.0", tk.END)
        
    def load_character(self):
        character_index = self.character_listbox.curselection()
        if character_index:
            character_index = int(character_index[0])
            self.selected_character = self.character_list[character_index]
            self.chat_log.insert(tk.END, f"Loaded character {self.selected_character.name}\n")
            self.populate_character_fields()
        else:
            self.chat_log.insert(tk.END, "Please select a character to load.\n")
        
    def send_message(self):
        user_message = self.message_entry.get()
        self.chat_log.insert(tk.END, f"You: {user_message}\n")

        # Use default character if none selected
        character_name = "GPTChatter"
        character_definition = "You are a helpful assistant."

        # Build the prompt with the default character's persona
        prompt = [
            {"role": "system", "content": f"You are to play the character of: {character_name}. {character_definition}"},
            {"role": "user", "content": user_message}
        ]
        
        ai_response = generate_response(prompt)
        
        self.chat_log.insert(tk.END, f"{character_name}: {ai_response}\n")
        self.message_entry.delete(0, tk.END)
        
        # Text-to-Speech with goofy effect
        self.tts_engine.say(ai_response)
        self.tts_engine.runAndWait()
    
    def update_character_listbox(self):
        self.character_listbox.delete(0, tk.END)
        for character in self.character_list:
            self.character_listbox.insert(tk.END, character.name)
            
    def clear_character_input_fields(self):
        self.name_entry.delete(0, tk.END)
        self.tagline_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.greeting_entry.delete(0, tk.END)
        self.definition_text.delete(1.0, tk.END)
        
    def populate_character_fields(self):
        self.clear_character_input_fields()
        self.name_entry.insert(0, self.selected_character.name)
        self.tagline_entry.insert(0, self.selected_character.tagline)
        self.description_entry.insert(0, self.selected_character.description)
        self.greeting_entry.insert(0, self.selected_character.greeting)
        self.definition_text.insert(tk.END, self.selected_character.definition)

    def load_characters_from_files(self):
        character_folder = "characters"
        if not os.path.exists(character_folder):
            os.makedirs(character_folder)
        
        for filename in os.listdir(character_folder):
            if filename.endswith(".json"):
                with open(os.path.join(character_folder, filename), "r") as file:
                    character_data = json.load(file)
                    character = Character(**character_data)
                    self.character_list.append(character)
        
        self.update_character_listbox()

    def save_character_to_file(self, character):
        character_folder = "characters"
        if not os.path.exists(character_folder):
            os.makedirs(character_folder)
        
        filename = f"{character.name}.json"
        filepath = os.path.join(character_folder, filename)
        with open(filepath, "w") as file:
            character_data = {
                "name": character.name,
                "tagline": character.tagline,
                "description": character.description,
                "greeting": character.greeting,
                "definition": character.definition
            }
            json.dump(character_data, file)

    def save_characters_to_files(self):
        for character in self.character_list:
            self.save_character_to_file(character)
            
    def save_characters_on_close(self):
        self.save_characters_to_files()
        self.root.destroy()

    def switch_to_markov_chain(self):
        # Destroy current widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Set up new Markov chain GUI
        self.chat_log = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=10)
        self.chat_log.pack()

        self.message_label = ttk.Label(self.root, text="Your Message")
        self.message_label.pack()
        self.message_entry = tk.Entry(self.root)
        self.message_entry.pack()

        self.send_button = tk.Button(self.root, text="Send", command=self.send_markov_message)
        self.send_button.pack()

        # Markov chain variables
        self.ngram = {}
        self.window_size = 2
        self.corpus = r"asleep Plug half Corpus half Here half there half i dont care lol. -mira"

    def preprocess_corpus(self, corpus):
        """Preprocess the corpus text."""
        return corpus.lower().replace('"','').replace("'",'').replace('\n','').replace(')','').replace('(','').replace('[','').replace(']','').replace('’','').replace("“",'').replace("”",'')

    def shannon_entropy(self, word_counts):
        """Calculate Shannon entropy."""
        total_count = sum(word_counts.values())
        entropy = 0
        for count in word_counts.values():
            probability = count / total_count
            entropy -= probability * math.log2(probability)
        return entropy

    def generate_markov_response(self, user_input):
        """Generate a response based on the user input and the n-gram model.
        You: hi
Bot: half here
You: mira?
Bot: there half
You: hi mira.
Bot: asleep plug
You: *snap* mida? iA?
Bot: asleep plug half
You: chatCorp: lol
Bot: here half
You: sleepy deepy miri 
Bot: corpus half here
You: gtg bye bye :)
Bot: asleep plug half corpus"""
        out = ''
        
        # Combine user input and base corpus
        combined_corpus = user_input + ' ' + self.corpus
        
        # Preprocess combined corpus
        combined_corpus = self.preprocess_corpus(combined_corpus)
        
        # Split combined corpus into tokens
        tokens = combined_corpus.split()
        
        # Populate n-gram from combined corpus
        for i in range(len(tokens) - self.window_size):
            word_pair = tuple(tokens[i:i+self.window_size])
            if '' in word_pair:
                continue
            next_word = tokens[i+self.window_size]
            self.ngram.setdefault(word_pair, []).append(next_word)
        
        # Calculate Shannon entropy for each word pair
        entropy_scores = {}
        for word_pair, next_words in self.ngram.items():
            next_word_counts = {}
            for word in next_words:
                next_word_counts[word] = next_word_counts.get(word, 0) + 1
            entropy_scores[word_pair] = self.shannon_entropy(next_word_counts)
        
        # Sort word pairs by entropy in descending order
        sorted_word_pairs = sorted(entropy_scores, key=entropy_scores.get, reverse=True)
        
        # Get the word pairs with the highest entropy
        high_entropy_word_pairs = sorted_word_pairs[:10]
        
        # Choose a word pair from the high entropy word pairs
        chosen_word_pair = random.choice(high_entropy_word_pairs)
        
        # Mirror the user's input length
        out = ' '.join(chosen_word_pair)
        
        while len(out.split()) < len(user_input.split()):
            if chosen_word_pair not in self.ngram.keys():
                break
            next_word = random.choice(self.ngram[chosen_word_pair])
            out += ' ' + next_word
            chosen_word_pair = (chosen_word_pair[1], next_word)
        
        return out

    def send_markov_message(self):
        user_message = self.message_entry.get()
        self.chat_log.insert(tk.END, f"You: {user_message}\n")

        response = self.generate_markov_response(user_message)
        
        self.chat_log.insert(tk.END, f"Bot: {response}\n")
        self.message_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = CharacterApp(root)
    root.mainloop()
