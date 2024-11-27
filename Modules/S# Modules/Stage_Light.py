from PIL import Image, ImageDraw
import math

def convert_to_rgb(hex_code):
    # Convert hexadecimal color code to RGB tuple
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def create_color_wheel(values, format, size=300):
    # Define color codes dictionary
    color_codes = {
        'p': '#680164',  # Purple
        'b': '#0000FF',  # Blue
        'g': '#216216',  # Green
        'r': '#FF0000',  # Red
        'y': '#FFFF00',  # Yellow
        'c': '#00FFFF',  # Cyan
        'o': '#F5A000',  # Orange
        'l': '#8BB58F',  # Lime
        'e': '#808080',  # Grey
    }
    
    # Calculate the angle step between colors
    angle_step = 360 / len(color_codes)
    
    # Create a blank image with white background
    image = Image.new("RGB", (size, size), "black")
    draw = ImageDraw.Draw(image)
    
    # Calculate the radius of the color wheel
    radius = size // 2
    
    # Calculate the center of the color wheel
    center = (size // 2, size // 2)
    
    # Iterate over the characters in the format
    for i, channel in enumerate(format):
        # Calculate the angle for this color
        angle = math.radians(i * angle_step)
        
        # Calculate the position of the color on the wheel
        x = int(center[0] + radius * math.cos(angle))
        y = int(center[1] + radius * math.sin(angle))
        
        # Get the hex code for the channel
        hex_code = color_codes[channel]
        
        # Print the original hex code
        print(f"Original Hex Code for {channel}: {hex_code}")
        
        # Convert hex code to RGB
        rgb = convert_to_rgb(hex_code)
        
        # Get the intensity modifier for this channel and round it to the nearest integer
        intensity_modifier = round(values[i])
        
        # Multiply each RGB component by the intensity modifier
        rgb = tuple(int(rgb_component * intensity_modifier) for rgb_component in rgb)
        
        # Convert the modified RGB values to hexadecimal
        hex_components = [min(255, max(0, component)) for component in rgb]
        altered_hex_code = '#' + ''.join(f'{component:02X}' for component in hex_components)
        
        # Print the altered hex code
        print(f"Altered Hex Code for {channel}: {altered_hex_code}")
        
        # Draw a circle with the color at the calculated position
        draw.ellipse((x - 70, y - 60, x + 60, y + 60), fill=altered_hex_code)
    
    # Save the image
    image.save("color_wheel.png")

# Test the function
input_values = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
format_string = "ppgperycogle"
create_color_wheel(input_values, format_string)
