"""
Experimental alternative renderer: Perlin-noise flow fields instead of the
shape-based patterns in art_generator.py.

Same idea as art_generator.generate_image() - takes the trait JSON the
Mistral agent produces and returns a deterministic PIL Image - but the
actual drawing technique is different: particles drift through a Perlin
noise vector field, leaving trails, which is the classic "flow field" look
(organic, veil-like, very different texture from the shard/orbit/bloom
patterns in the main renderer).

Not wired into main.py yet - this is a standalone experiment. Run this
file directly to generate sample images and see how it looks:
    python3 flow_field_generator.py

To swap it in later: in main.py, replace
    from art_generator import generate_image, image_to_bytes
with
    from flow_field_generator import generate_image, image_to_bytes
No other changes needed - the function signatures match.
"""

import hashlib
import random
from io import BytesIO

from PIL import Image, ImageDraw
from perlin_noise import PerlinNoise

CANVAS_SIZE = 800

# how many particles to draw, per density trait
DENSITY_PARTICLES = {"sparse": 250, "balanced": 600, "dense": 1200}

# how many steps each particle's trail takes, per rarity (rarer = longer,
# more developed trails - same "reward rarity visually" idea as the main
# renderer's glow effect)
RARITY_STEPS = {
    "common": 60,
    "uncommon": 80,
    "rare": 110,
    "epic": 150,
    "legendary": 200,
}

NOISE_SCALE = 0.006     # lower = larger, smoother swirls; higher = tighter chaos
STEP_LENGTH = 2.5


def _seed_from_prompt(user_input: str) -> int:
    digest = hashlib.sha256(user_input.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def _draw_background(base: Image.Image, palette: list[str]):
    """Same vertical gradient approach as art_generator, kept consistent."""
    draw = ImageDraw.Draw(base)
    top = _hex_to_rgb(palette[0])
    bottom = _hex_to_rgb(palette[1] if len(palette) > 1 else palette[0])
    for y in range(CANVAS_SIZE):
        t = y / CANVAS_SIZE
        draw.line([(0, y), (CANVAS_SIZE, y)], fill=_lerp_color(top, bottom, t))


def generate_image(traits: dict) -> Image.Image:
    """
    Same trait shape as art_generator.generate_image(): expects palette,
    traits.Density, rarity, and ideally seed_source (falls back to name).
    """
    seed_source = traits.get("seed_source", traits.get("name", "default"))
    seed = _seed_from_prompt(seed_source)
    rng = random.Random(seed)

    palette = traits["palette"]
    density = traits["traits"].get("Density", "balanced")
    rarity = traits.get("rarity", "common")

    particle_count = DENSITY_PARTICLES.get(density, 600)
    step_count = RARITY_STEPS.get(rarity, 60)

    # two independent noise fields (different seeds) so we can blend
    # between two accent colors across the canvas, not just draw one flat color
    noise_x = PerlinNoise(octaves=3, seed=seed % (2 ** 31))
    noise_y = PerlinNoise(octaves=3, seed=(seed + 1) % (2 ** 31))

    base = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE))
    _draw_background(base, palette)

    # draw trails on a transparent layer so overlapping lines build up
    # naturally (denser paths = brighter), then composite once at the end
    overlay = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    accent_a = _hex_to_rgb(palette[2] if len(palette) > 2 else palette[-1])
    accent_b = _hex_to_rgb(palette[1] if len(palette) > 1 else palette[0])

    for _ in range(particle_count):
        x = rng.uniform(0, CANVAS_SIZE)
        y = rng.uniform(0, CANVAS_SIZE)
        # color varies per particle based on where it started, so trails
        # form soft color bands rather than one uniform tone
        t = x / CANVAS_SIZE
        color = _lerp_color(accent_a, accent_b, t)

        for _ in range(step_count):
            # sample the noise field at this position to get a flow angle
            nx = noise_x([x * NOISE_SCALE, y * NOISE_SCALE])
            ny = noise_y([x * NOISE_SCALE, y * NOISE_SCALE])
            angle = (nx + ny) * 3.14159 * 2

            new_x = x + STEP_LENGTH * _cos(angle)
            new_y = y + STEP_LENGTH * _sin(angle)

            if not (0 <= new_x < CANVAS_SIZE and 0 <= new_y < CANVAS_SIZE):
                break

            draw.line([(x, y), (new_x, new_y)], fill=(*color, 30), width=1)
            x, y = new_x, new_y

    composited = Image.alpha_composite(base.convert("RGBA"), overlay)
    return composited.convert("RGB")


def _cos(a):
    import math
    return math.cos(a)


def _sin(a):
    import math
    return math.sin(a)


def image_to_bytes(img: Image.Image) -> bytes:
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


if __name__ == "__main__":
    # quick visual test - generates a few sample outputs so you can eyeball
    # the flow-field look before deciding whether to wire it into the API
    samples = [
        {
            "name": "Storm Test", "rarity": "legendary",
            "palette": ["#0b0a10", "#1a1a2e", "#e94560"],
            "traits": {"Density": "dense"}, "seed_source": "chaotic ocean storm",
        },
        {
            "name": "Calm Test", "rarity": "common",
            "palette": ["#0f2027", "#2c5364", "#c4e0e5"],
            "traits": {"Density": "sparse"}, "seed_source": "calm morning fog",
        },
        {
            "name": "Threshold Test", "rarity": "rare",
            "palette": ["#0f0c29", "#302b63", "#9d8cff"],
            "traits": {"Density": "balanced"}, "seed_source": "a decision I keep avoiding",
        },
    ]
    for i, s in enumerate(samples):
        img = generate_image(s)
        img.save(f"flow_test_{i}.png")
        print(f"saved flow_test_{i}.png - {s['traits']['Density']}, {s['rarity']}")
