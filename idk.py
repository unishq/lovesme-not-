import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Virtual low-res canvas for authentic pixel art look
WIDTH, HEIGHT = 160, 200
SCALE = 3
SCREEN_W, SCREEN_H = WIDTH * SCALE, HEIGHT * SCALE

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Loves me, loves me not")
canvas = pygame.Surface((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# 5x7 Pixel Bitmap Font
FONT_5X7 = {
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'I': ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
}

def draw_pixel_text(surf, text, y, color, shadow_color=(12, 14, 36), scale=2):
    text = text.upper()
    char_w = 5 * scale
    spacing = 1 * scale
    total_w = len(text) * (char_w + spacing) - spacing
    start_x = (WIDTH - total_w) // 2

    for i, ch in enumerate(text):
        glyph = FONT_5X7.get(ch, FONT_5X7[' '])
        gx = start_x + i * (char_w + spacing)
        for row_idx, row in enumerate(glyph):
            for col_idx, pixel in enumerate(row):
                if pixel == '1':
                    px = gx + col_idx * scale
                    py = y + row_idx * scale
                    pygame.draw.rect(surf, shadow_color, (px + 1, py + 1, scale, scale))
                    pygame.draw.rect(surf, color, (px, py, scale, scale))

# Scene setup
stars = [
    [random.randint(5, WIDTH - 5), random.randint(5, 145), random.uniform(0, 6.28)]
    for _ in range(32)
]
grass_blades = [
    (x, random.randint(4, 11), random.choice([(46, 139, 87), (60, 179, 113), (34, 110, 68)]))
    for x in range(0, WIDTH, 2)
]
flowers_bg = [
    (random.randint(4, WIDTH - 4), random.randint(172, 185), random.choice([(255, 182, 193), (255, 255, 150), (221, 160, 221)]))
    for _ in range(14)
]

# Flower state
CENTER_X, CENTER_Y = 80, 96
NUM_PETALS = random.randint(9, 12)
petals = [i * (2 * math.pi / NUM_PETALS) for i in range(NUM_PETALS)]
falling_petals = []
status_text = "CLICK"
text_loves = True
pluck_count = 0

def reset_flower():
    global petals, falling_petals, status_text, text_loves, pluck_count
    count = random.randint(9, 12)
    petals = [i * (2 * math.pi / count) for i in range(count)]
    falling_petals = []
    status_text = "CLICK"
    text_loves = True
    pluck_count = 0

def draw_petal(surf, cx, cy, angle, length=18, width=5, color=(235, 242, 255)):
    # Draw pixel-stepped ellipse along angle
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    for d in range(5, length + 1):
        # Taper width at ends
        progress = (d - 5) / (length - 5)
        w = int(width * math.sin(progress * math.pi))
        for offset in range(-w, w + 1):
            px = int(round(cx + cos_a * d - sin_a * offset))
            py = int(round(cy + sin_a * d + cos_a * offset))
            shade = (195, 210, 235) if abs(offset) == w else color
            if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                surf.set_at((px, py), shade)

running = True
tick = 0

while running:
    tick += 0.08
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if petals:
                # Pluck a petal
                angle = petals.pop(random.randrange(len(petals)))
                px = CENTER_X + math.cos(angle) * 14
                py = CENTER_Y + math.sin(angle) * 14
                falling_petals.append({
                    "x": px,
                    "y": py,
                    "angle": angle,
                    "vx": random.uniform(-0.4, 0.4),
                    "vy": random.uniform(0.35, 0.65),
                    "sway": random.uniform(0, 6.28)
                })
                pluck_count += 1
                text_loves = (pluck_count % 2 == 1)
                status_text = "LOVES ME" if text_loves else "LOVES ME NOT"
            else:
                reset_flower()

    # 1. Night Sky Gradient
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(12 + ratio * 18)
        g = int(22 + ratio * 38)
        b = int(58 + ratio * 75)
        pygame.draw.line(canvas, (r, g, b), (0, y), (WIDTH, y))

    # 2. Twinkling Stars
    for sx, sy, phase in stars:
        brightness = (math.sin(tick + phase) + 1) / 2
        if brightness > 0.25:
            c = int(140 + brightness * 115)
            canvas.set_at((sx, sy), (c, c, min(255, c + 20)))
            if brightness > 0.85:
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if 0 <= sx + dx < WIDTH and 0 <= sy + dy < HEIGHT:
                        canvas.set_at((sx + dx, sy + dy), (150, 160, 200))

    # 3. Pixel Moon
    moon_x, moon_y = 128, 46
    pygame.draw.circle(canvas, (238, 240, 215), (moon_x, moon_y), 9)
    pygame.draw.circle(canvas, (215, 218, 190), (moon_x - 2, moon_y - 2), 2)
    pygame.draw.circle(canvas, (215, 218, 190), (moon_x + 3, moon_y + 2), 2)

    # 4. Stem & Leaves
    for y in range(CENTER_Y + 6, 175):
        sway_x = int(math.sin((y - CENTER_Y) * 0.06) * 2)
        pygame.draw.rect(canvas, (45, 145, 75), (CENTER_X + sway_x - 1, y, 3, 1))
        canvas.set_at((CENTER_X + sway_x - 1, y), (65, 175, 95))

    # Left & Right Leaves
    for i in range(12):
        canvas.set_at((CENTER_X - 2 - i, 138 - i // 2), (45, 145, 75))
        canvas.set_at((CENTER_X - 2 - i, 139 - i // 2), (35, 115, 60))
        canvas.set_at((CENTER_X + 2 + i, 146 - i // 2), (45, 145, 75))
        canvas.set_at((CENTER_X + 2 + i, 147 - i // 2), (35, 115, 60))

    # 5. Attached Petals
    for angle in petals:
        draw_petal(canvas, CENTER_X, CENTER_Y, angle)

    # 6. Flower Center (Sunflower/Daisy core)
    pygame.draw.circle(canvas, (150, 90, 30), (CENTER_X, CENTER_Y), 8)
    pygame.draw.circle(canvas, (225, 165, 45), (CENTER_X, CENTER_Y), 6)
    for dx in range(-4, 5, 2):
        for dy in range(-4, 5, 2):
            if dx * dx + dy * dy <= 16:
                canvas.set_at((CENTER_X + dx, CENTER_Y + dy), (185, 120, 35))

    # 7. Falling Petals
    for fp in falling_petals[:]:
        fp["sway"] += 0.1
        fp["x"] += fp["vx"] + math.sin(fp["sway"]) * 0.35
        fp["y"] += fp["vy"]
        fp["angle"] += 0.03
        draw_petal(canvas, fp["x"], fp["y"], fp["angle"], length=12, width=4)
        if fp["y"] > HEIGHT + 15:
            falling_petals.remove(fp)

    # 8. Ground & Pixel Grass
    pygame.draw.rect(canvas, (28, 92, 52), (0, 172, WIDTH, 28))
    for gx, gh, gcol in grass_blades:
        pygame.draw.line(canvas, gcol, (gx, 172), (gx, 172 - gh))
    for fx, fy, fcol in flowers_bg:
        canvas.set_at((fx, fy), fcol)

    # 9. Status Text ("LOVES ME" in soft pink, "LOVES ME NOT" in pale blue)
    text_color = (255, 165, 192) if text_loves else (169, 188, 255)
    text_scale = 1 if len(status_text) > 9 else 2
    draw_pixel_text(canvas, status_text, 18, text_color, scale=text_scale)

    # Scale virtual canvas up to window
    scaled_surf = pygame.transform.scale(canvas, (SCREEN_W, SCREEN_H))
    screen.blit(scaled_surf, (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
