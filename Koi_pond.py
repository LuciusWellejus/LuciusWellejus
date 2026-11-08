import numpy as np
from PIL import Image, ImageDraw, ImageFont
from math import sin, pi

# 1. Configuration Constants (Optimized size for a GitHub Banner aspect ratio)
CHAR_WIDTH, CHAR_HEIGHT = 7, 12
COLS, ROWS = 130, 36  # Slightly shorter rows to give it a clean banner look
WIDTH, HEIGHT = COLS * CHAR_WIDTH, ROWS * CHAR_HEIGHT
FRAMES = 90  # 90 frames at 30 FPS gives a clean, 3-second seamless loop

def ss(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def render_frame(frame_idx):
    t = frame_idx * (2.0 * pi / FRAMES)
    img = Image.new("RGB", (WIDTH, HEIGHT), "black")
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for y_grid in range(-ROWS // 2, ROWS // 2):
        for x_grid in range(-COLS // 2, COLS // 2):
            # Calculate pixel positions
            px = (x_grid + COLS // 2) * CHAR_WIDTH
            py = (y_grid + ROWS // 2) * CHAR_HEIGHT
            
            # --- The Mathematics ---
            a, b = x_grid / 30, y_grid / 14
            d = 1 - a * a - b * b
            v = (0.99 * b - 0.14 * a) / 0.22
            r = ((0.99 * a + 0.14 * b) ** 2 + v * v) ** 0.5
            
            ring = 1.3 < r < 2.2 and abs(r - 1.8) > 0.05
            light = 0
            
            if ring and (d < 0 or v > 0):
                light = 0.7 + 0.25 * sin(r * 11 - t * 2)
            elif d >= 0:
                light = 0.3 + 0.7 * d ** 0.5 - a / 4 + sin(v * 5 + t) / 20
                
            q = int(min(max(light, 0), 0.99) * 256)
            i = q * 10 // 256
            char_str = " .:-=+*#%@"[i]
            
            # Amber styling colors
            r_color = q
            g_color = q * 85 // 100
            b_color = q * 60 // 100
            
            draw.text((px, py), char_str, fill=(r_color, g_color, b_color), font=font)
            
    return img

def generate_banner():
    print("Generating animated ASCII GitHub banner structure...")
    frames_list = []
    
    for f in range(FRAMES):
        frame_img = render_frame(f)
        frames_list.append(frame_img)
        if f % 15 == 0:
            print(f"Compilation status: {int(f / FRAMES * 100)}%")
            
    # Save directly as a lightweight looping GIF file
    frames_list[0].save(
        "ascii_banner.gif",
        save_all=True,
        append_images=frames_list[1:],
        duration=33,  # ~30 frames per second
        loop=0
    )
    print("Success! Your banner asset is saved as 'ascii_banner.gif'")

if __name__ == "__main__":
    generate_banner()