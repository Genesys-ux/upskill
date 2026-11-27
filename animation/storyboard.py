"""Master 75-second 3D Continuous Camera Choreography, Biomechanical Character Motion & Prop Sync."""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

FPS = 30.0


# ============================================================================
# 1. ORGANIC MOTION CURVES (EXPONENTIAL EASE-IN-OUT + SUBTLE OVERSHOOT)
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


def ease_out_overshoot(t: float, s: float = 1.15) -> float:
    """Smooth deceleration with subtle organic overshoot at the end of camera/character sweeps."""
    t = clamp01(t)
    u = t - 1.0
    return 1.0 + (s + 1.0) * (u ** 3) + s * (u ** 2)


def ease_snappy_ramp(t: float) -> float:
    """Fast speed-ramped punch with silky settle and subtle 3% overshoot."""
    t = clamp01(t)
    return ease_out_overshoot(ease_cubic_in_out(t), s=0.55)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp3(p0: Tuple[float, float, float], p1: Tuple[float, float, float], t: float) -> Tuple[float, float, float]:
    return (lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t), lerp(p0[2], p1[2], t))


def eval_camera_track(keyframes: List[Dict[str, Any]], t_sec: float) -> Dict[str, Any]:
    """Evaluate continuous multi-keyframe 3D camera track (pos, target, lens, roll_deg)."""
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
            dt = max(1e-5, k1["t"] - k0["t"])
            u = (t_sec - k0["t"]) / dt
            curve = k1.get("ease", "expo")
            if curve == "overshoot":
                e = ease_out_overshoot(u, s=0.65)
            elif curve == "snappy":
                e = ease_snappy_ramp(u)
            elif curve == "cubic":
                e = ease_cubic_in_out(u)
            elif curve == "linear":
                e = u
            else:
                e = ease_expo_in_out(u)

            # Optional orbital arc override for continuous orbit movements
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
            # Subtle handheld cinematic micro-breathing
            breath_x = math.sin(t_sec * 1.9) * 0.015
            breath_z = math.cos(t_sec * 2.4) * 0.012
            return {
                "pos": (pos[0] + breath_x, pos[1], pos[2] + breath_z),
                "target": target,
                "lens": max(15.0, min(85.0, lens)),
                "roll": roll,
            }
    k = keyframes[-1]
    return {"pos": k["pos"], "target": k["target"], "lens": k["lens"], "roll": k.get("roll", 0.0)}


# ============================================================================
# 2. 30+ CONTINUOUS 3D CAMERA MOVEMENTS ACROSS ALL 3 WORLDS (7 SUB-LOCATIONS)
# ============================================================================

# WORLD 1: Little Diomede Cliff Dock & Bering Strait (00:00.0 – 00:25.0)
CAMERA_DIOMEDE: List[Dict[str, Any]] = [
    # Move 1-2: 2-Second Hook! Extreme wide-angle dolly-in through snow particles locking onto Arka + Big Diomede behind
    {"t": 0.0,  "pos": (-3.6, -5.8, 5.2),  "target": (-1.3, 1.5, 3.7),  "lens": 18.0, "roll": -4.0},
    {"t": 1.85, "pos": (-1.55, -0.95, 3.72), "target": (-1.35, 1.5, 3.75), "lens": 22.0, "roll": 0.0, "ease": "snappy"},
    {"t": 4.0,  "pos": (-1.15, -1.35, 3.65), "target": (-1.2, 2.2, 3.65), "lens": 20.0, "roll": 1.5, "ease": "cubic"},
    # Move 3: Fast continuous 125° orbit circling Arka walking toward Kapten Soren
    {"t": 7.2,  "pos": (0.9, -2.5, 3.8), "target": (0.85, 1.55, 3.55), "lens": 21.0, "roll": 0.0, "ease": "cubic",
     "orbit": {"center": (0.5, 1.55, 3.6), "r0": 3.4, "r1": 3.6, "ang0": -118.0, "ang1": -58.0, "z0": 3.65, "z1": 3.85}},
    # Move 4: Dutch angle (+11°) emphasis push-in on Soren's SENIN calendar & brass binoculars + USA/RUSSIA sign
    {"t": 9.0,  "pos": (1.1, -0.75, 3.65), "target": (1.95, 1.65, 3.55), "lens": 28.0, "roll": 11.0, "ease": "overshoot"},
    # Move 5-6: Speed-ramped aerial travel launch skimming icy sea waves & slicing glowing GARIS TANGGAL INTERNASIONAL!
    {"t": 10.6, "pos": (0.4, 6.8, 3.4),    "target": (0.2, 24.0, 4.2),   "lens": 18.0, "roll": -6.0, "ease": "expo"},
    {"t": 12.2, "pos": (0.0, 18.8, 4.6),   "target": (0.0, 26.0, 4.6),   "lens": 20.0, "roll": 0.0,  "ease": "overshoot"},
    # Move 7-8: Whip-back crane sweep returning to Soren & Arka + emphasis zoom on Soren's grizzled dialog
    {"t": 13.6, "pos": (0.6, -1.5, 3.9),   "target": (1.7, 1.6, 3.65),   "lens": 26.0, "roll": 3.0,  "ease": "snappy"},
    {"t": 16.4, "pos": (1.45, -0.35, 3.82), "target": (1.8, 1.6, 3.78),  "lens": 36.0, "roll": 0.0,  "ease": "cubic"},
    # Move 9: Fast crane drop & push-in to thin frozen sea-ice shelf beneath Arka's stepping boot!
    {"t": 18.6, "pos": (-3.9, 0.9, 2.3),   "target": (-2.6, 3.2, 0.9),   "lens": 20.0, "roll": -5.0, "ease": "expo"},
    {"t": 20.2, "pos": (-3.4, 1.85, 0.95), "target": (-2.75, 3.35, 0.35), "lens": 26.0, "roll": -8.0, "ease": "snappy"},
    # Move 10-11: Snappy snap-zoom up as Soren yanks Arka's collar back, then whip-up to Soren's binoculars lens!
    {"t": 22.0, "pos": (-2.3, 0.55, 1.95), "target": (-2.25, 2.85, 1.55), "lens": 24.0, "roll": 4.0, "ease": "overshoot"},
    {"t": 23.8, "pos": (-1.85, 1.42, 1.85), "target": (-1.9, 2.6, 1.85), "lens": 42.0, "roll": 0.0, "ease": "snappy"},
    # Move 12: Lens flare flash + fast whip-pan upward into dark Nordic blue sky (Transition 1 -> 2)
    {"t": 25.0, "pos": (-1.85, 1.8, 2.15), "target": (-8.5, 5.5, 12.0),  "lens": 18.0, "roll": 18.0, "ease": "expo"},
]

# WORLD 2: Rjukan Dark Valley & Solspeilet Heliostat Mirrors (00:25.0 – 00:49.0)
CAMERA_RJUKAN: List[Dict[str, Any]] = [
    # Move 13: Dramatic crane dive plunging from high dark cliff peak down into shadowy noon Rjukan Torg!
    {"t": 25.0, "pos": (-6.5, 8.0, 26.0),  "target": (0.0, 0.0, 4.5),    "lens": 18.0, "roll": -12.0},
    {"t": 27.6, "pos": (-4.4, -7.8, 3.4),  "target": (-1.3, -1.6, 1.45), "lens": 20.0, "roll": 0.0, "ease": "snappy"},
    # Move 14: Lateral parallax sweep past foreground snow-topped iron streetlamp revealing shivering Arka
    {"t": 30.8, "pos": (-0.65, -5.0, 1.65), "target": (-1.55, -2.0, 1.35), "lens": 24.0, "roll": 2.0, "ease": "cubic"},
    # Move 15-16: High-speed vertical rocket crane climbing sheer black cliff to Astrid's heliostat deck + tablet push-in!
    {"t": 32.5, "pos": (-3.1, 16.5, 29.8), "target": (-1.5, 21.8, 29.3), "lens": 22.0, "roll": -5.0, "ease": "expo"},
    {"t": 34.4, "pos": (-1.35, 20.05, 29.25), "target": (-1.55, 21.65, 29.15), "lens": 34.0, "roll": 0.0, "ease": "overshoot"},
    # Move 17: Wide low-angle hero tilt showing all 3 giant Solspeilet mirrors pivoting open with sun glare!
    {"t": 36.2, "pos": (0.8, 17.0, 28.6),  "target": (0.0, 25.5, 31.6),  "lens": 18.0, "roll": 4.0, "ease": "snappy"},
    # Move 18-19: Tracking dive riding the blazing 450m golden volumetric god ray down into Rjukan Torg!
    {"t": 38.4, "pos": (2.8, 13.5, 16.5),  "target": (0.5, 1.2, 1.8),    "lens": 19.0, "roll": -7.0, "ease": "expo"},
    {"t": 40.3, "pos": (-3.6, -5.4, 3.2),  "target": (0.5, 0.8, 1.2),    "lens": 20.0, "roll": 0.0,  "ease": "overshoot"},
    # Move 20: Snappy speed-ramped dolly-in into the glowing sunlit square box revealing Kakek Henrik in beach chair!
    {"t": 43.2, "pos": (-0.6, -2.4, 1.45), "target": (0.85, 0.85, 1.05), "lens": 24.0, "roll": 2.0,  "ease": "snappy"},
    # Move 21: Smooth orbiting two-shot sweeping from jaw-dropped Arka to chuckling Henrik giving thumbs-up
    {"t": 46.8, "pos": (1.6, -1.8, 1.42),  "target": (0.4, 0.75, 1.12),  "lens": 26.0, "roll": 0.0,  "ease": "cubic",
     "orbit": {"center": (0.5, 0.75, 1.2), "r0": 3.3, "r1": 2.6, "ang0": -108.0, "ang1": -62.0, "z0": 1.45, "z1": 1.38}},
    # Move 22-23: Extreme macro zoom-in onto golden light reflection bar across Henrik's retro sunglasses (Match-Cut!)
    {"t": 48.35, "pos": (0.88, -0.35, 1.24), "target": (0.90, 0.78, 1.22), "lens": 52.0, "roll": 0.0, "ease": "expo"},
    {"t": 49.0,  "pos": (0.89, 0.22, 1.24),  "target": (0.90, 0.80, 1.23), "lens": 65.0, "roll": 0.0, "ease": "linear"},
]

# WORLD 3: Baarle-Nassau / Baarle-Hertog Cross-Border Café & Street (00:49.0 – 00:75.0)
CAMERA_BAARLE: List[Dict[str, Any]] = [
    # Move 24: Match-cut exit! Low-angle speed-tracking hugging Baarle cobblestone along white (+) & B|NL border tiles!
    {"t": 49.0, "pos": (0.0, -7.8, 0.42),  "target": (0.0, -1.0, 0.35),  "lens": 18.0, "roll": 0.0},
    {"t": 52.4, "pos": (0.05, -0.9, 0.48), "target": (0.0, 4.8, 0.95),   "lens": 19.0, "roll": 2.0, "ease": "cubic"},
    # Move 25: Fast vertical boom-up & dolly rising onto the varnished oak bar counter split by brass border strip
    {"t": 55.2, "pos": (0.3, 2.35, 1.72),  "target": (0.15, 5.4, 1.48),  "lens": 22.0, "roll": 0.0, "ease": "snappy"},
    # Move 26: Precision lateral tracking following Bram sliding steaming latte cup 30cm across NL -> B brass border!
    {"t": 58.8, "pos": (-0.65, 2.7, 1.55), "target": (-0.15, 5.05, 1.38), "lens": 28.0, "roll": -2.0, "ease": "overshoot"},
    # Move 27: Comedic snap-zoom on Clara's baffled expression, then whip-tilt down to her feet on NL while chair in B
    {"t": 60.4, "pos": (0.35, 1.95, 1.48), "target": (-0.55, 3.85, 1.38), "lens": 36.0, "roll": 4.0, "ease": "snappy"},
    {"t": 61.9, "pos": (0.55, 2.15, 1.10), "target": (-0.25, 3.85, 0.22), "lens": 26.0, "roll": -5.0, "ease": "overshoot"},
    # Move 28: Fast whip-pan & telephoto zoom through café glass window to opposite stepped-gable house dual-flag door!
    {"t": 63.3, "pos": (0.25, 1.2, 1.72),  "target": (0.0, -11.4, 1.95),  "lens": 40.0, "roll": 0.0, "ease": "expo"},
    {"t": 66.1, "pos": (0.10, -2.8, 1.85), "target": (0.0, -11.4, 1.95),  "lens": 52.0, "roll": 0.0, "ease": "cubic"},
    # Move 29: Whip-pan back inside catching Clara lifting BOTH feet onto chair rung while Arka & Bram burst out laughing!
    {"t": 67.4, "pos": (0.9, 1.45, 1.55),  "target": (-0.35, 4.1, 1.15),  "lens": 22.0, "roll": -3.0, "ease": "snappy"},
    {"t": 69.8, "pos": (1.15, 1.85, 1.48), "target": (-0.45, 3.9, 1.12),  "lens": 25.0, "roll": 0.0, "ease": "cubic"},
    # Move 30: Warm golden-hour smooth pull-back out onto Baarle street: Arka straddles B | NL border, winks & snaps!
    {"t": 71.2, "pos": (0.0, -5.2, 1.45),  "target": (0.0, -2.5, 1.18),   "lens": 22.0, "roll": 0.0, "ease": "expo"},
    {"t": 74.3, "pos": (0.0, -6.9, 1.72),  "target": (0.0, -2.5, 1.25),   "lens": 20.0, "roll": 0.0, "ease": "cubic"},
    {"t": 75.0, "pos": (0.0, -4.6, 1.52),  "target": (0.0, -2.5, 1.38),   "lens": 24.0, "roll": -3.0, "ease": "snappy"},
]


def get_camera_at_frame(scene_name: str, frame: int) -> Dict[str, Any]:
    t_sec = frame / FPS
    if scene_name == "diomede":
        return eval_camera_track(CAMERA_DIOMEDE, t_sec)
    if scene_name == "rjukan":
        return eval_camera_track(CAMERA_RJUKAN, t_sec)
    return eval_camera_track(CAMERA_BAARLE, t_sec)


def compute_view_angle_deg(char_pos: Tuple[float, float, float], facing_az_deg: float, cam_pos: Tuple[float, float, float]) -> float:
    """Compute exact 360° turntable viewAngleDeg so 2.5D character rotates faithfully with Blender's 3D camera."""
    dx = cam_pos[0] - char_pos[0]
    dy = cam_pos[1] - char_pos[1]
    cam_az = math.degrees(math.atan2(dy, dx))
    return (facing_az_deg - cam_az) % 360.0


def compute_billboard_rot_z(char_pos: Tuple[float, float, float], cam_pos: Tuple[float, float, float]) -> float:
    """Blender Z rotation (radians) so vertical character card faces camera squarely without paper-thin distortion."""
    dx = cam_pos[0] - char_pos[0]
    dy = cam_pos[1] - char_pos[1]
    return math.atan2(dy, dx) + math.pi * 0.5


def _lipsync_val(lipsync_curves: Optional[Dict[str, List[float]]], speaker: str, frame: int, t_sec: float) -> float:
    if lipsync_curves and speaker in lipsync_curves:
        arr = lipsync_curves[speaker]
        if 0 <= frame < len(arr):
            return float(arr[frame])
    # Fallback rhythmic speech envelope when running local dry-run without FFmpeg
    return 0.0


# ============================================================================
# 3. CHARACTER WORLD-SPACE POSITIONS, BIOMECHANICS & FREE-RIG ACTING
# ============================================================================

def get_characters_at_frame(
    scene_name: str,
    frame: int,
    lipsync_curves: Optional[Dict[str, List[float]]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Return exact 3D placement, facing yaw, camera-synced turntable angle, and Free-Rig kwargs per character."""
    t = frame / FPS
    cam = get_camera_at_frame(scene_name, frame)
    cam_pos = cam["pos"]
    out: Dict[str, Dict[str, Any]] = {}

    def pack(cid: str, pos: Tuple[float, float, float], facing_az: float, render_kwargs: Dict[str, Any], visible: bool = True) -> None:
        rk = dict(render_kwargs)
        rk["angle"] = compute_view_angle_deg(pos, facing_az, cam_pos)
        rk["ground_shadow"] = False  # Real 3D Blender low-sun shadow handles ground contact!
        out[cid] = {
            "visible": visible,
            "pos": pos,
            "facing_az": facing_az,
            "rot_z": compute_billboard_rot_z(pos, cam_pos),
            "render_kwargs": rk,
        }

    # ------------------------------------------------------------------
    # SCENE 1: DIOMEDE (Arka + Kapten Soren)
    # ------------------------------------------------------------------
    if scene_name == "diomede":
        arka_m = _lipsync_val(lipsync_curves, "arka", frame, t)
        soren_m = _lipsync_val(lipsync_curves, "kapten_soren", frame, t)

        # --- ARKA ---
        if t < 4.0:
            # Hook: Arka grinning & spinning snowball on raised right index finger!
            pos = (-1.35, 1.50, 2.40)
            facing = -90.0
            bob = math.sin(t * 4.5) * 3.0
            pack("arka", pos, facing, {
                "animation": "free",
                "pelvis_y": bob,
                "torso_lean_deg": 4.0 * math.sin(t * 2.5),
                "head_tilt_deg": -5.0 + 3.0 * math.sin(t * 3.2),
                "right_hand_target": (76.0, 152.0 + bob * 0.5, 48.0),  # Raised spinning snowball!
                "left_hand_target": (-52.0, 274.0, 14.0),
                "eyes": "honey_oval",
                "eyebrows": "thick_arch",
                "mouth": "confident_gap",
                "mouth_open": arka_m,
                "eye_gaze_x": 0.12,
                "eye_gaze_y": -0.05,
            })
        elif t < 7.2:
            # Walking energetically along wooden dock toward Kapten Soren!
            u = ease_cubic_in_out((t - 4.0) / 3.2)
            pos = (lerp(-1.35, 0.42, u), lerp(1.50, 1.55, u), 2.40)
            facing = lerp(-20.0, -55.0, u)
            pack("arka", pos, facing, {
                "animation": "walk",
                "arm_pose": "point" if u > 0.65 else "ready",
                "eyes": "honey_oval",
                "eyebrows": "thick_arch",
                "mouth": "confident_gap",
                "mouth_open": arka_m,
                "eye_gaze_x": 0.25,
            })
        elif t < 16.5:
            # Standing beside Soren pointing across strait to Big Diomede (Russia)
            pos = (0.42, 1.55, 2.40)
            facing = -55.0 if t < 11.5 else -25.0
            gest = math.sin(t * 5.0) * 8.0
            pack("arka", pos, facing, {
                "animation": "free",
                "pelvis_y": math.sin(t * 3.0) * 2.5,
                "torso_lean_deg": 5.0 if t < 11.5 else -3.0,
                "head_tilt_deg": -4.0 if t < 11.5 else 5.0,
                "right_hand_target": (92.0, 188.0 + gest, 42.0) if t < 11.5 else (62.0, 248.0, 26.0),
                "left_hand_target": (-48.0, 268.0, 18.0),
                "eyes": "starry" if t < 11.5 else "shocked",
                "eyebrows": "raised",
                "mouth": "confident_gap" if t < 11.5 else "small_o",
                "mouth_open": arka_m,
                "eye_gaze_x": 0.35,
            })
        else:
            # 16.5 - 25.0: Steps cautiously onto cracking thin sea-ice shelf, then yanked back by Soren at 20.5s!
            if t < 19.6:
                u = ease_cubic_in_out((t - 16.5) / 3.1)
                pos = (lerp(-2.25, -2.85, u), lerp(2.75, 3.40, u), lerp(0.45, 0.08, u))
                facing = 125.0
                pack("arka", pos, facing, {
                    "animation": "walk" if u < 0.85 else "free",
                    "pelvis_y": 5.0,
                    "torso_lean_deg": 8.0,
                    "head_tilt_deg": 8.0,
                    "eyes": "focused",
                    "eyebrows": "raised",
                    "mouth": "smirk",
                    "mouth_open": arka_m,
                    "eye_gaze_y": 0.45,
                })
            elif t < 20.8:
                # ICE CRACKS! Panic flail!
                pos = (-2.85, 3.40, 0.08)
                facing = -120.0
                flail = math.sin(t * 28.0) * 14.0
                pack("arka", pos, facing, {
                    "animation": "free",
                    "pelvis_y": -10.0 + abs(flail) * 0.4,
                    "torso_lean_deg": -10.0 + flail * 0.3,
                    "head_tilt_deg": -8.0,
                    "left_hand_target": (-85.0, 145.0 + flail, 36.0),
                    "right_hand_target": (85.0, 145.0 - flail, 36.0),
                    "eyes": "panic",
                    "eyebrows": "worried",
                    "mouth": "open_yell",
                    "mouth_open": max(0.75, arka_m),
                    "sweat_drop": True,
                })
            else:
                # Yanked cleanly backward by Soren onto safe wooden landing!
                u = ease_out_overshoot(clamp01((t - 20.8) / 0.75), s=0.9)
                pos = (lerp(-2.85, -2.35, u), lerp(3.40, 2.55, u), lerp(0.08, 0.45, u))
                facing = -110.0
                pack("arka", pos, facing, {
                    "animation": "free",
                    "pelvis_y": 4.0 * (1.0 - clamp01((t - 21.5) / 0.8)),
                    "torso_lean_deg": lerp(-14.0, 2.0, clamp01((t - 20.8) / 1.2)),
                    "head_tilt_deg": 6.0,
                    "left_hand_target": (-58.0, 228.0, 26.0),
                    "right_hand_target": (58.0, 228.0, 26.0),
                    "eyes": "asymmetric" if t < 22.5 else "honey_oval",
                    "eyebrows": "worried",
                    "mouth": "grin_teeth",
                    "mouth_open": arka_m,
                    "sweat_drop": t < 22.8,
                })

        # --- KAPTEN SOREN ---
        if t < 16.5:
            pos = (1.82, 1.60, 2.40)
            facing = -115.0
            breath = math.sin(t * 2.0) * 1.8
            raise_cal = ease_cubic_in_out(clamp01((t - 7.0) / 1.0))
            pack("kapten_soren", pos, facing, {
                "animation": "free",
                "pelvis_y": breath,
                "torso_lean_deg": -2.0,
                "head_tilt_deg": 3.0 * math.sin(t * 1.4),
                # Left hand raises torn SENIN calendar; right hand points across with brass binoculars!
                "left_hand_target": (-68.0, lerp(272.0, 194.0, raise_cal), 36.0),
                "right_hand_target": (88.0, lerp(262.0, 186.0, raise_cal), 38.0),
                "eyes": "chill",
                "eyebrows": "skeptical",
                "mouth": "smirk",
                "mouth_open": soren_m,
                "eye_gaze_x": -0.28,
            })
        else:
            pos = (-1.90, 2.60, 0.45)
            facing = -115.0 if t < 22.5 else -90.0
            pull_t = clamp01((t - 20.4) / 0.55)
            lift_bino = ease_cubic_in_out(clamp01((t - 22.8) / 0.9))
            shake = math.sin(t * 16.0) * 10.0 if 21.4 <= t <= 22.8 else 0.0
            if t < 22.6:
                rh = (lerp(66.0, 82.0, pull_t), lerp(252.0, 206.0, pull_t), 34.0)
                lh = (-54.0, 268.0, 18.0)
            else:
                # Raises brass binoculars right up to camera lens!
                rh = (lerp(66.0, 32.0, lift_bino), lerp(230.0, 154.0, lift_bino), lerp(28.0, 56.0, lift_bino))
                lh = (lerp(-54.0, -28.0, lift_bino), lerp(255.0, 158.0, lift_bino), lerp(20.0, 54.0, lift_bino))
            pack("kapten_soren", pos, facing, {
                "animation": "free",
                "pelvis_y": 2.0,
                "torso_lean_deg": -4.0 if t < 22.0 else 4.0,
                "head_tilt_deg": shake,
                "right_hand_target": rh,
                "left_hand_target": lh,
                "eyes": "suspicious" if t < 22.8 else "chill",
                "eyebrows": "angry" if 20.4 <= t <= 22.4 else "skeptical",
                "mouth": "frown" if 20.4 <= t <= 22.4 else "smirk",
                "mouth_open": soren_m,
            })

    # ------------------------------------------------------------------
    # SCENE 2: RJUKAN (Arka + Astrid + Kakek Henrik)
    # ------------------------------------------------------------------
    elif scene_name == "rjukan":
        arka_m = _lipsync_val(lipsync_curves, "arka", frame, t)
        astrid_m = _lipsync_val(lipsync_curves, "astrid", frame, t)
        henrik_m = _lipsync_val(lipsync_curves, "kakek_henrik", frame, t)

        # --- ARKA ---
        if t < 32.5:
            # Peeking out from behind snow-covered streetlamp rubbing cold hands!
            u = ease_cubic_in_out(clamp01((t - 27.2) / 1.4))
            pos = (lerp(-2.35, -1.55, u), -2.05, 0.0)
            facing = -80.0
            shiver = math.sin(t * 24.0) * 3.5
            pack("arka", pos, facing, {
                "animation": "free",
                "pelvis_y": 6.0 + abs(shiver) * 0.4,
                "torso_lean_deg": 5.0 + shiver * 0.4,
                "head_tilt_deg": shiver * 0.8,
                "left_hand_target": (-26.0 + shiver, 232.0, 42.0),
                "right_hand_target": (26.0 - shiver, 232.0, 42.0),
                "eyes": "shocked" if t < 29.0 else "honey_oval",
                "eyebrows": "worried",
                "mouth": "grit_teeth" if t < 29.0 else "confident_gap",
                "mouth_open": arka_m,
                "blush": True,
            })
        elif t < 47.0:
            # Walks toward sunlit square, jaw-dropped watching Henrik sunbathe in snow!
            u = ease_cubic_in_out(clamp01((t - 40.0) / 2.2))
            pos = (lerp(-1.55, -1.05, u), lerp(-1.20, 0.45, u), 0.0)
            facing = lerp(-30.0, 15.0, u)
            pack("arka", pos, facing, {
                "animation": "walk" if (40.0 <= t <= 42.0) else "free",
                "pelvis_y": -3.0 if t > 42.0 else 0.0,
                "torso_lean_deg": 6.0 if t > 42.0 else 2.0,
                "head_tilt_deg": -8.0 if 39.5 <= t <= 41.5 else 3.0,
                "right_hand_target": (78.0, 198.0, 38.0),
                "left_hand_target": (-48.0, 266.0, 16.0),
                "eyes": "starry" if t > 40.0 else "shocked",
                "eyebrows": "raised",
                "mouth": "small_o" if t < 43.0 else "confident_gap",
                "mouth_open": arka_m,
                "eye_gaze_x": 0.42,
            })
        else:
            # Leans in close to peer at Henrik's sunglasses reflection (Match-Cut!)
            u = ease_cubic_in_out(clamp01((t - 47.0) / 1.2))
            pos = (lerp(-1.05, -0.35, u), lerp(0.45, 0.60, u), 0.0)
            facing = 10.0
            pack("arka", pos, facing, {
                "animation": "free",
                "pelvis_y": 14.0 * u,
                "torso_lean_deg": 14.0 * u,
                "head_tilt_deg": 6.0,
                "left_hand_target": (-42.0, 255.0, 24.0),
                "right_hand_target": (46.0, 248.0, 28.0),
                "eyes": "focused",
                "eyebrows": "raised",
                "mouth": "small_o",
                "mouth_open": arka_m,
                "eye_gaze_x": 0.48,
            })

        # --- ASTRID (on cliffside heliostat observation deck at Z=28.0m) ---
        pos_a = (-1.60, 21.80, 28.00)
        facing_a = -95.0
        tap_u = math.sin(clamp01((t - 33.4) / 0.45) * math.pi)
        pack("astrid", pos_a, facing_a, {
            "animation": "free",
            "pelvis_y": math.sin(t * 2.2) * 1.5,
            "torso_lean_deg": 3.0,
            "head_tilt_deg": -4.0 if t < 34.5 else 3.0,
            # Left hand holds orange industrial tablet; right hand taps green ACTIVATE button!
            "left_hand_target": (-34.0, 246.0, 44.0),
            "right_hand_target": (36.0 - tap_u * 26.0, 242.0 - tap_u * 10.0, 48.0 + tap_u * 12.0),
            "eyes": "focused" if t < 34.8 else "happy",
            "eyebrows": "flat" if t < 34.8 else "happy",
            "mouth": "smirk" if t < 35.0 else "grin_teeth",
            "mouth_open": astrid_m,
            "eye_gaze_x": 0.12,
            "eye_gaze_y": 0.25 if t < 34.2 else -0.1,
        })

        # --- KAKEK HENRIK (seated comfortably in beach chair in the sunlit square!) ---
        # Seated offset: beach chair sling sits at Z=0.42m; pelvis crouched gently in chair
        pos_h = (0.90, 0.80, 0.0)
        facing_h = -105.0
        thumb_u = ease_out_overshoot(clamp01((t - 44.8) / 0.7), s=0.8)
        sip_u = math.sin(clamp01((t - 42.2) / 1.8) * math.pi)
        pack("kakek_henrik", pos_h, facing_h, {
            "animation": "free",
            "pelvis_y": 24.0 + math.sin(t * 2.0) * 1.6,  # Relaxed lounging posture matching beach chair!
            "torso_lean_deg": -7.0,
            "head_tilt_deg": 5.0 + math.sin(t * 1.8) * 2.5,
            "left_hand_target": (-42.0, 244.0 - sip_u * 48.0, 38.0 + sip_u * 14.0),   # Sipping cocoa!
            "right_hand_target": (lerp(56.0, 88.0, thumb_u), lerp(258.0, 192.0, thumb_u), 40.0),  # Thumbs-up!
            "left_foot_target": (-24.0, 466.0, 26.0),
            "right_foot_target": (24.0, 466.0, 26.0),
            "eyes": "happy",
            "eyebrows": "happy",
            "mouth": "happy_open",
            "mouth_open": max(0.25, henrik_m),
        })

    # ------------------------------------------------------------------
    # SCENE 3: BAARLE (Arka + Bram + Clara)
    # ------------------------------------------------------------------
    else:
        arka_m = _lipsync_val(lipsync_curves, "arka", frame, t)
        bram_m = _lipsync_val(lipsync_curves, "bram", frame, t)
        clara_m = _lipsync_val(lipsync_curves, "clara", frame, t)

        # --- ARKA ---
        if t < 59.5:
            # Playfully hops across the white (+) border tiles inside the café!
            hop_u = clamp01((t - 54.0) / 1.2)
            hop_arc = math.sin(hop_u * math.pi) * 0.32
            pos = (lerp(-1.10, 0.85, ease_cubic_in_out(hop_u)), 3.25, hop_arc)
            facing = -110.0
            pack("arka", pos, facing, {
                "animation": "jump" if (54.0 <= t <= 55.2) else "free",
                "pelvis_y": math.sin(t * 4.0) * 3.0,
                "torso_lean_deg": 4.0,
                "right_hand_target": (76.0, 202.0, 34.0),
                "left_hand_target": (-52.0, 264.0, 18.0),
                "eyes": "honey_oval",
                "eyebrows": "thick_arch",
                "mouth": "confident_gap",
                "mouth_open": arka_m,
                "eye_gaze_x": -0.25,
            })
        elif t < 70.0:
            # Laughing warmly with Bram as Clara lifts her feet onto chair rung!
            pos = (0.95, 3.35, 0.0)
            facing = -135.0
            is_laugh = t >= 67.5
            pack("arka", pos, facing, {
                "animation": "laugh" if is_laugh else "free",
                "pelvis_y": math.sin(t * 10.0) * 4.0 if is_laugh else 0.0,
                "torso_lean_deg": -5.0 if is_laugh else 4.0,
                "eyes": "happy" if is_laugh else "honey_oval",
                "eyebrows": "happy" if is_laugh else "raised",
                "mouth": "happy_open" if is_laugh else "confident_gap",
                "mouth_open": max(0.55, arka_m) if is_laugh else arka_m,
                "eye_gaze_x": -0.35,
            })
        else:
            # FINALE (70.0 - 75.0): Straddling the B | NL street border outside café, sipping coffee, winking & snapping!
            pos = (0.0, -2.50, 0.0)
            facing = -90.0  # Facing camera squarely!
            sip_u = math.sin(clamp01((t - 71.2) / 1.4) * math.pi)
            snap_u = ease_out_overshoot(clamp01((t - 73.9) / 0.45), s=1.0)
            is_wink = t >= 73.6
            pack("arka", pos, facing, {
                "animation": "free",
                "pelvis_y": 4.0 + math.sin(t * 3.0) * 2.0,
                "torso_lean_deg": lerp(0.0, -3.5, snap_u),
                "head_tilt_deg": lerp(-3.0, 7.0, snap_u),
                # Wide straddle stance: left foot firmly on B side, right foot firmly on NL side!
                "left_foot_target": (-34.0, 476.0, 0.0),
                "right_foot_target": (34.0, 476.0, 0.0),
                # Left hand holds coffee cup & sips; right hand snaps fingers at camera!
                "left_hand_target": (-46.0 + sip_u * 16.0, 238.0 - sip_u * 52.0, 38.0 + sip_u * 14.0),
                "right_hand_target": (lerp(58.0, 82.0, snap_u), lerp(255.0, 178.0, snap_u), lerp(24.0, 52.0, snap_u)),
                "eyes": "smug" if is_wink else "honey_oval",
                "eyebrows": "skeptical" if is_wink else "thick_arch",
                "mouth": "confident_gap",
                "mouth_open": arka_m,
                "eye_gaze_x": 0.0,
            })

        # --- BRAM (Barista behind oak bar counter on Netherlands +X side) ---
        pos_b = (0.78, 6.05, 0.0)
        facing_b = -95.0
        slide_u = ease_out_overshoot(clamp01((t - 56.2) / 2.2), s=0.6)
        is_laugh_b = 67.5 <= t < 70.0
        is_wave_b = t >= 70.0
        if is_wave_b:
            pack("bram", (0.85, 0.95, 0.0), -90.0, {
                "animation": "wave",
                "eyes": "happy",
                "eyebrows": "happy",
                "mouth": "grin_teeth",
            })
        elif is_laugh_b:
            pack("bram", pos_b, facing_b, {
                "animation": "laugh",
                "eyes": "happy",
                "eyebrows": "happy",
                "mouth": "happy_open",
                "mouth_open": 0.6,
            })
        else:
            # Theatrical magician slide pushing latte cup 30cm from NL (+X) to Belgium (-X)!
            pack("bram", pos_b, facing_b, {
                "animation": "free",
                "pelvis_y": math.sin(t * 3.0) * 2.0,
                "torso_lean_deg": lerp(4.0, -8.0, slide_u),
                "head_tilt_deg": lerp(-4.0, 6.0, slide_u),
                "right_hand_target": (lerp(42.0, -68.0, slide_u), 232.0, 44.0),
                "left_hand_target": (-44.0, 256.0, 26.0),
                "eyes": "honey_oval",
                "eyebrows": "raised",
                "mouth": "grin_teeth" if slide_u > 0.3 else "smirk",
                "mouth_open": bram_m,
                "eye_gaze_x": lerp(0.1, -0.35, slide_u),
            })

        # --- CLARA (Seated at border café table/chair in Belgium -X, feet initially on NL!) ---
        if t >= 70.0:
            pack("clara", (-0.85, 0.95, 0.0), -90.0, {
                "animation": "wave",
                "eyes": "happy",
                "eyebrows": "happy",
                "mouth": "happy_open",
            })
        else:
            pos_c = (-0.55, 3.85, 0.0)
            facing_c = -65.0
            lift_feet = ease_out_overshoot(clamp01((t - 66.8) / 0.85), s=0.95)
            look_down = ease_cubic_in_out(clamp01((t - 59.8) / 0.8))
            pack("clara", pos_c, facing_c, {
                "animation": "free",
                "pelvis_y": 18.0 + lift_feet * 4.0,  # Perched on café chair!
                "torso_lean_deg": lerp(2.0, 9.0, look_down) * (1.0 - lift_feet * 0.6),
                "head_tilt_deg": lerp(2.0, 12.0, look_down),
                # Comedic lift of BOTH feet off NL floor onto chair cross-rung so she's 100% in Belgium!
                "left_foot_target": (-20.0, lerp(474.0, 412.0, lift_feet), lerp(10.0, 32.0, lift_feet)),
                "right_foot_target": (24.0, lerp(474.0, 412.0, lift_feet), lerp(10.0, 32.0, lift_feet)),
                "left_hand_target": (-42.0, lerp(250.0, 212.0, look_down), 34.0),
                "right_hand_target": (52.0, lerp(244.0, 226.0, lift_feet), 34.0),
                "eyes": "shocked" if 60.0 <= t < 66.8 else ("happy" if t >= 68.5 else "honey_oval"),
                "eyebrows": "skeptical" if t < 68.5 else "raised",
                "mouth": "small_o" if t < 66.8 else "happy_open",
                "mouth_open": max(0.35, clara_m) if t >= 66.8 else clara_m,
                "eye_gaze_y": 0.55 if 60.0 <= t < 66.8 else 0.0,
            })

    return out


# ============================================================================
# 4. HERO PROP & DYNAMIC LIGHTING TIMELINE SYNC
# ============================================================================

def get_scene_dynamic_state(scene_name: str, frame: int) -> Dict[str, Any]:
    """Synchronized hero prop transforms + dynamic story lighting parameters per frame."""
    t = frame / FPS
    if scene_name == "diomede":
        # Snowball spinning above Arka's raised hand (visible 0..4.2s)
        # Sea ice crack progress at 19.6s; lens flare flash at 24.0..25.0s
        flare = clamp01((t - 23.95) / 0.55) if t >= 23.95 else 0.0
        return {
            "snowball_pos": (-1.05, 1.32, 3.85 + math.sin(t * 4.5) * 0.04),
            "snowball_visible": t < 4.3,
            "snowball_rot_z": t * 14.0,
            "ice_crack_factor": clamp01((t - 19.55) / 0.4),
            "dateline_pulse": 0.75 + 0.25 * math.sin(t * 5.0),
            "lens_flare_strength": flare,
            "soren_bino_raise": ease_cubic_in_out(clamp01((t - 22.8) / 0.9)),
        }

    if scene_name == "rjukan":
        # Dynamic Story Lighting Turn:
        # 25..34s: dark blue noon; 34..36.8s: mirrors pivot; 36.5..40.2s: god ray shoots down; 40..49s: warm bright golden square!
        mirror_pivot = ease_cubic_in_out(clamp01((t - 34.0) / 2.6))
        beam_shoot = ease_expo_in_out(clamp01((t - 36.4) / 3.4))
        square_lit = ease_out_overshoot(clamp01((t - 39.4) / 0.9), s=0.5)
        match_flash = clamp01((t - 48.35) / 0.55) if t >= 48.35 else 0.0
        return {
            "mirror_pivot": mirror_pivot,
            "beam_shoot": beam_shoot,
            "square_lit": clamp01(square_lit),
            "match_flash": match_flash,
        }

    # Baarle: Latte cup slides cleanly 30cm across NL (+0.42) -> B (-0.42) brass border strip on oak bar!
    cup_slide = ease_out_overshoot(clamp01((t - 56.2) / 2.2), s=0.45)
    return {
        "latte_pos": (lerp(0.42, -0.42, cup_slide), 4.98, 1.07),
        "arka_finale_cup_visible": t >= 70.0,
        "arka_finale_cup_pos": (-0.28, -2.72, 1.18 + math.sin(clamp01((t - 71.2) / 1.4) * math.pi) * 0.24),
        "glitch_outro": clamp01((t - 74.55) / 0.35) if t >= 74.55 else 0.0,
    }
