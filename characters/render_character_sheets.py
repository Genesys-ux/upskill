"""Render 360° turnaround sheets + Free-Rig acting pose + full cast lineup for all 6 characters."""
from __future__ import annotations

import os
import shutil
import sys

CHAR_DIR = r"D:\Lutfi\3D pro\bumi_ngebug\characters"
PREV_DIR = os.path.join(CHAR_DIR, "previews")
ART_PREV_DIR = r"C:\Users\Mr Matrial Boy\.gemini\antigravity\brain\6b9d325f-56bc-40a2-8e75-341ba9346a8d\previews"

sys.path.insert(0, CHAR_DIR)

from PIL import Image, ImageDraw, ImageFont

from arka_character import ArkaCharacter
from astrid_character import AstridCharacter
from bram_character import BramCharacter
from clara_character import ClaraCharacter
from kakek_henrik_character import KakekHenrikCharacter
from kapten_soren_character import KaptenSorenCharacter


def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"]
        if bold
        else [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]
    )
    for fpath in candidates:
        if os.path.exists(fpath):
            return ImageFont.truetype(fpath, size)
    return ImageFont.load_default()


def main() -> None:
    os.makedirs(PREV_DIR, exist_ok=True)
    os.makedirs(ART_PREV_DIR, exist_ok=True)

    f_title = load_font(34, bold=True)
    f_sub = load_font(20, bold=False)
    f_chip = load_font(18, bold=True)
    f_name = load_font(22, bold=True)
    f_role = load_font(16, bold=False)

    roster = [
        {
            "id": "arka",
            "cls": ArkaCharacter,
            "title": "1. ARKA — 24 thn • Host & Penjelajah (Semua Lokasi)",
            "subtitle": "Oranye Kunyit • Biru Dongker • Putih | Shared Engine + Free-Rig",
            "role": "Host • Semua Lokasi",
            "palette": ["#E08A1E", "#1F355E", "#F4F1EA", "#D9A06C"],
            "lineup_scale": 1.00,
            "acting_label": "Free-Rig: Hook & Narasi",
            "acting_kwargs": dict(
                angle=22,
                animation="free",
                blink=0.0,
                pelvis_y=-4,
                torso_lean_deg=5,
                head_tilt_deg=-6,
                right_hand_target=(86, 175, 42),
                left_hand_target=(-56, 268, 12),
                eyes="honey_oval",
                eyebrows="thick_arch",
                mouth="confident_gap",
                mouth_open=0.45,
                eye_gaze_x=0.18,
                eye_gaze_y=-0.05,
            ),
        },
        {
            "id": "kapten_soren",
            "cls": KaptenSorenCharacter,
            "title": "2. KAPTEN SOREN — 52 thn • Nelayan Alaska (Pulau Diomede)",
            "subtitle": "Merah Marun Pudar • Abu-abu Tua • Kuning | Shared Engine + Free-Rig",
            "role": "Nelayan • Diomede",
            "palette": ["#7E2D36", "#545D6B", "#DFA928", "#C5CED8"],
            "lineup_scale": 1.04,
            "acting_label": "Free-Rig: Menunjuk Seberang",
            "acting_kwargs": dict(
                angle=-22,
                animation="free",
                blink=0.0,
                pelvis_y=2,
                torso_lean_deg=-3,
                head_tilt_deg=4,
                right_hand_target=(92, 200, 32),
                left_hand_target=(-52, 275, 16),
                eyes="chill",
                eyebrows="skeptical",
                mouth="smirk",
                mouth_open=0.30,
                eye_gaze_x=-0.35,
                eye_gaze_y=0.0,
            ),
        },
        {
            "id": "astrid",
            "cls": AstridCharacter,
            "title": "3. ASTRID — 31 thn • Teknisi Optik Heliostat (Rjukan, Norwegia)",
            "subtitle": "Kuning Stabilo • Hitam Matte • Perak | Shared Engine + Free-Rig",
            "role": "Teknisi • Rjukan",
            "palette": ["#D8F526", "#21252D", "#F3F6FA", "#E8C568"],
            "lineup_scale": 0.99,
            "acting_label": "Free-Rig: Aktifkan Cermin",
            "acting_kwargs": dict(
                angle=25,
                animation="free",
                blink=0.0,
                pelvis_y=0,
                torso_lean_deg=2,
                head_tilt_deg=-3,
                left_hand_target=(-34, 248, 42),
                right_hand_target=(42, 236, 48),
                eyes="focused",
                eyebrows="flat",
                mouth="smirk",
                mouth_open=0.32,
                eye_gaze_x=0.25,
                eye_gaze_y=0.05,
            ),
        },
        {
            "id": "kakek_henrik",
            "cls": KakekHenrikCharacter,
            "title": "4. KAKEK HENRIK — 68 thn • Warga Lokal (Rjukan, Norwegia)",
            "subtitle": "Hijau Lumut • Krem • Cokelat | Shared Engine + Free-Rig",
            "role": "Warga • Rjukan",
            "palette": ["#4A6543", "#E8D8BC", "#6A4B35", "#3B2B20"],
            "lineup_scale": 0.90,
            "acting_label": "Free-Rig: Santai & Jempol",
            "acting_kwargs": dict(
                angle=20,
                animation="free",
                blink=0.0,
                pelvis_y=12,
                torso_lean_deg=4,
                head_tilt_deg=7,
                right_hand_target=(84, 198, 38),
                left_hand_target=(-42, 255, 28),
                eyes="happy",
                eyebrows="happy",
                mouth="happy_open",
                mouth_open=0.55,
            ),
        },
        {
            "id": "bram",
            "cls": BramCharacter,
            "title": "5. BRAM — 38 thn • Barista & Pemilik Kafe (Baarle, NL/BE)",
            "subtitle": "Cokelat Kopi • Oranye • Hitam-Kuning | Shared Engine + Free-Rig",
            "role": "Barista • Baarle",
            "palette": ["#5A3923", "#D87526", "#EAC038", "#E8EBEE"],
            "lineup_scale": 1.05,
            "acting_label": "Free-Rig: Geser Cangkir",
            "acting_kwargs": dict(
                angle=20,
                animation="free",
                blink=0.0,
                pelvis_y=0,
                torso_lean_deg=-4,
                head_tilt_deg=-5,
                right_hand_target=(88, 224, 38),
                left_hand_target=(-46, 268, 24),
                eyes="honey_oval",
                eyebrows="raised",
                mouth="grin_teeth",
                mouth_open=0.40,
                eye_gaze_x=0.25,
                eye_gaze_y=-0.04,
            ),
        },
        {
            "id": "clara",
            "cls": ClaraCharacter,
            "title": "6. CLARA — 26 thn • Pelanggan Kafe (Baarle, NL/BE)",
            "subtitle": "Merah Bata • Krem • Denim Biru | Shared Engine + Free-Rig",
            "role": "Pelanggan • Baarle",
            "palette": ["#B54534", "#F3E8D4", "#253D63", "#3A231B"],
            "lineup_scale": 0.95,
            "acting_label": "Free-Rig: Heran Melirik Lantai",
            "acting_kwargs": dict(
                angle=24,
                animation="free",
                blink=0.0,
                pelvis_y=6,
                torso_lean_deg=6,
                head_tilt_deg=10,
                left_hand_target=(-38, 212, 36),
                right_hand_target=(68, 262, 34),
                eyes="honey_oval",
                eyebrows="skeptical",
                mouth="small_o",
                mouth_open=0.42,
                eye_gaze_x=-0.12,
                eye_gaze_y=0.55,
            ),
        },
    ]

    # 1. Individual 5-view turnaround sheets
    for item in roster:
        char = item["cls"](scale=1.6, fps=30)
        views = [
            ("0° Depan", dict(angle=0, animation="free", blink=0.0)),
            ("35° Tiga-Perempat", dict(angle=35, animation="free", blink=0.0)),
            ("90° Samping", dict(angle=90, animation="free", blink=0.0)),
            ("180° Belakang", dict(angle=180, animation="free", blink=0.0)),
            (item["acting_label"], item["acting_kwargs"]),
        ]
        W, H = 2050, 1020
        canvas = Image.new("RGBA", (W, H), (244, 241, 235, 255))
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([0, 0, W, 118], fill=(24, 20, 34, 255))
        draw.text((34, 20), item["title"], font=f_title, fill=(248, 245, 252, 255))
        draw.text((34, 68), item["subtitle"], font=f_sub, fill=(176, 168, 198, 255))

        px = W - 260
        for col in item["palette"]:
            draw.rounded_rectangle([px, 34, px + 46, 80], radius=8, fill=col, outline=(255, 255, 255, 180), width=2)
            px += 56

        draw.line([(30, 912), (W - 30, 912)], fill=(210, 204, 194, 255), width=2)

        col_w = W // len(views)
        for i, (lbl, kwargs) in enumerate(views):
            sprite = char.render_pil(frame=0, **kwargs)
            sx = i * col_w + (col_w - sprite.width) // 2
            sy = 148
            canvas.alpha_composite(sprite, (sx, sy))
            bx = i * col_w + 18
            draw.rounded_rectangle([bx, 945, (i + 1) * col_w - 18, 992], radius=10, fill=(32, 27, 45, 240))
            tw = draw.textlength(lbl, font=f_chip)
            draw.text((i * col_w + (col_w - tw) / 2, 956), lbl, font=f_chip, fill=(230, 244, 255, 255))

        fname = f"turnaround_{item['id']}.png"
        out1 = os.path.join(PREV_DIR, fname)
        out2 = os.path.join(ART_PREV_DIR, fname)
        canvas.convert("RGB").save(out1, quality=95)
        shutil.copy2(out1, out2)
        print("Saved:", fname)

    # 2. Full 6-character lineup sheet
    LW, LH = 2280, 1080
    lineup = Image.new("RGBA", (LW, LH), (244, 241, 235, 255))
    ldraw = ImageDraw.Draw(lineup)
    ldraw.rectangle([0, 0, LW, 128], fill=(20, 17, 30, 255))
    ldraw.text(
        (38, 22),
        "CAST LINEUP — BUMI LAGI NGE-BUG! (6 Karakter Shared Engine & Free-Rig)",
        font=f_title,
        fill=(250, 247, 255, 255),
    )
    ldraw.text(
        (38, 72),
        'Export dari generator.html (Shared Engine + animation="free") • Perbandingan proporsi, siluet, & palet warna',
        font=f_sub,
        fill=(168, 222, 238, 255),
    )

    floor_y = 955
    for gy in [floor_y, floor_y - 250, floor_y - 500, floor_y - 720]:
        ldraw.line([(36, gy), (LW - 36, gy)], fill=(218, 212, 202, 255), width=2)

    slot_w = (LW - 60) // 6
    for idx, item in enumerate(roster):
        char = item["cls"](scale=1.65 * item["lineup_scale"], fps=30)
        sprite = char.render_pil(frame=0, **item["acting_kwargs"])
        cx = 30 + idx * slot_w + slot_w // 2
        sx = cx - sprite.width // 2
        foot_offset = int(round(sprite.height * 0.923))
        sy = floor_y - foot_offset
        lineup.alpha_composite(sprite, (sx, sy))

        name_txt = item["cls"].DEFAULT_CONFIG["name"]
        bx1 = 30 + idx * slot_w + 14
        bx2 = 30 + (idx + 1) * slot_w - 14
        ldraw.rounded_rectangle([bx1, 978, bx2, 1054], radius=12, fill=(28, 24, 40, 245))
        tw1 = ldraw.textlength(name_txt, font=f_name)
        ldraw.text((cx - tw1 / 2, 987), name_txt, font=f_name, fill=(255, 255, 255, 255))
        tw2 = ldraw.textlength(item["role"], font=f_role)
        ldraw.text((cx - tw2 / 2, 1020), item["role"], font=f_role, fill=(176, 218, 236, 255))

    l_out1 = os.path.join(PREV_DIR, "cast_lineup_all6.png")
    l_out2 = os.path.join(ART_PREV_DIR, "cast_lineup_all6.png")
    lineup.convert("RGB").save(l_out1, quality=95)
    shutil.copy2(l_out1, l_out2)
    print("Saved:", l_out1)


if __name__ == "__main__":
    main()
