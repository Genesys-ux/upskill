"""
KakekHenrikCharacter — Komponen Karakter 2.5D Ringan (Shared Engine • ~65 baris)
Character : Kakek Henrik
Prompt    : Kakek Henrik (68 thn), Warga Lokal Rjukan Norwegia. Wajah bulat ramah berpipi merona, senyum lebar hangat, rambut putih tipis mengintip dari balik topi musim dingin cokelat berpom-pom krem, kacamata hitam retro berbingkai tebal, mantel wol hijau lumut kebesaran, dan syal rajut bergaris krem-cokelat.
Requires  : character_engine_25d.py (simpan 1x di folder proyek yang sama)

Cara pakai (Free-Rig terbuka — tidak mengunci pose/ekspresi!):
    from kakek_henrik_character import KakekHenrikCharacter
    char = KakekHenrikCharacter(scale=3, fps=30)

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
    "name": "Kakek Henrik",
    "prompt": "Kakek Henrik (68 thn), Warga Lokal Rjukan Norwegia. Wajah bulat ramah berpipi merona, senyum lebar hangat, rambut putih tipis mengintip dari balik topi musim dingin cokelat berpom-pom krem, kacamata hitam retro berbingkai tebal, mantel wol hijau lumut kebesaran, dan syal rajut bergaris krem-cokelat.",
    "headShape": "round",
    "ears": True,
    "earPencil": False,
    "skinColor": "#F7DFD0",
    "blushColor": "#E3978E",
    "irisColor": "#4E5B66",
    "eyes": "happy",
    "eyebrows": "happy",
    "nose": "upturned_tiny",
    "mouth": "happy_open",
    "beard": "none",
    "faceAccessory": "sunglasses",
    "sweatDrop": False,
    "blush": True,
    "angerVein": False,
    "eyeGazeX": 0,
    "eyeGazeY": 0,
    "hat": "beanie",
    "hatPrimary": "#6A4B35",
    "hatAccent": "#EFE0C6",
    "hatTilt": 0,
    "hatLiftY": 0,
    "loupeOpen": True,
    "backHair": "twin_tufts",
    "hairColor": "#E6EAF0",
    "outfit": "safari_explorer",
    "robeColor": "#4A6543",
    "innerColor": "#EFE4CE",
    "sashColor": "#5C412E",
    "trimColor": "#7A5236",
    "beltStyle": "plain",
    "cape": "scarf",
    "capeColor": "#E8D8BC",
    "emblem": "none",
    "pose": "wave",
    "prop": "none",
    "limbColor": "#3B2B20",
    "groundShadow": True,
    "outlineShadow": 1.35,
    "outlineLit": 1,
    "rimIntensity": 0.45,
    "shadowDepth": 1.5,
    "customLayers": [],
}


class KakekHenrikCharacter(BaseCharacter25D):
    """Karakter 2.5D Kakek Henrik — Open Free-Rig, Layered IK, 360° Turntable."""

    DEFAULT_CONFIG: Dict[str, Any] = CHARACTER_CONFIG
    DEFAULT_ANIMATION = "free"
    DEFAULT_ANGLE: float = 0.0
    DEFAULT_FPS: int = 30
    DEFAULT_SCALE: float = 3.0
    DEFAULT_TIME_OFFSET: float = 2.84  # Fase unik otomatis agar multi-karakter tidak bergerak seragam


def render_demo_scene(output_path: str = "demo.mp4", width: int = 720, height: int = 1280, fps: int = 30, scale: float = 2.5, audio_path: str | None = None) -> str:
    return render_character_demo(KakekHenrikCharacter, output_path=output_path, width=width, height=height, fps=fps, scale=scale, audio_path=audio_path)


if __name__ == "__main__":
    run_character_cli(KakekHenrikCharacter)
