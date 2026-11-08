import numpy as np

def bird_migration_style(x_grid, y_grid, t):
    """
    Nyt design: En synkroniseret fuglesværm i bølgende V-formationer,
    der migrerer organisk hen over himlen.
    """
    ROWS, COLS = x_grid.shape
    
    # Skaler koordinater så mønsteret flyder naturligt hen over hele banneret
    a = x_grid / 20.0
    b = y_grid / 12.0
    
    light = np.zeros((ROWS, COLS))
    
    # --- 1. STRØMMEN (Den overordnede bølgende sværm-bevægelse) ---
    # Vi genbruger røg-matematikken til at skabe en usynlig motorvej på himlen,
    # som fuglene skal følge. Sværmen bugter sig i en stor S-kurve over tid.
    swarm_wave = b + 0.3 * np.sin(a * 2.0 - t * 1.2) + 0.15 * np.cos(a * 4.5 + t * 0.8)
    
    # --- 2. GENERERING AF DE ENKELTE FUGLE (Bittesmå V-formationer) ---
    # Højfrekvente matematiske modulations-bølger skaber de små skarpe silhuetter.
    # Vi tager den absolutte værdi (np.abs) for at skabe spidse 'V'-knæk i tegnene.
    bird_wings = np.abs(np.sin(x_grid * 1.4 - t * 3.5)) 
    bird_bodies = np.cos(y_grid * 1.8 + t * 2.5)
    
    # Kombiner vingeslagene med fuglekroppene
    individual_birds = (bird_wings < 0.25) & (bird_bodies > 0.80)
    
    # --- 3. MASKERING: PLACER FUGLE INDE I STRØMMEN ---
    # Vi tillader kun, at fugle-partiklerne dukker op tæt på vores overordnede sværm-bølge
    in_swarm = np.abs(swarm_wave) < 0.45
    
    # Definer sværmens kerne-tæthed (fuglene flyver tættest i midten af strømmen)
    density = 0.45 - np.abs(swarm_wave)
    
    # Kombiner det hele: Fuglene renderes kun i strømmen og får en varierende lysstyrke
    bird_field = in_swarm & individual_birds
    if np.any(bird_field):
        light[bird_field] = 0.5 + 0.5 * density[bird_field]
        
    # --- 4. FLIMRENDE BAGGRUNDS-ATMOSFÆRE (Vind / Luftstrømme) ---
    # En meget svag, blød baggrundsbølge, der simulerer vinden under vingerne
    wind = 0.08 * (0.5 + 0.5 * np.sin(a * 3.0 + b * 2.0 - t * 0.5))
    light = np.maximum(light, wind)
    
    # Minimalistisk, elegant sølv/sandfarvet Boho-profil (R=95%, G=90%, B=85%)
    return light, (0.95, 0.90, 0.85)