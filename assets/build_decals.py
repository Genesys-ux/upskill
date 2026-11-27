"""Generate crisp, real-reference PIL PNG texture decals for all 3 Blender worlds."""
from __future__ import annotations

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from PIL import Image, ImageDraw, ImageFont
from project_config import DECALS_DIR


def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def draw_centered(draw: ImageDraw.ImageDraw, text: str, cx: float, y: float, font: Any, fill: Any) -> None:
    w = draw.textlength(text, font=font)
    draw.text((cx - w * 0.5, y), text, font=font, fill=fill)


def make_diomede_sign() -> None:
    """Weathered wooden sign: USA / RUSSIA — 3.8 KM."""
    W, H = 1024, 512
    img = Image.new("RGBA", (W, H), (88, 62, 44, 255))
    d = ImageDraw.Draw(img)
    # Wood planks & frost edges
    for y in range(0, H, 128):
        d.line([(0, y), (W, y)], fill=(44, 29, 20, 255), width=6)
    for x in range(18, W, 38):
        d.line([(x, 0), (x + 12, H)], fill=(74, 51, 35, 255), width=3)
    d.rectangle([16, 16, W - 16, H - 16], outline=(232, 240, 248, 255), width=10)
    # Snow crust at top
    d.polygon([(0, 0), (W, 0), (W, 44), (820, 30), (610, 56), (390, 28), (180, 52), (0, 36)], fill=(238, 246, 255, 255))
    f_big = load_font(86, True)
    f_mid = load_font(62, True)
    f_sm = load_font(38, True)
    draw_centered(d, "USA  /  RUSSIA", W / 2, 92, f_big, (250, 244, 230, 255))
    d.line([(120, 210), (W - 120, 210)], fill=(238, 178, 68, 255), width=8)
    draw_centered(d, "3.8 KM  •  +21 JAM", W / 2, 240, f_mid, (255, 214, 112, 255))
    draw_centered(d, "LITTLE DIOMEDE  ←  |  →  BIG DIOMEDE", W / 2, 362, f_sm, (206, 232, 248, 255))
    img.save(os.path.join(DECALS_DIR, "sign_diomede_usa_russia.png"))


def make_dateline_banner() -> None:
    """Holographic glowing red International Date Line banner (RGBA)."""
    W, H = 1024, 512
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Glowing red vertical divider & scanlines
    for y in range(0, H, 12):
        d.line([(0, y), (W, y)], fill=(255, 48, 42, 42), width=2)
    d.rounded_rectangle([40, 96, W - 40, H - 96], radius=28, fill=(140, 14, 24, 155), outline=(255, 72, 62, 255), width=8)
    f_big = load_font(48, True)
    f_sub = load_font(38, True)
    draw_centered(d, "GARIS TANGGAL INTERNASIONAL", W / 2, 162, f_big, (255, 242, 236, 255))
    draw_centered(d, "← SENIN (USA)   |   SELASA (RUSIA) →", W / 2, 268, f_sub, (255, 198, 110, 255))
    img.save(os.path.join(DECALS_DIR, "holo_dateline.png"))


def make_soren_calendar() -> None:
    """Torn wall calendar page reading SENIN."""
    W, H = 512, 640
    img = Image.new("RGBA", (W, H), (246, 240, 226, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 150], fill=(192, 42, 38, 255))
    # Torn spiral holes
    for hx in range(56, W - 30, 56):
        d.ellipse([hx - 12, 18, hx + 12, 42], fill=(42, 34, 34, 255))
    draw_centered(d, "ALASKA • USA", W / 2, 66, load_font(44, True), (255, 248, 240, 255))
    draw_centered(d, "SENIN", W / 2, 200, load_font(112, True), (32, 26, 36, 255))
    draw_centered(d, "08:00 PAGI", W / 2, 370, load_font(56, True), (186, 46, 38, 255))
    draw_centered(d, "UTC -9", W / 2, 480, load_font(46, True), (82, 90, 108, 255))
    d.rectangle([10, 10, W - 10, H - 10], outline=(62, 54, 48, 255), width=8)
    img.save(os.path.join(DECALS_DIR, "calendar_senin.png"))


def make_astrid_tablet_ui() -> None:
    """Astrid's industrial heliostat control tablet screen with big green ACTIVATE button."""
    W, H = 768, 512
    img = Image.new("RGBA", (W, H), (14, 24, 36, 255))
    d = ImageDraw.Draw(img)
    # Grid lines
    for gx in range(0, W, 48):
        d.line([(gx, 0), (gx, H)], fill=(28, 56, 78, 140), width=2)
    for gy in range(0, H, 48):
        d.line([(0, gy), (W, gy)], fill=(28, 56, 78, 140), width=2)
    d.rectangle([0, 0, W, 74], fill=(22, 42, 64, 255))
    d.text((28, 18), "SOLSPEILET RJUKAN • HELIOSTAT 1-3", font=load_font(32, True), fill=(154, 242, 255, 255))
    # 3 mirror angle gauges
    for idx, x0 in enumerate([60, 286, 512], 1):
        d.rounded_rectangle([x0, 104, x0 + 196, 254], radius=16, fill=(20, 36, 52, 255), outline=(92, 214, 240, 255), width=4)
        draw_centered(d, f"CERMIN {idx}", x0 + 98, 122, load_font(28, True), (235, 248, 255, 255))
        draw_centered(d, "45.2° • LOCK", x0 + 98, 178, load_font(30, True), (222, 248, 64, 255))
    # Big green activate button
    d.rounded_rectangle([140, 300, W - 140, 456], radius=28, fill=(38, 206, 114, 255), outline=(196, 255, 218, 255), width=8)
    draw_centered(d, "AKTIFKAN SINAR!", W / 2, 344, load_font(52, True), (10, 32, 18, 255))
    img.save(os.path.join(DECALS_DIR, "tablet_heliostat_ui.png"))


def make_rjukan_sign() -> None:
    """Rjukan Torg municipal sign."""
    W, H = 768, 384
    img = Image.new("RGBA", (W, H), (26, 46, 78, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([14, 14, W - 14, H - 14], outline=(242, 210, 96, 255), width=8)
    draw_centered(d, "RJUKAN TORG", W / 2, 56, load_font(74, True), (250, 248, 240, 255))
    draw_centered(d, "SOLSPEILET • 450M", W / 2, 174, load_font(46, True), (255, 216, 92, 255))
    draw_centered(d, "TELEMARK, NORWAY", W / 2, 268, load_font(38, True), (186, 216, 246, 255))
    img.save(os.path.join(DECALS_DIR, "sign_rjukan_torg.png"))


def make_baarle_menu() -> None:
    """Baarle cross-border cafe chalkboard menu with funny dual-country tax note."""
    W, H = 640, 800
    img = Image.new("RGBA", (W, H), (30, 34, 38, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([16, 16, W - 16, H - 16], outline=(186, 134, 78, 255), width=18)
    draw_centered(d, "CAFÉ DE GRENS", W / 2, 58, load_font(56, True), (252, 244, 218, 255))
    draw_centered(d, "BAARLE  B  |  NL", W / 2, 136, load_font(38, True), (244, 188, 72, 255))
    d.line([(70, 204), (W - 70, 204)], fill=(230, 230, 220, 180), width=4)
    items = [
        ("Espresso", "€ 2.80"),
        ("Border Latte", "€ 3.90"),
        ("Stroopwafel", "€ 2.50"),
        ("Belgian Waffle", "€ 4.20"),
    ]
    y = 248
    f_item = load_font(38, False)
    for name, price in items:
        d.text((76, y), name, font=f_item, fill=(246, 246, 240, 255))
        pw = d.textlength(price, font=f_item)
        d.text((W - 76 - pw, y), price, font=f_item, fill=(255, 224, 132, 255))
        y += 78
    d.rounded_rectangle([54, 594, W - 54, 738], radius=16, fill=(52, 40, 36, 255), outline=(238, 178, 86, 255), width=4)
    draw_centered(d, "INFO PAJAK:", W / 2, 610, load_font(30, True), (255, 198, 92, 255))
    draw_centered(d, "Kiri = BTW Belgia (B)", W / 2, 654, load_font(28, False), (242, 242, 236, 255))
    draw_centered(d, "Kanan = BTW Belanda (NL)", W / 2, 692, load_font(28, False), (242, 242, 236, 255))
    img.save(os.path.join(DECALS_DIR, "baarle_cafe_menu.png"))


def make_baarle_dual_plaques() -> None:
    """Authentic Baarle house number plaques: Belgium (black-yellow-red) & Netherlands (red-white-blue)."""
    # Belgian plaque (B — 2)
    W, H = 512, 384
    img_b = Image.new("RGBA", (W, H), (248, 248, 244, 255))
    db = ImageDraw.Draw(img_b)
    db.rectangle([10, 10, W - 10, H - 10], outline=(24, 24, 28, 255), width=12)
    # Belgian vertical tricolor on left strip
    db.rectangle([22, 22, 82, H - 22], fill=(22, 22, 24, 255))
    db.rectangle([82, 22, 142, H - 22], fill=(248, 212, 36, 255))
    db.rectangle([142, 22, 202, H - 22], fill=(214, 42, 42, 255))
    draw_centered(db, "2", 346, 56, load_font(196, True), (22, 24, 30, 255))
    draw_centered(db, "BELGIË • B", 346, 288, load_font(40, True), (192, 36, 36, 255))
    img_b.save(os.path.join(DECALS_DIR, "plaque_belgium_2.png"))

    # Dutch plaque (NL — 19)
    img_nl = Image.new("RGBA", (W, H), (248, 248, 244, 255))
    dn = ImageDraw.Draw(img_nl)
    dn.rectangle([10, 10, W - 10, H - 10], outline=(24, 46, 106, 255), width=12)
    # Dutch horizontal tricolor on top strip
    dn.rectangle([22, 22, W - 22, 66], fill=(196, 36, 44, 255))
    dn.rectangle([22, 66, W - 22, 110], fill=(250, 250, 250, 255))
    dn.rectangle([22, 110, W - 22, 154], fill=(32, 68, 148, 255))
    draw_centered(dn, "19", W / 2, 148, load_font(154, True), (24, 42, 92, 255))
    draw_centered(dn, "NEDERLAND • NL", W / 2, 314, load_font(36, True), (32, 68, 148, 255))
    img_nl.save(os.path.join(DECALS_DIR, "plaque_netherlands_19.png"))

    # Aluminum B | NL ground stud tile
    img_tile = Image.new("RGBA", (512, 512), (126, 86, 68, 255))
    dt = ImageDraw.Draw(img_tile)
    # Clinker brick pattern
    for r in range(0, 512, 64):
        off = 48 if (r // 64) % 2 else 0
        for c in range(-64, 576, 128):
            dt.rectangle([c + off + 3, r + 3, c + off + 125, r + 61], fill=(138, 92, 72, 255), outline=(88, 60, 48, 255), width=3)
    # Iconic white cross (+) paver in center
    dt.rectangle([224, 56, 288, 456], fill=(242, 240, 234, 255), outline=(182, 178, 170, 255), width=4)
    dt.rectangle([56, 224, 456, 288], fill=(242, 240, 234, 255), outline=(182, 178, 170, 255), width=4)
    # Aluminum B and NL metal studs
    dt.rounded_rectangle([38, 340, 176, 466], radius=18, fill=(208, 214, 222, 255), outline=(74, 80, 92, 255), width=6)
    draw_centered(dt, "B", 107, 354, load_font(86, True), (28, 30, 36, 255))
    dt.rounded_rectangle([336, 340, 474, 466], radius=18, fill=(208, 214, 222, 255), outline=(74, 80, 92, 255), width=6)
    draw_centered(dt, "NL", 405, 360, load_font(76, True), (28, 30, 36, 255))
    img_tile.save(os.path.join(DECALS_DIR, "baarle_border_cross_tile.png"))


def main() -> None:
    os.makedirs(DECALS_DIR, exist_ok=True)
    make_diomede_sign()
    make_dateline_banner()
    make_soren_calendar()
    make_astrid_tablet_ui()
    make_rjukan_sign()
    make_baarle_menu()
    make_baarle_dual_plaques()
    print(f"[Decals] Generated all PNG decals in {DECALS_DIR}")


if __name__ == "__main__":
    main()
