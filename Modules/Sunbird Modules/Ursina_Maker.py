from youtube_transcript_api import YouTubeTranscriptApi
import re
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import openai
import os

# Function to extract video ID from YouTube link
def get_video_id(youtube_url):
    regex = r"(?<=v=)[^&#]+"
    match = re.search(regex, youtube_url)
    if match:
        return match.group(0)
    else:
        raise ValueError("Invalid YouTube URL")

# Function to fetch the transcript
def fetch_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return transcript

# Function to clean and format the transcript
def clean_transcript(transcript):
    cleaned_text = ' '.join([entry['text'] for entry in transcript])
    return cleaned_text

# Function to send transcript to OpenAI API and get response
def get_gpt_response(transcript, api_key):
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful youtube video idea to coder bot. Specifically, you are an expert in the ursina game engine, and users come to you with script ideas for ursina codes. You get sent transcript from youtube videos, and you respond promptly with a ursina library programming language full complete script inspired by it in python, using the ursina library! you do not explain the idea in plain text, just produce a script that you can run in a ide or environment that has ursina installed"},
            {"role": "user", "content": transcript}
        ]
    )
    return response.choices[0].message.content.strip()

# Function to get transcript from YouTube link and display it in the GUI
def get_transcript():
    youtube_url = url_entry.get()
    try:
        video_id = get_video_id(youtube_url)
        transcript = fetch_transcript(video_id)
        cleaned_transcript = clean_transcript(transcript)
        transcript_text.delete(1.0, tk.END)
        transcript_text.insert(tk.INSERT, cleaned_transcript)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to send transcript to OpenAI and display the response
def send_to_openai():
    transcript = transcript_text.get(1.0, tk.END).strip()
    if not transcript:
        messagebox.showerror("Error", "No transcript to send to OpenAI.")
        return
    
    api_key = simpledialog.askstring("OpenAI API Key", "Enter your OpenAI API Key:", show='*')
    if not api_key:
        messagebox.showerror("Error", "OpenAI API Key is required.")
        return
    
    try:
        response = get_gpt_response(transcript, api_key)
        response_text.delete(1.0, tk.END)
        response_text.insert(tk.INSERT, response)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create the main window
root = tk.Tk()
root.title("YouTube Transcript Fetcher and GPT Ursina Response")

# Create and place the URL entry widget
tk.Label(root, text="YouTube URL:").grid(row=0, column=0, padx=10, pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

# Create and place the Fetch Transcript button
fetch_button = tk.Button(root, text="Fetch Transcript", command=get_transcript)
fetch_button.grid(row=0, column=2, padx=10, pady=10)

# Create and place the scrolled text widget for displaying the transcript
transcript_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=10)
transcript_text.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

# Create and place the Send to OpenAI button
send_button = tk.Button(root, text="Send to OpenAI", command=send_to_openai)
send_button.grid(row=2, column=1, padx=10, pady=10)

# Create and place the scrolled text widget for displaying the GPT response
response_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=10)
response_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

# Start the Tkinter event loop
root.mainloop()
