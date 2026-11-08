import numpy as np
from math import pi

def nuclear_reactor_style(x_grid, y_grid, t):
    """
    Avanceret matematisk atomreaktor.
    Tårnet er skubbet helt ned i bunden af banneret, så røgen stiger opad.
    """
    ROWS, COLS = x_grid.shape
    
    # Skaler koordinater så motoren fylder hele banner-skærmen flot ud
    a = x_grid / 28.0
    # RETTELSE: Ændret til -6 for at tvinge tårnet helt ned i bunden af skærmen
    b = (y_grid - 6) / 14.0  
    
    light = np.zeros((ROWS, COLS))
    
    # --- 1. DET TREDIMENSIONELLE KØLETÅRN ---
    # Hyperbolsk kurve til tårn-profilen (smuk organisk indsnævring)
    tower_curve = 0.48 + 0.35 * (b - 0.1) ** 2
    dist_to_surface = np.abs(a) - tower_curve
    
    # Skab en knivskarp men anti-aliaset kant på tårnet (mellem bund b=-0.8 og top b=1.0)
    in_tower = (b > -0.8) & (b < 1.0) & (dist_to_surface < 0)
    
    # Brug np.clip til at forhindre negative tal under kvadratroden (** 0.5)
    inner_val = np.clip(1.0 - (a / tower_curve) ** 2, 0.0, 1.0)
    
    # 3D Skyggelægning: Giv tårnet volumetrisk dybde og lysindfald (venstre-mod-højre gradient)
    tower_shading = 0.35 + 0.55 * (inner_val ** 0.5) - (a / 3.0)
    light[in_tower] = tower_shading[in_tower]
    
    # --- 2. DET RADIOAKTIVE SYMBOL (INTEGRERET PÅ OVERFLADEN) ---
    # Polære koordinater centreret midt på tårnet
    sa = a / 0.22
    sb = (b - 0.1) / 0.22
    sr = (sa ** 2 + sb ** 2) ** 0.5
    s_angle = np.arctan2(sb, sa)
    
    # De tre faneblade (blade) og centrum defineres matematisk
    center_disk = (sr < 0.22)
    blades = (sr >= 0.38) & (sr < 0.95) & (
        ((s_angle > -pi/6) & (s_angle < pi/6)) |
        ((s_angle > 5*pi/6) | (s_angle < -5*pi/6)) |
        ((s_angle > -pi + pi/6) & (s_angle < -pi/2)) | 
        ((s_angle > pi/2 - pi/6) & (s_angle < pi/2 + pi/6))
    )
    
    # Brænd symbolet ind i tårnets overflade med intens lysstyrke
    symbol_mask = in_tower & (center_disk | blades)
    light[symbol_mask] = 0.98
    
    # --- 3. SMUK, ORGANISK RØG OG EMISSIONER (FYLDER SKÆRMEN) ---
    # Røg-feltet starter ved tårnets top (b = -0.8) og flyder opad
    smoke_height = -0.8 - b
    
    # Skab en sinus-interferens bølge, der driver langsomt opad (t * 1.5 i stedet for 4.0)
    smoke_wave = a + 0.4 * np.sin(smoke_height * 2.5 - t * 1.5) + 0.15 * np.cos(a * 4.0 + t)
    # Røgskyen spreder sig gradvist ud og fylder skærmen
    smoke_envelope = 0.35 + smoke_height * 0.45
    
    smoke_field = (b <= -0.8) & (np.abs(smoke_wave) < smoke_envelope)
    
    if np.any(smoke_field):
        # Flot turbulent tekstur inde i røgen ved at blande to sinusbølger over tid
        smoke_texture = 0.35 + 0.45 * np.sin(smoke_height[smoke_field] * 5.0 + t * 2.0) * np.cos(a[smoke_field] * 3.0 - t)
        # Fade røgen blødt ud i toppen af skærmen, så den ikke klipper råt
        smoke_fade = np.clip(1.5 - smoke_height[smoke_field] * 0.4, 0.0, 1.0)
        
        # Læg røgen ovenpå baggrunden
        light[smoke_field] = np.maximum(light[smoke_field], smoke_texture * smoke_fade)
        
    # --- 4. LANGSOMME, SVÆVENDE ATMOSFÆRISKE PARTIKLER ---
    # Gør hastigheden meget langsommere (f.eks. t * 0.8 og t * 0.5)
    # Dette skaber store, bløde, svævende glødepartikler i luften
    particle_grid = np.sin(x_grid * 0.25 - t * 0.8) * np.cos(y_grid * 0.35 + t * 0.5)
    
    # Partiklerne svæver over det meste af skærmen for at fylde tomrummet ud
    particle_mask = (b < 0.6) & (particle_grid > 0.88)
    # Lad partiklerne blinke/pulse roligt frem og tilbage
    light[particle_mask] = np.maximum(light[particle_mask], 0.4 + 0.55 * np.sin(x_grid[particle_mask] + t))
    
    # Strålende, levende radioaktiv grøn farveprofil (R=15%, G=100%, B=25%)
    return light, (0.15, 1.0, 0.25)