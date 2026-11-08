import os
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from math import pi

# --- Hent dine eksterne designs fra mappen ---
from styles.saturn import saturn_style
from styles.sun_signals import sun_signals_style
from styles.boho_sun import boho_sun_style
from styles.nuclear_reactor import nuclear_reactor_style

# =====================================================================
# CONFIGURATION & GLOBAL SETUP
# =====================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
OUTPUT_DIR = os.path.join(BASE_DIR, "ascii_banners")
GIF_DIR = os.path.join(OUTPUT_DIR, "gifs")
os.makedirs(GIF_DIR, exist_ok=True)

CHAR_WIDTH, CHAR_HEIGHT = 7, 12
COLS, ROWS = 130, 36  
WIDTH, HEIGHT = COLS * CHAR_WIDTH, ROWS * CHAR_HEIGHT
FRAMES = 90  

try:
    FONT = ImageFont.load_default()
except Exception:
    FONT = None

# =====================================================================
# UNIVERSAL RENDERING ENGINE
# =====================================================================
def render_ascii_banner(style_function, filename):
    """Kører core-computations og spytter GIF'en ud i ascii_banners/gifs/"""
    print(f"Kompilerer ASCII banner: '{filename}.gif'...")
    start_time = time.time()
    
    y_idx, x_idx = np.indices((ROWS, COLS))
    x_grid = x_idx - COLS // 2
    y_grid = y_idx - ROWS // 2
    
    px_coords = x_idx * CHAR_WIDTH
    py_coords = y_idx * CHAR_HEIGHT
    
    ascii_chars = " .:-=+*#%@"
    frames_list = []
    
    for f in range(FRAMES):
        t = f * (2.0 * pi / FRAMES)
        
        # Kald den eksterne matematiske kodefil
        light_matrix, rgb_ratios = style_function(x_grid, y_grid, t)
        r_ratio, g_ratio, b_ratio = rgb_ratios
        
        q = np.clip(light_matrix, 0.0, 0.99) * 256
        char_indices = (q * 10 // 256).astype(int)
        q_int = q.astype(int)
        
        img = Image.new("RGB", (WIDTH, HEIGHT), "black")
        draw = ImageDraw.Draw(img)
        
        for row in range(ROWS):
            for col in range(COLS):
                char_str = ascii_chars[char_indices[row, col]]
                val = q_int[row, col]
                
                color = (
                    int(val * r_ratio), 
                    int(val * g_ratio), 
                    int(val * b_ratio)
                )
                
                draw.text((px_coords[row, col], py_coords[row, col]), char_str, fill=color, font=FONT)
                
        frames_list.append(img)

    output_path = os.path.join(GIF_DIR, f"{filename}.gif")
    
    if frames_list:
        frames_list[0].save(
            output_path, 
            save_all=True, 
            append_images=frames_list[1:], 
            duration=33, 
            loop=0
        )
        print(f"Gemt succesfuldt i: {output_path} (Tog {time.time() - start_time:.2f}s)\n")
    else:
        print("Fejl: Kunne ikke generere rammer.")

# =====================================================================
# RUN CONTROL CENTRE
# =====================================================================
if __name__ == "__main__":
    # Kør dem du vil generere (sæt '#' foran hvis du vil springe en over)
    # render_ascii_banner(saturn_style, "saturn")
    # render_ascii_banner(sun_signals_style, "sun_signals")
    # render_ascii_banner(boho_sun_style, "boho_sun")
    render_ascii_banner(nuclear_reactor_style, "nuclear_reactor")
