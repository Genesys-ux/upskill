"""Master 75-second 3D Continuous Camera Choreography, Natural Biomechanical Walk, Barista Cup Contact & Speaker Emphasis Zooms (v3)."""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

FPS = 30.0

# ============================================================================
# GLOBAL FLOOR & SURFACE ELEVATION CONSTANTS (ANTI-CLIPPING SINGLE SOURCE OF TRUTH)
# ============================================================================
DOCK_Z = 2.40        # World 1: Little Diomede wooden pier deck top
ICE_LEDGE_Z = 1.65   # World 1: Lower dock sea-ice ledge (connected by wide wooden ramp)
CLIFF_DECK_Z = 24.0  # World 2: Rjukan Solspeilet open-air steel cliff platform
SQUARE_Z = 0.0       # World 2: Rjukan Torg cobblestone plaza & plowed street
CAFE_FLOOR_Z = 0.0   # World 3: Baarle clinker street & Café de Grens floor
BAR_TOP_Z = 0.92     # World 3: Oak bar counter top (hits Bram cleanly at y=316px lower apron!)
BRAM_STEP_Z = 0.31   # World 3: Raised oak barista duckboard behind bar -> legs 100% hidden (<0.85m), apron/arms/hand 100% clear & touching cup!

# Exact 1-frame camera cuts (where blocking changes are permitted simultaneously on the exact cut frame)
CAMERA_CUT_FRAMES = {
    750,   # 25.0s: Diomede -> Rjukan whip-pan exit
    1470,  # 49.0s: Rjukan sunglasses match-cut -> Baarle sidewalk (+)
    2100,  # 70.0s: Café interior -> Golden-hour Baarle street finale
}


# ============================================================================
# 1. ORGANIC MOTION CURVES & NATURAL STRIDE-SYNCED WALK BIOMECHANICS
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


def ease_cubic_in_out_deriv(t: float) -> float:
    t = clamp01(t)
    return 12.0 * t * t if t < 0.5 else 12.0 * ((1.0 - t) ** 2)


def ease_out_cubic(t: float) -> float:
    t = clamp01(t)
    return 1.0 - ((1.0 - t) ** 3)


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


def lerp_angle_deg(a0: float, a1: float, t: float) -> float:
    diff = ((a1 - a0 + 180.0) % 360.0) - 180.0
    return a0 + diff * t


def compute_natural_walk_rig(
    dist_traveled_m: float,
    speed_mps: float,
    stride_len_m: float = 0.58,
    arm_energy: float = 1.0,
) -> Dict[str, Any]:
    """
    True distance-locked biomechanical walk cycle using Free-Rig 2-Bone IK!
    - Foot phase phi is mathematically locked to world distance traveled -> ZERO foot sliding or dragging!
    - Includes heel-toe swing arc, pelvis weight bounce, forward momentum lean, squash-stretch, and head follow-through!
    """
    amp = clamp01(speed_mps / 0.50)
    phi = (dist_traveled_m / max(0.25, stride_len_m)) * math.pi

    # Real gait contact/passing dynamics: pelvis drops on foot strike, rises on mid-stance passing!
    stride_lift_wave = abs(math.sin(phi))
    pelvis_y = (4.5 - stride_lift_wave * 11.5) * amp
    head_bob_y = pelvis_y + math.sin(phi * 2.0 - 0.45) * 2.4 * amp
    torso_lean = (8.5 + math.sin(phi) * 2.5) * amp
    head_tilt = (-2.0 - math.sin(phi - 0.35) * 3.8) * amp
    squash_y = 1.0 + (stride_lift_wave - 0.45) * 0.045 * amp
    squash_x = 1.0 / squash_y

    # Opposite leg swing with generous stride depth (Z) + energetic arc lift (Y), strictly kissed to ground y=464!
    stride_px = 46.0 * amp
    lift_px = 42.0 * amp
    l_swing = max(0.0, math.sin(phi))
    r_swing = max(0.0, math.sin(phi + math.pi))
    l_z = -math.cos(phi) * stride_px
    r_z = -math.cos(phi + math.pi) * stride_px
    l_y = 464.0 - (l_swing ** 0.85) * lift_px
    r_y = 464.0 - (r_swing ** 0.85) * lift_px

    # Energetic visible counter-swinging arms (opposite phase to legs!) with clear silhouette in profile!
    l_arm = math.cos(phi) * amp * arm_energy
    r_arm = -math.cos(phi) * amp * arm_energy
    lh = (-52.0, 272.0 + pelvis_y - max(0.0, l_arm) * 44.0, l_arm * 92.0 + 8.0)
    rh = (56.0, 272.0 + pelvis_y - max(0.0, r_arm) * 44.0, r_arm * 92.0 + 8.0)

    return {
        "animation": "free",
        "pelvis_y": pelvis_y,
        "head_bob_y": head_bob_y,
        "torso_lean_deg": torso_lean,
        "head_tilt_deg": head_tilt,
        "hat_tilt_extra": math.sin(phi - 0.5) * 3.2 * amp,
        "squash_x": squash_x,
        "squash_y": squash_y,
        "left_foot_target": (-18.0, l_y, l_z),
        "right_foot_target": (22.0, r_y, r_z),
        "left_hand_target": lh,
        "right_hand_target": rh,
    }


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
            breath_x = math.sin(t_sec * 1.9) * 0.010
            breath_z = math.cos(t_sec * 2.4) * 0.008
            return {
                "pos": (pos[0] + breath_x, pos[1], pos[2] + breath_z),
                "target": target,
                "lens": max(16.0, min(85.0, lens)),
                "roll": roll,
            }
    k = keyframes[-1]
    return {"pos": k["pos"], "target": k["target"], "lens": k["lens"], "roll": k.get("roll", 0.0)}


# ============================================================================
# 2. 34+ DYNAMIC CONTINUOUS CAMERA MOVES WITH SPEAKER EMPHASIS ZOOM TRANSITIONS!
# ============================================================================

# WORLD 1: Little Diomede Pier, Ignaluk Village & Bering Strait (00:00.0 – 00:25.0)
CAMERA_DIOMEDE: List[Dict[str, Any]] = [
    # L01 Arka Hook (00:00-00:04.2): Immediate Wide Hook -> Punchy Zoom-In Push onto Arka & snowball!
    {"t": 0.0,   "pos": (-2.40, -3.15, 4.15), "target": (-1.30, 1.50, 3.62), "lens": 19.0, "roll": -4.0},
    {"t": 1.35,  "pos": (-1.40, -0.75, 3.68), "target": (-1.22, 1.50, 3.72), "lens": 29.0, "roll": 0.5,  "ease": "snappy"},
    {"t": 3.20,  "pos": (-1.35, -0.55, 3.68), "target": (-1.20, 1.50, 3.74), "lens": 33.0, "roll": 1.5,  "ease": "cubic"},
    # L02 Arka Diomede (00:04.2-00:09.4): Smooth Zoom-Out tracking Arka's natural profile walk toward Kapten Soren!
    {"t": 4.40,  "pos": (-1.05, -2.10, 3.85), "target": (-0.65, 1.50, 3.60), "lens": 21.0, "roll": 0.0,  "ease": "snappy"},
    {"t": 7.20,  "pos": (0.80, -2.10, 3.85),  "target": (1.05, 1.52, 3.55),  "lens": 22.0, "roll": 0.0,  "ease": "cubic",
     "orbit": {"center": (0.60, 1.50, 3.6), "r0": 3.6, "r1": 3.55, "ang0": -118.0, "ang1": -66.0, "z0": 3.80, "z1": 3.85}},
    # Dutch push-in on Soren's SENIN calendar & USA/RUSSIA sign
    {"t": 9.30,  "pos": (1.10, -0.80, 3.68),  "target": (2.00, 1.55, 3.55),  "lens": 31.0, "roll": 8.0,  "ease": "overshoot"},
    # Aerial Zoom-Out & Speed-Ramp Sweep over jagged Bering sea-ice slicing sheer holographic Date Line toward Big Diomede!
    {"t": 10.8,  "pos": (0.15, 6.20, 4.35),   "target": (0.0, 26.0, 4.20),   "lens": 19.0, "roll": -4.0, "ease": "expo"},
    {"t": 12.2,  "pos": (0.00, 16.5, 4.65),   "target": (0.0, 30.0, 4.40),   "lens": 26.0, "roll": 0.0,  "ease": "overshoot"},
    # L03 Kapten Soren Speaks (00:12.3-00:16.6): Whip-back -> Crisp Emphasis Zoom-In tight on Soren!
    {"t": 13.4,  "pos": (0.80, -1.45, 3.82),  "target": (1.75, 1.55, 3.62),  "lens": 24.0, "roll": 1.5,  "ease": "snappy"},
    {"t": 15.8,  "pos": (1.42, -0.35, 3.72),  "target": (1.85, 1.55, 3.68),  "lens": 38.0, "roll": 0.0,  "ease": "overshoot"},
    {"t": 16.6,  "pos": (1.42, -0.35, 3.72),  "target": (1.85, 1.55, 3.68),  "lens": 40.0, "roll": 0.0,  "ease": "cubic"},
    # L04 Arka Ice Bridge (00:16.7-00:24.2): Zoom-Out wide tracking walk -> Crash-Zoom on cracking ice -> Macro Zoom into Soren's binoculars!
    {"t": 18.4,  "pos": (-1.35, -1.85, 4.05), "target": (-2.10, 2.25, 2.85), "lens": 20.0, "roll": -3.0, "ease": "snappy"},
    {"t": 20.1,  "pos": (-0.95, 1.55, 3.88),  "target": (-2.85, 3.10, 2.40), "lens": 31.0, "roll": -5.5, "ease": "overshoot"},
    {"t": 21.9,  "pos": (-1.05, -0.55, 3.68), "target": (-2.05, 2.15, 3.25), "lens": 23.0, "roll": 2.5,  "ease": "snappy"},
    {"t": 24.2,  "pos": (-1.45, 0.35, 3.62),  "target": (-1.45, 2.05, 3.61), "lens": 46.0, "roll": 0.0,  "ease": "overshoot"},
    # Fast 8-frame high-speed whip-pan right + skyward
    {"t": 24.72, "pos": (-1.45, 0.35, 3.62),  "target": (-1.45, 2.05, 3.61), "lens": 48.0, "roll": 0.0,  "ease": "linear"},
    {"t": 25.0,  "pos": (-1.45, 0.35, 3.70),  "target": (12.0, 2.05, 8.50),  "lens": 18.0, "roll": 22.0, "ease": "expo"},
]

# WORLD 2: Rjukan Dark Valley, Norwegian Town & Solspeilet Cliff (00:25.0 – 00:49.0)
CAMERA_RJUKAN: List[Dict[str, Any]] = [
    # L05 Arka Intro (00:25.0-00:32.3): Dramatic aerial dive -> Emphasis Zoom-In onto shivering Arka!
    {"t": 25.0,  "pos": (-7.5, -10.5, 18.5),  "target": (-1.0, 0.5, 2.5),    "lens": 18.0, "roll": -12.0},
    {"t": 27.4,  "pos": (-4.4, -6.6, 3.15),   "target": (-1.55, -1.65, 1.35), "lens": 20.0, "roll": 0.0,  "ease": "snappy"},
    {"t": 29.6,  "pos": (-1.05, -5.0, 1.85),  "target": (-1.55, -1.65, 1.32), "lens": 24.0, "roll": 1.0,  "ease": "cubic"},
    {"t": 31.6,  "pos": (-0.95, -4.1, 1.62),  "target": (-1.55, -1.65, 1.34), "lens": 33.0, "roll": 1.5,  "ease": "overshoot"},
    # L06 Astrid Speaks (00:32.5-00:36.2): Rocket crane up -> Snappy Zoom-In onto Astrid & tablet -> Wide Zoom-Out revealing ALL 3 Solspeilet mirrors!
    {"t": 32.9,  "pos": (-2.20, 15.0, 26.25), "target": (-1.60, 22.0, 25.45), "lens": 21.0, "roll": -3.5, "ease": "expo"},
    {"t": 34.4,  "pos": (-1.45, 18.2, 25.92), "target": (-1.55, 22.0, 25.38), "lens": 36.0, "roll": 0.0,  "ease": "overshoot"},
    {"t": 36.3,  "pos": (1.10, 13.4, 25.35),  "target": (0.0, 26.0, 27.3),    "lens": 18.0, "roll": 2.5,  "ease": "snappy"},
    # L07 Arka Sunbeam (00:36.4-00:45.3): Ride golden beam down -> Wide plaza reveal -> Dolly Zoom-In onto sunlit square & Henrik!
    {"t": 38.5,  "pos": (3.20, 10.8, 14.2),   "target": (0.4, 0.8, 1.4),      "lens": 19.0, "roll": -5.5, "ease": "expo"},
    {"t": 40.4,  "pos": (-3.60, -5.2, 2.95),  "target": (0.4, 0.8, 1.25),     "lens": 20.0, "roll": 0.0,  "ease": "overshoot"},
    {"t": 43.2,  "pos": (-0.65, -2.55, 1.48), "target": (0.85, 0.85, 1.08),   "lens": 27.0, "roll": 1.5,  "ease": "snappy"},
    # L08 Kakek Henrik Speaks (00:45.5-00:48.4): Orbiting two-shot -> Punchy Emphasis Zoom-In straight onto Henrik's sunglasses!
    {"t": 45.4,  "pos": (1.45, -2.05, 1.44),  "target": (0.60, 0.80, 1.12),   "lens": 26.0, "roll": 0.0,  "ease": "cubic",
     "orbit": {"center": (0.50, 0.80, 1.2), "r0": 3.40, "r1": 2.95, "ang0": -108.0, "ang1": -72.0, "z0": 1.48, "z1": 1.42}},
    {"t": 47.4,  "pos": (1.20, -1.25, 1.32),  "target": (0.95, 0.80, 1.22),   "lens": 42.0, "roll": 0.0,  "ease": "overshoot"},
    {"t": 48.65, "pos": (0.95, -0.25, 1.24),  "target": (0.95, 0.80, 1.24),   "lens": 58.0, "roll": 0.0,  "ease": "expo"},
    {"t": 49.0,  "pos": (0.95, 0.25, 1.24),   "target": (0.95, 0.80, 1.24),   "lens": 74.0, "roll": 0.0,  "ease": "linear"},
]

# WORLD 3: Baarle-Nassau / Baarle-Hertog Corner Café & Dual-Flag Brick Street (00:49.0 – 00:75.0)
CAMERA_BAARLE: List[Dict[str, Any]] = [
    # L09 Arka Baarle Intro (00:49.0-00:56.5): Low tracking sweep through doorway -> Zoom-In Pop as Arka hops border!
    {"t": 49.0,  "pos": (0.0, -6.20, 0.48),   "target": (0.0, 0.5, 0.45),     "lens": 19.0, "roll": 0.0},
    {"t": 52.4,  "pos": (0.10, -0.50, 0.72),  "target": (0.0, 4.8, 1.18),     "lens": 20.0, "roll": 1.5,  "ease": "cubic"},
    {"t": 54.6,  "pos": (0.30, 1.75, 1.54),   "target": (0.25, 5.10, 1.38),   "lens": 26.0, "roll": 0.0,  "ease": "snappy"},
    # L10 Bram Speaks & Shoves Cup (00:56.6-00:59.4): Emphasis Zoom-In + crisp lateral track watching Bram's hand push the cup across brass line!
    {"t": 56.5,  "pos": (0.35, 2.05, 1.48),   "target": (0.32, 5.20, 1.26),   "lens": 24.0, "roll": 0.0,  "ease": "cubic"},
    {"t": 58.6,  "pos": (-0.28, 2.25, 1.44),  "target": (-0.08, 5.15, 1.24),  "lens": 33.0, "roll": -1.5, "ease": "overshoot"},
    # L11 Arka Explains Border Law (00:59.5-01:06.7): Comedic Snap-Zoom on Clara -> Whip-pan outside cleanly past awning -> Emphasis Zoom onto Dual-Flag House!
    {"t": 60.4,  "pos": (0.32, 1.75, 1.40),   "target": (-0.85, 3.74, 1.26),  "lens": 36.0, "roll": 3.0,  "ease": "snappy"},
    {"t": 61.9,  "pos": (0.42, 1.90, 1.05),   "target": (-0.55, 3.74, 0.30),  "lens": 24.0, "roll": -3.5, "ease": "overshoot"},
    # Start exterior push cleanly at Y=-2.45 (CLEAR of café awning!) -> Emphasis Zoom onto brick house & plaques!
    {"t": 63.1,  "pos": (0.0, -2.45, 2.05),   "target": (0.0, -11.2, 2.35),   "lens": 22.0, "roll": 0.0,  "ease": "expo"},
    {"t": 66.2,  "pos": (0.0, -4.95, 2.02),   "target": (0.0, -11.2, 2.18),   "lens": 29.0, "roll": 0.0,  "ease": "overshoot"},
    # L12 Clara Comedy Line (01:06.8-01:09.95): Whip-pan back inside -> Comedic Emphasis Zoom-In on Clara lifting BOTH feet while Arka & Bram laugh!
    {"t": 67.3,  "pos": (0.35, 0.80, 1.52),   "target": (-0.05, 4.10, 1.20),  "lens": 19.0, "roll": -2.0, "ease": "snappy"},
    {"t": 69.5,  "pos": (0.28, 1.35, 1.44),   "target": (-0.42, 3.90, 1.16),  "lens": 31.0, "roll": 2.0,  "ease": "overshoot"},
    {"t": 69.95, "pos": (0.28, 1.35, 1.44),   "target": (-0.42, 3.90, 1.16),  "lens": 32.0, "roll": 2.0,  "ease": "cubic"},
    # L13 Arka Finale (01:10.00-01:15.0): Exact 1-frame Cut Outside -> Wide Pull-Back -> Punchy Closing Emphasis Zoom-In on Arka!
    {"t": 70.00, "pos": (0.0, -5.50, 1.48),   "target": (0.0, -2.35, 1.20),   "lens": 21.0, "roll": 0.0,  "cut": True},
    {"t": 72.8,  "pos": (0.0, -7.10, 1.72),   "target": (0.0, -2.35, 1.26),   "lens": 19.0, "roll": 0.0,  "ease": "cubic"},
    {"t": 74.6,  "pos": (0.0, -4.50, 1.52),   "target": (0.0, -2.35, 1.38),   "lens": 30.0, "roll": -2.5, "ease": "overshoot"},
    {"t": 75.0,  "pos": (0.0, -4.40, 1.52),   "target": (0.0, -2.35, 1.38),   "lens": 31.0, "roll": -2.5, "ease": "linear"},
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
# 3. ZERO-FLICK, ANTI-CLIPPING, NATURAL BIOMECHANICAL CHARACTER BLOCKING (v3)
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
    # SCENE 1: DIOMEDE (Arka + Kapten Soren — NATURAL STRIDE WALK, ZERO OVERLAP!)
    # ------------------------------------------------------------------
    if scene_name == "diomede":
        arka_m = _lipsync_val(lipsync_curves, "arka", frame)
        soren_m = _lipsync_val(lipsync_curves, "kapten_soren", frame)

        if t < 4.0:
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
        elif t < 7.2:
            # NATURAL STRIDE-SYNCED PROFILE WALK along wooden dock toward Kapten Soren!
            dt_w = 3.2
            u_raw = (t - 4.0) / dt_w
            u = ease_cubic_in_out(u_raw)
            du_dt = ease_cubic_in_out_deriv(u_raw) / dt_w
            dx, dy = 1.85, 0.02
            total_d = math.hypot(dx, dy)
            pos_a = (lerp(-1.30, 0.55, u), lerp(1.50, 1.52, u), DOCK_Z)
            # Turn smoothly to face walking direction (+X = 0 deg) during stride, then face camera/Soren (-60 deg)!
            if u_raw < 0.18:
                fac_a = lerp_angle_deg(-90.0, 2.0, u_raw / 0.18)
            elif u_raw > 0.80:
                fac_a = lerp_angle_deg(2.0, -60.0, (u_raw - 0.80) / 0.20)
            else:
                fac_a = 2.0
            rk_a = compute_natural_walk_rig(total_d * u, total_d * du_dt, stride_len_m=0.56)
            rk_a.update({
                "eyes": "honey_oval", "eyebrows": "thick_arch", "mouth": "confident_gap",
                "mouth_open": arka_m, "eye_gaze_x": 0.20,
            })
        elif t < 16.4:
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
            # NATURAL STRIDE-SYNCED WALK left & down wide wooden ramp onto cracking sea-ice ledge!
            dt_w = 3.2
            u_raw = (t - 16.4) / dt_w
            u = ease_cubic_in_out(u_raw)
            du_dt = ease_cubic_in_out_deriv(u_raw) / dt_w
            dx, dy = -3.40, 1.58
            total_d = math.hypot(dx, dy)
            walk_az = math.degrees(math.atan2(dy, dx))  # ~155 deg (clear 3/4 profile stride!)
            pos_a = (lerp(0.55, -2.85, u), lerp(1.52, 3.10, u), lerp(DOCK_Z, ICE_LEDGE_Z, clamp01((u - 0.52) / 0.48)))
            if u_raw < 0.14:
                fac_a = lerp_angle_deg(-30.0, walk_az, u_raw / 0.14)
            elif u_raw > 0.85:
                fac_a = lerp_angle_deg(walk_az, -110.0, (u_raw - 0.85) / 0.15)
            else:
                fac_a = walk_az
            rk_a = compute_natural_walk_rig(total_d * u, total_d * du_dt, stride_len_m=0.60)
            rk_a.update({
                "eyes": "focused", "eyebrows": "raised", "mouth": "smirk", "mouth_open": arka_m, "eye_gaze_y": 0.32,
            })
        elif t < 20.8:
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

        # KAPTEN SOREN (Starts walking slightly after Arka & stays to Arka's right -> ZERO overlap + crisp binocular grip!)
        if t < 17.0:
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
        elif t < 20.0:
            dt_s = 3.0
            u_raw = (t - 17.0) / dt_s
            u = ease_cubic_in_out(u_raw)
            du_dt = ease_cubic_in_out_deriv(u_raw) / dt_s
            dx, dy = -3.30, 0.50
            total_d = math.hypot(dx, dy)
            walk_az = math.degrees(math.atan2(dy, dx))
            pos_s = (lerp(1.85, -1.45, u), lerp(1.55, 2.05, u), DOCK_Z)
            if u_raw < 0.14:
                fac_s = lerp_angle_deg(-112.0, walk_az, u_raw / 0.14)
            elif u_raw > 0.84:
                fac_s = lerp_angle_deg(walk_az, -108.0, (u_raw - 0.84) / 0.16)
            else:
                fac_s = walk_az
            rk_s = compute_natural_walk_rig(total_d * u, total_d * du_dt, stride_len_m=0.62, arm_energy=0.85)
            rk_s.update({"eyes": "suspicious", "eyebrows": "skeptical", "mouth": "flat", "mouth_open": soren_m})
        else:
            pos_s = (-1.45, 2.05, DOCK_Z)
            fac_s = -108.0 if t < 22.8 else -90.0
            pull_t = clamp01((t - 20.4) / 0.55)
            lift_bino = ease_cubic_in_out(clamp01((t - 22.85) / 0.95))
            shake = math.sin(t * 16.0) * 10.0 if 21.4 <= t <= 22.8 else 0.0
            if t < 22.8:
                rh = (lerp(66.0, 82.0, pull_t), lerp(252.0, 206.0, pull_t), 34.0)
                lh = (-54.0, 268.0, 18.0)
            else:
                # Both hands grip left & right barrels of brass binoculars EXACTLY at eye height (y=154px)!
                rh = (lerp(62.0, 44.0, lift_bino), lerp(234.0, 152.0, lift_bino), lerp(28.0, 56.0, lift_bino))
                lh = (lerp(-54.0, -42.0, lift_bino), lerp(254.0, 152.0, lift_bino), lerp(22.0, 56.0, lift_bino))
            rk_s = {
                "animation": "free", "pelvis_y": 1.5, "torso_lean_deg": -3.0 if t < 22.2 else 3.0,
                "head_tilt_deg": shake, "right_hand_target": rh, "left_hand_target": lh,
                "eyes": "suspicious" if t < 22.9 else "chill",
                "eyebrows": "angry" if 20.4 <= t <= 22.4 else "skeptical",
                "mouth": "frown" if 20.4 <= t <= 22.4 else "smirk", "mouth_open": soren_m,
            }
        pack("kapten_soren", pos_s, fac_s, rk_s)

    # ------------------------------------------------------------------
    # SCENE 2: RJUKAN (Arka Natural Walk + Astrid + Kakek Henrik)
    # ------------------------------------------------------------------
    elif scene_name == "rjukan":
        arka_m = _lipsync_val(lipsync_curves, "arka", frame)
        astrid_m = _lipsync_val(lipsync_curves, "astrid", frame)
        henrik_m = _lipsync_val(lipsync_curves, "kakek_henrik", frame)

        if t < 38.4:
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
        elif t < 41.6:
            # NATURAL STRIDE-SYNCED WALK from streetlamp into the newly lit golden sunlit square!
            dt_w = 3.2
            u_raw = (t - 38.4) / dt_w
            u = ease_cubic_in_out(u_raw)
            du_dt = ease_cubic_in_out_deriv(u_raw) / dt_w
            dx, dy = 0.50, 2.20
            total_d = math.hypot(dx, dy)
            walk_az = math.degrees(math.atan2(dy, dx))
            pos_a = (lerp(-1.55, -1.05, u), lerp(-1.65, 0.55, u), SQUARE_Z)
            if u_raw < 0.16:
                fac_a = lerp_angle_deg(-80.0, walk_az, u_raw / 0.16)
            elif u_raw > 0.80:
                fac_a = lerp_angle_deg(walk_az, 15.0, (u_raw - 0.80) / 0.20)
            else:
                fac_a = walk_az
            rk_a = compute_natural_walk_rig(total_d * u, total_d * du_dt, stride_len_m=0.58)
            rk_a.update({
                "eyes": "starry" if t > 39.5 else "shocked", "eyebrows": "raised",
                "mouth": "small_o" if t < 41.2 else "confident_gap", "mouth_open": arka_m, "eye_gaze_x": 0.30,
            })
        elif t < 47.0:
            pos_a = (-1.05, 0.55, SQUARE_Z)
            fac_a = 15.0
            rk_a = {
                "animation": "free", "pelvis_y": -2.0 + math.sin(t * 3.0) * 2.0, "torso_lean_deg": 6.0, "head_tilt_deg": 3.0,
                "right_hand_target": (78.0, 198.0, 38.0), "left_hand_target": (-48.0, 266.0, 16.0),
                "eyes": "starry", "eyebrows": "raised", "mouth": "confident_gap", "mouth_open": arka_m, "eye_gaze_x": 0.40,
            }
        else:
            u_raw = clamp01((t - 47.0) / 1.3)
            u = ease_cubic_in_out(u_raw)
            du_dt = ease_cubic_in_out_deriv(u_raw) / 1.3
            pos_a = (lerp(-1.05, -0.35, u), lerp(0.55, 0.65, u), SQUARE_Z)
            fac_a = 10.0
            rk_a = compute_natural_walk_rig(0.71 * u, 0.71 * du_dt, stride_len_m=0.55, arm_energy=0.6)
            rk_a.update({
                "torso_lean_deg": 12.0 * u, "head_tilt_deg": 6.0,
                "eyes": "focused", "eyebrows": "raised", "mouth": "small_o", "mouth_open": arka_m, "eye_gaze_x": 0.45,
            })
        pack("arka", pos_a, fac_a, rk_a)

        # ASTRID on cliff deck at Y=22.0 (0.5m cleanly back from front railing -> railing stays below waist!)
        pos_ast = (-1.60, 22.00, CLIFF_DECK_Z)
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

        # KAKEK HENRIK relaxing naturally in striped beach chair
        pos_h = (0.95, 0.80, SQUARE_Z)
        thumb_u = ease_out_overshoot(clamp01((t - 45.2) / 0.7), s=0.75)
        sip_u = math.sin(clamp01((t - 42.2) / 1.8) * math.pi)
        pack("kakek_henrik", pos_h, -105.0, {
            "animation": "free", "pelvis_y": 24.0 + math.sin(t * 2.0) * 1.6, "torso_lean_deg": -6.0,
            "head_tilt_deg": 5.0 + math.sin(t * 1.8) * 2.5,
            "left_hand_target": (-42.0, 244.0 - sip_u * 48.0, 38.0 + sip_u * 14.0),
            "right_hand_target": (lerp(56.0, 88.0, thumb_u), lerp(258.0, 192.0, thumb_u), 40.0),
            "left_foot_target": (-24.0, 474.0, 24.0), "right_foot_target": (24.0, 474.0, 24.0),
            "eyes": "happy", "eyebrows": "happy", "mouth": "happy_open", "mouth_open": max(0.25, henrik_m),
        })

    # ------------------------------------------------------------------
    # SCENE 3: BAARLE (Bram Hand-Locked Cup Shove, Seated Clara, Hopping Arka!)
    # ------------------------------------------------------------------
    else:
        arka_m = _lipsync_val(lipsync_curves, "arka", frame)
        bram_m = _lipsync_val(lipsync_curves, "bram", frame)
        clara_m = _lipsync_val(lipsync_curves, "clara", frame)

        if frame < 2100:  # Strictly 00:49.00 .. 01:09.97 (INSIDE CAFÉ)
            if t < 53.4:
                pos_a = (-0.35, 2.55, CAFE_FLOOR_Z)
                fac_a = -75.0
                rk_a = {
                    "animation": "free", "pelvis_y": math.sin(t * 3.5) * 2.5, "torso_lean_deg": 4.0,
                    "right_hand_target": (72.0, 206.0, 32.0), "left_hand_target": (-48.0, 266.0, 16.0),
                    "eyes": "honey_oval", "eyebrows": "thick_arch", "mouth": "confident_gap", "mouth_open": arka_m,
                }
            elif t < 55.2:
                # Playful energetic spring-hop across the Belgian/Dutch floor border!
                hop_u = clamp01((t - 53.4) / 1.8)
                hop_arc = math.sin(hop_u * math.pi) * 0.30
                pos_a = (lerp(-0.35, 1.12, ease_cubic_in_out(hop_u)), lerp(2.55, 3.35, ease_cubic_in_out(hop_u)), CAFE_FLOOR_Z + hop_arc)
                fac_a = lerp(-75.0, -130.0, hop_u)
                rk_a = {
                    "animation": "jump", "eyes": "starry", "eyebrows": "raised", "mouth": "happy_open", "mouth_open": arka_m,
                }
            else:
                pos_a = (1.12, 3.35, CAFE_FLOOR_Z)
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

            # BRAM: Standing on raised 0.31m oak duckboard behind 0.92m bar (Y=5.56) -> legs hidden (<0.85m), apron & arms 100% visible!
            # Phase A (t < 56.55): Bram at X=+0.62 with his SCREEN-LEFT hand (left_hand_target at x=-66px, y=300px) resting DIRECTLY ON cup at X=+0.36!
            # Phase B (56.55..57.45): Bram steps & leans left (X: +0.62 -> +0.16) as his hand stays LOCKED ON THE CUP pushing it across brass border X=0!
            # Phase C (57.45..67.4): Dramatic follow-through arm extended toward Belgium as cup glides on momentum to X=-0.58!
            push_u = ease_cubic_in_out(clamp01((t - 56.55) / 0.90))
            settle_u = ease_cubic_in_out(clamp01((t - 57.50) / 0.90))
            bram_x = lerp(0.62, 0.16, push_u)
            pos_b = (bram_x, 5.56, BRAM_STEP_Z)
            fac_b = lerp(-90.0, -104.0, push_u)
            is_laugh_b = t >= 67.4
            if is_laugh_b:
                rk_b = {"animation": "laugh", "eyes": "happy", "eyebrows": "happy", "mouth": "happy_open", "mouth_open": 0.6}
            else:
                # Screen-left arm (left_hand_target, x<0) rests directly on the cup at bar top height (y=298px, forward z=54px) & shoves it left!
                lh_x = lerp(-62.0, -96.0, push_u) + 12.0 * settle_u
                lh_y = lerp(298.0, 294.0, push_u) - 18.0 * settle_u
                rh_x = lerp(52.0, 32.0, push_u)
                rh_y = lerp(282.0, 276.0, push_u)
                rk_b = {
                    "animation": "free",
                    "pelvis_y": math.sin(t * 3.0) * 1.6 + push_u * 3.0 * (1.0 - settle_u),
                    "torso_lean_deg": lerp(4.0, -14.0, push_u) + 8.0 * settle_u,
                    "head_tilt_deg": lerp(-3.0, 7.0, push_u),
                    "left_hand_target": (lh_x, lh_y, 58.0),
                    "right_hand_target": (rh_x, rh_y, 26.0),
                    "eyes": "honey_oval", "eyebrows": "raised",
                    "mouth": "grin_teeth" if push_u > 0.25 else "smirk", "mouth_open": bram_m,
                    "eye_gaze_x": lerp(-0.15, -0.45, push_u),
                }
            pack("bram", pos_b, fac_b, rk_b)

            # CLARA: Seated naturally at (-0.85, 3.74, 0.0) directly in front of her rattan chair (-0.85, 3.92) with knees bent & feet clear!
            pos_c = (-0.85, 3.74, CAFE_FLOOR_Z)
            fac_c = -68.0
            lift_feet = ease_out_overshoot(clamp01((t - 66.8) / 0.85), s=0.90)
            look_down = ease_cubic_in_out(clamp01((t - 59.8) / 0.8))
            rk_c = {
                "animation": "free",
                "pelvis_y": 30.0 + lift_feet * 5.0,  # Lower seated hip height so she visibly sits on chair cushion!
                "torso_lean_deg": lerp(3.0, 9.0, look_down) * (1.0 - lift_feet * 0.65),
                "head_tilt_deg": lerp(2.0, 12.0, look_down),
                "left_foot_target": (-20.0, lerp(468.0, 396.0, lift_feet), lerp(36.0, 52.0, lift_feet)),
                "right_foot_target": (24.0, lerp(468.0, 396.0, lift_feet), lerp(36.0, 52.0, lift_feet)),
                "left_hand_target": (-42.0, lerp(256.0, 218.0, look_down), 36.0),
                "right_hand_target": (50.0, lerp(250.0, 226.0, lift_feet), 36.0),
                "eyes": "shocked" if 60.0 <= t < 66.8 else ("happy" if t >= 68.5 else "honey_oval"),
                "eyebrows": "skeptical" if t < 68.5 else "raised",
                "mouth": "small_o" if t < 66.8 else "happy_open",
                "mouth_open": max(0.35, clara_m) if t >= 66.8 else clara_m,
                "eye_gaze_y": 0.55 if 60.0 <= t < 66.8 else 0.0,
            }
            pack("clara", pos_c, fac_c, rk_c)
        else:
            # EXACT 1-FRAME SAFE CUT AT frame 2100 (70.00s): Golden-hour Baarle street finale!
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
# 4. HERO PROP & DYNAMIC LIGHTING TIMELINE SYNC (100% HAND-LOCKED CUP!)
# ============================================================================

def get_scene_dynamic_state(scene_name: str, frame: int) -> Dict[str, Any]:
    t = frame / FPS
    if scene_name == "diomede":
        flare = clamp01((t - 24.68) / 0.28) if t >= 24.68 else 0.0
        return {
            "snowball_pos": (-0.98, 1.32, DOCK_Z + 1.44 + math.sin(t * 4.5) * 0.035),
            "snowball_visible": t < 4.2,
            "snowball_rot_z": t * 14.0,
            "ice_crack_factor": clamp01((t - 19.55) / 0.4),
            "dateline_pulse": 0.8 + 0.2 * math.sin(t * 5.0),
            "lens_flare_strength": flare,
            "soren_bino_raise": ease_cubic_in_out(clamp01((t - 22.85) / 0.95)),
        }

    if scene_name == "rjukan":
        mirror_pivot = ease_cubic_in_out(clamp01((t - 34.0) / 2.4))
        beam_shoot = ease_expo_in_out(clamp01((t - 36.4) / 3.0))
        square_lit = ease_out_overshoot(clamp01((t - 39.2) / 0.9), s=0.4)
        match_flash = clamp01((t - 48.72) / 0.24) if t >= 48.72 else 0.0
        return {
            "mirror_pivot": mirror_pivot,
            "beam_shoot": beam_shoot,
            "square_lit": clamp01(square_lit),
            "match_flash": match_flash,
        }

    # Baarle: 2-stage physically coupled latte slide on BAR_TOP_Z=0.92!
    # Stage 1 (56.55..57.45): Locked directly against Bram's left hand (+0.36 -> -0.22 across X=0 brass line!)
    # Stage 2 (57.45..58.25): Smooth oak friction deceleration glide (-0.22 -> -0.60 into Belgium!)
    if t <= 56.55:
        cup_x = 0.36
    elif t <= 57.45:
        cup_x = lerp(0.36, -0.22, ease_cubic_in_out((t - 56.55) / 0.90))
    else:
        cup_x = lerp(-0.22, -0.60, ease_out_cubic(clamp01((t - 57.45) / 0.80)))

    return {
        "latte_visible": frame < 2100,
        "latte_pos": (cup_x, 5.10, BAR_TOP_Z + 0.008),
        "arka_finale_cup_visible": frame >= 2100,
        "arka_finale_cup_pos": (-0.28, -2.56, 1.16 + math.sin(clamp01((t - 71.2) / 1.4) * math.pi) * 0.22),
        "glitch_outro": clamp01((t - 74.68) / 0.28) if t >= 74.68 else 0.0,
    }
