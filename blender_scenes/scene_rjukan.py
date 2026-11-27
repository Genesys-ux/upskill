"""World 2 (v2 Audited): Rjukan Torg Norwegian Town, Open-Air Cliff Solspeilet Mirrors & Balanced Non-Whiteout God Ray."""
from __future__ import annotations

import math
import os
import random
from typing import Any, Dict, List

import bpy
from mathutils import Vector

from animation.storyboard import CLIFF_DECK_Z, SQUARE_Z, compute_billboard_rot_z, get_camera_at_frame, get_characters_at_frame, get_scene_dynamic_state, lerp
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
    make_soft_godray_material,
    point_camera_at,
    set_mix_rgba_b,
    set_transition_flash,
    setup_world_sky,
)
from blender_scenes.props_3d import (
    build_3d_car,
    build_jagged_mountain_ridge,
    build_norwegian_rjukan_house,
    build_snowy_pine_tree,
    build_solspeilet_heliostat,
    build_striped_beach_chair,
    build_thermos_and_mug,
)
from characters.npc_generator import NPC_ROSTER
from project_config import CHAR_HEIGHTS_M, DECALS_DIR


def build_and_bind_rjukan(
    sprites_dir: str,
    start_frame: int,
    end_frame: int,
    width: int = 720,
    height: int = 1280,
    samples: int = 8,
) -> bpy.types.Scene:
    clear_scene()
    scene = configure_render_eevee(width=width, height=height, fps=30, samples=samples, use_motion_blur=True)

    col_world = get_or_create_collection("COL_02_Rjukan")
    col_snow = get_or_create_collection("COL_02_SnowParticles")

    # Deep Freezing Nordic Blue-Violet Shadow Sky at 12:00 Noon + Atmospheric Snow Haze
    setup_world_sky(
        zenith_color=(0.04, 0.09, 0.24),
        horizon_color=(0.15, 0.24, 0.46),
        strength=0.46,
        haze_density=0.0028,
        haze_color=(0.38, 0.52, 0.76),
    )

    # ---------------- MATERIALS ----------------
    m_cobble = make_cel_pbr_material("RjukanCobble", (0.36, 0.38, 0.42), (0.14, 0.20, 0.38), roughness=0.58, bump_scale=6.0, bump_strength=0.25, pattern="cobble")
    m_cobble_wet = make_cel_pbr_material("RjukanCobbleWet", (0.48, 0.44, 0.36), (0.24, 0.26, 0.38), roughness=0.16, bump_scale=6.0, bump_strength=0.18, pattern="cobble")
    m_snow = make_cel_pbr_material("RjukanSnow", (0.86, 0.91, 0.97), (0.24, 0.38, 0.68), roughness=0.38, bump_scale=4.0, pattern="snow")
    m_icicle = make_cel_pbr_material("RjukanIcicle", (0.78, 0.92, 1.0), (0.35, 0.56, 0.85), roughness=0.10, metallic=0.1)
    m_cliff = make_cel_pbr_material("RjukanBlackCliff", (0.13, 0.15, 0.20), (0.05, 0.08, 0.18), roughness=0.86, bump_scale=1.8, bump_strength=0.35, pattern="noise")
    m_nordic_red = make_cel_pbr_material("NordicRedWood", (0.58, 0.15, 0.14), (0.16, 0.18, 0.36), roughness=0.62, bump_scale=5.0, pattern="wood")
    m_nordic_ochre = make_cel_pbr_material("NordicOchreWood", (0.76, 0.56, 0.20), (0.22, 0.24, 0.38), roughness=0.62, bump_scale=5.0, pattern="wood")
    m_nordic_white = make_cel_pbr_material("NordicWhiteWood", (0.86, 0.85, 0.82), (0.26, 0.34, 0.56), roughness=0.62, bump_scale=5.0, pattern="wood")
    m_white_trim = make_cel_pbr_material("NordicWindowTrim", (0.94, 0.94, 0.92), (0.36, 0.44, 0.64), roughness=0.52)
    m_roof_dark = make_cel_pbr_material("NordicSlateRoof", (0.16, 0.18, 0.24), (0.08, 0.12, 0.24), roughness=0.55)
    m_iron = make_cel_pbr_material("ClassicBlackIron", (0.12, 0.13, 0.16), (0.06, 0.08, 0.15), roughness=0.36, metallic=0.82)
    m_steel = make_cel_pbr_material("HeliostatSteel", (0.54, 0.58, 0.64), (0.20, 0.28, 0.44), roughness=0.30, metallic=0.85)
    m_solar = make_cel_pbr_material("SolarCellBlue", (0.08, 0.18, 0.42), (0.04, 0.10, 0.24), roughness=0.14, metallic=0.65)
    m_pine = make_cel_pbr_material("NordicPine", (0.10, 0.25, 0.16), (0.06, 0.14, 0.22), roughness=0.78)
    m_chair_blue = make_cel_pbr_material("BeachChairBlue", (0.12, 0.44, 0.84), (0.08, 0.22, 0.48), roughness=0.52)
    m_chair_white = make_cel_pbr_material("BeachChairWhite", (0.94, 0.94, 0.92), (0.36, 0.44, 0.62), roughness=0.52)
    m_wood_warm = make_cel_pbr_material("WarmBenchWood", (0.48, 0.30, 0.18), (0.18, 0.20, 0.34), roughness=0.55, pattern="wood")
    m_orange_rubber = make_cel_pbr_material("TabletRubberOrange", (0.92, 0.42, 0.10), (0.36, 0.22, 0.24), roughness=0.48)
    m_car_blue = make_cel_pbr_material("NordicCarBlue", (0.16, 0.36, 0.58), (0.08, 0.18, 0.36), roughness=0.22, metallic=0.45)
    m_car_red = make_cel_pbr_material("NordicCarRed", (0.68, 0.18, 0.18), (0.24, 0.16, 0.30), roughness=0.22, metallic=0.45)
    m_car_glass = make_cel_pbr_material("CarTintedGlass", (0.10, 0.18, 0.26), (0.05, 0.10, 0.18), roughness=0.08, metallic=0.5)
    m_tire = make_cel_pbr_material("RubberTire", (0.08, 0.08, 0.10), (0.04, 0.04, 0.06), roughness=0.82)

    m_win_warm = make_emissive_material("RjukanWinWarm", (1.0, 0.78, 0.36), strength=2.6)
    m_lamp_glow = make_emissive_material("StreetLampGlow", (1.0, 0.84, 0.48), strength=4.2)
    m_tail_red = make_emissive_material("CarTailRed", (1.0, 0.14, 0.10), strength=3.0)
    m_mirror_surface = make_emissive_material("SolspeiletMirrorGlow", (1.0, 0.90, 0.64), strength=1.5)
    # ANTI-WHITEOUT FEATHERED GOD RAY (Layer Weight Facing -> Transparent + Emission 0.38!)
    m_godray_soft = make_soft_godray_material("SoftVolumetricGodRay", (1.0, 0.84, 0.42), strength=0.38, max_opacity=0.24)
    m_spotlight_patch = make_emissive_material("SunlitSquarePatch", (1.0, 0.88, 0.52), strength=0.42, alpha=0.18)
    m_snow_flake = make_emissive_material("SnowFlakeR", (0.88, 0.94, 1.0), strength=1.0)

    m_tablet_ui = make_decal_material("AstridTabletUI", os.path.join(DECALS_DIR, "tablet_heliostat_ui.png"), emissive=2.0)
    m_sign_rjukan = make_decal_material("RjukanSignMat", os.path.join(DECALS_DIR, "sign_rjukan_torg.png"), emissive=0.18, roughness=0.42)

    # ---------------- BALANCED DYNAMIC STORY LIGHTING (ZERO WHITE-OUT!) ----------------
    bpy.ops.object.light_add(type="SUN", location=(-20.0, -20.0, 35.0), rotation=(math.radians(52), math.radians(15), math.radians(-30)))
    cold_sun = bpy.context.active_object
    cold_sun.name = "NordicShadowFill"
    cold_sun.data.energy = 1.25
    cold_sun.data.color = (0.46, 0.64, 1.0)

    # Dedicated warm golden sun illuminating Astrid & the 3 Solspeilet mirrors on the high cliff peak!
    bpy.ops.object.light_add(type="SPOT", location=(-10.0, 12.0, 36.0))
    peak_sun = bpy.context.active_object
    peak_sun.name = "PeakHeliostatSun"
    peak_sun.data.energy = 9500.0
    peak_sun.data.color = (1.0, 0.86, 0.58)
    peak_sun.data.spot_size = math.radians(58)
    peak_sun.data.spot_blend = 0.45
    peak_sun.rotation_euler = (Vector((0.0, 24.5, 26.5)) - peak_sun.location).to_track_quat("-Z", "Y").to_euler()

    # BALANCED HERO SPOTLIGHT (6,500W instead of 115,000W -> rich golden glow WITHOUT washing out outlines!)
    bpy.ops.object.light_add(type="SPOT", location=(0.0, 25.2, 26.8))
    hero_spot = bpy.context.active_object
    hero_spot.name = "SolspeiletGoldenSpot"
    hero_spot.data.energy = 0.0
    hero_spot.data.color = (1.0, 0.82, 0.44)
    hero_spot.data.spot_size = math.radians(19.0)
    hero_spot.data.spot_blend = 0.35
    hero_spot.data.shadow_soft_size = 0.7
    hero_spot.rotation_euler = (Vector((0.45, 0.80, 0.0)) - hero_spot.location).to_track_quat("-Z", "Y").to_euler()

    # Soft warm ground bounce light (max 180W -> preserves crisp dark ink outlines!)
    bpy.ops.object.light_add(type="POINT", location=(0.45, 0.4, 1.2))
    bounce_light = bpy.context.active_object
    bounce_light.name = "PlazaWarmBounce"
    bounce_light.data.energy = 0.0
    bounce_light.data.color = (1.0, 0.80, 0.42)

    bpy.ops.object.light_add(type="POINT", location=(-2.65, -2.05, 3.65))
    sl_light = bpy.context.active_object
    sl_light.data.energy = 140.0
    sl_light.data.color = (1.0, 0.82, 0.48)

    # ---------------- RJUKAN TORG PLAZA & SNOW BANKS (SQUARE_Z = 0.0) ----------------
    add_box("RjukanPlazaCobble", (0.0, 0.0, -0.25), (46.0, 46.0, 0.5), m_cobble, col=col_world)
    add_box("SunlitWetCobble", (0.45, 0.80, 0.008), (5.8, 5.4, 0.02), m_cobble_wet, col=col_world)
    square_patch = add_box("SunlitSquareOverlay", (0.45, 0.80, 0.020), (5.5, 5.1, 0.01), m_spotlight_patch, col=col_world)
    square_patch.visible_shadow = False

    add_box("SnowBankL", (-8.8, 1.0, 0.14), (9.5, 26.0, 0.32), m_snow, bevel=0.06, col=col_world)
    add_box("SnowBankR", (9.2, 1.0, 0.14), (9.5, 26.0, 0.32), m_snow, bevel=0.06, col=col_world)
    add_box("SnowBankBack", (0.0, 12.5, 0.25), (26.0, 9.0, 0.50), m_snow, bevel=0.08, col=col_world)
    add_box("SnowBankFront", (-5.2, -5.8, 0.12), (7.0, 4.8, 0.26), m_snow, bevel=0.05, col=col_world)

    # ---------------- JAGGED NORTHERN MOUNTAIN WALL (STRICTLY BEHIND Y >= +29m -> ZERO CLIFF BLOCKING!) ----------------
    build_jagged_mountain_ridge("RjukanMountainNorth", (0.0, 42.0, -1.0), 110.0, 26.0, 48.0, m_cliff, seed=31, col=col_world)
    build_jagged_mountain_ridge("RjukanMountainSnowCap", (0.0, 43.0, 35.0), 96.0, 20.0, 12.0, m_snow, seed=32, col=col_world)
    build_jagged_mountain_ridge("ValleyWallWest", (-38.0, 8.0, -1.0), 26.0, 74.0, 38.0, m_cliff, seed=33, col=col_world)
    build_jagged_mountain_ridge("ValleyWallEast", (38.0, 8.0, -1.0), 26.0, 74.0, 38.0, m_cliff, seed=34, col=col_world)

    # Loc 2A: Astrid's Open-Air Cliffside Steel Observation Deck (Y in [20.4, 26.8], Z = CLIFF_DECK_Z = 24.0m!)
    add_box("HeliostatDeck", (0.0, 23.6, CLIFF_DECK_Z - 0.15), (16.8, 6.4, 0.30), m_steel, bevel=0.03, col=col_world)
    # Support struts anchoring platform back into mountain cliff face
    for sx in (-6.0, 0.0, 6.0):
        add_box(f"DeckStrut_{sx}", (sx, 25.4, CLIFF_DECK_Z - 2.2), (0.35, 5.8, 0.35), m_iron, rot=(math.radians(38), 0, 0), col=col_world)
    for rx in (-7.2, -4.6, -2.8, 0.6, 3.8, 7.2):
        add_cylinder(f"DeckPost_{rx}", (rx, 20.5, CLIFF_DECK_Z + 0.45), 0.05, 0.90, m_iron, verts=8, col=col_world)
    add_box("DeckRailTop", (0.0, 20.5, CLIFF_DECK_Z + 0.88), (14.8, 0.07, 0.07), m_iron, col=col_world)

    # Solar power panels & animated 3-blade wind turbine (real Solspeilet detail!)
    add_box("SolarPanelL", (-7.4, 24.0, CLIFF_DECK_Z + 1.0), (2.4, 0.12, 1.5), m_solar, rot=(math.radians(55), 0, 0), col=col_world)
    add_cylinder("WindTurbinePole", (7.6, 23.8, CLIFF_DECK_Z + 2.2), 0.09, 4.4, m_steel, verts=10, col=col_world)
    turbine_hub = bpy.data.objects.new("WindTurbineHub", None)
    turbine_hub.location = (7.6, 23.65, CLIFF_DECK_Z + 4.3)
    col_world.objects.link(turbine_hub)
    for bi in range(3):
        blade = add_box(f"TurbineBlade_{bi}", (0, 0, 0), (0.14, 0.04, 1.85), m_nordic_white, rot=(0, math.radians(bi * 120), 0), col=col_world)
        blade.parent = turbine_hub

    # Astrid's glowing industrial orange tablet clearly visible to her side in open air (zero torso obstruction!)
    add_box("AstridTabletBody", (-1.15, 21.32, CLIFF_DECK_Z + 1.06), (0.50, 0.06, 0.35), m_orange_rubber, rot=(math.radians(-26), 0, math.radians(14)), bevel=0.02, col=col_world)
    add_decal_plane("AstridTabletScreen", (-1.15, 21.28, CLIFF_DECK_Z + 1.075), 0.44, 0.29, (math.radians(64), 0, math.radians(14)), m_tablet_ui, col=col_world)

    # 3 MASSIVE REAL-REFERENCE SOLSPEILET HELIOSTAT MIRRORS (Planted flush on steel deck Y=25.8, Z_feet=24.0 -> 100% VISIBLE IN 9:16!)
    mirror_pivots: List[bpy.types.Object] = []
    for mi, mx in enumerate((-3.85, 0.0, 3.85)):
        _, piv = build_solspeilet_heliostat(
            f"Solspeilet_{mi}", (mx, 25.8, CLIFF_DECK_Z + 2.22), m_steel, m_mirror_surface, m_orange_rubber, col=col_world
        )
        mirror_pivots.append(piv)

    # SOFT FEATHERED OPEN-ENDED VOLUMETRIC GOD RAY CONE (NO END CAPS, NO SHADOW CAST, NO WHITE-OUT!)
    beam_start = Vector((0.0, 25.4, CLIFF_DECK_Z + 2.2))
    beam_end = Vector((0.45, 0.80, 0.0))
    beam_vec = beam_end - beam_start
    beam_len = beam_vec.length
    bpy.ops.mesh.primitive_cone_add(vertices=28, radius1=2.9, radius2=1.30, depth=beam_len, end_fill_type="NOTHING", location=(beam_start + beam_end) * 0.5)
    god_ray_cone = bpy.context.active_object
    god_ray_cone.name = "VolumetricGodRayCone"
    god_ray_cone.rotation_euler = beam_vec.to_track_quat("-Z", "Y").to_euler()
    god_ray_cone.data.materials.append(m_godray_soft)
    god_ray_cone.visible_shadow = False  # Strictly disabled so it NEVER casts shadow!
    col_world.objects.link(god_ray_cone)
    for c in list(god_ray_cone.users_collection):
        if c != col_world:
            c.objects.unlink(god_ray_cone)

    # ---------------- AUTHENTIC NORWEGIAN EARLY-1900s RJUKAN TORG BUILDINGS ----------------
    house_specs = [
        (-12.6, -4.8, (6.2, 5.2, 6.2), m_nordic_red, "+X"),
        (-12.8, 2.8,  (7.0, 5.4, 7.2), m_nordic_ochre, "+X"),
        (-12.4, 10.6, (6.4, 5.0, 6.0), m_nordic_white, "+X"),
        (12.6, -4.4,  (6.4, 5.4, 6.4), m_nordic_ochre, "-X"),
        (12.8, 3.2,   (7.2, 5.2, 7.4), m_nordic_red, "-X"),
        (12.4, 11.0,  (6.2, 5.0, 6.2), m_nordic_white, "-X"),
        (-6.2, -14.2, (6.2, 5.2, 6.4), m_nordic_white, "+Y"),
        (0.5, -14.5,  (6.6, 5.2, 7.2), m_nordic_red, "+Y"),
        (7.2, -14.2,  (6.2, 5.2, 6.2), m_nordic_ochre, "+Y"),
    ]
    for bi, (bx, by, bsz, bmat, face) in enumerate(house_specs):
        build_norwegian_rjukan_house(
            f"RjukanBldg_{bi}", (bx, by, 0.0), bsz, bmat, m_white_trim, m_roof_dark, m_win_warm, m_snow, m_icicle, m_wood_warm, facing=face, col=col_world
        )

    # ---------------- FOREGROUND & HERO PROPS (ZERO CLIPPING CLEARANCES!) ----------------
    # Classic Black Iron Streetlamp at (-2.65, -2.05) -> 1.1m clear of Arka at (-1.55, -1.65)!
    add_cylinder("StreetLampPole", (-2.65, -2.05, 1.85), 0.08, 3.7, m_iron, verts=12, col=col_world)
    add_cylinder("StreetLampBase", (-2.65, -2.05, 0.32), 0.18, 0.65, m_iron, verts=12, col=col_world)
    add_box("StreetLampLantern", (-2.65, -2.05, 3.72), (0.42, 0.42, 0.52), m_lamp_glow, col=col_world)
    add_box("StreetLampCapSnow", (-2.65, -2.05, 4.04), (0.58, 0.58, 0.16), m_snow, bevel=0.04, col=col_world)

    # Kakek Henrik's REAL striped folding beach chair placed strictly BEHIND Henrik (+0.52m in +Y -> ZERO front-bar shin clip!)
    build_striped_beach_chair("HenrikBeachChair", (0.98, 1.32, 0.0), math.radians(-14), m_wood_warm, m_chair_blue, m_chair_white, col=col_world)
    build_thermos_and_mug("HenrikThermosSet", (1.65, 0.90, 0.0), m_steel, m_iron, m_nordic_red, col=col_world)

    # Frosted wooden benches, Rjukan sign, steaming coffee cart, & multi-branched snowy pines!
    for bx, by, rz in [(-4.8, 2.5, 22), (5.0, 2.8, -24)]:
        add_box(f"BenchSeat_{bx}", (bx, by, 0.48), (1.8, 0.52, 0.08), m_wood_warm, rot=(0, 0, math.radians(rz)), bevel=0.02, col=col_world)
        add_box(f"BenchSnow_{bx}", (bx, by, 0.54), (1.76, 0.48, 0.06), m_snow, rot=(0, 0, math.radians(rz)), bevel=0.02, col=col_world)
    add_box("RjukanSignStand", (-5.0, 5.4, 1.35), (0.14, 0.14, 2.7), m_iron, col=col_world)
    add_decal_plane("RjukanSignFace", (-5.0, 5.28, 2.15), 1.9, 0.95, (math.radians(90), 0, math.radians(12)), m_sign_rjukan, col=col_world)
    add_box("CoffeeCartBody", (5.8, -2.8, 0.72), (1.7, 0.95, 1.1), m_nordic_red, rot=(0, 0, math.radians(-20)), bevel=0.03, col=col_world)
    add_box("CoffeeCartAwning", (5.8, -2.8, 2.25), (1.9, 1.15, 0.14), m_nordic_ochre, rot=(math.radians(10), 0, math.radians(-20)), col=col_world)

    pines = []
    for pi, (px, py, ph) in enumerate([(-6.8, 6.4, 5.4), (6.8, 7.0, 5.8), (-7.4, -4.4, 4.6), (7.6, 0.6, 5.0)]):
        p_root = build_snowy_pine_tree(f"NordicPine_{pi}", (px, py, 0.0), ph, m_wood_warm, m_pine, m_snow, seed=50 + pi, col=col_world)
        pines.append((p_root, pi * 1.4))

    # ---------------- LIVING BUSY SET DRESSING (4 UNIFIED 2.5D BEAN-HEAD NPCs + 2 REAL 3D WHEELED CARS!) ----------------
    npc_dir = os.path.join(sprites_dir, "npcs")
    npc_starts = [(-5.8, -0.6), (-4.6, 4.8), (5.5, 4.2), (6.2, -0.6)]
    town_npcs = []
    for spec, (nx, ny) in zip(NPC_ROSTER["rjukan"], npc_starts):
        nid = spec["id"]
        p0 = os.path.join(npc_dir, nid, "pose_0.png")
        n_obj, n_tex, n_tint = create_character_card(nid, spec["height"], p0, ambient_tint=(0.70, 0.80, 1.0), col=col_world)
        n_obj.location = Vector((nx, ny, 0.0))
        town_npcs.append((n_obj, n_tint, nx, ny))

    cars = [
        (build_3d_car("NordicCar_0", (0, 9.2, 0.0), m_car_blue, m_car_glass, m_tire, m_steel, m_lamp_glow, m_tail_red, m_snow, 1.0, col=col_world), 9.2, 1.0),
        (build_3d_car("NordicCar_1", (0, -9.2, 0.0), m_car_red, m_car_glass, m_tire, m_steel, m_lamp_glow, m_tail_red, m_snow, -1.0, col=col_world), -9.2, -1.0),
    ]

    # 95 Falling Snow Particles isolated in COL_02_SnowParticles
    rng = random.Random(202)
    snow_flakes = []
    for si in range(95):
        sx = rng.uniform(-10.0, 10.0)
        sy = rng.uniform(-9.0, 10.0)
        sz = rng.uniform(0.6, 9.5)
        fl = add_sphere(f"RjuSnow_{si}", (sx, sy, sz), rng.uniform(0.015, 0.032), m_snow_flake, segments=6, col=col_snow)
        fl.visible_shadow = False
        snow_flakes.append((fl, sx, sy, sz, rng.uniform(0.6, 1.3), rng.uniform(0, 6.28)))

    # ---------------- HERO PYTHON 2.5D CHARACTERS (Arka, Astrid, Kakek Henrik) ----------------
    char_cards: Dict[str, Any] = {}
    for cid in ("arka", "astrid", "kakek_henrik"):
        first_png = os.path.join(sprites_dir, cid, f"frame_{start_frame:04d}.png")
        obj, tex_node, tint_node = create_character_card(cid, CHAR_HEIGHTS_M[cid], first_png, ambient_tint=(0.72, 0.82, 1.0), col=col_world)
        char_cards[cid] = (obj, tex_node, tint_node)

    # ---------------- CAMERA ----------------
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.clip_start = 0.08
    cam_data.clip_end = 260.0
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    col_world.objects.link(cam_obj)
    scene.camera = cam_obj

    for f in range(max(750, start_frame - 1), end_frame + 2):
        c_st = get_camera_at_frame("rjukan", f)
        point_camera_at(cam_obj, c_st["pos"], c_st["target"], c_st["lens"], c_st["roll"])
        cam_obj.keyframe_insert(data_path="location", frame=f)
        cam_obj.keyframe_insert(data_path="rotation_quaternion", frame=f)
        cam_data.keyframe_insert(data_path="lens", frame=f)

    # ---------------- DYNAMIC FRAME UPDATE HANDLER ----------------
    def update_rjukan_frame(scn: bpy.types.Scene) -> None:
        f = scn.frame_current
        t = f / 30.0
        dyn = get_scene_dynamic_state("rjukan", f)
        chars = get_characters_at_frame("rjukan", f)
        cam_pos = get_camera_at_frame("rjukan", f)["pos"]

        piv_u = dyn["mirror_pivot"]
        beam_u = dyn["beam_shoot"]
        lit_u = dyn["square_lit"]

        # BALANCED STORY LIGHTING TURN (ZERO WHITE-OUT!)
        hero_spot.data.energy = 6500.0 * lit_u
        bounce_light.data.energy = 180.0 * lit_u
        square_patch.hide_render = lit_u < 0.05

        for mi, piv in enumerate(mirror_pivots):
            piv.rotation_euler = (math.radians(lerp(-8.0, 24.0, piv_u)), 0.0, math.radians((mi - 1) * 7.0 * (1.0 - piv_u)))
        turbine_hub.rotation_euler = (0.0, t * 4.5, 0.0)

        if beam_u < 0.02:
            god_ray_cone.hide_render = True
        else:
            god_ray_cone.hide_render = False
            cur_end = beam_start.lerp(beam_end, beam_u)
            god_ray_cone.location = (beam_start + cur_end) * 0.5
            god_ray_cone.scale = (0.50 + 0.50 * beam_u, 0.50 + 0.50 * beam_u, max(0.05, beam_u))

        for cid, (obj, tex_node, tint_node) in char_cards.items():
            st = chars[cid]
            obj.location = Vector(st["pos"])
            obj.rotation_euler = (0.0, 0.0, st["rot_z"])
            obj.hide_render = not st["visible"]
            if cid == "astrid":
                set_mix_rgba_b(tint_node, (1.02, 0.98, 0.92, 1.0))
            else:
                # Crisp cold blue shadow -> rich warm sunlit gold WITHOUT exceeding 1.05 (protects dark outlines!)
                set_mix_rgba_b(tint_node, (lerp(0.68, 1.04, lit_u), lerp(0.78, 0.98, lit_u), lerp(1.00, 0.86, lit_u), 1.0))
            png_path = os.path.join(sprites_dir, cid, f"frame_{f:04d}.png")
            if os.path.exists(png_path):
                tex_node.image = bpy.data.images.load(png_path, check_existing=True)

        # Unified 2.5D bean-head townspeople NPCs
        for idx, (n_obj, n_tint, nx, ny) in enumerate(town_npcs):
            cx = lerp(nx, nx * 0.72 + 0.25, lit_u) + math.sin(t * 0.85 + idx) * 0.35
            cy = lerp(ny, ny * 0.72 + 0.40, lit_u) + math.cos(t * 0.75 + idx) * 0.25
            n_obj.location = Vector((cx, cy, abs(math.sin(t * 4.5 + idx)) * 0.04))
            n_obj.rotation_euler = (0.0, 0.0, compute_billboard_rot_z((cx, cy, 0.0), cam_pos))
            set_mix_rgba_b(n_tint, (lerp(0.68, 0.96, lit_u), lerp(0.78, 0.94, lit_u), lerp(1.00, 0.88, lit_u), 1.0))

        for c_root, cy, dir_s in cars:
            cx = ((t * 3.8 * dir_s + 15.0) % 36.0) - 18.0
            c_root.location = Vector((cx, cy, 0.0))

        for p_root, ph in pines:
            p_root.rotation_euler = (math.sin(t * 1.4 + ph) * 0.025, math.cos(t * 1.2 + ph) * 0.02, 0.0)

        for fl, sx, sy, sz, spd, ph in snow_flakes:
            nx = sx + math.sin(t * 1.8 + ph) * 0.40
            nz = 0.4 + ((sz - t * 1.2 * spd) % 9.0)
            fl.location = Vector((nx, sy, nz))

        # Crisp 6-frame golden sunglasses glint match-cut ONLY at 48.72..49.0s!
        set_transition_flash(scn, (dyn["match_flash"] ** 1.4) * 0.72, (1.0, 0.96, 0.86))

    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(update_rjukan_frame)
    scene.frame_start = start_frame
    scene.frame_end = end_frame - 1
    scene.frame_set(start_frame)
    update_rjukan_frame(scene)
    return scene
