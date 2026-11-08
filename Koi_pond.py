from PIL import Image, ImageDraw
import math
import random

WIDTH, HEIGHT = 700, 700
FRAMES = 60

def make_fish(size=1):
    # We build the fish on a slightly larger canvas to accommodate the fins and whiskers
    w, h = int(200 * size), int(140 * size)
    fish = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(fish)
    
    cx, cy = w // 2, h // 2

    # 1. Flowing Embroidery Tail (Layered fans)
    tail_points = [
        (cx - int(40*size), cy),
        (cx - int(90*size), cy - int(45*size)),
        (cx - int(75*size), cy - int(10*size)),
        (cx - int(95*size), cy),
        (cx - int(75*size), cy + int(10*size)),
        (cx - int(90*size), cy + int(45*size))
    ]
    d.polygon(tail_points, fill=(240, 240, 245, 230))
    
    # 2. Main Body Oval
    body_box = (cx - int(55*size), cy - int(28*size), cx + int(55*size), cy + int(28*size))
    d.ellipse(body_box, fill=(245, 242, 235, 255))

    # 3. Organic Koi Markings (Layered, non-perfect shapes)
    d.ellipse((cx - int(20*size), cy - int(24*size), cx + int(15*size), cy - int(2*size)), fill=(225, 80, 30, 255))
    d.ellipse((cx + int(10*size), cy - int(10*size), cx + int(45*size), cy + int(15*size)), fill=(225, 80, 30, 255))
    d.ellipse((cx - int(45*size), cy - int(15*size), cx - int(20*size), cy + int(15*size)), fill=(20, 20, 20, 255)) # Black patch

    # 4. Long Whiskers (Barbels)
    d.arc((cx + int(35*size), cy - int(35*size), cx + int(70*size), cy + int(5*size)), start=160, end=270, fill=(245, 242, 235), width=2)
    d.arc((cx + int(35*size), cy - int(5*size), cx + int(70*size), cy + int(35*size)), start=90, end=200, fill=(245, 242, 235), width=2)

    # 5. Eyes
    d.ellipse((cx + int(32*size), cy - int(16*size), cx + int(38*size), cy - int(10*size)), fill="black")
    d.ellipse((cx + int(32*size), cy + int(10*size), cx + int(38*size), cy + int(16*size)), fill="black")

    # Apply directional embroidery stitches across the fish body
    pixels = fish.load()
    for y in range(h):
        for x in range(w):
            if pixels[x, y][3] > 0:  # Only modify non-transparent pixels
                r, g, b, a = pixels[x, y]
                # Cross-hatch texturing to simulate threaded bundle volume
                if (x + y) % 3 == 0:
                    r, g, b = map(lambda c: max(0, c - 35), (r, g, b))
                elif (x - y) % 4 == 0:
                    r, g, b = map(lambda c: min(255, c + 20), (r, g, b))
                pixels[x, y] = (r, g, b, a)

    return fish

def apply_global_canvas(image):
    """
    Applies a uniform cross-stitch grid fabric texture overlaying 
    the entire scene to mimic physical canvas material.
    """
    img = image.convert("RGBA")
    pixels = img.load()
    w, h = img.size
    
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            # Canvas grid lines (warp and weft threads)
            if x % 3 == 0 or y % 3 == 0:
                # Dim the intersections to create deep thread holes
                shadow = 0.65 if (x % 3 == 0 and y % 3 == 0) else 0.82
                r = int(r * shadow)
                g = int(g * shadow)
                b = int(b * shadow)
            pixels[x, y] = (r, g, b, a)
    return img

def create_pond():
    # Dark textured base canvas like the source image
    pond = Image.new("RGBA", (WIDTH, HEIGHT), (12, 16, 18, 255))
    pixels = pond.load()
    
    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Fine background noise simulating textured backing fabric
            noise = random.randint(-8, 8)
            r = max(0, min(255, 12 + noise))
            g = max(0, min(255, 18 + noise))
            b = max(0, min(255, 22 + noise))
            pixels[x, y] = (r, g, b, 255)
            
    return pond

def animate():
    background = create_pond()
    fish = make_fish(1.1)
    small_fish = make_fish(0.85)

    frames = []

    for frame in range(FRAMES):
        img = background.copy().convert("RGBA")
        draw = ImageDraw.Draw(img)

        # 1. Glowing Stitched Water Ripples (Dotted/Dithered design)
        for i in range(4):
            radius = 60 + i * 55 + (frame * 1.5 % 55)
            alpha = int(140 * (1.0 - (radius / (WIDTH * 0.7))))
            if alpha < 0: alpha = 0

            # Draw broken stitched segments along the circumference
            for angle in range(0, 360, 3):
                # Animate the ripples pulsing outwards sequentially
                rad_angle = math.radians(angle + frame * 0.5)
                px = int(WIDTH/2 + math.cos(rad_angle) * radius)
                py = int(HEIGHT/2 + math.sin(rad_angle) * radius)
                
                if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                    # Give it a glowing cyan cross-stitch pattern
                    if (px + py) % 2 == 0:
                        draw.point((px, py), fill=(10, 210, 200, alpha))
                        # Soft glow neighbor point
                        draw.point((px + 1, py), fill=(10, 180, 180, int(alpha * 0.5)))

        # 2. Moving Fish Layout
        for index in range(2):
            # Opposing positions along the circle loop
            angle = frame * (2 * math.pi / FRAMES) + index * math.pi

            x = WIDTH/2 + math.cos(angle) * 160
            y = HEIGHT/2 + math.sin(angle) * 160

            # Calculate movement vector angle for seamless rotation
            dx = -math.sin(angle)
            dy = math.cos(angle)
            direction = -math.degrees(math.atan2(dy, dx))

            current_fish = fish if index == 0 else small_fish

            rotated = current_fish.rotate(
                direction,
                resample=Image.Resampling.BICUBIC,
                expand=True
            )

            # Composite fish over backdrops cleanly
            img.alpha_composite(
                rotated,
                (int(x - rotated.width/2),
                 int(y - rotated.height/2))
            )

        # 3. Apply the global needlework fabric thread pass
        final_frame = apply_global_canvas(img)
        frames.append(final_frame.convert("RGB"))

    frames[0].save(
        "koi_embroidery.gif",
        save_all=True,
        append_images=frames[1:],
        duration=50,
        loop=0
    )

    print("Embroidered Koi GIF successfully created!")

animate()