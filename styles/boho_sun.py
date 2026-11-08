import numpy as np

def boho_sun_style(x_grid, y_grid, t):
    """Boho-sol med lagdelte konturer, skarpe takker og pulserende chokbølger."""
    # Hent formen direkte fra koordinat-matricerne
    ROWS, COLS = x_grid.shape
    a = x_grid / 22.0
    b = y_grid / 10.0
    r = (a ** 2 + b ** 2) ** 0.5
    angle = np.arctan2(b, a)
    
    light = np.zeros((ROWS, COLS))
    
    core_mask = r < 0.35
    light[core_mask] = 0.9
    
    ring_lines = (np.abs(r - 0.45) < 0.04) | (np.abs(r - 0.58) < 0.04)
    light[ring_lines] = 0.85 + 0.1 * np.sin(t)
    
    base_spikes = 0.8 + 0.25 * np.sin(angle * 6.0)
    ray_mask = (r >= 0.65) & (r < base_spikes)
    light[ray_mask] = 0.75
    
    wave_pulse = 0.5 + 0.5 * np.sin(r * 12.0 - t * 4.0)
    outer_mask = (r >= base_spikes) & (r < 2.0)
    light[outer_mask] = wave_pulse[outer_mask] * np.clip(2.0 - r[outer_mask] * 1.1, 0.0, 1.0) * 0.45
    
    return light, (1.0, 0.68, 0.35)