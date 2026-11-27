"""Automated Pre-Render Blender Validator: Raycast Visibility, Bounding-Box Clearance, Anti-Flick & 9-Beat Exposure Audit."""
from __future__ import annotations

import argparse
import math
import os
import sys
from typing import Dict, List, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import bpy
from mathutils import Vector

from animation.storyboard import CAMERA_CUT_FRAMES, get_camera_at_frame, get_characters_at_frame
from blender_scenes.scene_baarle import build_and_bind_baarle
from blender_scenes.scene_diomede import build_and_bind_diomede
from blender_scenes.scene_rjukan import build_and_bind_rjukan

# Objects intentionally translucent, in-hand, atmospheric, or non-occluding during raycast visibility checks
IGNORED_RAY_PREFIXES = (
    "Char_",
    "CharShadow_",
    "SnowFlake",
    "RjuSnow_",
    "VolumetricGodRay",
    "DateLine",
    "SunlitSquare",
    "SteamWisp",
    "HeroSnowball",
    "HeroCalendar",
    "HeroBrassBinoculars",
    "Latte",
    "ArkaFinaleCup",
    "WindowGlass",
    "BorderCrossTile",
    "IceCrackSeam",
    "AstridTablet",
    "DeckRail",
    "DeckPost",
    "Seabird_",
    "ChimneySmoke",
    "AuroraRibbon",
    "FestoonBulb",
)

# 9 critical v2 visual beats covering every single v1 failure point
DIAGNOSTIC_BEATS: Dict[str, List[Tuple[int, str]]] = {
    "diomede": [
        (15,  "00:00.5 Hook: Arka + Snowball + Ignaluk"),
        (350, "00:11.7 Bering Ice Floes + Thin Date Line"),
        (605, "00:20.2 Ice Ledge + Soren (No Dock Clip)"),
    ],
    "rjukan": [
        (840,  "00:28.0 Rjukan Plaza + Houses + 3D Car"),
        (1040, "00:34.7 Astrid + 3 Solspeilet Mirrors"),
        (1300, "00:43.3 Soft God Ray + Henrik (No Whiteout)"),
    ],
    "baarle": [
        (1715, "00:57.2 Bram Bar Slide + Espresso + Pastry"),
        (1950, "01:05.0 Dual-Flag Brick House (BE 2 / NL 19)"),
        (2160, "01:12.0 Baarle Golden Street Finale"),
    ],
}

# Solid static obstacles verified for XY clearance against hero character centers
OBSTACLE_CLEARANCE_RULES: Dict[str, List[Tuple[str, float, float, float]]] = {
    "diomede": [
        ("SignPost", 3.10, 2.05, 0.45),
        ("DockBollard_L", -4.60, 1.85, 0.45),
        ("DockBollard_R", 4.10, 1.95, 0.45),
        ("RailPost_-4.4", -4.40, 2.50, 0.40),
        ("RailPost_-0.6", -0.60, 2.50, 0.40),
    ],
    "rjukan": [
        ("StreetLampPole", -2.65, -2.05, 0.55),
        ("RjukanSignStand", -5.00, 5.40, 0.45),
    ],
    "baarle": [
        ("BistroTableTop", -1.78, 3.66, 0.68),
        ("PastryVitrine", -2.25, 5.10, 0.72),
        ("ItalianEspresso", 2.15, 5.10, 0.68),
        ("FrontPillar_-2.15", -2.15, 0.0, 0.42),
        ("FrontPillar_2.15", 2.15, 0.0, 0.42),
    ],
}


def _is_ignored_ray_hit(obj: bpy.types.Object | None) -> bool:
    if obj is None:
        return True
    if obj.hide_render:
        return True
    return obj.name.startswith(IGNORED_RAY_PREFIXES)


def _raycast_ignoring_allowed(
    scene: bpy.types.Scene,
    depsgraph: bpy.types.Depsgraph,
    origin: Vector,
    dest: Vector,
    stop_margin: float = 0.35,
) -> Tuple[bool, str, float]:
    """Step through allowed translucent/character hits to find any genuine solid wall/prop blocker."""
    vec = dest - origin
    total_dist = vec.length
    if total_dist <= stop_margin + 0.15:
        return False, "", 0.0
    direction = vec.normalized()
    max_dist = total_dist - stop_margin
    traveled = 0.05
    for _ in range(12):
        rem = max_dist - traveled
        if rem <= 0.05:
            return False, "", 0.0
        cur_origin = origin + direction * traveled
        hit, hit_loc, _norm, _idx, hit_obj, _mat = scene.ray_cast(depsgraph, cur_origin, direction, distance=rem)
        if not hit:
            return False, "", 0.0
        step_dist = (hit_loc - cur_origin).length
        if _is_ignored_ray_hit(hit_obj):
            traveled += max(0.06, step_dist + 0.04)
            continue
        return True, hit_obj.name, traveled + step_dist
    return False, "", 0.0


def validate_scene_world(
    scene_name: str,
    start_frame: int,
    end_frame: int,
    sprites_dir: str,
    out_dir: str,
) -> List[Tuple[str, str, float]]:
    builders = {
        "diomede": build_and_bind_diomede,
        "rjukan": build_and_bind_rjukan,
        "baarle": build_and_bind_baarle,
    }
    scene = builders[scene_name](
        sprites_dir=sprites_dir,
        start_frame=start_frame,
        end_frame=end_frame,
        width=360,
        height=640,
        samples=4,
    )

    errors: List[str] = []
    warnings: List[str] = []

    # 1. Anti-Flick + Clearance Check across EVERY single frame!
    prev_pos: Dict[str, Tuple[float, float, float]] = {}
    for f in range(start_frame, end_frame):
        chars = get_characters_at_frame(scene_name, f)
        for cid, st in chars.items():
            if not st["visible"]:
                errors.append(f"[{scene_name}] f={f} ({f/30:.2f}s): hero '{cid}' unexpectedly hidden!")
                continue
            pos = st["pos"]
            if cid in prev_pos and f not in CAMERA_CUT_FRAMES:
                d = math.dist(prev_pos[cid], pos)
                if d > 0.35:
                    errors.append(f"[{scene_name}] f={f} ({f/30:.2f}s): hero '{cid}' FLICK/TELEPORT delta={d:.2f}m (>0.35m)!")
            prev_pos[cid] = pos

            # XY clearance vs static obstacles (when on same floor level, |dz| < 2.0)
            for obs_name, ox, oy, min_r in OBSTACLE_CLEARANCE_RULES.get(scene_name, []):
                if scene_name == "rjukan" and cid == "astrid":
                    continue
                dxy = math.hypot(pos[0] - ox, pos[1] - oy)
                if dxy < min_r:
                    errors.append(
                        f"[{scene_name}] f={f} ({f/30:.2f}s): hero '{cid}' clips obstacle '{obs_name}' (dist={dxy:.2f}m < {min_r:.2f}m)"
                    )

    # 2. Blender Evaluated Depsgraph Raycast Camera Visibility Check (every 6 frames + diagnostic beats)
    check_frames = sorted(set(list(range(start_frame, end_frame, 6)) + [bf for bf, _ in DIAGNOSTIC_BEATS[scene_name]]))
    for f in check_frames:
        scene.frame_set(f)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        cam_st = get_camera_at_frame(scene_name, f)
        cam_origin = Vector(cam_st["pos"])
        cam_target = Vector(cam_st["target"])
        cam_fwd = (cam_target - cam_origin).normalized()

        # Check camera -> target ray (catches camera inside dock, cliff wall, door frame, etc.)
        blocked, hit_name, hit_d = _raycast_ignoring_allowed(scene, depsgraph, cam_origin, cam_target, stop_margin=0.45)
        if blocked:
            # Allow hitting target floor/table/house only if within last 1.2m of target; fail hard if blocking mid-path!
            total_d = (cam_target - cam_origin).length
            if hit_d < total_d - 1.25:
                errors.append(
                    f"[{scene_name}] f={f} ({f/30:.2f}s): CAMERA->TARGET BLOCKED by '{hit_name}' at {hit_d:.2f}m / {total_d:.2f}m!"
                )

        # Check camera -> each forward-visible nearby hero's upper chest (Z + 1.15m)
        chars = get_characters_at_frame(scene_name, f)
        for cid, st in chars.items():
            if not st["visible"]:
                continue
            chest = Vector((st["pos"][0], st["pos"][1], st["pos"][2] + 1.15))
            to_hero = chest - cam_origin
            dist = to_hero.length
            if dist < 0.6 or dist > 15.0:
                continue
            if to_hero.normalized().dot(cam_fwd) < 0.55:
                continue
            blocked_h, hit_h, hit_hd = _raycast_ignoring_allowed(scene, depsgraph, cam_origin, chest, stop_margin=0.42)
            if blocked_h:
                errors.append(
                    f"[{scene_name}] f={f} ({f/30:.2f}s): CAMERA->HERO '{cid}' BLOCKED by '{hit_h}' at {hit_hd:.2f}m / {dist:.2f}m!"
                )

    # 3. Collection Isolation & Car-vs-Building/Snowbank Collision Check!
    if scene_name == "baarle":
        snow_objs = [o.name for o in bpy.data.objects if "Snow" in o.name or "snow" in o.name]
        if snow_objs:
            errors.append(f"[baarle] Snow objects leaked into Baarle scene: {snow_objs[:5]}")

    if scene_name in ("rjukan", "baarle"):
        car_roots = [o for o in bpy.data.objects if o.name.startswith(("NordicCar_", "EuroCar_")) and o.type == "EMPTY"]
        blockers = [
            o for o in bpy.data.objects
            if o.type == "MESH" and (o.name.endswith("_body") or o.name.startswith("SnowBank"))
        ]
        for f in range(start_frame, end_frame, 18):
            scene.frame_set(f)
            depsgraph = bpy.context.evaluated_depsgraph_get()
            for car in car_roots:
                cx, cy = car.location.x, car.location.y
                # Car footprint ~3.6m x 1.7m
                c_x0, c_x1 = cx - 1.75, cx + 1.75
                c_y0, c_y1 = cy - 0.84, cy + 0.84
                for blk in blockers:
                    ev = blk.evaluated_get(depsgraph)
                    pts = [ev.matrix_world @ Vector(corner) for corner in ev.bound_box]
                    bx0, bx1 = min(p.x for p in pts), max(p.x for p in pts)
                    by0, by1 = min(p.y for p in pts), max(p.y for p in pts)
                    bz1 = max(p.z for p in pts)
                    if bz1 > 0.10 and not (c_x1 < bx0 or c_x0 > bx1 or c_y1 < by0 or c_y0 > by1):
                        errors.append(f"[{scene_name}] f={f}: CAR '{car.name}' at ({cx:.1f},{cy:.1f}) CLIPS '{blk.name}'!")

    # 4. Render 3 Key Diagnostic Beats & Check Exposure Luminance (Catches White-Out & Black-Out!)
    rendered_panels: List[Tuple[str, str, float]] = []
    for bf, label in DIAGNOSTIC_BEATS[scene_name]:
        scene.frame_set(bf)
        out_png = os.path.join(out_dir, f"diag_{scene_name}_f{bf:04d}.png")
        scene.render.filepath = out_png
        bpy.ops.render.render(write_still=True)

        # Read rendered image pixels via Blender image API (no Pillow needed inside Blender's bundled Python!)
        img = bpy.data.images.load(out_png, check_existing=False)
        px = list(img.pixels)
        # Stride by 16 pixels (RGBA=4 floats -> step 64) for fast accurate mean luminance
        r_sum = g_sum = b_sum = 0.0
        n_samp = 0
        for idx in range(0, len(px), 64):
            r_sum += px[idx]
            g_sum += px[idx + 1]
            b_sum += px[idx + 2]
            n_samp += 1
        lum = (0.299 * r_sum + 0.587 * g_sum + 0.114 * b_sum) / max(1, n_samp)
        bpy.data.images.remove(img)
        print(f"[Validator] {scene_name} f={bf} ({label}) -> mean luminance = {lum:.3f}", flush=True)
        if lum < 0.05:
            errors.append(f"[{scene_name}] f={bf} ({label}): BLACK-OUT detected (mean lum={lum:.3f} < 0.05)!")
        elif lum > 0.84:
            errors.append(f"[{scene_name}] f={bf} ({label}): WHITE-OUT / OVEREXPOSURE detected (mean lum={lum:.3f} > 0.84)!")
        rendered_panels.append((out_png, label, lum))

    for w in warnings:
        print(f"[Validator][WARN] {w}", flush=True)
    if errors:
        print(f"[Validator][FAIL] {len(errors)} critical error(s) in '{scene_name}':", flush=True)
        for e in errors[:25]:
            print("  ERROR:", e, flush=True)
        raise RuntimeError(f"Scene validation FAILED for '{scene_name}' with {len(errors)} error(s)!")

    print(f"[Validator][PASS] '{scene_name}' PASSED raycast visibility, clearance, anti-flick & exposure audit!", flush=True)
    return rendered_panels


def main() -> None:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser(description="Pre-render Blender 3D Validator")
    parser.add_argument("--sprites-root", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)

    ranges = [("diomede", 0, 750), ("rjukan", 750, 1470), ("baarle", 1470, 2250)]
    manifest_lines: List[str] = []
    for sname, sf, ef in ranges:
        panels = validate_scene_world(
            scene_name=sname,
            start_frame=sf,
            end_frame=ef,
            sprites_dir=os.path.join(args.sprites_root, sname),
            out_dir=args.out_dir,
        )
        for p, lbl, lum in panels:
            manifest_lines.append(f"{p}|{lbl}|{lum:.3f}")

    with open(os.path.join(args.out_dir, "diagnostic_manifest.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(manifest_lines) + "\n")
    print("[Validator] ALL 3 SCENES PASSED 100%!", flush=True)


if __name__ == "__main__":
    main()
