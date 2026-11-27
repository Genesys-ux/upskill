"""Render camera-yaw-synced Python 2.5D Free-Rig hero + unified 2.5D bean-head NPC RGBA sprites for Blender."""
from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "characters"))

from animation.storyboard import get_characters_at_frame
from characters.npc_generator import render_scene_npc_sprites
from project_config import AUDIO_DIR, BUILD_DIR, FPS

from arka_character import ArkaCharacter
from astrid_character import AstridCharacter
from bram_character import BramCharacter
from clara_character import ClaraCharacter
from kakek_henrik_character import KakekHenrikCharacter
from kapten_soren_character import KaptenSorenCharacter

CHAR_CLASSES = {
    "arka": ArkaCharacter,
    "kapten_soren": KaptenSorenCharacter,
    "astrid": AstridCharacter,
    "kakek_henrik": KakekHenrikCharacter,
    "bram": BramCharacter,
    "clara": ClaraCharacter,
}

SCENE_CHARS = {
    "diomede": ["arka", "kapten_soren"],
    "rjukan": ["arka", "astrid", "kakek_henrik"],
    "baarle": ["arka", "bram", "clara"],
}


def load_lipsync() -> Optional[Dict[str, List[float]]]:
    p = os.path.join(AUDIO_DIR, "lipsync_curves.json")
    if not os.path.exists(p):
        return None
    with open(p, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("curves")


def render_character_sprites(
    scene_name: str,
    start_frame: int,
    end_frame: int,
    scale: float = 1.65,
    workers: int = 4,
    out_root: Optional[str] = None,
) -> str:
    """Render RGBA PNG image sequences for hero characters AND unified 2.5D bean-head NPCs."""
    base_dir = out_root or os.path.join(BUILD_DIR, "sprites", scene_name)
    lipsync = load_lipsync()
    char_ids = SCENE_CHARS[scene_name]
    instances = {cid: CHAR_CLASSES[cid](scale=scale, fps=FPS) for cid in char_ids}

    for cid in char_ids:
        os.makedirs(os.path.join(base_dir, cid), exist_ok=True)

    # Render unified 2.5D bean-head NPCs for this scene (identical studio style to hero characters!)
    render_scene_npc_sprites(scene_name, os.path.join(base_dir, "npcs"), scale=min(1.3, scale))

    jobs: List[Tuple[str, int, Dict[str, Any], str]] = []
    for f in range(start_frame, end_frame):
        states = get_characters_at_frame(scene_name, f, lipsync)
        for cid in char_ids:
            st = states[cid]
            out_png = os.path.join(base_dir, cid, f"frame_{f:04d}.png")
            if os.path.exists(out_png) and os.path.getsize(out_png) > 200:
                continue
            jobs.append((cid, f, st["render_kwargs"], out_png))

    def _run_one(job: Tuple[str, int, Dict[str, Any], str]) -> None:
        cid, f, rk, out_png = job
        instances[cid].save_frame(out_png, frame=f, fps=FPS, **rk)

    if jobs:
        print(f"[Sprites] Rendering {len(jobs)} hero frames + unified 2.5D NPCs for '{scene_name}' ({start_frame}..{end_frame - 1})...")
        if workers > 1:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                list(pool.map(_run_one, jobs))
        else:
            for j in jobs:
                _run_one(j)
    print(f"[Sprites] Ready in {base_dir}")
    return base_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Render camera-synced 2.5D hero & NPC sprites for Blender.")
    parser.add_argument("--scene", required=True, choices=["diomede", "rjukan", "baarle"])
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--scale", type=float, default=1.65)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    render_character_sprites(args.scene, args.start, args.end, scale=args.scale, workers=args.workers)


if __name__ == "__main__":
    main()
