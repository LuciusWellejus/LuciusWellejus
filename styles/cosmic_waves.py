import numpy as np

def cosmic_waves_style(x_grid, y_grid, t):
    """
    Nyt design: Fuldskærms volumetrisk bølgefelt.
    Baseret på reaktorens røg-interferens, men skaleret til at dække 100% af skærmen.
    """
    ROWS, COLS = x_grid.shape
    
    # Blød synsfelt-skalering
    a = x_grid / 24.0
    b = y_grid / 14.0
    
    # --- INTERFERENS-MOTOR (4 koordinerede bølgestrømme) ---
    # Bølge 1: Den tunge, langsomme understrøm (fra reaktorens røg)
    wave1 = np.sin(a * 1.2 - t * 1.5) * np.cos(b * 0.8 + t * 0.5)
    
    # Bølge 2: Den hurtigere vertikale turbulens
    wave2 = np.sin(b * 2.5 + np.cos(a * 1.8 - t) * 1.2 + t * 1.3)
    
    # Bølge 3: Diagonale hvirvler, der klemmer mønsteret sammen i midten
    wave3 = np.sin((a + b) * 1.5 - t * 2.0) * np.cos((a - b) * 1.0 + t)
    
    # Bølge 4: En dyb pulserende radial gradient (skaber 3D-dybde i mønsteret)
    radial_r = (a**2 + b**2)**0.5
    wave4 = np.sin(radial_r * 2.0 - t * 1.8)

    # --- SAMMENSMELTNING AF BØLGERNE ---
    # Vi lægger alle felterne sammen og normaliserer resultatet
    combined_field = (wave1 + wave2 + wave3 + 0.5 * wave4 + 3.5) / 7.0
    
    # Skab en kontrast-kurve (gør de lyse områder skarpere og de mørke dybere)
    light = np.clip(combined_field, 0.0, 0.99)
    light = light ** 1.3  # Giver det Saturn-agtige bløde skygger overalt
    
    # Flot, glødende dyb-lilla til elektrisk neon-cyan farveprofil (R=40%, G=80%, B=100%)
    return light, (0.40, 0.80, 1.0)