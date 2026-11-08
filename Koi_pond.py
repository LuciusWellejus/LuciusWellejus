from PIL import Image, ImageDraw
import math

WIDTH, HEIGHT = 700, 700
FRAMES = 60

def make_fish(size=1):
    w, h = int(150 * size), int(90 * size)

    fish = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(fish)

    # Tail
    d.polygon(
        [(25*size, 45*size),
         (0, 15*size),
         (5*size, 45*size),
         (0, 75*size)],
        fill="white"
    )

    # Main body
    d.ellipse(
        (15*size, 15*size, 135*size, 75*size),
        fill=(245, 240, 220),
        outline=(180, 180, 170),
        width=max(1, int(2*size))
    )

    # Orange koi markings
    d.ellipse(
        (45*size, 18*size, 85*size, 48*size),
        fill=(235, 90, 35)
    )

    d.ellipse(
        (95*size, 40*size, 125*size, 68*size),
        fill=(235, 90, 35)
    )

    # Eye
    d.ellipse(
        (115*size, 35*size, 123*size, 43*size),
        fill="black"
    )

    # Fins
    d.polygon(
        [(65*size, 25*size),
         (75*size, 0),
         (90*size, 25*size)],
        fill=(220, 200, 175)
    )

    return fish


def create_pond():
    pond = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = pond.load()

    for y in range(HEIGHT):
        for x in range(WIDTH):
            wave = math.sin(x/35) * 4
            wave += math.cos(y/40) * 4

            pixels[x, y] = (
                15,
                int(95 + wave),
                int(115 + wave)
            )

    return pond


def animate():
    background = create_pond()
    fish = make_fish(1.0)
    small_fish = make_fish(0.7)

    frames = []

    for frame in range(FRAMES):
        img = background.copy().convert("RGBA")

        # Moving fish
        for index in range(4):

            angle = frame * 0.07 + index * 1.57

            x = WIDTH/2 + math.cos(angle) * 190
            y = HEIGHT/2 + math.sin(angle) * 140

            # Direction of swimming
            direction = -math.degrees(
                math.atan2(
                    math.cos(angle) * 140,
                    -math.sin(angle) * 190
                )
            )

            current_fish = fish if index % 2 == 0 else small_fish

            rotated = current_fish.rotate(
                direction,
                resample=Image.Resampling.BICUBIC,
                expand=True
            )

            img.alpha_composite(
                rotated,
                (int(x-rotated.width/2),
                 int(y-rotated.height/2))
            )

        # Water ripples
        draw = ImageDraw.Draw(img)

        for i in range(8):
            radius = 20 + i * 35 + (frame % 20)

            draw.ellipse(
                (WIDTH/2-radius,
                 HEIGHT/2-radius,
                 WIDTH/2+radius,
                 HEIGHT/2+radius),
                outline=(100, 190, 190, 70),
                width=1
            )

        frames.append(img.convert("RGB"))

    frames[0].save(
        "koi_animation.gif",
        save_all=True,
        append_images=frames[1:],
        duration=60,
        loop=0
    )

    print("Koi GIF created!")


animate()