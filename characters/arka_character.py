"""
ArkaCharacter — Komponen Karakter 2.5D Ringan (Shared Engine • ~65 baris)
Character : Arka
Prompt    : Arka (24 thn), Host & Penjelajah. Kulit sawo matang hangat berona pipi, mata besar ekspresif cokelat madu, alis tebal dinamis, senyum percaya diri, rambut jabrik rapi gelap, jaket parka outdoor oranye kunyit dengan lapisan dalam hoodie biru dongker, aksen putih, sabuk utility, dan ransel kanvas kecil.
Requires  : character_engine_25d.py (simpan 1x di folder proyek yang sama)

Cara pakai (Free-Rig terbuka — tidak mengunci pose/ekspresi!):
    from arka_character import ArkaCharacter
    char = ArkaCharacter(scale=3, fps=30)

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
    "name": "Arka",
    "prompt": "Arka (24 thn), Host & Penjelajah. Kulit sawo matang hangat berona pipi, mata besar ekspresif cokelat madu, alis tebal dinamis, senyum percaya diri, rambut jabrik rapi gelap, jaket parka outdoor oranye kunyit dengan lapisan dalam hoodie biru dongker, aksen putih, sabuk utility, dan ransel kanvas kecil.",
    "headShape": "chubby_oval",
    "ears": True,
    "earPencil": False,
    "skinColor": "#D9A06C",
    "blushColor": "#C8785E",
    "irisColor": "#5C3317",
    "eyes": "honey_oval",
    "eyebrows": "thick_arch",
    "nose": "upturned_tiny",
    "mouth": "confident_gap",
    "beard": "none",
    "faceAccessory": "none",
    "sweatDrop": False,
    "blush": True,
    "angerVein": False,
    "eyeGazeX": 0.05,
    "eyeGazeY": 0,
    "hat": "none",
    "hatPrimary": "#221A18",
    "hatAccent": "#E08A1E",
    "hatTilt": 0,
    "hatLiftY": 0,
    "loupeOpen": True,
    "backHair": "windswept_bolt",
    "hairColor": "#221A18",
    "outfit": "safari_explorer",
    "robeColor": "#E08A1E",
    "innerColor": "#1F355E",
    "sashColor": "#1F355E",
    "trimColor": "#F4F1EA",
    "beltStyle": "utility_belt",
    "cape": "backpack",
    "capeColor": "#5A4A3B",
    "emblem": "none",
    "pose": "point",
    "prop": "none",
    "limbColor": "#282E38",
    "groundShadow": True,
    "outlineShadow": 1.35,
    "outlineLit": 1,
    "rimIntensity": 0.45,
    "shadowDepth": 1.5,
    "customLayers": [],
}


class ArkaCharacter(BaseCharacter25D):
    """Karakter 2.5D Arka — Open Free-Rig, Layered IK, 360° Turntable."""

    DEFAULT_CONFIG: Dict[str, Any] = CHARACTER_CONFIG
    DEFAULT_ANIMATION = "free"
    DEFAULT_ANGLE: float = 0.0
    DEFAULT_FPS: int = 30
    DEFAULT_SCALE: float = 3.0
    DEFAULT_TIME_OFFSET: float = 0.33  # Fase unik otomatis agar multi-karakter tidak bergerak seragam


def render_demo_scene(output_path: str = "demo.mp4", width: int = 720, height: int = 1280, fps: int = 30, scale: float = 2.5, audio_path: str | None = None) -> str:
    return render_character_demo(ArkaCharacter, output_path=output_path, width=width, height=height, fps=fps, scale=scale, audio_path=audio_path)


if __name__ == "__main__":
    run_character_cli(ArkaCharacter)
