import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from math import sin, cos, pi
import subprocess
import os

# Setup character dimensions and grid size
CHAR_WIDTH, CHAR_HEIGHT = 8, 14
COLS, ROWS = 150, 42
WIDTH = COLS * CHAR_WIDTH
HEIGHT = ROWS * CHAR_HEIGHT
FRAMES = 120  # Total frames for a seamless animation loop

# Setup video writer
video_filename = "ascii_planet.mp4"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(video_filename, fourcc, 30, (WIDTH, HEIGHT))

# Try to load a default monospace font
try:
    font = ImageFont.load_default()
except Exception:
    font = None

print("Rendering animated ASCII planet video... Please wait.")

for frame in range(FRAMES):
    # t moves from 0 to 2*pi over the course of the video for a perfect loop
    t = frame * (2 * pi / FRAMES)
    
    # Create blank frame canvas
    img = Image.new("RGB", (WIDTH, HEIGHT), "black")
    draw = ImageDraw.Draw(img)

    # Loop through every cell matching your original console grid
    for y_grid in range(-21, 21):
        for x_grid in range(-75, 75):
            px = (x_grid + 75) * CHAR_WIDTH
            py = (y_grid + 21) * CHAR_HEIGHT
            
            # Base grid coordinates
            a, b = x_grid / 34, y_grid / 20
            
            # --- Animated Mathematics ---
            d = 1 - a * a - b * b
            
            # We animate the surface current lines (v) and ring waves over time
            v = (0.99 * b - 0.14 * a) / 0.22
            r = ((0.99 * a + 0.14 * b) ** 2 + v * v) ** 0.5
            
            ring = 1.3 < r < 2.2 and abs(r - 1.8) > 0.05
            light = 0
            
            if ring and (d < 0 or v > 0):
                # Adding + t makes the rings ripple outwards
                light = 0.7 + 0.25 * sin(r * 11 - t * 2)
            elif d >= 0:
                # Adding - t makes the planet surface texture shift/rotate
                light = 0.3 + 0.7 * d ** 0.5 - a / 4 + sin(v * 5 + t) / 20
                
            # Determine character index mapping
            q = int(min(max(light, 0), 0.99) * 256)
            i = q * 10 // 256
            char_str = " .:-=+*#%@"[i]
            
            # Match your precise amber/golden RGB balance ratios
            r_color = q
            g_color = q * 85 // 100
            b_color = q * 60 // 100
            
            # Draw individual character element
            draw.text((px, py), char_str, fill=(r_color, g_color, b_color), font=font)

    # Convert PIL Image frame to OpenCV BGR array format
    frame_np = np.array(img)
    frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
    video_writer.write(frame_bgr)

# Save and release video stream
video_writer.release()
print(f"Animated ASCII video successfully saved as {video_filename}!")

# Auto-open player execution layer
if os.path.exists(video_filename):
    subprocess.run(["open", video_filename])