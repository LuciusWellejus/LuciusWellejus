import numpy as np

def saturn_style(x_grid, y_grid, t):
    """Den matematiske planet- og ring-animation (Saturn-look)."""
    ROWS, COLS = x_grid.shape
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
    
    return light, (1.0, 0.85, 0.60)