"""
KaptenSorenCharacter — Komponen Karakter 2.5D Ringan (Shared Engine • ~65 baris)
Character : Kapten Soren
Prompt    : Kapten Soren (52 thn), Nelayan Alaska Pulau Diomede. Rahang persegi kokoh, kulit kemerahan terpapar angin kutub, kumis dan jenggot abu-abu lebat bersalju, kupluk rajut wol abu-abu, jaket nelayan tebal merah marun pudar berbahan waxed canvas, sabuk gesper kuningan, tatapan tenang santai.
Requires  : character_engine_25d.py (simpan 1x di folder proyek yang sama)

Cara pakai (Free-Rig terbuka — tidak mengunci pose/ekspresi!):
    from kapten_soren_character import KaptenSorenCharacter
    char = KaptenSorenCharacter(scale=3, fps=30)

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
    "name": "Kapten Soren",
    "prompt": "Kapten Soren (52 thn), Nelayan Alaska Pulau Diomede. Rahang persegi kokoh, kulit kemerahan terpapar angin kutub, kumis dan jenggot abu-abu lebat bersalju, kupluk rajut wol abu-abu, jaket nelayan tebal merah marun pudar berbahan waxed canvas, sabuk gesper kuningan, tatapan tenang santai.",
    "headShape": "wide",
    "ears": True,
    "earPencil": False,
    "skinColor": "#EDC4AC",
    "blushColor": "#CF7D70",
    "irisColor": "#4A5D6E",
    "eyes": "chill",
    "eyebrows": "skeptical",
    "nose": "upturned_tiny",
    "mouth": "smirk",
    "beard": "full_beard",
    "faceAccessory": "none",
    "sweatDrop": False,
    "blush": True,
    "angerVein": False,
    "eyeGazeX": -0.15,
    "eyeGazeY": 0,
    "hat": "beanie",
    "hatPrimary": "#545D6B",
    "hatAccent": "#98A3B3",
    "hatTilt": 0,
    "hatLiftY": 0,
    "loupeOpen": True,
    "backHair": "short",
    "hairColor": "#C5CED8",
    "outfit": "safari_explorer",
    "robeColor": "#7E2D36",
    "innerColor": "#454C57",
    "sashColor": "#39404A",
    "trimColor": "#DFA928",
    "beltStyle": "buckle",
    "cape": "none",
    "capeColor": "#39404A",
    "emblem": "none",
    "pose": "akimbo",
    "prop": "none",
    "limbColor": "#252A33",
    "groundShadow": True,
    "outlineShadow": 1.35,
    "outlineLit": 1,
    "rimIntensity": 0.45,
    "shadowDepth": 1.5,
    "customLayers": [],
}


class KaptenSorenCharacter(BaseCharacter25D):
    """Karakter 2.5D Kapten Soren — Open Free-Rig, Layered IK, 360° Turntable."""

    DEFAULT_CONFIG: Dict[str, Any] = CHARACTER_CONFIG
    DEFAULT_ANIMATION = "free"
    DEFAULT_ANGLE: float = 0.0
    DEFAULT_FPS: int = 30
    DEFAULT_SCALE: float = 3.0
    DEFAULT_TIME_OFFSET: float = 2.98  # Fase unik otomatis agar multi-karakter tidak bergerak seragam


def render_demo_scene(output_path: str = "demo.mp4", width: int = 720, height: int = 1280, fps: int = 30, scale: float = 2.5, audio_path: str | None = None) -> str:
    return render_character_demo(KaptenSorenCharacter, output_path=output_path, width=width, height=height, fps=fps, scale=scale, audio_path=audio_path)


if __name__ == "__main__":
    run_character_cli(KaptenSorenCharacter)
