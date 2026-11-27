"""Blender headless CLI entry point: builds the selected 3D world, binds Python characters, and renders PNG frames."""
from __future__ import annotations

import argparse
import os
import sys

# Ensure project root is importable inside Blender's bundled Python
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import bpy

from blender_scenes.scene_baarle import build_and_bind_baarle
from blender_scenes.scene_diomede import build_and_bind_diomede
from blender_scenes.scene_rjukan import build_and_bind_rjukan


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    parser = argparse.ArgumentParser(description="Render 3D Blender scene chunk.")
    parser.add_argument("--scene", required=True, choices=["diomede", "rjukan", "baarle"])
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--sprites", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--width", type=int, default=720)
    parser.add_argument("--height", type=int, default=1280)
    parser.add_argument("--samples", type=int, default=20)
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    builders = {
        "diomede": build_and_bind_diomede,
        "rjukan": build_and_bind_rjukan,
        "baarle": build_and_bind_baarle,
    }
    scene = builders[args.scene](
        sprites_dir=args.sprites,
        start_frame=args.start,
        end_frame=args.end,
        width=args.width,
        height=args.height,
        samples=args.samples,
    )

    print(f"[Blender] Rendering {args.scene} frames {args.start}..{args.end - 1} ({args.width}x{args.height}, {args.samples} samples)")
    for f in range(args.start, args.end):
        out_png = os.path.join(args.out_dir, f"frame_{f:04d}.png")
        if os.path.exists(out_png) and os.path.getsize(out_png) > 1024:
            continue
        scene.frame_set(f)
        scene.render.filepath = out_png
        bpy.ops.render.render(write_still=True)
        if (f - args.start) % 15 == 0 or f == args.end - 1:
            print(f"[Blender] {args.scene}: frame {f}/{args.end - 1} done", flush=True)


if __name__ == "__main__":
    main()
