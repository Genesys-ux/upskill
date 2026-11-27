"""World 1: Little Diomede Cliff Dock, Ignaluk Stilt Houses, Bering Strait Sea Ice & International Date Line."""
from __future__ import annotations

import math
import os
import random
from typing import Any, Dict, List

import bpy
from mathutils import Vector

from animation.storyboard import get_camera_at_frame, get_characters_at_frame, get_scene_dynamic_state
from blender_scenes.materials_lib import (
    add_box,
    add_cylinder,
    add_decal_plane,
    add_sphere,
    add_stylized_npc,
    clear_scene,
    configure_render_eevee,
    create_character_card,
    make_cel_pbr_material,
    make_decal_material,
    make_emissive_material,
    point_camera_at,
    set_transition_flash,
    setup_world_sky,
)
from project_config import CHAR_HEIGHTS_M, DECALS_DIR


def build_and_bind_diomede(
    sprites_dir: str,
    start_frame: int,
    end_frame: int,
    width: int = 720,
    height: int = 1280,
    samples: int = 22,
) -> bpy.types.Scene:
    clear_scene()
    scene = configure_render_eevee(width=width, height=height, fps=30, samples=samples, use_motion_blur=True)

    # Arctic Low Sun Twilight Sky + subtle blue sea haze
    setup_world_sky(
        zenith_color=(0.06, 0.13, 0.28),
        horizon_color=(0.45, 0.56, 0.72),
        strength=0.72,
        haze_density=0.0045,
        haze_color=(0.62, 0.78, 0.94),
    )

    # ---------------- MATERIALS (Cel-Shaded Semi-Realistic + PBR) ----------------
    m_dock_wood = make_cel_pbr_material("DiomedeDockWood", (0.28, 0.21, 0.16), (0.14, 0.24, 0.42), roughness=0.38, bump_scale=16.0, bump_strength=0.22, pattern="wood", color_b=(0.20, 0.16, 0.13))
    m_snow = make_cel_pbr_material("ArcticSnow", (0.88, 0.93, 0.98), (0.38, 0.56, 0.82), roughness=0.34, bump_scale=24.0, bump_strength=0.14, pattern="snow", color_b=(0.78, 0.86, 0.95))
    m_sea_ice = make_cel_pbr_material("SeaIce", (0.76, 0.89, 0.97), (0.30, 0.50, 0.78), roughness=0.16, bump_scale=18.0, bump_strength=0.12, pattern="snow", color_b=(0.62, 0.80, 0.92))
    m_ocean = make_cel_pbr_material("BeringOcean", (0.04, 0.12, 0.22), (0.02, 0.06, 0.14), roughness=0.14, bump_scale=10.0, bump_strength=0.20, pattern="water", color_b=(0.08, 0.20, 0.34))
    m_rock = make_cel_pbr_material("GraniteCliff", (0.22, 0.24, 0.28), (0.10, 0.16, 0.30), roughness=0.82, bump_scale=8.0, bump_strength=0.32, pattern="noise", color_b=(0.14, 0.16, 0.20))
    m_big_diomede = make_cel_pbr_material("BigDiomedeMesa", (0.12, 0.15, 0.22), (0.06, 0.10, 0.22), roughness=0.88, bump_scale=5.0, bump_strength=0.25, pattern="noise")
    m_house_red = make_cel_pbr_material("IgnalukRed", (0.56, 0.22, 0.20), (0.20, 0.24, 0.42), roughness=0.68, bump_scale=14.0, pattern="wood")
    m_house_blue = make_cel_pbr_material("IgnalukBlue", (0.26, 0.38, 0.48), (0.14, 0.22, 0.38), roughness=0.68, bump_scale=14.0, pattern="wood")
    m_house_ochre = make_cel_pbr_material("IgnalukOchre", (0.64, 0.50, 0.28), (0.22, 0.28, 0.42), roughness=0.68, bump_scale=14.0, pattern="wood")
    m_rust_metal = make_cel_pbr_material("RustedMetal", (0.34, 0.20, 0.16), (0.14, 0.18, 0.28), roughness=0.72, metallic=0.65, bump_scale=22.0, pattern="metal")
    m_crate_blue = make_cel_pbr_material("CrateBlue", (0.12, 0.42, 0.72), (0.08, 0.20, 0.45), roughness=0.42)
    m_crate_org = make_cel_pbr_material("CrateOrange", (0.86, 0.38, 0.10), (0.32, 0.20, 0.28), roughness=0.42)
    m_drum_red = make_cel_pbr_material("FuelDrumRed", (0.72, 0.14, 0.14), (0.24, 0.16, 0.28), roughness=0.38, metallic=0.55)
    m_brass = make_cel_pbr_material("BrassClassic", (0.80, 0.62, 0.24), (0.36, 0.28, 0.16), roughness=0.24, metallic=0.88)
    m_win_glow = make_emissive_material("WarmWindowGlow", (1.0, 0.76, 0.38), strength=3.6)
    m_red_beacon = make_emissive_material("RedBeacon", (1.0, 0.12, 0.10), strength=6.0)
    m_holo_beam = make_emissive_material("DateLineHoloBeam", (1.0, 0.16, 0.14), strength=5.5, alpha=0.28)
    m_holo_line = make_emissive_material("DateLineLaser", (1.0, 0.26, 0.18), strength=14.0, alpha=0.92)
    m_snow_flake = make_emissive_material("SnowFlakeGlow", (0.94, 0.98, 1.0), strength=1.4)
    m_white_hull = make_cel_pbr_material("CutterWhite", (0.86, 0.89, 0.92), (0.34, 0.46, 0.66), roughness=0.35)
    m_npc_skin = make_cel_pbr_material("NpcSkin", (0.86, 0.70, 0.58), (0.40, 0.42, 0.56), roughness=0.6)
    m_dark = make_cel_pbr_material("DarkGear", (0.14, 0.16, 0.20), (0.08, 0.12, 0.20), roughness=0.65)

    m_sign_decal = make_decal_material("SignDiomedeMat", os.path.join(DECALS_DIR, "sign_diomede_usa_russia.png"), roughness=0.48)
    m_holo_decal = make_decal_material("HoloDateLineMat", os.path.join(DECALS_DIR, "holo_dateline.png"), emissive=4.8, use_alpha=True)
    m_cal_decal = make_decal_material("CalSeninMat", os.path.join(DECALS_DIR, "calendar_senin.png"), roughness=0.55)

    # ---------------- LIGHTING (Arctic Low Sun Twilight + Blue Shade) ----------------
    # Low warm golden sun behind Big Diomede ("Tomorrow" glow across horizon!)
    bpy.ops.object.light_add(type="SUN", location=(12.0, 60.0, 8.0), rotation=(math.radians(82), math.radians(-12), math.radians(172)))
    sun = bpy.context.active_object
    sun.name = "ArcticLowSun"
    sun.data.energy = 4.2
    sun.data.color = (1.0, 0.68, 0.42)
    sun.data.angle = math.radians(2.2)

    # Cool Arctic cyan-blue fill from Alaska sky (Blue Shade!)
    bpy.ops.object.light_add(type="AREA", location=(-4.0, -5.0, 9.0), rotation=(math.radians(38), 0, math.radians(-20)))
    fill = bpy.context.active_object
    fill.name = "ArcticCyanFill"
    fill.data.energy = 1100.0
    fill.data.color = (0.48, 0.76, 1.0)
    fill.data.size = 12.0

    # Warm dockside practical lantern glow near stilt houses
    bpy.ops.object.light_add(type="POINT", location=(3.2, 1.8, 4.4))
    p_l = bpy.context.active_object
    p_l.data.energy = 240.0
    p_l.data.color = (1.0, 0.78, 0.48)

    # ---------------- OCEAN & BIG DIOMEDE (RUSSIA) ----------------
    ocean = add_box("BeringOceanPlane", (0.0, 48.0, -0.5), (180.0, 140.0, 1.0), m_ocean)
    # Massive flat-topped dark cliff silhouette of Big Diomede (3.8 km across strait, cinematic scale!)
    add_box("BigDiomedeMain", (4.0, 86.0, 10.5), (72.0, 26.0, 24.0), m_big_diomede, rot=(0, 0, math.radians(-8)))
    add_box("BigDiomedeSnowCap", (4.0, 86.0, 22.8), (68.0, 23.0, 1.6), m_snow, rot=(0, 0, math.radians(-8)))
    add_box("BigDiomedeRidgeL", (-32.0, 92.0, 7.5), (30.0, 20.0, 18.0), m_big_diomede, rot=(0, math.radians(8), math.radians(14)))
    # Warm sunrise rim glow sphere sitting just behind Big Diomede horizon
    add_sphere("RussiaHorizonGlow", (14.0, 104.0, 6.0), 16.0, make_emissive_material("HorizonSunDisc", (1.0, 0.62, 0.30), strength=5.0), scale=(2.8, 0.4, 1.1))

    # ---------------- LITTLE DIOMEDE CLIFF DOCK (Z = 2.40m) ----------------
    # Main timber pier planks
    for i in range(18):
        py = -4.2 + i * 0.40
        add_box(f"DockPlank_{i}", (0.0, py, 2.34), (18.0, 0.36, 0.12), m_dock_wood)
    # Pier pilings dipping into Bering sea
    for px in (-8.2, -5.0, -1.8, 1.8, 5.0, 8.2):
        for py in (-3.6, 0.0, 2.3):
            add_cylinder(f"DockPile_{px}_{py}", (px, py, 1.0), 0.16, 2.7, m_dock_wood, verts=10)
    # Snow drifts & crust on dock edges
    add_box("DockSnowEdgeR", (5.5, 2.1, 2.44), (6.5, 0.85, 0.12), m_snow)
    add_box("DockSnowEdgeL", (-6.4, 1.8, 2.44), (4.5, 1.1, 0.14), m_snow)

    # Wooden safety railing along front edge (open at X in [-4.0, -1.8] for lower ice landing!)
    for rx in (-8.2, -6.2, -4.4, -1.4, 0.6, 2.6, 4.6, 6.6, 8.2):
        add_box(f"RailPost_{rx}", (rx, 2.52, 2.95), (0.12, 0.12, 1.12), m_dock_wood)
    add_box("RailTopR", (3.4, 2.52, 3.45), (9.8, 0.14, 0.10), m_dock_wood)
    add_box("RailSnowR", (3.4, 2.52, 3.52), (9.8, 0.15, 0.06), m_snow)
    add_box("RailMidR", (3.4, 2.52, 2.96), (9.8, 0.10, 0.08), m_dock_wood)
    add_box("RailTopL", (-6.3, 2.52, 3.45), (4.0, 0.14, 0.10), m_dock_wood)
    add_box("RailSnowL", (-6.3, 2.52, 3.52), (4.0, 0.15, 0.06), m_snow)

    # Lower boat landing (Z = 0.45m) + Cracking thin sea-ice shelf (Z = 0.08m) for 00:17–00:24 sequence!
    add_box("LowerLanding", (-2.15, 2.55, 0.35), (2.4, 1.4, 0.20), m_dock_wood)
    add_box("LowerSteps", (-2.15, 1.45, 1.40), (1.3, 1.6, 0.22), m_dock_wood, rot=(math.radians(-42), 0, 0))
    thin_ice_a = add_box("ThinIceShelfA", (-2.95, 3.55, 0.03), (2.2, 1.8, 0.10), m_sea_ice)
    thin_ice_b = add_box("ThinIceShelfB", (-3.85, 4.25, 0.03), (1.6, 1.5, 0.10), m_sea_ice)
    ice_crack_glow = add_box("IceCrackSeam", (-2.88, 3.42, 0.085), (1.7, 0.04, 0.02), make_emissive_material("IceCrackCyan", (0.45, 0.88, 1.0), strength=2.6))

    # ---------------- HERO & BACKGROUND PROPS ----------------
    # Leaning weathered wooden sign: USA / RUSSIA — 3.8 KM
    add_cylinder("SignPost", (3.15, 2.15, 3.35), 0.07, 1.95, m_dock_wood, rot=(0, math.radians(6), 0), verts=8)
    add_box("SignBoardBack", (3.22, 2.18, 3.92), (1.42, 0.08, 0.72), m_dock_wood, rot=(0, math.radians(6), math.radians(-16)))
    add_decal_plane("SignBoardFace", (3.19, 2.12, 3.92), 1.38, 0.68, (math.radians(90), math.radians(6), math.radians(-16)), m_sign_decal)

    # Arka's spinning snowball (animated in handler)
    snowball = add_sphere("HeroSnowball", (-1.05, 1.32, 3.85), 0.13, m_snow, segments=16)

    # Kapten Soren's torn SENIN calendar & brass binoculars (animated with Soren!)
    soren_cal = add_decal_plane("HeroCalendarSenin", (1.42, 1.45, 3.45), 0.34, 0.42, (math.radians(90), 0, math.radians(-22)), m_cal_decal)
    soren_bino_root = bpy.data.objects.new("HeroBrassBinoculars", None)
    bpy.context.collection.objects.link(soren_bino_root)
    for bx in (-0.065, 0.065):
        tube = add_cylinder(f"BinoTube_{bx}", (bx, 0, 0), 0.048, 0.24, m_brass, rot=(math.radians(90), 0, 0), verts=14)
        tube.parent = soren_bino_root
    bridge = add_box("BinoBridge", (0, 0, 0), (0.14, 0.08, 0.04), m_dark)
    bridge.parent = soren_bino_root

    # Overturned wooden fishing boat on snow, fish crates, fuel drums, coiled rope, rusted radio antenna
    add_box("OverturnedBoat", (-5.4, 0.2, 2.65), (3.4, 1.45, 0.75), m_house_blue, rot=(math.radians(170), math.radians(6), math.radians(24)))
    add_box("BoatSnowTop", (-5.4, 0.2, 3.04), (3.0, 1.15, 0.14), m_snow, rot=(0, math.radians(6), math.radians(24)))
    for idx, (cx, cy, mat_c) in enumerate([(4.6, 1.2, m_crate_blue), (5.2, 1.5, m_crate_org), (4.85, 1.35, m_crate_blue), (-4.2, -1.6, m_crate_org)]):
        cz = 2.64 if idx != 2 else 3.12
        add_box(f"FishCrate_{idx}", (cx, cy, cz), (0.72, 0.48, 0.46), mat_c, rot=(0, 0, math.radians(idx * 17)))
    for dx, dy in [(6.4, 0.6), (6.95, 1.1), (6.3, 1.35)]:
        add_cylinder(f"FuelDrum_{dx}", (dx, dy, 2.86), 0.30, 0.90, m_drum_red, verts=14)
    # Rusted radio antenna tower on rocky outcrop with blinking red aviation beacon
    add_cylinder("RadioTowerMast", (7.4, -3.5, 6.8), 0.11, 8.5, m_rust_metal, verts=8)
    add_box("RadioCrossbar", (7.4, -3.5, 10.2), (1.8, 0.08, 0.08), m_rust_metal)
    beacon_orb = add_sphere("RadioBeaconOrb", (7.4, -3.5, 11.1), 0.16, m_red_beacon, segments=10)

    # ---------------- IGNALUK STILT HOUSES ON 45° GRANITE BOULDER SLOPE ----------------
    add_box("LittleDiomedeSlope", (0.0, -14.0, 4.0), (54.0, 24.0, 14.0), m_rock, rot=(math.radians(-32), 0, 0))
    add_box("LittleDiomedeSnowBlanket", (0.0, -13.6, 4.4), (52.0, 22.0, 12.8), m_snow, rot=(math.radians(-32), 0, 0))
    house_specs = [
        (-7.5, -6.4, 5.2, m_house_red),
        (-2.2, -7.8, 6.4, m_house_blue),
        (3.4, -6.8, 5.6, m_house_ochre),
        (8.6, -8.2, 6.8, m_house_red),
        (-5.2, -12.0, 9.2, m_house_ochre),
        (1.6, -12.6, 9.8, m_house_blue),
    ]
    smoke_puffs: List[bpy.types.Object] = []
    for hi, (hx, hy, hz, hmat) in enumerate(house_specs):
        # Tall timber stilts (12-15 ft authentic Ignaluk stilt architecture!)
        for sx in (-1.35, 1.35):
            for sy in (-1.05, 1.05):
                add_cylinder(f"Stilt_{hi}_{sx}_{sy}", (hx + sx, hy + sy, hz - 2.0), 0.11, 4.2, m_dock_wood, verts=8)
        add_box(f"StiltHouse_{hi}", (hx, hy, hz + 1.05), (3.4, 2.7, 2.2), hmat)
        add_box(f"StiltRoof_{hi}", (hx, hy, hz + 2.32), (3.8, 3.0, 0.35), m_snow, rot=(math.radians(-12), 0, 0))
        # Warm glowing windows facing the strait
        for wx in (-0.85, 0.85):
            add_box(f"StiltWin_{hi}_{wx}", (hx + wx, hy + 1.37, hz + 1.15), (0.62, 0.05, 0.68), m_win_glow)
        # Chimney + animated rising smoke puff
        add_cylinder(f"Chimney_{hi}", (hx + 1.0, hy - 0.6, hz + 2.85), 0.14, 1.0, m_rust_metal, verts=8)
        for pi in range(3):
            puff = add_sphere(f"Smoke_{hi}_{pi}", (hx + 1.0, hy - 0.6, hz + 3.6 + pi * 0.8), 0.28 + pi * 0.12, m_snow, segments=8)
            smoke_puffs.append((puff, hx + 1.0, hy - 0.6, hz + 3.4, hi * 1.3 + pi * 1.1))

    # ---------------- INTERNATIONAL DATE LINE HOLOGRAM (Y = +24.0m) ----------------
    dateline_wall = add_box("DateLineWall", (0.0, 24.0, 8.0), (140.0, 0.08, 18.0), m_holo_beam)
    add_box("DateLineWaterLaser", (0.0, 24.0, 0.12), (140.0, 0.28, 0.24), m_holo_line)
    dateline_banner = add_decal_plane("DateLineBanner", (0.0, 23.85, 4.65), 8.2, 4.1, (math.radians(90), 0, 0), m_holo_decal)

    # ---------------- LIVING BUSY ANIMATED SET DRESSING ----------------
    # 1) 28 Bobbing Sea-Ice Floes across Bering Strait
    rng = random.Random(101)
    ice_floes = []
    for fi in range(28):
        fx = rng.uniform(-28.0, 28.0)
        fy = rng.uniform(6.0, 62.0)
        sx = rng.uniform(1.8, 5.6)
        sy = rng.uniform(1.4, 4.4)
        floe = add_box(f"IceFloe_{fi}", (fx, fy, 0.06), (sx, sy, 0.22), m_sea_ice, rot=(0, 0, rng.uniform(0, 6.28)))
        ice_floes.append((floe, fx, fy, rng.uniform(0, 6.28)))

    # 2) Distant Arctic Coast-Guard Patrol Cutter cruising across strait!
    cutter_root = bpy.data.objects.new("ArcticPatrolCutter", None)
    bpy.context.collection.objects.link(cutter_root)
    c_hull = add_box("CutterHull", (0, 0, 0.55), (8.2, 2.4, 1.3), m_drum_red)
    c_cabin = add_box("CutterCabin", (-0.8, 0, 1.75), (3.4, 1.8, 1.35), m_white_hull)
    c_bridge = add_box("CutterBridgeWin", (-0.4, 0, 2.0), (2.2, 1.86, 0.42), m_win_glow)
    for part in (c_hull, c_cabin, c_bridge):
        part.parent = cutter_root

    # 3) 3 Animated Background Fishermen NPCs working on far sides of the dock
    bg_npcs = [
        (add_stylized_npc("FishermanNPC_1", (5.8, -0.4, 2.40), m_crate_org, m_npc_skin, m_dark, m_dark, 0.96), 5.8, -0.4, 2.40, 0.0),
        (add_stylized_npc("FishermanNPC_2", (-6.2, -1.2, 2.40), m_house_blue, m_npc_skin, m_crate_org, m_dark, 0.98), -6.2, -1.2, 2.40, 2.1),
        (add_stylized_npc("FishermanNPC_3", (4.2, -2.5, 2.40), m_house_red, m_npc_skin, m_dark, m_dark, 0.94), 4.2, -2.5, 2.40, 4.0),
    ]

    # 4) 6 Gliding Arctic Seabirds circling high over the strait
    birds = []
    for bi in range(6):
        b_obj = add_box(f"Seabird_{bi}", (0, 22, 11), (0.9, 0.22, 0.06), m_white_hull)
        birds.append((b_obj, 10.0 + bi * 3.0, 9.5 + (bi % 3) * 2.2, bi * 1.1))

    # 5) 140 Swirling 3D Snow Particles blowing across foreground/midground!
    snow_flakes = []
    for si in range(140):
        sx = rng.uniform(-9.0, 9.0)
        sy = rng.uniform(-6.0, 12.0)
        sz = rng.uniform(1.0, 8.5)
        fl = add_sphere(f"SnowFlake_{si}", (sx, sy, sz), rng.uniform(0.018, 0.042), m_snow_flake, segments=6)
        snow_flakes.append((fl, sx, sy, sz, rng.uniform(0.8, 1.6), rng.uniform(0, 6.28)))

    # ---------------- PYTHON 2.5D CHARACTERS (Arka & Kapten Soren) ----------------
    char_cards: Dict[str, Any] = {}
    for cid in ("arka", "kapten_soren"):
        first_png = os.path.join(sprites_dir, cid, f"frame_{start_frame:04d}.png")
        obj, tex_node, tint_node = create_character_card(cid, CHAR_HEIGHTS_M[cid], first_png, ambient_tint=(0.86, 0.94, 1.05))
        char_cards[cid] = (obj, tex_node, tint_node)

    # ---------------- CAMERA ----------------
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.clip_start = 0.08
    cam_data.clip_end = 260.0
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Bake camera keyframes so EEVEE Motion Blur calculates real sub-frame velocity on whip-pans!
    for f in range(max(0, start_frame - 1), end_frame + 2):
        c_st = get_camera_at_frame("diomede", f)
        point_camera_at(cam_obj, c_st["pos"], c_st["target"], c_st["lens"], c_st["roll"])
        cam_obj.keyframe_insert(data_path="location", frame=f)
        cam_obj.keyframe_insert(data_path="rotation_quaternion", frame=f)
        cam_data.keyframe_insert(data_path="lens", frame=f)

    # ---------------- DYNAMIC FRAME UPDATE HANDLER ----------------
    def update_diomede_frame(scn: bpy.types.Scene) -> None:
        f = scn.frame_current
        t = f / 30.0
        dyn = get_scene_dynamic_state("diomede", f)
        chars = get_characters_at_frame("diomede", f)

        # Update character cards + swap exact yaw-synced RGBA PNG sprite
        for cid, (obj, tex_node, _) in char_cards.items():
            st = chars[cid]
            obj.location = Vector(st["pos"])
            obj.rotation_euler = (0.0, 0.0, st["rot_z"])
            obj.hide_render = not st["visible"]
            png_path = os.path.join(sprites_dir, cid, f"frame_{f:04d}.png")
            if os.path.exists(png_path):
                img = bpy.data.images.load(png_path, check_existing=True)
                tex_node.image = img

        # Hero props sync
        snowball.location = Vector(dyn["snowball_pos"])
        snowball.rotation_euler = (t * 6.0, t * 4.0, dyn["snowball_rot_z"])
        snowball.hide_render = not dyn["snowball_visible"]

        # Soren's calendar & binoculars sync
        sp = chars["kapten_soren"]["pos"]
        soren_cal.location = Vector((sp[0] - 0.42, sp[1] - 0.14, sp[2] + 1.05))
        soren_cal.hide_render = t > 16.5
        if t < 16.5:
            soren_bino_root.location = Vector((sp[0] + 0.36, sp[1] - 0.16, sp[2] + 1.15))
            soren_bino_root.rotation_euler = (0.0, 0.0, math.radians(-18))
            soren_bino_root.scale = (1.0, 1.0, 1.0)
        else:
            rb = dyn["soren_bino_raise"]
            # Pulls binoculars straight toward camera at 23.0-24.8s!
            soren_bino_root.location = Vector((sp[0] + 0.05, sp[1] - 0.25 - rb * 0.72, sp[2] + 1.25 + rb * 0.15))
            soren_bino_root.rotation_euler = (0.0, 0.0, math.radians(180))
            soren_bino_root.scale = (1.0 + rb * 0.7, 1.0 + rb * 0.7, 1.0 + rb * 0.7)

        # Cracking thin ice shelf reaction!
        cr = dyn["ice_crack_factor"]
        thin_ice_a.rotation_euler = (math.radians(-6.5 * cr), math.radians(4.0 * cr), 0.0)
        thin_ice_a.location.z = 0.03 - 0.06 * cr
        thin_ice_b.rotation_euler = (math.radians(5.0 * cr), math.radians(-7.0 * cr), 0.0)
        ice_crack_glow.hide_render = cr < 0.05

        # Animated background world
        ocean.location.z = -0.5 + math.sin(t * 1.6) * 0.05
        for floe, fx, fy, ph in ice_floes:
            floe.location.x = fx + math.sin(t * 0.35 + ph) * 0.6
            floe.location.z = 0.06 + math.sin(t * 1.5 + ph) * 0.05
            floe.rotation_euler.x = math.sin(t * 1.1 + ph) * 0.03

        cutter_root.location = Vector((-16.0 + t * 1.35, 36.0 + math.sin(t * 0.4) * 1.2, 0.05 + math.sin(t * 2.0) * 0.08))
        cutter_root.rotation_euler = (math.sin(t * 1.8) * 0.025, 0.0, math.radians(4))

        for npc, nx, ny, nz, ph in bg_npcs:
            npc.location = Vector((nx + math.sin(t * 0.8 + ph) * 0.65, ny + math.cos(t * 0.6 + ph) * 0.35, nz + abs(math.sin(t * 4.5 + ph)) * 0.05))
            npc.rotation_euler.z = math.sin(t * 0.7 + ph) * 0.5

        for b_obj, rad, bz, ph in birds:
            ang = t * 0.55 + ph
            b_obj.location = Vector((math.cos(ang) * rad, 20.0 + math.sin(ang) * rad * 0.5, bz + math.sin(t * 2.5 + ph) * 0.6))
            b_obj.rotation_euler = (0.0, math.sin(t * 10.0 + ph) * 0.25, ang + math.pi * 0.5)

        for puff, cx, cy, cz, ph in smoke_puffs:
            cyc = (t * 0.65 + ph) % 3.0
            puff.location = Vector((cx + cyc * 0.45, cy + math.sin(cyc * 2.0) * 0.15, cz + cyc * 0.95))
            sc = 0.7 + cyc * 0.35
            puff.scale = (sc, sc, sc)

        for fl, sx, sy, sz, spd, ph in snow_flakes:
            ny = sy - ((t * 2.2 * spd + ph) % 16.0) + 8.0
            nx = sx + math.sin(t * 2.5 + ph) * 0.55
            nz = 1.0 + ((sz - t * 1.8 * spd) % 7.5)
            fl.location = Vector((nx, ny, nz))

        beacon_orb.hide_render = (int(t * 2.0) % 2) == 1
        dateline_banner.location.z = 4.65 + math.sin(t * 2.5) * 0.18
        set_transition_flash(scn, dyn["lens_flare_strength"] ** 1.4, (1.0, 0.94, 0.78))

    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(update_diomede_frame)
    scene.frame_start = start_frame
    scene.frame_end = end_frame - 1
    scene.frame_set(start_frame)
    update_diomede_frame(scene)
    return scene
