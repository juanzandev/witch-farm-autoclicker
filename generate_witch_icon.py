from pathlib import Path

from PIL import Image, ImageDraw


def draw_witch_icon(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background moon glow
    draw.ellipse(
        (size * 0.1, size * 0.1, size * 0.9, size * 0.9),
        fill=(38, 43, 66, 255),
    )
    draw.ellipse(
        (size * 0.2, size * 0.2, size * 0.8, size * 0.8),
        fill=(22, 26, 40, 255),
    )

    # Witch hat
    hat_color = (86, 55, 130, 255)
    brim_color = (60, 39, 94, 255)
    draw.polygon(
        [
            (size * 0.5, size * 0.18),
            (size * 0.68, size * 0.54),
            (size * 0.32, size * 0.54),
        ],
        fill=hat_color,
    )
    draw.rectangle((size * 0.26, size * 0.5, size *
                   0.74, size * 0.6), fill=brim_color)

    # Face
    face = (105, 165, 92, 255)
    draw.rectangle((size * 0.34, size * 0.58, size *
                   0.66, size * 0.84), fill=face)

    # Eyes
    draw.rectangle((size * 0.4, size * 0.67, size * 0.45,
                   size * 0.72), fill=(18, 18, 18, 255))
    draw.rectangle((size * 0.55, size * 0.67, size * 0.6,
                   size * 0.72), fill=(18, 18, 18, 255))

    # Nose
    draw.rectangle((size * 0.485, size * 0.71, size * 0.53,
                   size * 0.79), fill=(90, 145, 82, 255))

    return img


def main():
    out_dir = Path(__file__).resolve().parent / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)

    icon_image = draw_witch_icon(256)
    png_path = out_dir / "witch.png"
    ico_path = out_dir / "witch.ico"

    icon_image.save(png_path, format="PNG")
    icon_image.save(ico_path, format="ICO", sizes=[
                    (256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

    print(f"Created: {png_path}")
    print(f"Created: {ico_path}")


if __name__ == "__main__":
    main()
