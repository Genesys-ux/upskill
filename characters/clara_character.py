"""
ClaraCharacter — Komponen Karakter 2.5D Ringan (Shared Engine • ~65 baris)
Character : Clara
Prompt    : Clara (26 thn), Pelanggan Kafe Baarle. Wajah ekspresif mata lebar penuh rasa ingin tahu, rambut pendek cokelat gelap rapi, mantel trench coat pendek merah bata wol halus, turtleneck krem, syal tipis krem-biru, dan denim biru tua.
Requires  : character_engine_25d.py (simpan 1x di folder proyek yang sama)

Cara pakai (Free-Rig terbuka — tidak mengunci pose/ekspresi!):
    from clara_character import ClaraCharacter
    char = ClaraCharacter(scale=3, fps=30)

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
    "name": "Clara",
    "prompt": "Clara (26 thn), Pelanggan Kafe Baarle. Wajah ekspresif mata lebar penuh rasa ingin tahu, rambut pendek cokelat gelap rapi, mantel trench coat pendek merah bata wol halus, turtleneck krem, syal tipis krem-biru, dan denim biru tua.",
    "headShape": "chubby_oval",
    "ears": True,
    "earPencil": False,
    "skinColor": "#FCE9DB",
    "blushColor": "#EAB3AA",
    "irisColor": "#543828",
    "eyes": "honey_oval",
    "eyebrows": "raised",
    "nose": "upturned_tiny",
    "mouth": "small_o",
    "beard": "none",
    "faceAccessory": "none",
    "sweatDrop": False,
    "blush": True,
    "angerVein": False,
    "eyeGazeX": -0.1,
    "eyeGazeY": 0.15,
    "hat": "none",
    "hatPrimary": "#3A231B",
    "hatAccent": "#3A231B",
    "hatTilt": 0,
    "hatLiftY": 0,
    "loupeOpen": True,
    "backHair": "short",
    "hairColor": "#3A231B",
    "outfit": "trench_coat",
    "robeColor": "#B54534",
    "innerColor": "#F3E8D4",
    "sashColor": "#7D3025",
    "trimColor": "#253D63",
    "beltStyle": "buckle",
    "cape": "scarf",
    "capeColor": "#E5CFAF",
    "emblem": "none",
    "pose": "think",
    "prop": "none",
    "limbColor": "#253D63",
    "groundShadow": True,
    "outlineShadow": 1.35,
    "outlineLit": 1,
    "rimIntensity": 0.45,
    "shadowDepth": 1.5,
    "customLayers": [],
}


class ClaraCharacter(BaseCharacter25D):
    """Karakter 2.5D Clara — Open Free-Rig, Layered IK, 360° Turntable."""

    DEFAULT_CONFIG: Dict[str, Any] = CHARACTER_CONFIG
    DEFAULT_ANIMATION = "free"
    DEFAULT_ANGLE: float = 0.0
    DEFAULT_FPS: int = 30
    DEFAULT_SCALE: float = 3.0
    DEFAULT_TIME_OFFSET: float = 0.23  # Fase unik otomatis agar multi-karakter tidak bergerak seragam


def render_demo_scene(output_path: str = "demo.mp4", width: int = 720, height: int = 1280, fps: int = 30, scale: float = 2.5, audio_path: str | None = None) -> str:
    return render_character_demo(ClaraCharacter, output_path=output_path, width=width, height=height, fps=fps, scale=scale, audio_path=audio_path)


if __name__ == "__main__":
    run_character_cli(ClaraCharacter)
