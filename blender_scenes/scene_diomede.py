"""World 1 (v2 Audited): Little Diomede Pier, Ignaluk Stilt Village, Jagged Bering Sea Ice & Thin Date Line."""
from __future__ import annotations

import math
import os
import random
from typing import Any, Dict, List

import bpy
from mathutils import Vector

from animation.storyboard import DOCK_Z, ICE_LEDGE_Z, compute_billboard_rot_z, get_camera_at_frame, get_characters_at_frame, get_scene_dynamic_state
from blender_scenes.materials_lib import (
    add_box,
    add_cylinder,
    add_decal_plane,
    add_sphere,
    clear_scene,
    configure_render_eevee,
    create_character_card,
    get_or_create_collection,
    make_cel_pbr_material,
    make_decal_material,
    make_emissive_material,
    make_hologram_curtain_material,
    point_camera_at,
    set_transition_flash,
    setup_world_sky,
)
from blender_scenes.props_3d import (
    build_dock_bollard_and_rope,
    build_ignaluk_stilt_house,
    build_jagged_ice_floe,
    build_jagged_mountain_ridge,
    build_wooden_dory_boat,
)
from characters.npc_generator import NPC_ROSTER
from project_config import CHAR_HEIGHTS_M, DECALS_DIR


def build_and_bind_diomede(
    sprites_dir: str,
    start_frame: int,
    end_frame: int,
    width: int = 720,
    height: int = 1280,
    samples: int = 8,
) -> bpy.types.Scene:
    clear_scene()
    scene = configure_render_eevee(width=width, height=height, fps=30, samples=samples, use_motion_blur=True)

    col_world = get_or_create_collection("COL_01_Diomede")
    col_snow = get_or_create_collection("COL_01_SnowParticles")

    # Arctic Low Sun Twilight Sky + subtle blue sea haze
    setup_world_sky(
        zenith_color=(0.06, 0.14, 0.30),
        horizon_color=(0.48, 0.60, 0.78),
        strength=0.78,
        haze_density=0.0028,
        haze_color=(0.64, 0.80, 0.96),
    )

    # ---------------- MATERIALS ----------------
    m_dock_wood = make_cel_pbr_material("DiomedeDockWood", (0.32, 0.24, 0.18), (0.14, 0.24, 0.44), roughness=0.36, bump_scale=6.0, bump_strength=0.26, pattern="wood", color_b=(0.20, 0.15, 0.12))
    m_dock_dark = make_cel_pbr_material("DiomedeDockDark", (0.22, 0.17, 0.13), (0.10, 0.18, 0.34), roughness=0.45, bump_scale=6.0, pattern="wood")
    m_snow = make_cel_pbr_material("ArcticSnow", (0.88, 0.93, 0.98), (0.36, 0.54, 0.80), roughness=0.34, bump_scale=5.0, bump_strength=0.14, pattern="snow", color_b=(0.76, 0.86, 0.96))
    m_sea_ice = make_cel_pbr_material("SeaIceJagged", (0.76, 0.89, 0.97), (0.28, 0.48, 0.76), roughness=0.16, bump_scale=6.0, bump_strength=0.16, pattern="snow", color_b=(0.58, 0.78, 0.92))
    m_ocean = make_cel_pbr_material("BeringOcean", (0.04, 0.14, 0.26), (0.02, 0.08, 0.18), roughness=0.14, bump_scale=3.0, bump_strength=0.22, pattern="water", color_b=(0.09, 0.24, 0.38))
    m_rock = make_cel_pbr_material("GraniteCliff", (0.24, 0.26, 0.31), (0.10, 0.17, 0.32), roughness=0.84, bump_scale=2.2, bump_strength=0.35, pattern="noise", color_b=(0.14, 0.16, 0.21))
    m_big_diomede = make_cel_pbr_material("BigDiomedeMesa", (0.13, 0.17, 0.25), (0.06, 0.11, 0.24), roughness=0.88, bump_scale=1.6, bump_strength=0.28, pattern="noise")
    m_house_red = make_cel_pbr_material("IgnalukRed", (0.58, 0.22, 0.20), (0.20, 0.24, 0.42), roughness=0.66, bump_scale=5.0, pattern="wood")
    m_house_blue = make_cel_pbr_material("IgnalukBlue", (0.26, 0.40, 0.52), (0.14, 0.22, 0.40), roughness=0.66, bump_scale=5.0, pattern="wood")
    m_house_ochre = make_cel_pbr_material("IgnalukOchre", (0.68, 0.52, 0.28), (0.24, 0.28, 0.42), roughness=0.66, bump_scale=5.0, pattern="wood")
    m_white_trim = make_cel_pbr_material("IgnalukWhiteTrim", (0.92, 0.93, 0.95), (0.38, 0.48, 0.68), roughness=0.55)
    m_roof_corr = make_cel_pbr_material("CorrugatedRoof", (0.26, 0.29, 0.34), (0.12, 0.18, 0.30), roughness=0.45, metallic=0.6)
    m_rust_iron = make_cel_pbr_material("RustedBollardIron", (0.30, 0.18, 0.14), (0.12, 0.16, 0.26), roughness=0.68, metallic=0.72, pattern="metal")
    m_rope = make_cel_pbr_material("FrozenHempRope", (0.64, 0.54, 0.38), (0.28, 0.30, 0.42), roughness=0.82, pattern="noise")
    m_crate_blue = make_cel_pbr_material("CrateBlue", (0.12, 0.44, 0.74), (0.08, 0.22, 0.46), roughness=0.42)
    m_crate_org = make_cel_pbr_material("CrateOrange", (0.86, 0.38, 0.10), (0.32, 0.20, 0.28), roughness=0.42)
    m_drum_red = make_cel_pbr_material("FuelDrumRed", (0.72, 0.14, 0.14), (0.24, 0.16, 0.28), roughness=0.38, metallic=0.55)
    m_brass = make_cel_pbr_material("BrassClassic", (0.82, 0.64, 0.24), (0.36, 0.28, 0.16), roughness=0.24, metallic=0.88)
    m_net = make_cel_pbr_material("FrozenFishNet", (0.22, 0.38, 0.36), (0.12, 0.22, 0.32), roughness=0.75)
    m_white_hull = make_cel_pbr_material("CutterWhite", (0.88, 0.90, 0.94), (0.34, 0.46, 0.66), roughness=0.35)
    m_dark = make_cel_pbr_material("DarkGear", (0.14, 0.16, 0.20), (0.08, 0.12, 0.20), roughness=0.65)

    m_win_glow = make_emissive_material("WarmWindowGlow", (1.0, 0.78, 0.38), strength=3.2)
    m_red_beacon = make_emissive_material("RedBeacon", (1.0, 0.14, 0.10), strength=5.5)
    m_holo_curtain = make_hologram_curtain_material("ThinHoloDateLineCurtain")
    m_holo_line = make_emissive_material("DateLineWaterLaser", (1.0, 0.26, 0.18), strength=7.5, alpha=0.85)
    m_snow_flake = make_emissive_material("SnowFlakeGlow", (0.94, 0.98, 1.0), strength=1.15)

    m_sign_decal = make_decal_material("SignDiomedeMat", os.path.join(DECALS_DIR, "sign_diomede_usa_russia.png"), emissive=0.25, roughness=0.48)
    m_holo_decal = make_decal_material("HoloDateLineMat", os.path.join(DECALS_DIR, "holo_dateline.png"), emissive=3.2, use_alpha=True)
    m_cal_decal = make_decal_material("CalSeninMat", os.path.join(DECALS_DIR, "calendar_senin.png"), emissive=0.18, roughness=0.55)

    # ---------------- ARCTIC LOW SUN TWILIGHT LIGHTING ----------------
    bpy.ops.object.light_add(type="SUN", location=(14.0, 62.0, 9.0), rotation=(math.radians(80), math.radians(-12), math.radians(170)))
    sun = bpy.context.active_object
    sun.name = "ArcticLowSun"
    sun.data.energy = 4.0
    sun.data.color = (1.0, 0.72, 0.46)
    sun.data.angle = math.radians(2.2)

    bpy.ops.object.light_add(type="AREA", location=(-2.0, -5.0, 9.0), rotation=(math.radians(40), 0, math.radians(-12)))
    fill = bpy.context.active_object
    fill.name = "ArcticCyanFill"
    fill.data.energy = 1150.0
    fill.data.color = (0.52, 0.78, 1.0)
    fill.data.size = 14.0

    bpy.ops.object.light_add(type="POINT", location=(3.2, 1.2, 4.5))
    p_l = bpy.context.active_object
    p_l.data.energy = 260.0
    p_l.data.color = (1.0, 0.80, 0.50)

    # ---------------- BERING STRAIT OCEAN & BIG DIOMEDE (RUSSIA) ----------------
    ocean = add_box("BeringOceanPlane", (0.0, 50.0, -0.5), (220.0, 160.0, 1.0), m_ocean, col=col_world)
    # Jagged flat-topped volcanic mesa silhouette of Big Diomede (Russia) across the strait!
    build_jagged_mountain_ridge("BigDiomedeMain", (6.0, 78.0, -0.5), 68.0, 26.0, 22.0, m_big_diomede, seed=42, flat_top=True, col=col_world)
    build_jagged_mountain_ridge("BigDiomedeSnowCap", (6.0, 78.0, 19.2), 54.0, 18.0, 2.2, m_snow, seed=43, flat_top=True, col=col_world)
    build_jagged_mountain_ridge("BigDiomedeFlankL", (-28.0, 84.0, -0.5), 34.0, 22.0, 14.5, m_big_diomede, seed=44, flat_top=True, col=col_world)
    # Warm golden "tomorrow" sunrise rim glow behind Big Diomede horizon
    add_sphere("RussiaHorizonGlow", (16.0, 102.0, 5.5), 14.0, make_emissive_material("HorizonSunDisc", (1.0, 0.64, 0.30), strength=4.2), scale=(2.8, 0.35, 1.0), col=col_world)

    # ---------------- LITTLE DIOMEDE CLIFF SLOPE & IGNALUK STILT VILLAGE (LEFT COASTAL BACKDROP — 100% CLEAR OF CAMERA!) ----------------
    # Positioned strictly along X in [-24..-8.5] & Y in [+2..+34] so it frames the LEFT side of the strait unmistakably while NEVER blocking camera!
    build_jagged_mountain_ridge("LittleDiomedeCliffL", (-18.5, 14.0, -0.5), 22.0, 36.0, 16.5, m_rock, seed=11, flat_top=False, col=col_world)
    build_jagged_mountain_ridge("LittleDiomedeSnowL", (-18.0, 14.0, 1.2), 20.0, 34.0, 15.2, m_snow, seed=12, flat_top=False, col=col_world)
    # Secondary rocky headland far behind dock (Y <= -14.0, well behind camera Y=-3.2!)
    build_jagged_mountain_ridge("LittleDiomedeBackCliff", (0.0, -21.0, -0.5), 52.0, 14.0, 14.0, m_rock, seed=15, flat_top=False, col=col_world)

    ignaluk_specs = [
        (-11.2, 5.8, 4.4, m_house_red, math.radians(-58)),
        (-12.6, 11.4, 6.2, m_house_blue, math.radians(-68)),
        (-11.5, 17.5, 5.4, m_house_ochre, math.radians(-74)),
        (-14.8, 8.8, 9.2, m_house_ochre, math.radians(-62)),
        (-15.2, 15.6, 8.8, m_house_red, math.radians(-70)),
        (-12.2, 23.8, 5.0, m_house_blue, math.radians(-80)),
    ]
    smoke_puffs = []
    for hi, (hx, hy, hz, hmat, rz) in enumerate(ignaluk_specs):
        build_ignaluk_stilt_house(
            f"IgnalukHouse_{hi}", (hx, hy, hz), hmat, m_dock_wood, m_white_trim, m_roof_corr, m_win_glow, m_snow, m_rust_iron, rot_z=rz, col=col_world
        )
        for pi in range(3):
            puff = add_sphere(f"ChimneySmoke_{hi}_{pi}", (hx, hy, hz + 3.5 + pi * 0.8), 0.25 + pi * 0.1, m_snow, segments=8, col=col_world)
            smoke_puffs.append((puff, hx, hy, hz + 3.4, hi * 1.2 + pi * 1.1))

    # ---------------- LITTLE DIOMEDE TIMBER CLIFF PIER (DOCK_Z = 2.40m) ----------------
    # Heavy under-deck stringers + beveled wooden pier planks
    add_box("DockSubDeck", (0.0, -0.75, DOCK_Z - 0.16), (17.6, 6.4, 0.18), m_dock_dark, col=col_world)
    for i in range(16):
        py = -3.75 + i * 0.40
        add_box(f"DockPlank_{i}", (0.0, py, DOCK_Z - 0.045), (17.8, 0.36, 0.09), m_dock_wood, bevel=0.012, col=col_world)
    for px in (-8.2, -5.2, -2.2, 1.4, 4.8, 8.2):
        for py in (-3.2, 0.0, 2.25):
            add_cylinder(f"DockPile_{px}_{py}", (px, py, 1.05), 0.16, 2.55, m_dock_dark, verts=10, col=col_world)

    # Snow drifts & crust on outer pier edges (clear of central walking lane!)
    add_box("DockSnowR", (6.2, 1.9, DOCK_Z + 0.04), (5.2, 0.95, 0.12), m_snow, bevel=0.04, col=col_world)
    add_box("DockSnowL", (-6.8, 1.7, DOCK_Z + 0.04), (4.0, 1.1, 0.14), m_snow, bevel=0.04, col=col_world)

    # Wooden safety railing along front dock edge (WIDE OPEN at X in [-4.0, -0.8] for ice-ledge ramp so Soren NEVER clips a post!)
    for rx in (-8.2, -6.2, -4.4, -0.6, 1.4, 3.6, 5.8, 8.0):
        add_box(f"RailPost_{rx}", (rx, 2.50, DOCK_Z + 0.54), (0.12, 0.12, 1.08), m_dock_dark, col=col_world)
    add_box("RailTopR", (3.7, 2.50, DOCK_Z + 1.04), (8.8, 0.14, 0.10), m_dock_wood, col=col_world)
    add_box("RailSnowR", (3.7, 2.50, DOCK_Z + 1.11), (8.8, 0.15, 0.06), m_snow, col=col_world)
    add_box("RailMidR", (3.7, 2.50, DOCK_Z + 0.54), (8.8, 0.10, 0.08), m_dock_wood, col=col_world)
    add_box("RailTopL", (-6.3, 2.50, DOCK_Z + 1.04), (4.0, 0.14, 0.10), m_dock_wood, col=col_world)
    add_box("RailSnowL", (-6.3, 2.50, DOCK_Z + 1.11), (4.0, 0.15, 0.06), m_snow, col=col_world)

    # Continuous wide wooden ramp descending cleanly to elevated coastal sea-ice ledge (ICE_LEDGE_Z = 1.65m — ZERO FLOATING FEET!)
    add_box("IceRampWood", (-2.35, 2.75, (DOCK_Z + ICE_LEDGE_Z) * 0.5 - 0.06), (2.55, 1.25, 0.12), m_dock_wood, rot=(math.radians(-34), 0, 0), col=col_world)
    thin_ice_a = build_jagged_ice_floe("ThinIceLedgeA", (-2.85, 3.35, ICE_LEDGE_Z - 0.14), 1.45, 0.28, m_sea_ice, seed=71, col=col_world)
    thin_ice_b = build_jagged_ice_floe("ThinIceLedgeB", (-4.15, 4.10, ICE_LEDGE_Z - 0.20), 1.30, 0.26, m_sea_ice, seed=72, col=col_world)
    ice_crack_glow = add_box("IceCrackSeam", (-2.85, 3.22, ICE_LEDGE_Z + 0.015), (1.6, 0.04, 0.02), make_emissive_material("IceCrackCyan", (0.45, 0.88, 1.0), strength=2.6), col=col_world)

    # ---------------- HERO & REAL-REFERENCE DOCK PROPS ----------------
    # Cast-iron dock mooring bollards & coiled hemp ropes!
    build_dock_bollard_and_rope("DockBollard_L", (-4.6, 1.85, DOCK_Z), m_rust_iron, m_rope, col=col_world)
    build_dock_bollard_and_rope("DockBollard_R", (4.1, 1.95, DOCK_Z), m_rust_iron, m_rope, col=col_world)
    # Leaning weathered wooden sign: USA / RUSSIA — 3.8 KM
    add_cylinder("SignPost", (3.10, 2.05, DOCK_Z + 0.95), 0.075, 1.95, m_dock_dark, rot=(0, math.radians(5), 0), verts=8, col=col_world)
    add_box("SignBoardBack", (3.16, 2.08, DOCK_Z + 1.54), (1.46, 0.09, 0.74), m_dock_wood, rot=(0, math.radians(5), math.radians(-16)), bevel=0.02, col=col_world)
    add_decal_plane("SignBoardFace", (3.13, 2.01, DOCK_Z + 1.54), 1.40, 0.68, (math.radians(90), math.radians(5), math.radians(-16)), m_sign_decal, col=col_world)

    # Arka's spinning snowball + Soren's torn SENIN calendar & brass binoculars
    snowball = add_sphere("HeroSnowball", (-0.98, 1.32, DOCK_Z + 1.44), 0.13, m_snow, segments=16, col=col_world)
    soren_cal = add_decal_plane("HeroCalendarSenin", (1.42, 1.40, DOCK_Z + 1.05), 0.36, 0.45, (math.radians(90), 0, math.radians(-20)), m_cal_decal, col=col_world)
    soren_bino_root = bpy.data.objects.new("HeroBrassBinoculars", None)
    col_world.objects.link(soren_bino_root)
    for bx in (-0.065, 0.065):
        tube = add_cylinder(f"BinoTube_{bx}", (bx, 0, 0), 0.048, 0.24, m_brass, rot=(math.radians(90), 0, 0), verts=14, col=col_world)
        tube.parent = soren_bino_root
    bridge = add_box("BinoBridge", (0, 0, 0), (0.14, 0.08, 0.04), m_dark, col=col_world)
    bridge.parent = soren_bino_root

    # Upturned ribbed wooden dory boat, beveled fish crates, draped frozen fishnets, fuel drums, radio antenna
    build_wooden_dory_boat("OverturnedDory", (-5.8, -0.4, DOCK_Z), math.radians(22), m_house_blue, m_dock_wood, m_snow, col=col_world)
    for idx, (cx, cy, cz_off, mat_c) in enumerate([(4.9, 0.8, 0.23, m_crate_blue), (5.6, 1.1, 0.23, m_crate_org), (5.2, 0.95, 0.69, m_crate_blue), (-4.5, -1.8, 0.23, m_crate_org)]):
        add_box(f"FishCrate_{idx}", (cx, cy, DOCK_Z + cz_off), (0.74, 0.48, 0.46), mat_c, rot=(0, 0, math.radians(idx * 16)), bevel=0.025, col=col_world)
    # Draped frozen fishnet hanging on far-right railing
    add_box("FrozenNetDrape", (6.8, 2.42, DOCK_Z + 0.65), (1.8, 0.14, 0.82), m_net, rot=(math.radians(8), 0, 0), bevel=0.04, col=col_world)
    for dx, dy in [(6.8, 0.1), (7.4, 0.65), (6.7, 0.95)]:
        add_cylinder(f"FuelDrum_{dx}", (dx, dy, DOCK_Z + 0.45), 0.30, 0.90, m_drum_red, verts=14, col=col_world)
    add_cylinder("RadioTowerMast", (7.8, -3.0, DOCK_Z + 4.4), 0.10, 8.8, m_rust_iron, verts=8, col=col_world)
    add_box("RadioCrossbar", (7.8, -3.0, DOCK_Z + 7.8), (1.8, 0.08, 0.08), m_rust_iron, col=col_world)
    beacon_orb = add_sphere("RadioBeaconOrb", (7.8, -3.0, DOCK_Z + 8.9), 0.16, m_red_beacon, segments=10, col=col_world)

    # ---------------- THIN TRANSLUCENT HOLOGRAPHIC INTERNATIONAL DATE LINE (Y = +24.0m) ----------------
    dateline_wall = add_box("DateLineThinCurtain", (0.0, 24.0, 6.5), (140.0, 0.04, 13.0), m_holo_curtain, col=col_world)
    dateline_wall.visible_shadow = False
    add_box("DateLineWaterLaser", (0.0, 24.0, 0.10), (140.0, 0.18, 0.16), m_holo_line, col=col_world)
    dateline_banner = add_decal_plane("DateLineBanner", (0.0, 23.85, 4.65), 8.2, 4.1, (math.radians(90), 0, 0), m_holo_decal, col=col_world)
    dateline_banner.visible_shadow = False

    # ---------------- LIVING BUSY ANIMATED SET DRESSING ----------------
    # 32 Jagged Polygonal Sea-Ice Floes across Bering Strait
    rng = random.Random(101)
    ice_floes = []
    for fi in range(32):
        fx = rng.uniform(-28.0, 28.0)
        fy = rng.uniform(6.5, 62.0)
        rad = rng.uniform(1.1, 3.4)
        floe = build_jagged_ice_floe(f"JaggedIceFloe_{fi}", (fx, fy, 0.05), rad, rng.uniform(0.18, 0.34), m_sea_ice, seed=200 + fi, col=col_world)
        ice_floes.append((floe, fx, fy, rng.uniform(0, 6.28)))

    # Arctic Coast-Guard Patrol Cutter cruising across strait
    cutter_root = bpy.data.objects.new("ArcticPatrolCutter", None)
    col_world.objects.link(cutter_root)
    for part in [
        add_box("CutterHull", (0, 0, 0.55), (8.6, 2.4, 1.3), m_drum_red, bevel=0.14, col=col_world),
        add_box("CutterCabin", (-0.8, 0, 1.75), (3.4, 1.8, 1.35), m_white_hull, bevel=0.06, col=col_world),
        add_box("CutterBridgeWin", (-0.4, 0, 2.02), (2.2, 1.86, 0.42), m_win_glow, col=col_world),
        add_cylinder("CutterMast", (-0.6, 0, 3.1), 0.08, 1.5, m_white_hull, verts=8, col=col_world),
    ]:
        part.parent = cutter_root

    # 3 UNIFIED 2.5D BEAN-HEAD FISHERMEN NPCs (exact same style as Arka & Soren!)
    npc_dir = os.path.join(sprites_dir, "npcs")
    npc_positions = [(5.6, -0.8, DOCK_Z), (-6.2, -1.6, DOCK_Z), (4.2, -2.5, DOCK_Z)]
    npc_cards = []
    for spec, (nx, ny, nz) in zip(NPC_ROSTER["diomede"], npc_positions):
        nid = spec["id"]
        p0 = os.path.join(npc_dir, nid, "pose_0.png")
        n_obj, n_tex, _ = create_character_card(nid, spec["height"], p0, ambient_tint=(0.86, 0.94, 1.05), col=col_world)
        n_obj.location = Vector((nx, ny, nz))
        npc_cards.append((n_obj, n_tex, nid, nx, ny, nz))

    # 6 Gliding Seabirds + 110 Swirling 3D Snow Particles (isolated in COL_01_SnowParticles!)
    birds = []
    for bi in range(6):
        b_obj = add_box(f"Seabird_{bi}", (0, 22, 11), (0.95, 0.20, 0.05), m_white_hull, col=col_world)
        birds.append((b_obj, 10.0 + bi * 3.0, 9.5 + (bi % 3) * 2.2, bi * 1.1))

    snow_flakes = []
    for si in range(110):
        sx = rng.uniform(-9.0, 9.0)
        sy = rng.uniform(-5.0, 12.0)
        sz = rng.uniform(2.0, 8.5)
        fl = add_sphere(f"SnowFlake_{si}", (sx, sy, sz), rng.uniform(0.015, 0.032), m_snow_flake, segments=6, col=col_snow)
        fl.visible_shadow = False
        snow_flakes.append((fl, sx, sy, sz, rng.uniform(0.8, 1.5), rng.uniform(0, 6.28)))

    # ---------------- HERO PYTHON 2.5D CHARACTERS (Arka & Kapten Soren) ----------------
    char_cards: Dict[str, Any] = {}
    for cid in ("arka", "kapten_soren"):
        first_png = os.path.join(sprites_dir, cid, f"frame_{start_frame:04d}.png")
        obj, tex_node, tint_node = create_character_card(cid, CHAR_HEIGHTS_M[cid], first_png, ambient_tint=(0.88, 0.95, 1.05), col=col_world)
        char_cards[cid] = (obj, tex_node, tint_node)

    # ---------------- CAMERA ----------------
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.clip_start = 0.08
    cam_data.clip_end = 260.0
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    col_world.objects.link(cam_obj)
    scene.camera = cam_obj

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
        cam_pos = get_camera_at_frame("diomede", f)["pos"]

        for cid, (obj, tex_node, _) in char_cards.items():
            st = chars[cid]
            obj.location = Vector(st["pos"])
            obj.rotation_euler = (0.0, 0.0, st["rot_z"])
            obj.hide_render = not st["visible"]
            png_path = os.path.join(sprites_dir, cid, f"frame_{f:04d}.png")
            if os.path.exists(png_path):
                tex_node.image = bpy.data.images.load(png_path, check_existing=True)

        # Unified 2.5D bean-head NPCs face camera smoothly with subtle living idle bob!
        for idx, (n_obj, n_tex, nid, nx, ny, nz) in enumerate(npc_cards):
            px = nx + math.sin(t * 0.7 + idx * 1.9) * 0.45
            py = ny + math.cos(t * 0.5 + idx * 1.3) * 0.25
            n_obj.location = Vector((px, py, nz + abs(math.sin(t * 3.8 + idx)) * 0.03))
            n_obj.rotation_euler = (0.0, 0.0, compute_billboard_rot_z((px, py, nz), cam_pos))

        snowball.location = Vector(dyn["snowball_pos"])
        snowball.rotation_euler = (t * 6.0, t * 4.0, dyn["snowball_rot_z"])
        snowball.hide_render = not dyn["snowball_visible"]

        sp = chars["kapten_soren"]["pos"]
        soren_cal.location = Vector((sp[0] - 0.44, sp[1] - 0.16, sp[2] + 1.05))
        soren_cal.hide_render = t > 16.4
        if t < 16.4:
            soren_bino_root.location = Vector((sp[0] + 0.36, sp[1] - 0.16, sp[2] + 1.15))
            soren_bino_root.rotation_euler = (0.0, 0.0, math.radians(-18))
            soren_bino_root.scale = (1.0, 1.0, 1.0)
        else:
            rb = dyn["soren_bino_raise"]
            soren_bino_root.location = Vector((sp[0] + 0.04, sp[1] - 0.24 - rb * 0.68, sp[2] + 1.24 + rb * 0.14))
            soren_bino_root.rotation_euler = (0.0, 0.0, math.radians(180))
            soren_bino_root.scale = (1.0 + rb * 0.65, 1.0 + rb * 0.65, 1.0 + rb * 0.65)

        cr = dyn["ice_crack_factor"]
        thin_ice_a.rotation_euler = (math.radians(-6.5 * cr), math.radians(4.0 * cr), 0.0)
        thin_ice_a.location.z = (ICE_LEDGE_Z - 0.14) - 0.05 * cr
        thin_ice_b.rotation_euler = (math.radians(5.0 * cr), math.radians(-7.0 * cr), 0.0)
        ice_crack_glow.hide_render = cr < 0.05

        ocean.location.z = -0.5 + math.sin(t * 1.6) * 0.05
        for floe, fx, fy, ph in ice_floes:
            floe.location.x = fx + math.sin(t * 0.35 + ph) * 0.55
            floe.location.z = 0.05 + math.sin(t * 1.5 + ph) * 0.05
            floe.rotation_euler.x = math.sin(t * 1.1 + ph) * 0.025

        cutter_root.location = Vector((-16.0 + t * 1.35, 36.0 + math.sin(t * 0.4) * 1.2, 0.05 + math.sin(t * 2.0) * 0.08))
        cutter_root.rotation_euler = (math.sin(t * 1.8) * 0.025, 0.0, math.radians(4))

        for b_obj, rad, bz, ph in birds:
            ang = t * 0.55 + ph
            b_obj.location = Vector((math.cos(ang) * rad, 20.0 + math.sin(ang) * rad * 0.5, bz + math.sin(t * 2.5 + ph) * 0.6))
            b_obj.rotation_euler = (0.0, math.sin(t * 10.0 + ph) * 0.25, ang + math.pi * 0.5)

        for puff, cx, cy, cz, ph in smoke_puffs:
            cyc = (t * 0.65 + ph) % 3.0
            puff.location = Vector((cx + cyc * 0.45, cy + math.sin(cyc * 2.0) * 0.15, cz + cyc * 0.95))
            sc = 0.65 + cyc * 0.30
            puff.scale = (sc, sc, sc)

        for fl, sx, sy, sz, spd, ph in snow_flakes:
            ny = sy - ((t * 2.2 * spd + ph) % 16.0) + 8.0
            nx = sx + math.sin(t * 2.5 + ph) * 0.50
            nz = 2.0 + ((sz - t * 1.6 * spd) % 6.5)
            fl.location = Vector((nx, ny, nz))

        beacon_orb.hide_render = (int(t * 2.0) % 2) == 1
        dateline_banner.location.z = 4.65 + math.sin(t * 2.5) * 0.16
        # Crisp brief golden glint ONLY on final 8 frames (NO dull gray fade!)
        set_transition_flash(scn, (dyn["lens_flare_strength"] ** 1.5) * 0.72, (1.0, 0.92, 0.72))

    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(update_diomede_frame)
    scene.frame_start = start_frame
    scene.frame_end = end_frame - 1
    scene.frame_set(start_frame)
    update_diomede_frame(scene)
    return scene
