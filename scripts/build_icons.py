from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE_ICON = ROOT / "talos_icon.png"
ICON_DIR = ROOT / "assets" / "icons"
PNG_SIZES = (16, 24, 32, 48, 64, 128, 256)

def square_icon(source: Image.Image, size: int) -> Image.Image:
    image = source.convert("RGBA")
    image.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - image.width) // 2
    y = (size - image.height) // 2
    canvas.alpha_composite(image, (x, y))
    return canvas

def build_icon_set() -> list[Path]:
    if not SOURCE_ICON.exists():
        raise FileNotFoundError(f"Missing source icon: {SOURCE_ICON}")

    ICON_DIR.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE_ICON)
    written: list[Path] = []
    icon_images: list[Image.Image] = []

    for size in PNG_SIZES:
        icon = square_icon(source, size)
        png_path = ICON_DIR / f"talos_{size}.png"
        icon.save(png_path)
        icon_images.append(icon)
        written.append(png_path)

    ico_path = ICON_DIR / "talos.ico"
    icon_images[-1].save(ico_path, sizes=[(size, size) for size in PNG_SIZES])
    written.append(ico_path)
    return written

def main() -> None:
    for path in build_icon_set():
        print(path.relative_to(ROOT))

if __name__ == "__main__":
    main()
