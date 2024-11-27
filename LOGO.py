import tkinter as tk
import math

def create_bouba_shape(canvas, x_center, y_center, outer_radius, inner_radius, **kwargs):
    points = []
    for i in range(16):  # Double points to create a scalloped edge
        angle_deg = 22.5 * i  # 360 / 16 = 22.5 degrees per segment
        angle_rad = math.radians(angle_deg)
        radius = outer_radius if i % 2 == 0 else inner_radius
        x = x_center + radius * math.cos(angle_rad)
        y = y_center + radius * math.sin(angle_rad)
        points.extend([x, y])
    canvas.create_polygon(points, smooth=True, **kwargs)  # smooth=True applied here

def create_kiki_shape(canvas, x_center, y_center, outer_radius, inner_radius, **kwargs):
    points = []
    for i in range(16):
        angle_deg = 22.5 * i
        angle_rad = math.radians(angle_deg)
        radius = outer_radius if i % 2 == 0 else inner_radius
        x = x_center + radius * math.cos(angle_rad)
        y = y_center + radius * math.sin(angle_rad)
        points.extend([x, y])
    canvas.create_polygon(points, **kwargs)

root = tk.Tk()
root.title("Bouba and Kiki Shapes")

canvas_width = 400
canvas_height = 200

canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg='white')
canvas.pack()

# Draw bouba shape (wavy scalloped octagon)
create_bouba_shape(canvas, 100, 100, 80, 60, fill='black', outline='black', width=3)

# Draw kiki shape (8-pointed star)
create_kiki_shape(canvas, 300, 100, 80, 30, fill='black')

root.mainloop()
