import numpy as np
from math import pi

def nuclear_reactor_style(x_grid, y_grid, t):
    """Nyt design: Atomreaktor med grøn røg, partikler og et radioaktivt symbol på tårnet."""
    ROWS, COLS = x_grid.shape
    
    # Juster akserne (tårnet placeres lavt i midten)
    a = x_grid / 20.0
    b = (y_grid + 8) / 10.0  # Skub tårnets bund nedad
    
    light = np.zeros((ROWS, COLS))
    
    # --- 1. BYGNING: KØLETÅRNETS SILHUET ---
    # Klassisk hyperbolsk tårnform (bred bund, smallere talje, bred top)
    tower_width = 0.5 + 0.4 * (b - 0.2) ** 2
    # Begræns tårnet i højden (b skal være mellem bund og toppen af skorstenen)
    tower_mask = (b > -0.8) & (b < 1.2) & (np.abs(a) < tower_width)
    light[tower_mask] = 0.45
    
    # --- 2. DET RADIOAKTIVE SYMBOL PÅ TÅRNET ---
    # Centreret på tårnet
    sa = a / 0.35
    sb = (b - 0.1) / 0.35
    sr = (sa ** 2 + sb ** 2) ** 0.5
    s_angle = np.arctan2(sb, sa)
    
    if np.any(tower_mask):
        # Lille indre cirkel
        center_circle = (sr < 0.25)
        # De tre faneblade (blade) i symbolet med 60 graders mellemrum
        blades = (sr >= 0.35) & (sr < 1.0) & (
            ((s_angle > -pi/6) & (s_angle < pi/6)) |
            ((s_angle > 5*pi/6) | (s_angle < -5*pi/6)) |
            ((s_angle > -pi + pi/6) & (s_angle < -pi/2)) | 
            ((s_angle > pi/2 - pi/6) & (s_angle < pi/2 + pi/6))
        )
        # Maskér det præcist over tårnets overflade
        symbol_zone = tower_mask & (center_circle | blades)
        light[symbol_zone] = 0.95
        
    # --- 3. GRØN RØG OG GASEMISSIONER ---
    # Røgen starter over tårnets top (b <= -0.8)
    smoke_y = b + 0.8
    
    # Røgen spreder sig ud og driver opad som en sinuskurve over tid (t)
    smoke_wave = a + 0.3 * np.sin(smoke_y * 3.0 - t * 4.0)
    smoke_spread = 0.4 - smoke_y * 0.25  # Spreder sig mere ud jo højere op den kommer
    
    # RETTELSE: Vi bygger en ren, samlet 2D boolean maske for hele røgskyen
    full_smoke_mask = (b <= -0.8) & (np.abs(smoke_wave) < smoke_spread) & (smoke_y > -2.0)
    
    # Nu tildeles værdierne fejlfrit i 2D
    light[full_smoke_mask] = 0.65 + 0.25 * np.sin(smoke_y[full_smoke_mask] * 6.0 + t * 5.0)
        
    # --- 4. RADIOAKTIVE PARTIKLER (FLIMRENDE GNISTER) ---
    # Abstrakte partikler der skydes op i luften over tårnet
    particle_wave = np.sin(x_grid * 0.8 + t * 6.0) * np.cos(y_grid * 0.5 - t * 4.0)
    particle_zone = (b <= -0.6) & (np.abs(a) < 1.8) & (particle_wave > 0.78)
    light[particle_zone] = 0.99
    
    # Strålende radioaktiv grøn farveprofil (R=10%, G=100%, B=20%)
    return light, (0.10, 1.0, 0.20)