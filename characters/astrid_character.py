"""
AstridCharacter — Komponen Karakter 2.5D Ringan (Shared Engine • ~65 baris)
Character : Astrid
Prompt    : Astrid (31 thn), Teknisi Optik Heliostat Rjukan Norwegia. Wajah tirus Skandinavia, rambut pirang pendek rapi keluar sedikit dari bawah helm proyek putih, kacamata pelindung goggles dinaikkan di dahi, tatapan fokus profesional, jaket keselamatan teknis hitam matte dengan garis reflektif kuning stabilo dan aksen perak.
Requires  : character_engine_25d.py (simpan 1x di folder proyek yang sama)

Cara pakai (Free-Rig terbuka — tidak mengunci pose/ekspresi!):
    from astrid_character import AstridCharacter
    char = AstridCharacter(scale=3, fps=30)

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
    "name": "Astrid",
    "prompt": "Astrid (31 thn), Teknisi Optik Heliostat Rjukan Norwegia. Wajah tirus Skandinavia, rambut pirang pendek rapi keluar sedikit dari bawah helm proyek putih, kacamata pelindung goggles dinaikkan di dahi, tatapan fokus profesional, jaket keselamatan teknis hitam matte dengan garis reflektif kuning stabilo dan aksen perak.",
    "headShape": "tall",
    "ears": True,
    "earPencil": False,
    "skinColor": "#FCEBE0",
    "blushColor": "#EEBEB6",
    "irisColor": "#4A82AD",
    "eyes": "focused",
    "eyebrows": "flat",
    "nose": "upturned_tiny",
    "mouth": "smirk",
    "beard": "none",
    "faceAccessory": "goggles",
    "sweatDrop": False,
    "blush": True,
    "angerVein": False,
    "eyeGazeX": 0,
    "eyeGazeY": 0,
    "hat": "miner_helmet",
    "hatPrimary": "#F3F6FA",
    "hatAccent": "#D8F526",
    "hatTilt": 0,
    "hatLiftY": 0,
    "loupeOpen": True,
    "backHair": "windswept_bolt",
    "hairColor": "#E8C568",
    "outfit": "cyber_jacket",
    "robeColor": "#21252D",
    "innerColor": "#D8F526",
    "sashColor": "#2D3440",
    "trimColor": "#D8F526",
    "beltStyle": "utility_belt",
    "cape": "none",
    "capeColor": "#21252D",
    "emblem": "none",
    "pose": "ready",
    "prop": "none",
    "limbColor": "#222730",
    "groundShadow": True,
    "outlineShadow": 1.35,
    "outlineLit": 1,
    "rimIntensity": 0.45,
    "shadowDepth": 1.5,
    "customLayers": [],
}


class AstridCharacter(BaseCharacter25D):
    """Karakter 2.5D Astrid — Open Free-Rig, Layered IK, 360° Turntable."""

    DEFAULT_CONFIG: Dict[str, Any] = CHARACTER_CONFIG
    DEFAULT_ANIMATION = "free"
    DEFAULT_ANGLE: float = 0.0
    DEFAULT_FPS: int = 30
    DEFAULT_SCALE: float = 3.0
    DEFAULT_TIME_OFFSET: float = 0.89  # Fase unik otomatis agar multi-karakter tidak bergerak seragam


def render_demo_scene(output_path: str = "demo.mp4", width: int = 720, height: int = 1280, fps: int = 30, scale: float = 2.5, audio_path: str | None = None) -> str:
    return render_character_demo(AstridCharacter, output_path=output_path, width=width, height=height, fps=fps, scale=scale, audio_path=audio_path)


if __name__ == "__main__":
    run_character_cli(AstridCharacter)
