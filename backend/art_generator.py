"""
Turns the agent's trait decisions into an actual image, with plain shape
drawing (Pillow) - no image generation model involved.

Important property: it's deterministic. Same user_input -> same seed ->
same image, every time. That's what lets you later say "this art is
provably derived from this prompt and these traits" if you add the
verifiability step.
"""

import hashlib
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter

CANVAS_SIZE = 800

DENSITY_COUNTS = {"sparse": 18, "balanced": 40, "dense": 80}

RARITY_GLOW = {
    "common": 0,
    "uncommon": 2,
    "rare": 4,
    "epic": 7,
    "legendary": 12,
}


def _seed_from_prompt(user_input: str) -> int:
    """Deterministic seed: same text always produces the same number."""
    digest = hashlib.sha256(user_input.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _draw_background(draw: ImageDraw.ImageDraw, palette: list[str]):
    """Simple vertical gradient between the first two palette colors."""
    top = _hex_to_rgb(palette[0])
    bottom = _hex_to_rgb(palette[1] if len(palette) > 1 else palette[0])
    for y in range(CANVAS_SIZE):
        t = y / CANVAS_SIZE
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (CANVAS_SIZE, y)], fill=(r, g, b))


def _draw_waves(draw, rng, accent, count):
    for _ in range(count):
        y = rng.randint(0, CANVAS_SIZE)
        amplitude = rng.randint(10, 60)
        points = []
        for x in range(0, CANVAS_SIZE, 10):
            offset = amplitude * random_sin(x, rng)
            points.append((x, y + offset))
        draw.line(points, fill=accent, width=rng.randint(1, 3))


def random_sin(x, rng):
    # cheap pseudo-wave without importing math repeatedly per point
    import math
    return math.sin(x / 40.0 + rng.random() * 6)


def _draw_shards(draw, rng, accent, count):
    for _ in range(count):
        cx, cy = rng.randint(0, CANVAS_SIZE), rng.randint(0, CANVAS_SIZE)
        size = rng.randint(20, 120)
        points = [
            (cx, cy - size),
            (cx + size * 0.6, cy),
            (cx, cy + size),
            (cx - size * 0.6, cy),
        ]
        draw.polygon(points, outline=accent, width=2)


def _draw_orbits(draw, rng, accent, count):
    cx, cy = CANVAS_SIZE // 2, CANVAS_SIZE // 2
    for i in range(count):
        radius = rng.randint(30, 380)
        bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
        draw.ellipse(bbox, outline=accent, width=1)


def _draw_static(draw, rng, accent, count):
    for _ in range(count * 5):
        x, y = rng.randint(0, CANVAS_SIZE), rng.randint(0, CANVAS_SIZE)
        r = rng.randint(1, 3)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=accent)


def _draw_bloom(draw, rng, accent, count):
    cx, cy = CANVAS_SIZE // 2, CANVAS_SIZE // 2
    for _ in range(count):
        angle = rng.uniform(0, 360)
        dist = rng.randint(0, 300)
        import math
        x = cx + dist * math.cos(math.radians(angle))
        y = cy + dist * math.sin(math.radians(angle))
        r = rng.randint(3, 20)
        draw.ellipse([x - r, y - r, x + r, y + r], outline=accent, width=2)


PATTERN_FUNCS = {
    "waves": _draw_waves,
    "shards": _draw_shards,
    "orbits": _draw_orbits,
    "static": _draw_static,
    "bloom": _draw_bloom,
}


def generate_image(traits: dict) -> Image.Image:
    """
    traits expects the "final" dict shape from agent.run_agent(), i.e. it
    needs: palette (list of hex strings), traits.Pattern, traits.Density,
    rarity, and ideally the original user_input for seeding.
    """
    seed_source = traits.get("seed_source", traits.get("name", "default"))
    rng = random.Random(_seed_from_prompt(seed_source))

    palette = traits["palette"]
    pattern = traits["traits"].get("Pattern", "static")
    density = traits["traits"].get("Density", "balanced")
    rarity = traits.get("rarity", "common")

    img = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE))
    draw = ImageDraw.Draw(img)
    _draw_background(draw, palette)

    accent = _hex_to_rgb(palette[2] if len(palette) > 2 else palette[-1])
    count = DENSITY_COUNTS.get(density, 40)

    draw_fn = PATTERN_FUNCS.get(pattern, _draw_static)
    draw_fn(draw, rng, accent, count)

    # rarer pieces get a soft glow pass - purely visual reward for rarity
    glow_strength = RARITY_GLOW.get(rarity, 0)
    if glow_strength:
        glow = img.filter(ImageFilter.GaussianBlur(glow_strength))
        img = Image.blend(img, glow, alpha=0.35)

    # legendary gets a gold border
    if rarity == "legendary":
        border = ImageDraw.Draw(img)
        border.rectangle(
            [4, 4, CANVAS_SIZE - 4, CANVAS_SIZE - 4],
            outline=(212, 175, 55),
            width=6,
        )

    return img


def image_to_bytes(img: Image.Image) -> bytes:
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
