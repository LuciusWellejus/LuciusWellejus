import numpy as np

def sun_signals_style(x_grid, y_grid, t):
    """Sol med koncentriske signalringe."""
    ROWS, COLS = x_grid.shape
    a = x_grid / 24.0
    b = y_grid / 11.0
    r = (a ** 2 + b ** 2) ** 0.5
    angle = np.arctan2(b, a)
    
    light = np.zeros((ROWS, COLS))
    core_mask = r < 0.4
    light[core_mask] = 0.95 + 0.05 * np.sin(t)
    
    signal_waves = 0.5 + 0.5 * np.sin(r * 9.0 - t * 3.0)
    ring_mask = (r >= 0.4) & (r < 1.6)
    light[ring_mask] = 0.25 + 0.45 * signal_waves[ring_mask]
    
    spikes = 0.75 + 0.25 * np.abs(np.sin(angle * 7.0))
    ray_mask = (r >= 0.4) & (r < spikes)
    light[ray_mask] = np.maximum(light[ray_mask], 0.4 + 0.4 * signal_waves[ray_mask])
    light = light * np.clip(1.7 - r * 0.9, 0.0, 1.0)
    
    return light, (1.0, 0.75, 0.30)