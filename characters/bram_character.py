"""
BramCharacter — Komponen Karakter 2.5D Ringan (Shared Engine • ~65 baris)
Character : Bram
Prompt    : Bram (38 thn), Barista & Pemilik Kafe Perbatasan Baarle. Wajah lonjong ramah, kumis tipis melengkung rapi, rambut cokelat belah samping, mata jenaka, kemeja putih-abu dibalut celemek kanvas cokelat kopi tua dengan sabuk oranye hangat dan aksen kuningan.
Requires  : character_engine_25d.py (simpan 1x di folder proyek yang sama)

Cara pakai (Free-Rig terbuka — tidak mengunci pose/ekspresi!):
    from bram_character import BramCharacter
    char = BramCharacter(scale=3, fps=30)

    # 1) Bebas atur badan, kepala, tangan IK, mulut & ekspresi sendiri (tanpa preset terkunci):
    img = char.render_pil(
        frame=15, animation="free", angle=20,
        pelvis_y=10, torso_lean_deg=6, head_tilt_deg=-5,
        right_hand_target=(82, 175, 34), mouth_open=0.65, eyes="suspicious",
    )

    # 2) Campur layer bebas (mis. lari sambil panik / jalan sambil bicara & bersedekap):
    img = char.render_pil(frame=15, animation="walk", arm_pose="crossed", mouth_open=0.5, eyes="smug")
    img = char.render_pil(frame=15, animation="talk", pose="think", gesture_energy=0.8)
"""

from __future__ import annotations

from typing import Any, Dict

from character_engine_25d import (
    BaseCharacter25D,
    Easing,
    StoryboardScene,
    Vec3,
    extract_lipsync_curve,
    interpolate,
    render_character_demo,
    run_character_cli,
    spring,
)

CHARACTER_CONFIG: Dict[str, Any] = {
    "name": "Bram",
    "prompt": "Bram (38 thn), Barista & Pemilik Kafe Perbatasan Baarle. Wajah lonjong ramah, kumis tipis melengkung rapi, rambut cokelat belah samping, mata jenaka, kemeja putih-abu dibalut celemek kanvas cokelat kopi tua dengan sabuk oranye hangat dan aksen kuningan.",
    "headShape": "tall",
    "ears": True,
    "earPencil": False,
    "skinColor": "#F9E3D2",
    "blushColor": "#E4B5A4",
    "irisColor": "#5C4028",
    "eyes": "honey_oval",
    "eyebrows": "raised",
    "nose": "upturned_tiny",
    "mouth": "smirk",
    "beard": "handlebar",
    "faceAccessory": "none",
    "sweatDrop": False,
    "blush": False,
    "angerVein": False,
    "eyeGazeX": 0.1,
    "eyeGazeY": 0,
    "hat": "none",
    "hatPrimary": "#523421",
    "hatAccent": "#EAC038",
    "hatTilt": 0,
    "hatLiftY": 0,
    "loupeOpen": True,
    "backHair": "side_part",
    "hairColor": "#523421",
    "outfit": "mechanic_overall",
    "robeColor": "#5A3923",
    "innerColor": "#E8EBEE",
    "sashColor": "#D87526",
    "trimColor": "#EAC038",
    "beltStyle": "buckle",
    "cape": "none",
    "capeColor": "#5A3923",
    "emblem": "none",
    "pose": "point",
    "prop": "none",
    "limbColor": "#26242B",
    "groundShadow": True,
    "outlineShadow": 1.35,
    "outlineLit": 1,
    "rimIntensity": 0.45,
    "shadowDepth": 1.5,
    "customLayers": [],
}


class BramCharacter(BaseCharacter25D):
    """Karakter 2.5D Bram — Open Free-Rig, Layered IK, 360° Turntable."""

    DEFAULT_CONFIG: Dict[str, Any] = CHARACTER_CONFIG
    DEFAULT_ANIMATION = "free"
    DEFAULT_ANGLE: float = 0.0
    DEFAULT_FPS: int = 30
    DEFAULT_SCALE: float = 3.0
    DEFAULT_TIME_OFFSET: float = 1.4  # Fase unik otomatis agar multi-karakter tidak bergerak seragam


def render_demo_scene(output_path: str = "demo.mp4", width: int = 720, height: int = 1280, fps: int = 30, scale: float = 2.5, audio_path: str | None = None) -> str:
    return render_character_demo(BramCharacter, output_path=output_path, width=width, height=height, fps=fps, scale=scale, audio_path=audio_path)


if __name__ == "__main__":
    run_character_cli(BramCharacter)
