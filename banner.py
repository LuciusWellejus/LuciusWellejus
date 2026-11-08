import os
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from math import pi

# =====================================================================
# 1. MAPPETRÆ & KONFIGURATION
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
# 2. BANNER BIBLIOTEK (Her tilføjer du nye designs i fremtiden)
# =====================================================================

def saturn_gif(x_grid, y_grid, t):
    """Den matematiske planet- og ring-animation (Saturn-look)."""
    a = x_grid / 30.0
    b = y_grid / 14.0
    d = 1.0 - (a ** 2) - (b ** 2)
    v = (0.99 * b - 0.14 * a) / 0.22
    r = ((0.99 * a + 0.14 * b) ** 2 + v ** 2) ** 0.5
    
    ring = (1.3 < r) & (r < 2.2) & (np.abs(r - 1.8) > 0.05)
    light = np.zeros((ROWS, COLS))
    
    cond_ring = ring & ((d < 0) | (v > 0))
    light[cond_ring] = 0.7 + 0.25 * np.sin(r[cond_ring] * 11 - t * 2)
    
    cond_body = ~cond_ring & (d >= 0)
    light[cond_body] = 0.3 + 0.7 * (d[cond_body] ** 0.5) - (a[cond_body] / 4.0) + (np.sin(v[cond_body] * 5 + t) / 20.0)
    
    # Returnerer lysstyrke-matrix samt RGB-farveprofil (Amber/Orange toner)
    return light, (1.0, 0.85, 0.60) 

# =====================================================================
# 3. UNIVERSAL GRAFIK-MOTOR
# =====================================================================

def render_ascii_banner(style_function, filename):
    """Kører grafik-motoren med den valgte matematiske formel."""
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
        
        # Hent logik fra den valgte funktion
        light_matrix, rgb_ratios = style_function(x_grid, y_grid, t)
        
        # Pak R, G og B procenterne ud af tuplen
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
                
                # RETTELSE: Udregn hver farvekanal individuelt baseret på procenterne
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
        print("Fejl: Ingen billedrammer genereret.")

# =====================================================================
# 4. AFVIKLING
# =====================================================================
if __name__ == "__main__":
    # Genererer filen direkte som saturn.gif i den rigtige mappe
    render_ascii_banner(saturn_gif, "saturn")