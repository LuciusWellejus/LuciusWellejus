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
from styles.bird_migration import bird_migration_style
from styles.cosmic_waves import cosmic_waves_style

# =====================================================================
# CONFIGURATION & GLOBAL SETUP
# =====================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
OUTPUT_DIR = os.path.join(BASE_DIR, "ascii_banners")
GIF_DIR = os.path.join(OUTPUT_DIR, "gifs")
os.makedirs(GIF_DIR, exist_ok=True)

CHAR_WIDTH, CHAR_HEIGHT = 7, 12
COLS, ROWS = 160, 48  # Kæmpe skærm-layout, der fylder terminalen ud!
WIDTH, HEIGHT = COLS * CHAR_WIDTH, ROWS * CHAR_HEIGHT
FRAMES = 90  

# Vi bruger standardskrifttypen til den endelige tegn-rendering på skærmen
RENDER_FONT = ImageFont.load_default()

# =====================================================================
# RETRO 8-BIT PIXEL ART TEXT GENERATOR (Rettet rækkefølge & størrelse)
# =====================================================================
def get_pixel_logo_mask(logo_text):
    """Genererer en perfekt, skarp retro-maske til gridet uden slørede fonte."""
    mask = np.zeros((ROWS, COLS), dtype=bool)
    if not logo_text or logo_text != "Lxirxus":
        return mask
        
    # Håndlavet 5x5 pixel-art bitmap for hvert bogstav i "Lxirxus"
    font_map = {
        'L': ["10000",
              "10000",
              "10000",
              "10000",
              "11111"],
        'x': ["10001",
              "01010",
              "00100",
              "01010",
              "10001"],
        'i': ["00100",
              "00000",
              "00100",
              "00100",
              "00100"],
        'r': ["01110",
              "01001",
              "01000",
              "01000",
              "01000"],
        'u': ["10001",
              "10001",
              "10001",
              "10001",
              "01110"],
        's': ["01111",
              "10000",
              "01110",
              "00001",
              "11110"]
    }
    
    # Byg strengen i den rigtige rækkefølge fra venstre mod højre
    combined_rows = ["", "", "", "", ""]
    for char in logo_text:
        bitmap = font_map.get(char, ["00000"]*5)
        for i in range(5):
            combined_rows[i] += bitmap[i] + "0"  # Mindre mellemrum mellem tegn (1 pixel)
            
    # Find dimensionerne af vores pixel-logo
    text_w = len(combined_rows[0])
    text_h = 5
    
    # Sat ned til en blødere 3x3 pixelblok pr. bit, så alt kan være på skærmen
    scale_x, scale_y = 3, 3
    
    # Find startpositionen så teksten centreres præcist i midten af skærmen
    start_x = (COLS - (text_w * scale_x)) // 2
    start_y = (ROWS - (text_h * scale_y)) // 2
    
    # Tegn bogstaverne direkte ind i det binære boolean grid
    for r_pix in range(text_h):
        for c_pix in range(text_w):
            if combined_rows[r_pix][c_pix] == '1':
                y_pos = start_y + r_pix * scale_y
                x_pos = start_x + c_pix * scale_x
                mask[y_pos:y_pos+scale_y, x_pos:x_pos+scale_x] = True
                
    return mask

# =====================================================================
# UNIVERSAL RENDERING ENGINE WITH SCANLINE EFFECT
# =====================================================================
def render_ascii_banner(style_function, filename, logo_text=None):
    """Kører core-computations og spytter GIF'en ud i ascii_banners/gifs/"""
    print(f"Kompilerer ASCII banner: '{filename}.gif'...")
    start_time = time.time()
    
    y_idx, x_idx = np.indices((ROWS, COLS))
    x_grid = x_idx - COLS // 2
    y_grid = y_idx - ROWS // 2
    
    px_coords = x_idx * CHAR_WIDTH
    py_coords = y_idx * CHAR_HEIGHT
    
    # Hent den knivskarpe, pixelerede logo-maske
    logo_mask = get_pixel_logo_mask(logo_text)
    
    ascii_chars = " .:-=+*#%@"
    frames_list = []
    
    for f in range(FRAMES):
        t = f * (2.0 * pi / FRAMES)
        
        # Hent baggrundsmateriale og RGB-værdier fra stilen
        light_matrix, rgb_ratios = style_function(x_grid, y_grid, t)
        r_ratio, g_ratio, b_ratio = rgb_ratios
        
        # Udregn placeringen af den lodrette scanningslinje
        # Linjen starter i venstre side og bevæger sig glat over kolonnerne hen over tid (t)
        scan_progress = f / FRAMES
        scan_col = int(scan_progress * COLS)
        
        # Skab en blød glød (linjetykkelse) på 3 kolonner omkring centrum af linjen
        scan_mask = (x_idx >= scan_col - 1) & (x_idx <= scan_col + 1)
        
        # Tving logoet helt frem i forgrunden med maksimal tegnstyrke
        if logo_text:
            light_matrix[logo_mask] = 0.99
        
        q = np.clip(light_matrix, 0.0, 0.99) * 256
        char_indices = (q * 10 // 256).astype(int)
        q_int = q.astype(int)
        
        img = Image.new("RGB", (WIDTH, HEIGHT), "black")
        draw = ImageDraw.Draw(img)
        
        for row in range(ROWS):
            for col in range(COLS):
                char_str = ascii_chars[char_indices[row, col]]
                val = q_int[row, col]
                
                # Standard farveprofil fra stilen
                r_c, g_c, b_c = r_ratio, g_ratio, b_ratio
                
                # Hvis scanningslinjen krydser et bogstavs-pixel, skifter det til hvidt!
                if logo_text and logo_mask[row, col] and scan_mask[row, col]:
                    # Ren hvid lysstyrke (val, val, val) uafhængigt af baggrunden
                    color = (val, val, val)
                else:
                    color = (
                        int(val * r_c), 
                        int(val * g_c), 
                        int(val * b_c)
                    )
                
                draw.text((px_coords[row, col], py_coords[row, col]), char_str, fill=color, font=RENDER_FONT)
                
        frames_list.append(img)

    output_path = os.path.join(GIF_DIR, f"{filename}.gif")
    
    # RETTELSE: listen kaldes nu korrekt via frames_list[0].save for fejlfrit output
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
    # render_ascii_banner(nuclear_reactor_style, "nuclear_reactor")
    # render_ascii_banner(bird_migration_style, "bird_migration")
    render_ascii_banner(cosmic_waves_style, "cosmic_waves", logo_text="Lxirxus")