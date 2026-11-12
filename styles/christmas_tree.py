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
        self.P, self.N, self.C, self.K, self.PH = [], [], [], [], []

    def add(self, p, n, col, kind, ph=0.0):
        m = len(p)
        self.P.append(np.asarray(p, dtype=float))
        self.N.append(unit(np.broadcast_to(np.asarray(n, dtype=float), (m, 3))))
        self.C.append(np.broadcast_to(np.asarray(col, dtype=float), (m, 3)))
        self.K.append(np.full(m, kind))
        self.PH.append(np.broadcast_to(np.asarray(ph, dtype=float), (m,)))

    def done(self):
        return [np.concatenate(v) for v in (self.P, self.N, self.C, self.K, self.PH)]

def _fib_sphere(n):
    i = np.arange(n) + 0.5
    y = 1.0 - 2.0 * i / n
    r = np.sqrt(np.maximum(1.0 - y * y, 0.0))
    th = np.pi * (3.0 - np.sqrt(5.0)) * i
    return np.stack([r * np.cos(th), y, r * np.sin(th)], 1)

def _add_gift(q, center, size, box_col, ribbon_col):
    cx, cy, cz = center
    sx, sy, sz = size
    u = np.linspace(-0.5, 0.5, 14)
    v = np.linspace(-0.5, 0.5, 14)
    uu, vv = np.meshgrid(u, v)
    uu, vv = uu.ravel(), vv.ravel()
    
    faces = [
        (uu * sx, vv * sy, np.full_like(uu, 0.5 * sz), [0.0, 0.0, 1.0]),
        (uu * sx, vv * sy, np.full_like(uu, -0.5 * sz), [0.0, 0.0, -1.0]),
        (np.full_like(uu, 0.5 * sx), vv * sy, uu * sz, [1.0, 0.0, 0.0]),
        (np.full_like(uu, -0.5 * sx), vv * sy, uu * sz, [-1.0, 0.0, 0.0]),
        (uu * sx, np.full_like(uu, 0.5 * sy), vv * sz, [0.0, 1.0, 0.0]),
    ]
    for fx, fy, fz, nrm in faces:
        pts = np.stack([fx + cx, fy + cy, fz + cz], -1)
        is_ribbon = (np.abs(fx) < 0.03) | (np.abs(fz) < 0.03)
        cols = np.where(is_ribbon[:, None], ribbon_col, box_col)
        q.add(pts, nrm, cols, kind=2)

def _build_scene():
    rng = np.random.default_rng(7)
    q = Part()

    # 1. Pine needles & snowcaps
    tiers = np.linspace(Y0 + 0.02, Y1 - 0.04, 24)
    for i, y in enumerate(tiers):
        R = envelope(y)
        nb = int(7 + 11 * (1.0 - (y - Y0) / (Y1 - Y0)))
        for b in range(nb):
            a = TAU * b / nb + i * 0.618 * TAU + rng.normal(0, 0.08)
            L = R * rng.uniform(0.82, 1.06)
            n = int(180 + 850 * L)
            s = rng.random(n) ** 0.65
            
            d = np.array([-np.cos(a), 0.0, np.sin(a)])
            side = np.array([-np.sin(a), 0.0, np.cos(a)])
            spread = (0.035 + 0.11 * s) * rng.normal(0, 1, n)
            
            yy = y + 0.07 * s * L - 0.22 * (s * L) ** 2 + rng.normal(0, 0.015, n)
            p = d[None] * (s * L)[:, None] + side[None] * spread[:, None]
            p[:, 1] = yy
            
            nrm = unit(p - np.array([0.0, y, 0.0]))
            ao = 0.45 + 0.55 * (s ** 1.2)
            pine_col = np.array([0.12, 0.72, 0.28]) * ao[:, None]
            
            snow = (s > 0.55) & (nrm[:, 1] > 0.35) & (rng.random(n) < 0.25)
            q.add(p[~snow], nrm[~snow], pine_col[~snow], kind=0)
            if np.any(snow):
                q.add(p[snow] + [0.0, 0.012, 0.0], [0.0, 1.0, 0.0], [0.85, 0.92, 1.0], kind=1)

    # 2. Trunk
    h, a = np.meshgrid(np.linspace(0.0, 0.5, 25), np.linspace(0, TAU, 25))
    p_trunk = np.stack([0.09 * np.cos(a), h, 0.09 * np.sin(a)], -1).reshape(-1, 3)
    n_trunk = np.stack([np.cos(a), np.zeros_like(a), np.sin(a)], -1).reshape(-1, 3)
    q.add(p_trunk, n_trunk, [0.55, 0.35, 0.18], kind=1)

    # 3. Gold tinsel garland
    u = np.linspace(0, 1, 2400)
    turns = 3.8
    yg = Y0 + 0.12 + (Y1 - Y0 - 0.35) * u - 0.04 * np.abs(np.sin(turns * np.pi * u))
    ag = TAU * turns * u + 0.9
    rg = envelope(yg) * 1.04
    p_garland = np.stack([-rg * np.cos(ag), yg, rg * np.sin(ag)], -1)
    q.add(p_garland, p_garland, [1.0, 0.82, 0.25], kind=2)

    # 4. Baubles / Ornaments (red and gold)
    sphere_pts = _fib_sphere(45)
    for _ in range(55):
        oy = rng.uniform(Y0 + 0.08, Y1 - 0.25)
        oa = rng.uniform(0, TAU)
        orad = envelope(oy) * 0.96
        center = np.array([-orad * np.cos(oa), oy, orad * np.sin(oa)])
        col = [1.0, 0.18, 0.18] if rng.random() < 0.65 else [1.0, 0.85, 0.25]
        q.add(center + sphere_pts * 0.048, sphere_pts, col, kind=2)

    # 5. Twinkling fairy lights (170 lights)
    ul = rng.random(170)
    yl = Y0 + 0.08 + (Y1 - Y0 - 0.18) * ul
    al = rng.uniform(0, TAU, 170)
    rl = envelope(yl) * rng.uniform(0.88, 1.05, 170)
    p_lights = np.stack([-rl * np.cos(al), yl, rl * np.sin(al)], -1)
    light_cols = np.where((rng.random(170) < 0.5)[:, None], [1.0, 0.95, 0.55], [1.0, 0.45, 0.25])
    q.add(p_lights, p_lights, light_cols, kind=3, ph=rng.uniform(0, TAU, 170))

    # 6. Topper star
    star_pts = _fib_sphere(90) * 0.065
    star_pts[:, 1] += Y1 + 0.08
    q.add(star_pts, star_pts, [1.0, 0.95, 0.45], kind=4)

    # 7. Gift boxes under the tree
    _add_gift(q, [-0.45, 0.14, 0.35], [0.36, 0.28, 0.36], [0.95, 0.18, 0.18], [1.0, 0.88, 0.30])
    _add_gift(q, [0.48, 0.12, 0.30], [0.34, 0.24, 0.34], [0.22, 0.48, 1.0], [1.0, 0.92, 0.40])
    _add_gift(q, [0.05, 0.10, 0.52], [0.28, 0.20, 0.28], [0.95, 0.72, 0.20], [0.95, 0.20, 0.20])

    # 8. Snowy ground plane
    gx, gz = np.meshgrid(np.linspace(-1.7, 1.7, 75), np.linspace(-1.7, 1.7, 75))
    gr = np.sqrt(gx**2 + gz**2)
    mask_g = gr < 1.65
    p_ground = np.stack([gx[mask_g], np.zeros(np.sum(mask_g)), gz[mask_g]], -1)
    ground_shade = 0.55 * (1.0 - gr[mask_g] / 1.8)
    ground_cols = np.stack([ground_shade * 0.85, ground_shade * 0.90, ground_shade], -1)
    q.add(p_ground, [0.0, 1.0, 0.0], ground_cols, kind=1)

    return q.done()

TREE_DATA = _build_scene()

# Compact 3x5 pixel font for HUD telemetry
_HUD_FONT = {
    '0': ["111", "101", "101", "101", "111"], '1': ["010", "110", "010", "010", "111"],
    '2': ["111", "001", "111", "100", "111"], '3': ["111", "001", "111", "001", "111"],
    '4': ["101", "101", "111", "001", "001"], '5': ["111", "100", "111", "001", "111"],
    '6': ["111", "100", "111", "101", "111"], '7': ["111", "001", "001", "010", "010"],
    '8': ["111", "101", "111", "101", "111"], '9': ["111", "101", "111", "001", "111"],
    't': ["010", "111", "010", "010", "011"], 's': ["011", "100", "010", "001", "110"],
    'r': ["000", "101", "110", "100", "100"], 'o': ["000", "111", "101", "101", "111"],
    'a': ["000", "011", "101", "101", "011"], 'i': ["010", "000", "010", "010", "010"],
    'n': ["000", "110", "101", "101", "101"], 'l': ["100", "100", "100", "100", "011"],
    'g': ["000", "011", "101", "011", "111"], 'h': ["100", "100", "110", "101", "101"],
    '.': ["000", "000", "000", "000", "010"], ':': ["000", "010", "000", "010", "000"],
    '@': ["111", "101", "111", "100", "111"], ' ': ["000", "000", "000", "000", "000"],
}

def _draw_hud(light_mat, color_mat, text, start_r, start_c, col=(0.7, 0.75, 0.85)):
    ROWS, COLS = light_mat.shape
    c = start_c
    for ch in text:
        glyph = _HUD_FONT.get(ch, _HUD_FONT[' '])
        for r_off in range(5):
            for c_off in range(3):
                if glyph[r_off][c_off] == '1':
                    rr, cc = start_r + r_off, c + c_off
                    if 0 <= rr < ROWS and 0 <= cc < COLS:
                        light_mat[rr, cc] = 0.85
                        color_mat[rr, cc] = col
        c += 4

def christmas_tree_style(x_grid, y_grid, t):
    ROWS, COLS = x_grid.shape
    P, N, C, K, PH = TREE_DATA

    light_matrix = np.zeros((ROWS, COLS))
    color_matrix = np.zeros((ROWS, COLS, 3))

    # 1. Background starry sky
    star_hash = np.sin(x_grid * 12.9898 + y_grid * 78.233) * 43758.5453
    star_hash = star_hash - np.floor(star_hash)
    stars = star_hash > 0.985
    light_matrix[stars] = 0.25 + 0.25 * np.sin(t * 2.0 + star_hash[stars] * 20.0)
    color_matrix[stars] = [0.75, 0.82, 0.95]

    # 2. Rotate 3D tree
    cos_t, sin_t = np.cos(t), np.sin(t)
    x_rot = P[:, 0] * cos_t - P[:, 2] * sin_t
    z_rot = P[:, 0] * sin_t + P[:, 2] * cos_t
    y_rot = P[:, 1]

    nx_rot = N[:, 0] * cos_t - N[:, 2] * sin_t
    nz_rot = N[:, 0] * sin_t + N[:, 2] * cos_t

    cam_dist = 3.55
    z_cam = z_rot + cam_dist
    fov = 26.0
    
    col_proj = np.round((x_rot / z_cam) * fov * 1.9 + (COLS / 2.0)).astype(int)
    row_proj = np.round((-(y_rot - 1.28) / z_cam) * fov + (ROWS / 2.0)).astype(int)

    valid = (col_proj >= 0) & (col_proj < COLS) & (row_proj >= 0) & (row_proj < ROWS)
    c_v, r_v, z_v = col_proj[valid], row_proj[valid], z_cam[valid]
    col_v = C[valid].copy()
    k_v, ph_v = K[valid], PH[valid]
    nx_v, nz_v = nx_rot[valid], nz_rot[valid]

    # Diffuse shading
    diffuse = np.clip(-0.4 * nx_v - 0.85 * nz_v + 0.55, 0.35, 1.15)
    b_v = np.where(k_v < 3, 0.72 * diffuse, 0.95)

    # Twinkling lights & glowing star
    is_light = (k_v == 3)
    b_v[is_light] = 0.45 + 0.54 * (0.5 + 0.5 * np.sin(t * 5.0 + ph_v[is_light]))
    b_v[k_v == 4] = 0.99

    # Z-buffer sort (far to near)
    order = np.argsort(-z_v)
    light_matrix[r_v[order], c_v[order]] = b_v[order]
    color_matrix[r_v[order], c_v[order]] = col_v[order]

    # 3. Starlight rays radiating from the top star
    star_r = int(round((-(Y1 + 0.08 - 1.28) / cam_dist) * fov + (ROWS / 2.0)))
    star_c = COLS // 2
    dy = y_grid - (star_r - ROWS // 2)
    dx = (x_grid - (star_c - COLS // 2)) * 0.55
    dist = np.sqrt(dx**2 + dy**2)
    ang = np.arctan2(dy, dx)
    rays = (dist > 1.5) & (dist < 7.5) & (np.abs(np.sin(ang * 3.0)) > 0.96)
    light_matrix[rays] = np.maximum(light_matrix[rays], 0.65 * (1.0 - dist[rays] / 8.0))
    color_matrix[rays] = [1.0, 0.92, 0.45]

    # 4. Corner HUD telemetry
    deg = (np.degrees(t) % 360.0)
    sec = (t / TAU) * 15.0
    _draw_hud(light_matrix, color_matrix, f"t {sec:05.2f}s", 1, COLS - 36, (0.95, 0.55, 0.55))