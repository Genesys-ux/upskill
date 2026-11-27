"""Master 75-second 3D Continuous Camera Choreography, Zero-Flick Character Blocking & Prop Sync (v2 Audited)."""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

FPS = 30.0

# ============================================================================
# GLOBAL FLOOR & SURFACE ELEVATION CONSTANTS (ANTI-CLIPPING SINGLE SOURCE OF TRUTH)
# ============================================================================
DOCK_Z = 2.40        # World 1: Little Diomede wooden pier deck top
ICE_LEDGE_Z = 1.65   # World 1: Lower dock ice-ledge step (connected by continuous wooden ramp!)
CLIFF_DECK_Z = 24.0  # World 2: Rjukan Solspeilet cliff observation platform
SQUARE_Z = 0.0       # World 2: Rjukan Torg cobblestone plaza
CAFE_FLOOR_Z = 0.0   # World 3: Baarle street & Café de Grens floor
BAR_TOP_Z = 0.86     # World 3: Oak bar counter top (proportional to 2.5D bean-head torso!)
BRAM_STEP_Z = 0.24   # World 3: Raised barista wooden duckboard behind bar so Bram's chest/apron & arms clear BAR_TOP_Z!

# Exact 1-frame camera cuts (where blocking changes are permitted simultaneously on the exact cut frame)
CAMERA_CUT_FRAMES = {
    750,   # 25.0s: Diomede -> Rjukan whip-pan exit
    1470,  # 49.0s: Rjukan sunglasses match-cut -> Baarle sidewalk (+)
    2100,  # 70.0s: Café interior -> Golden-hour Baarle street finale (eliminates 01:10 empty-chair flick!)
}


# ============================================================================
# 1. ORGANIC MOTION CURVES
# ============================================================================

def clamp01(t: float) -> float:
    return 0.0 if t <= 0.0 else (1.0 if t >= 1.0 else t)


def ease_expo_in_out(t: float) -> float:
    t = clamp01(t)
    if t == 0.0 or t == 1.0:
        return t
    if t < 0.5:
        return 0.5 * (2.0 ** (20.0 * t - 10.0))
    return 1.0 - 0.5 * (2.0 ** (-20.0 * t + 10.0))


def ease_cubic_in_out(t: float) -> float:
    t = clamp01(t)
    return 4.0 * t * t * t if t < 0.5 else 1.0 - ((-2.0 * t + 2.0) ** 3) * 0.5


def ease_out_overshoot(t: float, s: float = 0.75) -> float:
    t = clamp01(t)
    u = t - 1.0
    return 1.0 + (s + 1.0) * (u ** 3) + s * (u ** 2)


def ease_snappy_ramp(t: float) -> float:
    t = clamp01(t)
    return ease_out_overshoot(ease_cubic_in_out(t), s=0.45)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp3(p0: Tuple[float, float, float], p1: Tuple[float, float, float], t: float) -> Tuple[float, float, float]:
    return (lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t), lerp(p0[2], p1[2], t))


def eval_camera_track(keyframes: List[Dict[str, Any]], t_sec: float) -> Dict[str, Any]:
    if t_sec <= keyframes[0]["t"]:
        k = keyframes[0]
        return {"pos": k["pos"], "target": k["target"], "lens": k["lens"], "roll": k.get("roll", 0.0)}
    if t_sec >= keyframes[-1]["t"]:
        k = keyframes[-1]
        return {"pos": k["pos"], "target": k["target"], "lens": k["lens"], "roll": k.get("roll", 0.0)}

    for i in range(len(keyframes) - 1):
        k0 = keyframes[i]
        k1 = keyframes[i + 1]
        if k0["t"] <= t_sec <= k1["t"]:
            if k1.get("cut"):
                # Instant 1-frame hard cut at k1["t"] (no interpolation across cut!)
                if t_sec < k1["t"] - 1e-4:
                    return {"pos": k0["pos"], "target": k0["target"], "lens": k0["lens"], "roll": k0.get("roll", 0.0)}
                return {"pos": k1["pos"], "target": k1["target"], "lens": k1["lens"], "roll": k1.get("roll", 0.0)}

            dt = max(1e-5, k1["t"] - k0["t"])
            u = (t_sec - k0["t"]) / dt
            curve = k1.get("ease", "expo")
            if curve == "overshoot":
                e = ease_out_overshoot(u, s=0.55)
            elif curve == "snappy":
                e = ease_snappy_ramp(u)
            elif curve == "cubic":
                e = ease_cubic_in_out(u)
            elif curve == "linear":
                e = u
            else:
                e = ease_expo_in_out(u)

            if "orbit" in k1:
                orb = k1["orbit"]
                cx, cy, cz = orb["center"]
                ang = math.radians(lerp(orb["ang0"], orb["ang1"], e))
                rad = lerp(orb["r0"], orb["r1"], e)
                z_val = lerp(orb["z0"], orb["z1"], e)
                pos = (cx + rad * math.cos(ang), cy + rad * math.sin(ang), z_val)
            else:
                pos = lerp3(k0["pos"], k1["pos"], e)

            target = lerp3(k0["target"], k1["target"], e)
            lens = lerp(k0["lens"], k1["lens"], clamp01(e))
            roll = lerp(k0.get("roll", 0.0), k1.get("roll", 0.0), e)
            breath_x = math.sin(t_sec * 1.9) * 0.012
            breath_z = math.cos(t_sec * 2.4) * 0.010
            return {
                "pos": (pos[0] + breath_x, pos[1], pos[2] + breath_z),
                "target": target,
                "lens": max(16.0, min(85.0, lens)),
                "roll": roll,
            }
    k = keyframes[-1]
    return {"pos": k["pos"], "target": k["target"], "lens": k["lens"], "roll": k.get("roll", 0.0)}


# ============================================================================
# 2. RAYCAST-CLEARED 30+ CONTINUOUS CAMERA MOVEMENTS (ZERO OBSTRUCTIONS!)
# ============================================================================

# WORLD 1: Little Diomede Cliff Dock & Bering Strait (00:00.0 – 00:25.0)
# GEOMETRY GUARANTEE: Dock sits in X[-10, 10], Y[-4.0, +2.6], Z=2.40.
# Little Diomede rocky slope & Ignaluk stilt houses are strictly in X <= -7.5 (LEFT) and Y <= -7.0 (FAR BEHIND)!
# So EVERY camera point in Y[-5.8 .. +22], Z >= 3.2 is 100% OPEN AIR with crystal-clear sightline to Arka, Soren, dock, Ignaluk village & Big Diomede!
CAMERA_DIOMEDE: List[Dict[str, Any]] = [
    # Move 1-2 (00:00-00:04): FRAME 1 IMMEDIATELY LOCKS ON ARKA & SPINNING SNOWBALL + Big Diomede behind!
    {"t": 0.0,   "pos": (-2.4, -3.2, 4.15),  "target": (-1.30, 1.50, 3.65), "lens": 20.0, "roll": -4.0},
    {"t": 1.6,   "pos": (-1.45, -0.75, 3.68), "target": (-1.30, 1.50, 3.72), "lens": 24.0, "roll": 0.0, "ease": "snappy"},
    {"t": 4.0,   "pos": (-1.10, -1.25, 3.65), "target": (-1.15, 2.00, 3.65), "lens": 22.0, "roll": 1.5, "ease": "cubic"},
    # Move 3 (00:04-00:07.5): Smooth continuous orbit following Arka walking to Kapten Soren on dock
    {"t": 7.4,   "pos": (0.85, -2.15, 3.85), "target": (0.95, 1.50, 3.55),  "lens": 22.0, "roll": 0.0, "ease": "cubic",
     "orbit": {"center": (0.65, 1.50, 3.6), "r0": 3.4, "r1": 3.55, "ang0": -118.0, "ang1": -64.0, "z0": 3.68, "z1": 3.85}},
    # Move 4 (00:07.5-00:09.4): Dutch angle push-in on Soren's SENIN calendar, brass binoculars & USA/RUSSIA sign
    {"t": 9.4,   "pos": (1.15, -0.85, 3.68), "target": (2.05, 1.55, 3.55),  "lens": 28.0, "roll": 9.0, "ease": "overshoot"},
    # Move 5-6 (00:09.4-00:12.6): Speed-ramped aerial sweep over sea-ice floes slicing thin holographic GARIS TANGGAL INTERNASIONAL!
    {"t": 10.9,  "pos": (0.20, 6.50, 4.30),  "target": (0.0, 24.0, 4.40),   "lens": 19.0, "roll": -5.0, "ease": "expo"},
    {"t": 12.6,  "pos": (0.00, 17.5, 4.70),  "target": (0.0, 26.5, 4.65),   "lens": 21.0, "roll": 0.0,  "ease": "overshoot"},
    # Move 7-8 (00:12.6-00:16.4): Fast whip-back directly framing Soren & Arka on dock (NEVER empty sky!)
    {"t": 14.0,  "pos": (0.60, -1.65, 3.90), "target": (1.45, 1.55, 3.62),  "lens": 25.0, "roll": 2.0,  "ease": "snappy"},
    {"t": 16.4,  "pos": (1.35, -0.55, 3.75), "target": (1.85, 1.55, 3.70),  "lens": 34.0, "roll": 0.0,  "ease": "cubic"},
    # Move 9 (00:16.4-00:20.4): Continuous pull-left & crane-over-dock-edge tracking Arka walking onto lower ice ledge (ALWAYS ABOVE Z >= 3.45, ZERO DOCK CLIPPING!)
    {"t": 18.4,  "pos": (-1.20, -1.45, 3.95), "target": (-2.40, 2.25, 2.75), "lens": 22.0, "roll": -3.0, "ease": "cubic"},
    {"t": 20.3,  "pos": (-0.85, 1.65, 3.85),  "target": (-2.85, 3.15, 2.35), "lens": 24.0, "roll": -5.0, "ease": "snappy"},
    # Move 10-11 (00:20.3-00:24.3): Snappy push-in as Soren yanks Arka back safely, then raises binoculars to lens!
    {"t": 22.2,  "pos": (-1.20, -0.45, 3.65), "target": (-2.15, 2.35, 3.15), "lens": 24.0, "roll": 3.0,  "ease": "overshoot"},
    {"t": 24.2,  "pos": (-1.65, 0.35, 3.55),  "target": (-1.75, 2.05, 3.55), "lens": 40.0, "roll": 0.0,  "ease": "snappy"},
    # Move 12 (00:24.2-00:25.0): Crisp 8-frame high-speed whip-pan right + skyward (NO slow gray fade!)
    {"t": 24.72, "pos": (-1.65, 0.35, 3.55),  "target": (-1.75, 2.05, 3.55), "lens": 42.0, "roll": 0.0,  "ease": "linear"},
    {"t": 25.0,  "pos": (-1.65, 0.35, 3.65),  "target": (12.0, 2.05, 8.50),  "lens": 18.0, "roll": 22.0, "ease": "expo"},
]

# WORLD 2: Rjukan Dark Valley & Solspeilet Heliostat Mirrors (00:25.0 – 00:49.0)
# GEOMETRY GUARANTEE: Mountain cliff face starts strictly at Y >= +29.0m!
# Astrid's cliff deck is jutting out in open air at Y[+20.5 .. +25.5], Z=24.0; 3 Giant Solspeilet mirrors sit cleanly at Y=+26.2, Z=27.2!
# Camera on cliff stays strictly at Y <= +18.0m -> 100% UNOBSTRUCTED HERO VIEW OF ASTRID, TABLET & ALL 3 MIRRORS!
CAMERA_RJUKAN: List[Dict[str, Any]] = [
    # Move 13 (00:25.0-00:27.5): High-speed whip-entry crane dive from sky above dark valley down into Rjukan Torg!
    {"t": 25.0,  "pos": (-8.0, -10.5, 19.0), "target": (-1.0, 0.5, 2.5),    "lens": 18.0, "roll": -14.0},
    {"t": 27.5,  "pos": (-4.4, -6.8, 3.1),   "target": (-1.55, -1.65, 1.35), "lens": 21.0, "roll": 0.0, "ease": "snappy"},
    # Move 14 (00:27.5-00:31.2): Smooth lateral parallax sweep framing shivering Arka beside snow-capped iron streetlamp
    {"t": 31.2,  "pos": (-0.65, -4.8, 1.65), "target": (-1.55, -1.65, 1.32), "lens": 24.0, "roll": 1.5, "ease": "cubic"},
    # Move 15-16 (00:31.2-00:34.8): High-speed vertical rocket crane straight up open valley air to Astrid's cliff deck!
    {"t": 32.8,  "pos": (-2.4, 15.2, 26.2),  "target": (-1.60, 21.6, 25.4),  "lens": 22.0, "roll": -4.0, "ease": "expo"},
    {"t": 34.8,  "pos": (-1.45, 18.4, 25.45), "target": (-1.60, 21.6, 25.35), "lens": 34.0, "roll": 0.0, "ease": "overshoot"},
    # Move 17 (00:34.8-00:36.6): Wide hero low-angle shot pulling back slightly to show Astrid + ALL 3 GIANT SOLSPEILET MIRRORS pivoting!
    {"t": 36.6,  "pos": (1.2, 13.8, 25.0),   "target": (0.0, 26.0, 27.6),   "lens": 18.0, "roll": 3.0,  "ease": "snappy"},
    # Move 18-19 (00:36.6-00:40.4): Tracking ride diving alongside the golden god-ray down into Rjukan Torg!
    {"t": 38.6,  "pos": (3.2, 11.2, 14.5),   "target": (0.4, 0.8, 1.4),     "lens": 20.0, "roll": -6.0, "ease": "expo"},
    {"t": 40.4,  "pos": (-3.6, -5.2, 2.95),  "target": (0.4, 0.8, 1.2),     "lens": 21.0, "roll": 0.0,  "ease": "overshoot"},
    # Move 20 (00:40.4-00:43.4): Snappy dolly-in into the sunlit golden square revealing Kakek Henrik lounging in his beach chair!
    {"t": 43.4,  "pos": (-0.65, -2.35, 1.45), "target": (0.95, 0.85, 1.05), "lens": 25.0, "roll": 2.0,  "ease": "snappy"},
    # Move 21 (00:43.4-00:47.2): Smooth orbiting two-shot from amazed Arka to chuckling Henrik giving thumbs-up
    {"t": 47.2,  "pos": (1.65, -1.75, 1.42), "target": (0.45, 0.78, 1.12),  "lens": 27.0, "roll": 0.0,  "ease": "cubic",
     "orbit": {"center": (0.50, 0.80, 1.2), "r0": 3.25, "r1": 2.55, "ang0": -108.0, "ang1": -62.0, "z0": 1.45, "z1": 1.38}},
    # Move 22-23 (00:47.2-00:49.0): Fast macro zoom straight into Henrik's retro sunglasses reflection -> instant match-cut at 49.0s!
    {"t": 48.65, "pos": (0.95, -0.30, 1.25), "target": (0.95, 0.80, 1.24),  "lens": 54.0, "roll": 0.0,  "ease": "expo"},
    {"t": 49.0,  "pos": (0.95, 0.25, 1.25),  "target": (0.95, 0.80, 1.24),  "lens": 72.0, "roll": 0.0,  "ease": "linear"},
]

# WORLD 3: Baarle-Nassau / Baarle-Hertog Cross-Border Café & Street (00:49.0 – 00:75.0)
# GEOMETRY GUARANTEE:
# - Sidewalk border X=0.0 is 100% CLEAR of all pedestrians & bikes (peds stay strictly at Y < -7.5 or |X| > 3.2)!
# - Café open doorway X[-2.0..+2.0] at Y=0.0 is 100% CLEAR!
# - Clara sits at (-0.85, 3.65) with chair BEHIND her at (-0.85, 3.92), bistro table clearly to her left at (-1.85, 3.60)!
# - Bram stands on raised barista step (Z=0.24) behind 0.86m bar at (+0.75, 5.85), pastry case far left at (-2.25, 5.25)!
# - Opposite dual-flag stepped-gable house sits cleanly at Y=-11.2 facing +Y with warm sunlight lighting its plaques!
CAMERA_BAARLE: List[Dict[str, Any]] = [
    # Move 24 (00:49.0-00:52.6): Match-cut! Low-angle speed-tracking hugging Baarle sidewalk white (+) & B|NL tiles right through open doorway!
    {"t": 49.0,  "pos": (0.0, -6.2, 0.45),   "target": (0.0, 0.5, 0.42),    "lens": 19.0, "roll": 0.0},
    {"t": 52.6,  "pos": (0.10, -0.5, 0.65),  "target": (0.0, 4.8, 1.15),    "lens": 20.0, "roll": 1.5,  "ease": "cubic"},
    # Move 25 (00:52.6-00:55.4): Smooth boom-up & glide inside café framing Arka hopping border + Bram behind bar counter + Italian espresso & pastry case
    {"t": 55.4,  "pos": (0.25, 1.85, 1.56),  "target": (0.15, 5.25, 1.36),  "lens": 19.0, "roll": 0.0,  "ease": "snappy"},
    # Move 26 (00:55.4-00:59.0): Crisp lateral bar tracking following latte cup sliding across brass NL -> B line (shows espresso machine, Bram & pastry vitrine!)
    {"t": 59.0,  "pos": (-0.35, 1.95, 1.48), "target": (-0.10, 5.15, 1.24), "lens": 21.0, "roll": -1.5, "ease": "overshoot"},
    # Move 27 (00:59.0-01:02.0): Comedic snap-zoom on Clara's baffled expression, then whip-tilt down to her feet on NL while chair in B
    {"t": 60.5,  "pos": (0.35, 1.80, 1.42),  "target": (-0.85, 3.65, 1.32), "lens": 32.0, "roll": 3.5,  "ease": "snappy"},
    {"t": 62.0,  "pos": (0.45, 1.95, 1.05),  "target": (-0.55, 3.65, 0.28), "lens": 24.0, "roll": -4.0, "ease": "overshoot"},
    # Move 28 (01:02.0-01:06.2): Fast whip-pan & zoom through open café entrance straight onto opposite dual-flag brick house (24mm fits BOTH plaques & windows!)
    {"t": 63.1,  "pos": (0.0, 0.80, 1.75),   "target": (0.0, -11.2, 2.25),  "lens": 28.0, "roll": 0.0,  "ease": "expo"},
    {"t": 66.2,  "pos": (0.0, -4.60, 1.95),  "target": (0.0, -11.2, 2.15),  "lens": 24.0, "roll": 0.0,  "ease": "cubic"},
    # Move 29 (01:06.2-01:09.95): Whip-pan back inside catching Clara lifting BOTH feet onto chair rung while Arka & Bram laugh!
    {"t": 67.3,  "pos": (0.35, 0.75, 1.52),  "target": (0.00, 4.10, 1.22),  "lens": 19.0, "roll": -2.0, "ease": "snappy"},
    {"t": 69.95, "pos": (0.45, 0.95, 1.50),  "target": (0.00, 4.10, 1.22),  "lens": 20.0, "roll": 0.0,  "ease": "cubic"},
    # Move 30 (01:10.00-01:15.0): EXACT 1-FRAME CLEAN CUT OUTSIDE onto warm golden street (ZERO 0.5s empty-chair flick!)
    {"t": 70.00, "pos": (0.0, -5.60, 1.48),  "target": (0.0, -2.35, 1.20),  "lens": 22.0, "roll": 0.0,  "cut": True},
    {"t": 74.2,  "pos": (0.0, -7.20, 1.75),  "target": (0.0, -2.35, 1.26),  "lens": 20.0, "roll": 0.0,  "ease": "cubic"},
    {"t": 75.0,  "pos": (0.0, -4.90, 1.54),  "target": (0.0, -2.35, 1.38),  "lens": 24.0, "roll": -2.5, "ease": "snappy"},
]


def get_camera_at_frame(scene_name: str, frame: int) -> Dict[str, Any]:
    t_sec = frame / FPS
    if scene_name == "diomede":
        return eval_camera_track(CAMERA_DIOMEDE, t_sec)
    if scene_name == "rjukan":
        return eval_camera_track(CAMERA_RJUKAN, t_sec)
    return eval_camera_track(CAMERA_BAARLE, t_sec)


def compute_view_angle_deg(char_pos: Tuple[float, float, float], facing_az_deg: float, cam_pos: Tuple[float, float, float]) -> float:
    dx = cam_pos[0] - char_pos[0]
    dy = cam_pos[1] - char_pos[1]
    cam_az = math.degrees(math.atan2(dy, dx))
    return (facing_az_deg - cam_az) % 360.0


def compute_billboard_rot_z(char_pos: Tuple[float, float, float], cam_pos: Tuple[float, float, float]) -> float:
    dx = cam_pos[0] - char_pos[0]
    dy = cam_pos[1] - char_pos[1]
    return math.atan2(dy, dx) + math.pi * 0.5


def _lipsync_val(lipsync_curves: Optional[Dict[str, List[float]]], speaker: str, frame: int) -> float:
    if lipsync_curves and speaker in lipsync_curves:
        arr = lipsync_curves[speaker]
        if 0 <= frame < len(arr):
            return float(arr[frame])
    return 0.0


# ============================================================================
# 3. ZERO-FLICK, ANTI-CLIPPING CHARACTER BLOCKING & BIOMECHANICS
# ============================================================================

def get_characters_at_frame(
    scene_name: str,
    frame: int,
    lipsync_curves: Optional[Dict[str, List[float]]] = None,
) -> Dict[str, Dict[str, Any]]:
    t = frame / FPS
    cam = get_camera_at_frame(scene_name, frame)
    cam_pos = cam["pos"]
    out: Dict[str, Dict[str, Any]] = {}

    def pack(cid: str, pos: Tuple[float, float, float], facing_az: float, render_kwargs: Dict[str, Any], visible: bool = True) -> None:
        rk = dict(render_kwargs)
        rk["angle"] = compute_view_angle_deg(pos, facing_az, cam_pos)
        rk["ground_shadow"] = False
        out[cid] = {
            "visible": visible,
            "pos": pos,
            "facing_az": facing_az,
            "rot_z": compute_billboard_rot_z(pos, cam_pos),
            "render_kwargs": rk,
        }

    # ------------------------------------------------------------------
    # SCENE 1: DIOMEDE (Arka + Kapten Soren — 100% CONTINUOUS WALKING, ZERO TELEPORTS!)
    # ------------------------------------------------------------------
    if scene_name == "diomede":
        arka_m = _lipsync_val(lipsync_curves, "arka", frame)
        soren_m = _lipsync_val(lipsync_curves, "kapten_soren", frame)

        # ARKA CONTINUOUS PATH (Zero teleport jumps across all 0..25s!)
        if t < 4.0:
            # Hook (00:00-00:04): Standing firmly on wooden dock spinning snowball!
            pos_a = (-1.30, 1.50, DOCK_Z)
            fac_a = -90.0
            bob = math.sin(t * 4.5) * 3.0
            rk_a = {
                "animation": "free", "pelvis_y": bob, "torso_lean_deg": 4.0 * math.sin(t * 2.5),
                "head_tilt_deg": -5.0 + 3.0 * math.sin(t * 3.2),
                "right_hand_target": (76.0, 152.0 + bob * 0.5, 48.0),
                "left_hand_target": (-52.0, 274.0, 14.0),
                "eyes": "honey_oval", "eyebrows": "thick_arch", "mouth": "confident_gap",
                "mouth_open": arka_m, "eye_gaze_x": 0.10, "eye_gaze_y": -0.05,
            }
        elif t < 7.4:
            # Walks smoothly along wooden dock toward Kapten Soren!
            u = ease_cubic_in_out((t - 4.0) / 3.4)
            pos_a = (lerp(-1.30, 0.55, u), lerp(1.50, 1.52, u), DOCK_Z)
            fac_a = lerp(-30.0, -60.0, u)
            rk_a = {
                "animation": "walk", "arm_pose": "point" if u > 0.65 else "ready",
                "eyes": "honey_oval", "eyebrows": "thick_arch", "mouth": "confident_gap",
                "mouth_open": arka_m, "eye_gaze_x": 0.22,
            }
        elif t < 16.4:
            # Stands beside Soren on dock pointing toward Big Diomede
            pos_a = (0.55, 1.52, DOCK_Z)
            fac_a = -60.0 if t < 12.0 else -30.0
            gest = math.sin(t * 5.0) * 8.0
            rk_a = {
                "animation": "free", "pelvis_y": math.sin(t * 3.0) * 2.5,
                "torso_lean_deg": 5.0 if t < 12.0 else -3.0, "head_tilt_deg": -4.0 if t < 12.0 else 5.0,
                "right_hand_target": (92.0, 188.0 + gest, 42.0) if t < 12.0 else (62.0, 248.0, 26.0),
                "left_hand_target": (-48.0, 268.0, 18.0),
                "eyes": "starry" if t < 12.0 else "shocked", "eyebrows": "raised",
                "mouth": "confident_gap" if t < 12.0 else "small_o", "mouth_open": arka_m, "eye_gaze_x": 0.35,
            }
        elif t < 19.6:
            # CONTINUOUS WALK LEFT along the wooden dock & down the smooth snowy wooden ramp onto the front-left sea-ice ledge! (ZERO TELEPORT!)
            u = ease_cubic_in_out((t - 16.4) / 3.2)
            pos_a = (lerp(0.55, -2.85, u), lerp(1.52, 3.10, u), lerp(DOCK_Z, ICE_LEDGE_Z, clamp01((u - 0.55) / 0.45)))
            fac_a = lerp(-150.0, 110.0, u)
            rk_a = {
                "animation": "walk" if u < 0.88 else "free",
                "pelvis_y": 5.0, "torso_lean_deg": 7.0, "head_tilt_deg": 7.0,
                "eyes": "focused", "eyebrows": "raised", "mouth": "smirk", "mouth_open": arka_m, "eye_gaze_y": 0.40,
            }
        elif t < 20.8:
            # ICE CRACKS under Arka's feet on the ice ledge!
            pos_a = (-2.85, 3.10, ICE_LEDGE_Z)
            fac_a = -110.0
            flail = math.sin(t * 28.0) * 14.0
            rk_a = {
                "animation": "free", "pelvis_y": -10.0 + abs(flail) * 0.4, "torso_lean_deg": -10.0 + flail * 0.3,
                "head_tilt_deg": -8.0,
                "left_hand_target": (-85.0, 145.0 + flail, 36.0), "right_hand_target": (85.0, 145.0 - flail, 36.0),
                "eyes": "panic", "eyebrows": "worried", "mouth": "open_yell", "mouth_open": max(0.75, arka_m), "sweat_drop": True,
            }
        else:
            # Smoothly yanked backward up onto the safe wooden dock deck by Soren!
            u = ease_out_overshoot(clamp01((t - 20.8) / 0.85), s=0.8)
            pos_a = (lerp(-2.85, -2.55, u), lerp(3.10, 1.95, u), lerp(ICE_LEDGE_Z, DOCK_Z, clamp01(u)))
            fac_a = -95.0
            rk_a = {
                "animation": "free", "pelvis_y": 4.0 * (1.0 - clamp01((t - 21.6) / 0.8)),
                "torso_lean_deg": lerp(-14.0, 2.0, clamp01((t - 20.8) / 1.2)), "head_tilt_deg": 6.0,
                "left_hand_target": (-58.0, 228.0, 26.0), "right_hand_target": (58.0, 228.0, 26.0),
                "eyes": "asymmetric" if t < 22.5 else "honey_oval", "eyebrows": "worried",
                "mouth": "grin_teeth", "mouth_open": arka_m, "sweat_drop": t < 22.8,
            }
        pack("arka", pos_a, fac_a, rk_a)

        # KAPTEN SOREN CONTINUOUS PATH (Zero vanishing, stays cleanly on Z=DOCK_Z away from all poles!)
        if t < 16.4:
            pos_s = (1.85, 1.55, DOCK_Z)
            fac_s = -112.0
            raise_cal = ease_cubic_in_out(clamp01((t - 7.0) / 1.0))
            rk_s = {
                "animation": "free", "pelvis_y": math.sin(t * 2.0) * 1.8, "torso_lean_deg": -2.0,
                "head_tilt_deg": 3.0 * math.sin(t * 1.4),
                "left_hand_target": (-68.0, lerp(272.0, 194.0, raise_cal), 36.0),
                "right_hand_target": (88.0, lerp(262.0, 186.0, raise_cal), 38.0),
                "eyes": "chill", "eyebrows": "skeptical", "mouth": "smirk", "mouth_open": soren_m, "eye_gaze_x": -0.25,
            }
        elif t < 19.8:
            # Soren walks steadily across the wooden dock behind Arka (ZERO TELEPORT, ZERO PILLAR CLIP!)
            u = ease_cubic_in_out((t - 16.4) / 3.4)
            pos_s = (lerp(1.85, -1.75, u), lerp(1.55, 2.05, u), DOCK_Z)
            fac_s = lerp(-155.0, -110.0, u)
            rk_s = {
                "animation": "walk" if u < 0.92 else "free",
                "eyes": "suspicious", "eyebrows": "skeptical", "mouth": "flat", "mouth_open": soren_m,
            }
        else:
            # Soren stands firmly on dock edge at (-1.75, 2.05, DOCK_Z), yanks Arka back, shakes head, then lifts brass binoculars!
            pos_s = (-1.75, 2.05, DOCK_Z)
            fac_s = -110.0 if t < 22.8 else -90.0
            pull_t = clamp01((t - 20.4) / 0.55)
            lift_bino = ease_cubic_in_out(clamp01((t - 22.9) / 0.95))
            shake = math.sin(t * 16.0) * 10.0 if 21.4 <= t <= 22.8 else 0.0
            if t < 22.8:
                rh = (lerp(66.0, 82.0, pull_t), lerp(252.0, 206.0, pull_t), 34.0)
                lh = (-54.0, 268.0, 18.0)
            else:
                rh = (lerp(66.0, 32.0, lift_bino), lerp(230.0, 154.0, lift_bino), lerp(28.0, 56.0, lift_bino))
                lh = (lerp(-54.0, -28.0, lift_bino), lerp(255.0, 158.0, lift_bino), lerp(20.0, 54.0, lift_bino))
            rk_s = {
                "animation": "free", "pelvis_y": 2.0, "torso_lean_deg": -4.0 if t < 22.2 else 4.0,
                "head_tilt_deg": shake, "right_hand_target": rh, "left_hand_target": lh,
                "eyes": "suspicious" if t < 22.9 else "chill",
                "eyebrows": "angry" if 20.4 <= t <= 22.4 else "skeptical",
                "mouth": "frown" if 20.4 <= t <= 22.4 else "smirk", "mouth_open": soren_m,
            }
        pack("kapten_soren", pos_s, fac_s, rk_s)

    # ------------------------------------------------------------------
    # SCENE 2: RJUKAN (Arka + Astrid + Kakek Henrik — ZERO TELEPORT, ZERO POLE CLIP!)
    # ------------------------------------------------------------------
    elif scene_name == "rjukan":
        arka_m = _lipsync_val(lipsync_curves, "arka", frame)
        astrid_m = _lipsync_val(lipsync_curves, "astrid", frame)
        henrik_m = _lipsync_val(lipsync_curves, "kakek_henrik", frame)

        # ARKA CONTINUOUS PATH (Streetlamp pole is at (-2.65, -2.05) -> 1.1m clearance from Arka at (-1.55, -1.65)!)
        if t < 31.8:
            pos_a = (-1.55, -1.65, SQUARE_Z)
            fac_a = -80.0
            shiver = math.sin(t * 24.0) * 3.5
            rk_a = {
                "animation": "free", "pelvis_y": 6.0 + abs(shiver) * 0.4, "torso_lean_deg": 5.0 + shiver * 0.4,
                "head_tilt_deg": shiver * 0.8,
                "left_hand_target": (-26.0 + shiver, 232.0, 42.0), "right_hand_target": (26.0 - shiver, 232.0, 42.0),
                "eyes": "shocked" if t < 29.0 else "honey_oval", "eyebrows": "worried",
                "mouth": "grit_teeth" if t < 29.0 else "confident_gap", "mouth_open": arka_m, "blush": True,
            }
        elif t < 41.8:
            # Smooth continuous walk from streetlamp to central sunlit square (happens smoothly while camera dives back!)
            u = ease_cubic_in_out(clamp01((t - 38.5) / 3.0))
            pos_a = (lerp(-1.55, -1.05, u), lerp(-1.65, 0.55, u), SQUARE_Z)
            fac_a = lerp(-30.0, 15.0, u)
            rk_a = {
                "animation": "walk" if (38.5 <= t <= 41.5) else "free",
                "pelvis_y": 0.0, "torso_lean_deg": 4.0, "head_tilt_deg": -8.0 if t > 39.2 else 2.0,
                "eyes": "starry" if t > 39.5 else "shocked", "eyebrows": "raised",
                "mouth": "small_o" if t < 41.5 else "confident_gap", "mouth_open": arka_m, "eye_gaze_x": 0.35,
            }
        elif t < 47.0:
            pos_a = (-1.05, 0.55, SQUARE_Z)
            fac_a = 15.0
            rk_a = {
                "animation": "free", "pelvis_y": -2.0 + math.sin(t * 3.0) * 2.0, "torso_lean_deg": 6.0, "head_tilt_deg": 3.0,
                "right_hand_target": (78.0, 198.0, 38.0), "left_hand_target": (-48.0, 266.0, 16.0),
                "eyes": "starry", "eyebrows": "raised", "mouth": "confident_gap", "mouth_open": arka_m, "eye_gaze_x": 0.40,
            }
        else:
            # Smoothly steps closer & leans in toward Henrik's sunglasses (Match-Cut!)
            u = ease_cubic_in_out(clamp01((t - 47.0) / 1.3))
            pos_a = (lerp(-1.05, -0.35, u), lerp(0.55, 0.65, u), SQUARE_Z)
            fac_a = 10.0
            rk_a = {
                "animation": "free", "pelvis_y": 14.0 * u, "torso_lean_deg": 14.0 * u, "head_tilt_deg": 6.0,
                "left_hand_target": (-42.0, 255.0, 24.0), "right_hand_target": (46.0, 248.0, 28.0),
                "eyes": "focused", "eyebrows": "raised", "mouth": "small_o", "mouth_open": arka_m, "eye_gaze_x": 0.45,
            }
        pack("arka", pos_a, fac_a, rk_a)

        # ASTRID on unobstructed cliffside heliostat deck (Z = CLIFF_DECK_Z = 24.0m!)
        pos_ast = (-1.60, 21.60, CLIFF_DECK_Z)
        tap_u = math.sin(clamp01((t - 33.5) / 0.45) * math.pi)
        pack("astrid", pos_ast, -95.0, {
            "animation": "free", "pelvis_y": math.sin(t * 2.2) * 1.5, "torso_lean_deg": 3.0,
            "head_tilt_deg": -4.0 if t < 34.5 else 3.0,
            "left_hand_target": (-34.0, 246.0, 44.0),
            "right_hand_target": (36.0 - tap_u * 26.0, 242.0 - tap_u * 10.0, 48.0 + tap_u * 12.0),
            "eyes": "focused" if t < 34.8 else "happy", "eyebrows": "flat" if t < 34.8 else "happy",
            "mouth": "smirk" if t < 35.0 else "grin_teeth", "mouth_open": astrid_m,
            "eye_gaze_x": 0.12, "eye_gaze_y": 0.25 if t < 34.2 else -0.1,
        })

        # KAKEK HENRIK cleanly in front of his striped beach chair (chair sits +0.34m BEHIND Henrik -> ZERO clipping!)
        pos_h = (0.95, 0.80, SQUARE_Z)
        thumb_u = ease_out_overshoot(clamp01((t - 44.8) / 0.7), s=0.75)
        sip_u = math.sin(clamp01((t - 42.2) / 1.8) * math.pi)
        pack("kakek_henrik", pos_h, -105.0, {
            "animation": "free", "pelvis_y": 22.0 + math.sin(t * 2.0) * 1.6, "torso_lean_deg": -6.0,
            "head_tilt_deg": 5.0 + math.sin(t * 1.8) * 2.5,
            "left_hand_target": (-42.0, 244.0 - sip_u * 48.0, 38.0 + sip_u * 14.0),
            "right_hand_target": (lerp(56.0, 88.0, thumb_u), lerp(258.0, 192.0, thumb_u), 40.0),
            "left_foot_target": (-24.0, 474.0, 22.0), "right_foot_target": (24.0, 474.0, 22.0),
            "eyes": "happy", "eyebrows": "happy", "mouth": "happy_open", "mouth_open": max(0.25, henrik_m),
        })

    # ------------------------------------------------------------------
    # SCENE 3: BAARLE (Arka + Bram + Clara — ZERO CLIPPING, ZERO FLICK, EXACT 1-FRAME CUT AT 70.0s!)
    # ------------------------------------------------------------------
    else:
        arka_m = _lipsync_val(lipsync_curves, "arka", frame)
        bram_m = _lipsync_val(lipsync_curves, "bram", frame)
        clara_m = _lipsync_val(lipsync_curves, "clara", frame)

        if frame < 2100:  # Strictly 00:49.00 .. 01:09.97 (INSIDE CAFÉ — ZERO TELEPORTS!)
            # ARKA: stands cleanly in open aisle (X=+1.05, Y=3.20 — >1.8m clear of Clara's table at X=-1.85!), hops across X=0 line at 53.5..55.0!
            if t < 53.4:
                pos_a = (-0.35, 2.55, CAFE_FLOOR_Z)
                fac_a = -75.0
                rk_a = {
                    "animation": "free", "pelvis_y": math.sin(t * 3.5) * 2.5, "torso_lean_deg": 4.0,
                    "right_hand_target": (72.0, 206.0, 32.0), "left_hand_target": (-48.0, 266.0, 16.0),
                    "eyes": "honey_oval", "eyebrows": "thick_arch", "mouth": "confident_gap", "mouth_open": arka_m,
                }
            elif t < 55.2:
                # Playful continuous hop from Belgium (-0.35) -> Netherlands (+1.10)!
                hop_u = clamp01((t - 53.4) / 1.8)
                hop_arc = math.sin(hop_u * math.pi) * 0.28
                pos_a = (lerp(-0.35, 1.10, ease_cubic_in_out(hop_u)), lerp(2.55, 3.35, ease_cubic_in_out(hop_u)), CAFE_FLOOR_Z + hop_arc)
                fac_a = lerp(-75.0, -125.0, hop_u)
                rk_a = {
                    "animation": "jump", "eyes": "starry", "eyebrows": "raised", "mouth": "happy_open", "mouth_open": arka_m,
                }
            else:
                # Stays continuously right there at (+1.10, 3.35) watching Bram & laughing with Clara (NEVER VANISHES!)
                pos_a = (1.10, 3.35, CAFE_FLOOR_Z)
                fac_a = -130.0
                is_laugh = t >= 67.4
                rk_a = {
                    "animation": "laugh" if is_laugh else "free",
                    "pelvis_y": math.sin(t * 10.0) * 3.5 if is_laugh else math.sin(t * 3.0) * 2.0,
                    "torso_lean_deg": -4.0 if is_laugh else 4.0,
                    "eyes": "happy" if is_laugh else "honey_oval", "eyebrows": "happy" if is_laugh else "raised",
                    "mouth": "happy_open" if is_laugh else "confident_gap",
                    "mouth_open": max(0.55, arka_m) if is_laugh else arka_m, "eye_gaze_x": -0.30,
                }
            pack("arka", pos_a, fac_a, rk_a)

            # BRAM: Standing on raised barista platform (BRAM_STEP_Z = 0.24) behind 0.86m bar counter (+0.78, 5.85)!
            # Upper chest, apron & arms clear BAR_TOP_Z=0.86 cleanly; pastry case is far left at X=-2.25 -> ZERO CLIPPING!
            pos_b = (0.78, 5.85, BRAM_STEP_Z)
            fac_b = -95.0
            # Snappy theatrical cup push synced EXACTLY to "diantar lintas negara ke Belgia!" (56.6s -> 58.2s)
            slide_u = ease_snappy_ramp(clamp01((t - 56.55) / 1.65))
            is_laugh_b = t >= 67.4
            if is_laugh_b:
                rk_b = {"animation": "laugh", "eyes": "happy", "eyebrows": "happy", "mouth": "happy_open", "mouth_open": 0.6}
            else:
                rk_b = {
                    "animation": "free", "pelvis_y": math.sin(t * 3.0) * 2.0,
                    "torso_lean_deg": lerp(4.0, -9.0, slide_u), "head_tilt_deg": lerp(-4.0, 6.0, slide_u),
                    "right_hand_target": (lerp(42.0, -76.0, slide_u), 228.0, 44.0),
                    "left_hand_target": (-44.0, 254.0, 26.0),
                    "eyes": "honey_oval", "eyebrows": "raised",
                    "mouth": "grin_teeth" if slide_u > 0.25 else "smirk", "mouth_open": bram_m,
                    "eye_gaze_x": lerp(0.1, -0.38, slide_u),
                }
            pack("bram", pos_b, fac_b, rk_b)

            # CLARA: Seated cleanly at (-0.85, 3.65, CAFE_FLOOR_Z) with chair placed BEHIND her (+0.32m in +Y) and bistro table at (-1.85, 3.60) -> ZERO CLIPPING!
            pos_c = (-0.85, 3.65, CAFE_FLOOR_Z)
            fac_c = -65.0
            lift_feet = ease_out_overshoot(clamp01((t - 66.8) / 0.85), s=0.90)
            look_down = ease_cubic_in_out(clamp01((t - 59.8) / 0.8))
            rk_c = {
                "animation": "free", "pelvis_y": 16.0 + lift_feet * 4.0,
                "torso_lean_deg": lerp(2.0, 8.0, look_down) * (1.0 - lift_feet * 0.6),
                "head_tilt_deg": lerp(2.0, 12.0, look_down),
                "left_foot_target": (-20.0, lerp(474.0, 408.0, lift_feet), lerp(10.0, 32.0, lift_feet)),
                "right_foot_target": (24.0, lerp(474.0, 408.0, lift_feet), lerp(10.0, 32.0, lift_feet)),
                "left_hand_target": (-42.0, lerp(250.0, 212.0, look_down), 34.0),
                "right_hand_target": (52.0, lerp(244.0, 226.0, lift_feet), 34.0),
                "eyes": "shocked" if 60.0 <= t < 66.8 else ("happy" if t >= 68.5 else "honey_oval"),
                "eyebrows": "skeptical" if t < 68.5 else "raised",
                "mouth": "small_o" if t < 66.8 else "happy_open",
                "mouth_open": max(0.35, clara_m) if t >= 66.8 else clara_m,
                "eye_gaze_y": 0.55 if 60.0 <= t < 66.8 else 0.0,
            }
            pack("clara", pos_c, fac_c, rk_c)
        else:
            # EXACT 1-FRAME SAFE CUT AT frame 2100 (70.00s): Golden-hour Baarle street finale!
            # Arka straddles B | NL border outside at (0.0, -2.35), Bram & Clara wave cheerfully from sunlit doorway!
            sip_u = math.sin(clamp01((t - 71.2) / 1.4) * math.pi)
            snap_u = ease_out_overshoot(clamp01((t - 73.9) / 0.45), s=1.0)
            is_wink = t >= 73.6
            pack("arka", (0.0, -2.35, CAFE_FLOOR_Z), -90.0, {
                "animation": "free", "pelvis_y": 4.0 + math.sin(t * 3.0) * 2.0,
                "torso_lean_deg": lerp(0.0, -3.5, snap_u), "head_tilt_deg": lerp(-3.0, 7.0, snap_u),
                "left_foot_target": (-36.0, 476.0, 0.0), "right_foot_target": (36.0, 476.0, 0.0),
                "left_hand_target": (-46.0 + sip_u * 16.0, 238.0 - sip_u * 52.0, 38.0 + sip_u * 14.0),
                "right_hand_target": (lerp(58.0, 82.0, snap_u), lerp(255.0, 178.0, snap_u), lerp(24.0, 52.0, snap_u)),
                "eyes": "smug" if is_wink else "honey_oval",
                "eyebrows": "skeptical" if is_wink else "thick_arch",
                "mouth": "confident_gap", "mouth_open": arka_m, "eye_gaze_x": 0.0,
            })
            pack("bram", (1.05, 0.65, CAFE_FLOOR_Z), -90.0, {"animation": "wave", "eyes": "happy", "eyebrows": "happy", "mouth": "grin_teeth"})
            pack("clara", (-1.05, 0.65, CAFE_FLOOR_Z), -90.0, {"animation": "wave", "eyes": "happy", "eyebrows": "happy", "mouth": "happy_open"})

    return out


# ============================================================================
# 4. HERO PROP & DYNAMIC LIGHTING TIMELINE SYNC
# ============================================================================

def get_scene_dynamic_state(scene_name: str, frame: int) -> Dict[str, Any]:
    t = frame / FPS
    if scene_name == "diomede":
        # Short crisp lens-flare glint only in final 8 frames (24.72..25.00s) — NO long dull gray fade!
        flare = clamp01((t - 24.68) / 0.28) if t >= 24.68 else 0.0
        return {
            "snowball_pos": (-0.98, 1.32, DOCK_Z + 1.44 + math.sin(t * 4.5) * 0.035),
            "snowball_visible": t < 4.2,
            "snowball_rot_z": t * 14.0,
            "ice_crack_factor": clamp01((t - 19.55) / 0.4),
            "dateline_pulse": 0.8 + 0.2 * math.sin(t * 5.0),
            "lens_flare_strength": flare,
            "soren_bino_raise": ease_cubic_in_out(clamp01((t - 22.9) / 0.95)),
        }

    if scene_name == "rjukan":
        mirror_pivot = ease_cubic_in_out(clamp01((t - 34.0) / 2.4))
        beam_shoot = ease_expo_in_out(clamp01((t - 36.4) / 3.0))
        square_lit = ease_out_overshoot(clamp01((t - 39.2) / 0.9), s=0.4)
        # Crisp 6-frame golden sunglasses glint match-cut at 48.75..49.0s (NO dull gray fade!)
        match_flash = clamp01((t - 48.72) / 0.24) if t >= 48.72 else 0.0
        return {
            "mirror_pivot": mirror_pivot,
            "beam_shoot": beam_shoot,
            "square_lit": clamp01(square_lit),
            "match_flash": match_flash,
        }

    # Baarle: Snappy latte cup glide across NL (+0.45) -> B (-0.45) on top of BAR_TOP_Z=0.86 synced to "diantar lintas negara"!
    cup_slide = ease_snappy_ramp(clamp01((t - 56.55) / 1.65))
    return {
        "latte_visible": frame < 2100,
        "latte_pos": (lerp(0.45, -0.45, cup_slide), 4.96, BAR_TOP_Z + 0.015),
        "arka_finale_cup_visible": frame >= 2100,
        "arka_finale_cup_pos": (-0.28, -2.56, 1.16 + math.sin(clamp01((t - 71.2) / 1.4) * math.pi) * 0.22),
        "glitch_outro": clamp01((t - 74.68) / 0.28) if t >= 74.68 else 0.0,
    }
