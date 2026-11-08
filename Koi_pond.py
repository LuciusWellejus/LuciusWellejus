from PIL import Image, ImageDraw, ImageFilter
import math
import random
import cv2
import numpy as np
import subprocess
import os

WIDTH, HEIGHT = 800, 800
FRAMES = 160  # Extra frames for an incredibly smooth, elegant, and slow swim loop

def make_fish_texture(size=1):
    """Generates a high-detail textured straight fish sprite to be used as our embroidery canvas."""
    w, h = int(260 * size), int(140 * size)
    fish = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(fish)
    cx, cy = w // 2, h // 2

    # 1. Elegant multi-layered flowy fins & tail (with distinct thread ribs)
    tail_points = [
        (cx - int(40*size), cy),
        (cx - int(120*size), cy - int(45*size)),
        (cx - int(95*size), cy - int(12*size)),
        (cx - int(115*size), cy),
        (cx - int(95*size), cy + int(12*size)),
        (cx - int(120*size), cy + int(45*size))
    ]
    d.polygon(tail_points, fill=(245, 248, 252, 235))
    
    # Thread ribbing accents on tail
    for offset in range(-40, 45, 10):
        d.line([(cx - int(50*size), cy), (cx - int(115*size), cy + int(offset*size))], fill=(190, 210, 230, 180), width=2)

    # Side pectoral fins
    d.polygon([(cx + int(10*size), cy - int(15*size)), (cx - int(15*size), cy - int(55*size)), (cx + int(35*size), cy - int(20*size))], fill=(240, 245, 250, 240))
    d.polygon([(cx + int(10*size), cy + int(15*size)), (cx - int(15*size), cy + int(55*size)), (cx + int(35*size), cy + int(20*size))], fill=(240, 245, 250, 240))

    # 2. Main sleek fish body
    body_box = (cx - int(75*size), cy - int(24*size), cx + int(75*size), cy + int(24*size))
    d.ellipse(body_box, fill=(252, 250, 245, 255))

    # 3. Vivid Koi spots matching the reference configuration
    d.ellipse((cx - int(30*size), cy - int(22*size), cx + int(20*size), cy + int(5*size)), fill=(235, 90, 30, 255))
    d.ellipse((cx + int(15*size), cy - int(12*size), cx + int(55*size), cy + int(18*size)), fill=(235, 90, 30, 255))
    d.ellipse((cx - int(65*size), cy - int(8*size), cx - int(25*size), cy + int(18*size)), fill=(25, 28, 35, 255)) # Dark patch

    # 4. Prominent whiskers (Barbels) sweeping backwards from the nose
    d.arc((cx + int(55*size), cy - int(45*size), cx + int(100*size), cy + int(5*size)), start=160, end=270, fill=(252, 250, 245), width=3)
    d.arc((cx + int(55*size), cy - int(5*size), cx + int(100*size), cy + int(45*size)), start=90, end=200, fill=(252, 250, 245), width=3)

    # 5. Eyes with tiny focal points
    d.ellipse((cx + int(52*size), cy - int(14*size), cx + int(59*size), cy - int(7*size)), fill="black")
    d.ellipse((cx + int(52*size), cy + int(7*size), cx + int(59*size), cy + int(14*size)), fill="black")

    # Apply directional stitch bundle shading
    pixels = fish.load()
    for y in range(h):
        for x in range(w):
            if pixels[x, y][3] > 0:
                r, g, b, a = pixels[x, y]
                # Simulates parallel wool strands running horizontally along the spine
                if y % 4 == 0:
                    r, g, b = map(lambda c: max(0, c - 38), (r, g, b))
                elif y % 4 == 2:
                    r, g, b = map(lambda c: min(255, c + 18), (r, g, b))
                pixels[x, y] = (r, g, b, a)
    return fish

def bend_and_rotate_fish(fish_image, angle_path, swim_phase):
    """
    Deforms the fish sprite using a math matrix to bend its spine organically 
    into an arc, adds a secondary tail wave, and aligns it to its swimming trajectory.
    """
    # Convert PIL to NumPy array for fast coordinate mapping
    src_img = np.array(fish_image)
    h, w, c = src_img.shape
    
    # Create blank canvas destination maps
    map_x = np.zeros((h, w), dtype=np.float32)
    map_y = np.zeros((h, w), dtype=np.float32)
    
    cx, cy = w / 2, h / 2

    for y in range(h):
        for x in range(w):
            # Distance from head to tail along horizontal axis
            dis_from_center = x - cx
            
            # 1. Body Bending Math: Curve body into a circle track + add tail swing wag
            # Bends head one way, body into an arc, and wags tail using a sine wave modifier
            bend_amount = 0.0016
            wave_frequency = 0.04
            wave_amplitude = 6.5 * math.sin(swim_phase - dis_from_center * wave_frequency)
            
            # Apply dynamic vertical displacement along the spine profile
            dy = (dis_from_center ** 2) * bend_amount + wave_amplitude
            
            # Map coordinates backwards to prevent pixel gaps
            map_x[y, x] = x
            map_y[y, x] = y - dy

    # Remap image pixels using bicubic interpolation for smooth thread lines
    bent_img = cv2.remap(src_img, map_x, map_y, cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
    
    # Convert back to PIL to handle clean alpha composition and crisp rotations
    pil_bent = Image.fromarray(bent_img)
    
    # Calculate trajectory heading direction vector
    direction = -math.degrees(angle_path) + 90
    return pil_bent.rotate(direction, resample=Image.Resampling.BICUBIC, expand=True)

def apply_global_canvas(image):
    """Applies a fine embroidery grid matrix across the frame to lock pixels into a weave pattern."""
    img = image.convert("RGBA")
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if x % 3 == 0 or y % 3 == 0:
                # Darken holes between canvas matrix cross points
                shadow = 0.52 if (x % 3 == 0 and y % 3 == 0) else 0.78
                r = int(r * shadow)
                g = int(g * shadow)
                b = int(b * shadow)
            pixels[x, y] = (r, g, b, a)
    return img

def create_pond():
    # Ultra-deep dark textured background fabric
    pond = Image.new("RGBA", (WIDTH, HEIGHT), (6, 10, 12, 255))
    pixels = pond.load()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            noise = random.randint(-14, 14)
            r = max(0, min(255, 8 + noise))
            g = max(0, min(255, 12 + noise))
            b = max(0, min(255, 15 + noise))
            pixels[x, y] = (r, g, b, 255)
    return pond

def animate():
    background = create_pond()
    
    # Generate base textures
    fish_base = make_fish_texture(1.2)
    small_fish_base = make_fish_texture(0.95)

    video_filename = "koi_embroidery.mp4"
    fps = 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (WIDTH, HEIGHT))

    print("Generating slow, naturally bending koi video frames...")

    for frame in range(FRAMES):
        img = background.copy().convert("RGBA")
        draw = ImageDraw.Draw(img)

        # 1. Vibrant, glowing cyan stitched ripples
        for i in range(5):
            radius = 50 + i * 75 + (frame * 0.6 % 75)
            alpha = int(190 * (1.0 - (radius / (WIDTH * 0.75))))
            if alpha < 0: alpha = 0

            for angle in range(0, 360, 2):
                rad_angle = math.radians(angle + frame * 0.2)
                px = int(WIDTH/2 + math.cos(rad_angle) * radius)
                py = int(HEIGHT/2 + math.sin(rad_angle) * radius)
                if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                    if (px + py) % 3 == 0:
                        draw.point((px, py), fill=(0, 240, 225, alpha))
                        draw.point((px + 1, py), fill=(0, 185, 205, int(alpha * 0.5)))

        # 2. Moving & Bending Fish Layout
        for index in range(2):
            # Current progress position along circular lap track
            angle_path = frame * (2 * math.pi / FRAMES) + index * math.pi
            
            # Slower tail wag cycle frequency linked to position frames
            swim_phase = frame * 0.28 + index * math.pi

            x = WIDTH/2 + math.cos(angle_path) * 190
            y = HEIGHT/2 + math.sin(angle_path) * 190

            current_base = fish_base if index == 0 else small_fish_base
            
            # Dynamic deformation engine step
            deformed_fish = bend_and_rotate_fish(current_base, angle_path, swim_phase)

            img.alpha_composite(
                deformed_fish, 
                (int(x - deformed_fish.width/2), int(y - deformed_fish.height/2))
            )

        # 3. Layer the global woven thread texture overlay
        final_frame = apply_global_canvas(img)
        
        # Format convert stream pass
        frame_rgb = final_frame.convert("RGB")
        frame_np = np.array(frame_rgb)
        frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        video_writer.write(frame_bgr)

    video_writer.release()
    print(f"Video saved successfully as {video_filename}!")

    # Auto-open launch execution
    print("Launching video player automatically...")
    if os.path.exists(video_filename):
        subprocess.run(["open", video_filename])

if __name__ == "__main__":
    animate()