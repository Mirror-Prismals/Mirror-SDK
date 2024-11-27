#v4
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import pygame

class GoDAWApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_widgets()
        pygame.mixer.init()  # Initialize pygame mixer for audio playback
        self.tracks = [None, None, None, None]  # List to store instances of pygame.mixer.Sound for each track
        self.loaded_files = ["", "", "", ""]  # List to store file paths for each track

    def setup_window(self):
        self.root.title("GoDAW")
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.root.minsize(800, 600)

    def exit_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', False)

    def create_widgets(self):
        self.create_menu()
        self.create_tracks()
        self.transport_controls()

    def create_menu(self):
        menubar = tk.Menu(self.root)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        self.root.config(menu=menubar)

    def create_tracks(self):
        self.track_frames = []
        self.track_labels = []
        self.track_buttons = []

        for i in range(4):
            track_frame = tk.Frame(self.root, bg="gray", height=100)
            track_frame.pack(fill=tk.X, padx=5, pady=2)
            self.track_frames.append(track_frame)

            track_label = tk.Label(track_frame, text=f"Track {i+1}", bg="white", height=2)
            track_label.pack(side=tk.LEFT, padx=10, pady=10)
            self.track_labels.append(track_label)

            play_btn = tk.Button(track_frame, text="Play", command=lambda idx=i: self.play_track(idx), width=10)
            play_btn.pack(side=tk.LEFT, padx=10, pady=10)
            self.track_buttons.append(play_btn)

    def transport_controls(self):
        transport = tk.Frame(self.root, height=100, bg="#444")
        transport.pack(fill=tk.X, side=tk.BOTTOM)

        self.global_play_btn = tk.Button(transport, text="Global Play", command=self.global_play, width=15)
        self.global_play_btn.pack(side=tk.LEFT, padx=10, pady=20)

        self.global_stop_btn = tk.Button(transport, text="Global Stop", command=self.global_stop, width=15)
        self.global_stop_btn.pack(side=tk.LEFT, padx=10, pady=20)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if file_path:
            self.prompt_track_selection(file_path)

    def prompt_track_selection(self, file_path):
        # Prompt user to select a track for loading the audio file
        track_selection = tk.simpledialog.askinteger("Track Selection", "Enter track number (1-4):", initialvalue=1, minvalue=1, maxvalue=4)
        if track_selection is not None:
            self.load_audio(file_path, track_selection - 1)

    def save_file(self):
        # Placeholder for save functionality
        messagebox.showinfo("Save", "Save functionality is not implemented yet.")

    def load_audio(self, file_path, track_idx):
        try:
            # Stop current track if playing
            if self.tracks[track_idx]:
                self.tracks[track_idx].stop()

            # Load audio onto the selected track index
            self.tracks[track_idx] = pygame.mixer.Sound(file_path)
            self.loaded_files[track_idx] = file_path.split("/")[-1]  # Store file name
            self.track_labels[track_idx].config(text=self.loaded_files[track_idx], bg="yellow")  # Update track label
            messagebox.showinfo("Open", f"Loaded audio file: {file_path} on Track {track_idx + 1}")
        except pygame.error:
            messagebox.showerror("Error", "Failed to load audio file.")

    def play_track(self, idx):
        # Start playing individual track if loaded
        if self.tracks[idx]:
            self.tracks[idx].play()
            self.track_labels[idx].config(bg="green")  # Visual indication of playing
        else:
            messagebox.showwarning("Track Not Loaded", f"Track {idx + 1} is not loaded.")

    def global_play(self):
        # Start playing all tracks simultaneously if loaded
        for i in range(4):
            if self.tracks[i]:
                self.tracks[i].play()
                self.track_labels[i].config(bg="green")  # Visual indication of playing

    def global_stop(self):
        # Stop all tracks
        for i in range(4):
            if self.tracks[i]:
                self.tracks[i].stop()
                self.track_labels[i].config(bg="white")  # Reset visual indication

if __name__ == "__main__":
    root = tk.Tk()
    app = GoDAWApp(root)
    root.mainloop()
