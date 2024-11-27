import tkinter as tk
from tkinter import messagebox

def expand_hex(custom_hex):
    try:
        # Ensure the input starts with %~ and contains only allowed characters
        if not custom_hex.startswith("%~") or not all(c in "%~08Ff-" for c in custom_hex):
            raise ValueError("Invalid input format")

        # Extract the content after %~
        hex_content = custom_hex[2:]

        # Check for a single negative sign and ensure the hex content has exactly six characters
        if hex_content.count('-') != 1 or len(hex_content.replace('-', '')) != 6:
            raise ValueError("Input must contain exactly one negative sign and be six characters long")

        # Find the position of the negative sign
        neg_pos = hex_content.find('-')

        # Initialize channel values
        red = orange = green = cyan = blue = purple = ""

        # Extract the hex characters ignoring the negative sign
        hex_chars = hex_content.replace('-', '')

        # Place the negative sign logically
        if neg_pos == 0:
            red = "-" + hex_chars[0] + hex_chars[1]
            orange = hex_chars[1] + hex_chars[2]
            green = hex_chars[2] + "-" + hex_chars[3]
            cyan = "-" + hex_chars[3] + hex_chars[4]
            blue = hex_chars[4] + hex_chars[5]
            purple = hex_chars[5] + hex_chars[0]
        elif neg_pos == 1:
            red = hex_chars[0] + "-" + hex_chars[1]
            orange = "-" + hex_chars[1] + hex_chars[2]
            green = hex_chars[2] + hex_chars[3]
            cyan = hex_chars[3] + hex_chars[4]
            blue = hex_chars[4] + hex_chars[5]
            purple = hex_chars[5] + hex_chars[0]
        elif neg_pos == 2:
            red = hex_chars[0] + hex_chars[1]
            orange = hex_chars[1] + "-" + hex_chars[2]
            green = "-" + hex_chars[2] + hex_chars[3]
            cyan = hex_chars[3] + hex_chars[4]
            blue = hex_chars[4] + hex_chars[5]
            purple = hex_chars[5] + hex_chars[0]
        elif neg_pos == 3:
            red = hex_chars[0] + hex_chars[1]
            orange = hex_chars[1] + hex_chars[2]
            green = hex_chars[2] + "-" + hex_chars[3]
            cyan = "-" + hex_chars[3] + hex_chars[4]
            blue = hex_chars[4] + hex_chars[5]
            purple = hex_chars[5] + hex_chars[0]
        elif neg_pos == 4:
            red = hex_chars[0] + hex_chars[1]
            orange = hex_chars[1] + hex_chars[2]
            green = hex_chars[2] + hex_chars[3]
            cyan = hex_chars[3] + "-" + hex_chars[4]
            blue = "-" + hex_chars[4] + hex_chars[5]
            purple = hex_chars[5] + hex_chars[0]
        elif neg_pos == 5:
            red = hex_chars[0] + hex_chars[1]
            orange = hex_chars[1] + hex_chars[2]
            green = hex_chars[2] + hex_chars[3]
            cyan = hex_chars[3] + hex_chars[4]
            blue = hex_chars[4] + "-" + hex_chars[5]
            purple = "-" + hex_chars[5] + hex_chars[0]
        else:
            raise ValueError("Invalid format for custom hex content")

        # Debug statements to print the values
        print(f"Red = {red}")
        print(f"Orange = {orange}")
        print(f"Green = {green}")
        print(f"Cyan = {cyan}")
        print(f"Blue = {blue}")
        print(f"Purple = {purple}")

        return (red, orange, green, cyan, blue, purple)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None

def on_expand():
    custom_hex = entry.get()
    if not all(c in "%~08Ff-" for c in custom_hex):
        messagebox.showerror("Error", "Invalid characters in input. Only %~08Ff- are allowed.")
        return
    expanded_values = expand_hex(custom_hex)
    if expanded_values:
        result_label.config(text=f"Red: {expanded_values[0]}, Orange: {expanded_values[1]}, Green: {expanded_values[2]}, "
                                 f"Cyan: {expanded_values[3]}, Blue: {expanded_values[4]}, Purple: {expanded_values[5]}")

# Setup the main application window
root = tk.Tk()
root.title("Custom Hex Expander")
root.attributes("-fullscreen", True)

# Create a frame for input and output
frame = tk.Frame(root)
frame.pack(pady=20)

# Input label and entry
input_label = tk.Label(frame, text="Enter custom hex code:")
input_label.grid(row=0, column=0, padx=10, pady=10)
entry = tk.Entry(frame, width=20)
entry.grid(row=0, column=1, padx=10, pady=10)

# Expand button
expand_button = tk.Button(frame, text="Expand", command=on_expand)
expand_button.grid(row=0, column=2, padx=10, pady=10)

# Result label
result_label = tk.Label(frame, text="Expanded hex values will appear here")
result_label.grid(row=1, column=0, columnspan=3, pady=10)

# Exit button
exit_button = tk.Button(root, text="Exit", command=root.quit)
exit_button.pack(pady=20)

# Run the main loop
root.mainloop()
