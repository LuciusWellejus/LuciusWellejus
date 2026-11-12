import numpy as np

TAU = 2.0 * np.pi
Y0, Y1 = 0.42, 2.55

def unit(v):
    norm = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(norm, 1e-8)

def envelope(y):
    f = np.clip((y - Y0) / (Y1 - Y0), 0.0, 1.0)
    return 0.03 + 0.84 * (1.0 - f) ** 1.08

class Part:
    def __init__(self):
        self.P, self.N, self.B, self.K, self.PH = [], [], [], [], []

    def add(self, p, n, brightness, kind, ph=0.0):
        m = len(p)
        self.P.append(np.asarray(p, dtype=float))
        self.N.append(unit(np.broadcast_to(np.asarray(n, dtype=float), (m, 3))))
        self.B.append(np.broadcast_to(np.asarray(brightness, dtype=float), (m,)))
        self.K.append(np.full(m, kind))
        self.PH.append(np.broadcast_to(np.asarray(ph, dtype=float), (m,)))

    def done(self):
        return [np.concatenate(v) for v in (self.P, self.N, self.B, self.K, self.PH)]

def _build_tree():
    rng = np.random.default_rng(7)
    q = Part()

    # 1. Needles: 24 tiers of drooping branches
    tiers = np.linspace(Y0 + 0.02, Y1 - 0.04, 24)
    for i, y in enumerate(tiers):
        R = envelope(y)
        nb = int(7 + 11 * (1.0 - (y - Y0) / (Y1 - Y0)))
        for b in range(nb):
            a = TAU * b / nb + i * 0.618 * TAU + rng.normal(0, 0.08)
            L = R * rng.uniform(0.82, 1.06)
            n = int(120 + 600 * L)
            s = rng.random(n) ** 0.65
            
            d = np.array([-np.cos(a), 0.0, np.sin(a)])
            side = np.array([-np.sin(a), 0.0, np.cos(a)])
            spread = (0.035 + 0.11 * s) * rng.normal(0, 1, n)
            
            yy = y + 0.07 * s * L - 0.22 * (s * L) ** 2 + rng.normal(0, 0.015, n)
            p = d[None] * (s * L)[:, None] + side[None] * spread[:, None]
            p[:, 1] = yy
            
            nrm = p - np.array([0.0, y, 0.0])
            ao = 0.35 + 0.65 * (s ** 1.3)
            q.add(p, nrm, ao * 0.65, kind=0)

    # 2. Trunk
    h, a = np.meshgrid(np.linspace(-0.05, 0.55, 30), np.linspace(0, TAU, 30))
    p_trunk = np.stack([0.085 * np.cos(a), h, 0.085 * np.sin(a)], -1).reshape(-1, 3)
    n_trunk = np.stack([np.cos(a), np.zeros_like(a), np.sin(a)], -1).reshape(-1, 3)
    bark = 0.25 + 0.10 * np.sin(h * 90 + a * 3).ravel()
    q.add(p_trunk, n_trunk, bark, kind=1)

    # 3. Tinsel Garland: drooping spiral in swags
    u = np.linspace(0, 1, 1800)
    turns = 3.8
    yg = Y0 + 0.12 + (Y1 - Y0 - 0.35) * u - 0.04 * np.abs(np.sin(turns * np.pi * u))
    ag = TAU * turns * u + 0.9
    rg = envelope(yg) * 1.04
    p_garland = np.stack([-rg * np.cos(ag), yg, rg * np.sin(ag)], -1)
    n_garland = np.stack([-np.cos(ag), np.full_like(ag, 0.3), np.sin(ag)], -1)
    q.add(p_garland, n_garland, 0.85, kind=2)

    # 4. Twinkling Fairy Lights & Ornaments
    ul = rng.random(220)
    yl = Y0 + 0.1 + (Y1 - Y0 - 0.2) * ul
    al = rng.uniform(0, TAU, 220)
    rl = envelope(yl) * rng.uniform(0.85, 1.05, 220)
    p_lights = np.stack([-rl * np.cos(al), yl, rl * np.sin(al)], -1)
    phases = rng.uniform(0, TAU, 220)
    q.add(p_lights, p_lights, 0.99, kind=3, ph=phases)

    # 5. Topper Star
    star_pts = rng.normal(0, 0.035, (150, 3))
    star_pts[:, 1] += Y1 + 0.05
    q.add(star_pts, star_pts, 0.99, kind=4)

    return q.done()

# Build the 3D point cloud once when the module loads so rendering stays fast
TREE_DATA = _build_tree()

def christmas_tree_style(x_grid, y_grid, t):
    """Projects the 3D Christmas tree onto the 2D ASCII grid with rotation and twinkling lights."""
    ROWS, COLS = x_grid.shape
    P, N, B, K, PH = TREE_DATA

    # Rotate the tree smoothly over time (t)
    cos_t, sin_t = np.cos(t), np.sin(t)
    x_rot = P[:, 0] * cos_t - P[:, 2] * sin_t
    z_rot = P[:, 0] * sin_t + P[:, 2] * cos_t
    y_rot = P[:, 1]

    nx_rot = N[:, 0] * cos_t - N[:, 2] * sin_t
    nz_rot = N[:, 0] * sin_t + N[:, 2] * cos_t

    # Perspective camera projection
    cam_dist = 3.6
    z_cam = z_rot + cam_dist
    fov = 26.0
    
    # Map 3D coordinates to 2D grid indices (compensating for character aspect ratio)
    col_proj = np.round((x_rot / z_cam) * fov * 2.0 + (COLS / 2.0)).astype(int)
    row_proj = np.round((-(y_rot - 1.32) / z_cam) * fov + (ROWS / 2.0)).astype(int)

    # Filter points inside screen bounds
    valid = (col_proj >= 0) & (col_proj < COLS) & (row_proj >= 0) & (row_proj < ROWS)
    c_v = col_proj[valid]
    r_v = row_proj[valid]
    z_v = z_cam[valid]
    b_v = B[valid].copy()
    k_v = K[valid]
    ph_v = PH[valid]
    nx_v = nx_rot[valid]
    nz_v = nz_rot[valid]

    # Directional lighting from front-left
    diffuse = np.clip(-0.5 * nx_v - 0.8 * nz_v + 0.5, 0.25, 1.2)
    b_v = np.where(k_v < 3, b_v * diffuse, b_v)

    # Twinkle animation for lights (kind == 3) and star (kind == 4)
    is_light = (k_v == 3)
    b_v[is_light] = 0.35 + 0.64 * (0.5 + 0.5 * np.sin(t * 4.0 + ph_v[is_light]))
    b_v[k_v == 4] = 0.85 + 0.14 * np.sin(t * 6.0)

    # Z-buffer sorting: draw furthest points first so front branches occlude back ones
    order = np.argsort(-z_v)
    light_matrix = np.zeros((ROWS, COLS))
    light_matrix[r_v[order], c_v[order]] = b_v[order]

    # Subtle falling snow in the background
    snow_wave = np.sin(x_grid * 0.45 + np.cos(y_grid * 0.3 - t)) * np.cos(y_grid * 0.4 - t * 2.0)
    snow_mask = (light_matrix == 0) & (snow_wave > 0.92)
    light_matrix[snow_mask] = 0.45

    # Pine-emerald green tint
    return np.clip(light_matrix, 0.0, 0.99), (0.20, 0.95, 0.45)
