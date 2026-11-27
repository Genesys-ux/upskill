"""World 2 (v3 Cinematic): Rjukan Torg Norwegian Town, Textured Alpine Granite Cliffs, Clear Plowed Car Street & Silky Golden God Ray."""
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
    link_to_collection,
    make_cel_pbr_material,
    make_decal_material,
    make_emissive_material,
    make_snowy_cliff_material,
    make_soft_godray_material,
    point_camera_at,
    set_mix_rgba_b,
    set_transition_flash,
    setup_world_sky,
)
from blender_scenes.props_3d import (
    build_3d_car,
    build_jagged_mountain_ridge,
    build_nordic_waffle_kiosk,
    build_norwegian_rjukan_house,
    build_plaza_bench_with_legs,
    build_snowman,
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

    # Crisp Freezing Nordic Winter Twilight Sky (rich deep steel-blue with pale alpine horizon — ZERO pitch-black sky!)
    setup_world_sky(
        zenith_color=(0.07, 0.14, 0.34),
        mid_color=(0.18, 0.29, 0.52),
        horizon_color=(0.46, 0.58, 0.78),
        strength=0.86,
    )

    # ---------------- MATERIALS (CRISP ALPINE GRANITE+SNOW CLIFFS, CLAPBOARD WOOD, HIGHLIGHTS & SHADOWS) ----------------
    m_cobble = make_cel_pbr_material("RjukanCobble", (0.38, 0.40, 0.46), (0.12, 0.18, 0.36), roughness=0.52, bump_scale=6.0, bump_strength=0.28, pattern="cobble")
    m_asphalt = make_cel_pbr_material("RjukanPlowedRoad", (0.20, 0.22, 0.26), (0.08, 0.12, 0.24), roughness=0.48, bump_scale=5.0, bump_strength=0.22, pattern="noise")
    m_road_line = make_cel_pbr_material("RoadStripeWhite", (0.88, 0.88, 0.84), (0.36, 0.44, 0.62), roughness=0.55)
    m_cobble_wet = make_cel_pbr_material("RjukanCobbleWet", (0.50, 0.46, 0.38), (0.20, 0.24, 0.38), roughness=0.14, bump_scale=6.0, bump_strength=0.20, pattern="cobble", rim_strength=0.30)
    m_snow = make_cel_pbr_material("RjukanSnow", (0.88, 0.93, 0.99), (0.24, 0.38, 0.70), roughness=0.34, bump_scale=4.0, pattern="snow", rim_strength=0.28)
    m_icicle = make_cel_pbr_material("RjukanIcicle", (0.80, 0.94, 1.0), (0.34, 0.56, 0.86), roughness=0.08, metallic=0.12)
    # REAL TEXTURED NORWEGIAN GRANITE CLIFF + AUTOMATIC SLOPE-MAPPED SNOW LEDGES (ZERO FLAT BLACK HILL!)
    m_cliff_alpine = make_snowy_cliff_material("RjukanAlpineGranite", rock_light=(0.36, 0.42, 0.54), rock_dark=(0.16, 0.22, 0.34), snow_color=(0.86, 0.92, 0.99), snow_slope_threshold=0.50)
    m_nordic_red = make_cel_pbr_material("NordicRedWood", (0.62, 0.16, 0.15), (0.16, 0.18, 0.38), roughness=0.54, bump_scale=5.5, pattern="clapboard")
    m_nordic_ochre = make_cel_pbr_material("NordicOchreWood", (0.80, 0.58, 0.20), (0.22, 0.24, 0.40), roughness=0.54, bump_scale=5.5, pattern="clapboard")
    m_nordic_white = make_cel_pbr_material("NordicWhiteWood", (0.88, 0.87, 0.84), (0.26, 0.36, 0.60), roughness=0.54, bump_scale=5.5, pattern="clapboard")
    m_nordic_slate = make_cel_pbr_material("NordicBlueWood", (0.26, 0.42, 0.56), (0.12, 0.20, 0.38), roughness=0.54, bump_scale=5.5, pattern="clapboard")
    m_white_trim = make_cel_pbr_material("NordicWindowTrim", (0.95, 0.95, 0.93), (0.36, 0.46, 0.66), roughness=0.46)
    m_roof_dark = make_cel_pbr_material("NordicSlateRoof", (0.18, 0.21, 0.28), (0.08, 0.12, 0.26), roughness=0.50)
    m_iron = make_cel_pbr_material("ClassicBlackIron", (0.12, 0.14, 0.18), (0.06, 0.08, 0.16), roughness=0.34, metallic=0.82)
    m_steel = make_cel_pbr_material("HeliostatSteel", (0.58, 0.62, 0.68), (0.22, 0.30, 0.48), roughness=0.28, metallic=0.84)
    m_solar = make_cel_pbr_material("SolarCellBlue", (0.08, 0.20, 0.46), (0.04, 0.10, 0.26), roughness=0.14, metallic=0.65)
    m_pine = make_cel_pbr_material("NordicPine", (0.10, 0.28, 0.17), (0.06, 0.14, 0.24), roughness=0.72)
    m_chair_blue = make_cel_pbr_material("BeachChairBlue", (0.12, 0.46, 0.86), (0.08, 0.22, 0.48), roughness=0.48)
    m_chair_white = make_cel_pbr_material("BeachChairWhite", (0.95, 0.95, 0.93), (0.36, 0.44, 0.62), roughness=0.48)
    m_wood_warm = make_cel_pbr_material("WarmBenchWood", (0.50, 0.31, 0.18), (0.18, 0.20, 0.36), roughness=0.50, pattern="wood")
    m_orange_rubber = make_cel_pbr_material("TabletRubberOrange", (0.94, 0.42, 0.10), (0.36, 0.22, 0.24), roughness=0.42)
    m_car_blue = make_cel_pbr_material("NordicCarBlue", (0.16, 0.38, 0.64), (0.08, 0.18, 0.38), roughness=0.18, metallic=0.48)
    m_car_red = make_cel_pbr_material("NordicCarRed", (0.74, 0.18, 0.18), (0.24, 0.16, 0.30), roughness=0.18, metallic=0.48)
    m_car_cream = make_cel_pbr_material("NordicCarCream", (0.86, 0.78, 0.56), (0.34, 0.32, 0.44), roughness=0.20, metallic=0.40)
    m_car_glass = make_cel_pbr_material("CarTintedGlass", (0.10, 0.18, 0.28), (0.05, 0.10, 0.18), roughness=0.06, metallic=0.55)
    m_tire = make_cel_pbr_material("RubberTire", (0.08, 0.08, 0.10), (0.04, 0.04, 0.06), roughness=0.82)

    m_win_warm = make_emissive_material("RjukanWinWarm", (1.0, 0.80, 0.38), strength=3.0)
    m_lamp_glow = make_emissive_material("StreetLampGlow", (1.0, 0.84, 0.48), strength=4.6)
    m_festoon_glow = make_emissive_material("FestoonBulbGlow", (1.0, 0.82, 0.44), strength=5.0)
    m_tail_red = make_emissive_material("CarTailRed", (1.0, 0.14, 0.10), strength=3.2)
    m_led_green = make_emissive_material("ControlLedGreen", (0.18, 0.96, 0.42), strength=4.2)
    m_mirror_surface = make_emissive_material("SolspeiletMirrorGlow", (1.0, 0.92, 0.66), strength=1.7)
    # SILKY ADDITIVE GOLDEN GOD RAY (ZERO grey muddiness, ZERO white-out!)
    m_godray_soft = make_soft_godray_material("SoftVolumetricGodRay", (1.0, 0.86, 0.42), strength=0.22)
    m_spotlight_patch = make_emissive_material("SunlitSquarePatch", (1.0, 0.88, 0.52), strength=0.38, alpha=0.16)
    m_snow_flake = make_emissive_material("SnowFlakeR", (0.90, 0.95, 1.0), strength=1.05)

    m_tablet_ui = make_decal_material("AstridTabletUI", os.path.join(DECALS_DIR, "tablet_heliostat_ui.png"), emissive=2.0)
    m_sign_rjukan = make_decal_material("RjukanSignMat", os.path.join(DECALS_DIR, "sign_rjukan_torg.png"), emissive=0.18, roughness=0.42)

    # ---------------- DYNAMIC STORY LIGHTING (CRISP SHADOWS + ALPINE RIM + GOLDEN TURN!) ----------------
    bpy.ops.object.light_add(type="SUN", location=(-24.0, -24.0, 28.0), rotation=(math.radians(60), math.radians(18), math.radians(-34)))
    cold_sun = bpy.context.active_object
    cold_sun.name = "NordicAlpineLight"
    cold_sun.data.energy = 2.0
    cold_sun.data.color = (0.56, 0.72, 1.0)
    cold_sun.data.angle = math.radians(1.0)  # Crisp readable winter shadows!
    link_to_collection(cold_sun, col_world)

    # Warm golden sun grazing the high mountain cliff, Astrid & all 3 Solspeilet mirrors!
    bpy.ops.object.light_add(type="SPOT", location=(-12.0, 10.0, 38.0))
    peak_sun = bpy.context.active_object
    peak_sun.name = "PeakHeliostatSun"
    peak_sun.data.energy = 12500.0
    peak_sun.data.color = (1.0, 0.86, 0.58)
    peak_sun.data.spot_size = math.radians(68)
    peak_sun.data.spot_blend = 0.45
    peak_sun.rotation_euler = (Vector((0.0, 26.0, 27.0)) - peak_sun.location).to_track_quat("-Z", "Y").to_euler()
    link_to_collection(peak_sun, col_world)

    # HERO SOLSPEILET GOLDEN SPOTLIGHT (Crisp dramatic golden light + sharp shadows on Henrik & plaza, zero white-out!)
    bpy.ops.object.light_add(type="SPOT", location=(0.0, 25.2, 26.8))
    hero_spot = bpy.context.active_object
    hero_spot.name = "SolspeiletGoldenSpot"
    hero_spot.data.energy = 0.0
    hero_spot.data.color = (1.0, 0.82, 0.42)
    hero_spot.data.spot_size = math.radians(20.0)
    hero_spot.data.spot_blend = 0.30
    hero_spot.data.shadow_soft_size = 0.35
    hero_spot.rotation_euler = (Vector((0.45, 0.80, 0.0)) - hero_spot.location).to_track_quat("-Z", "Y").to_euler()
    link_to_collection(hero_spot, col_world)

    bpy.ops.object.light_add(type="POINT", location=(0.45, 0.4, 1.3))
    bounce_light = bpy.context.active_object
    bounce_light.name = "PlazaWarmBounce"
    bounce_light.data.energy = 0.0
    bounce_light.data.color = (1.0, 0.80, 0.42)
    link_to_collection(bounce_light, col_world)

    # Warm glowing iron streetlamps around Rjukan Torg
    lamp_coords = [(-2.65, -2.05), (4.80, -3.20), (-5.20, 4.60), (5.20, 4.80)]
    for lx, ly in lamp_coords:
        add_cylinder(f"StreetLampPole_{lx}", (lx, ly, 1.85), 0.08, 3.7, m_iron, verts=12, col=col_world)
        add_cylinder(f"StreetLampBase_{lx}", (lx, ly, 0.32), 0.18, 0.65, m_iron, verts=12, col=col_world)
        add_box(f"StreetLampLantern_{lx}", (lx, ly, 3.72), (0.42, 0.42, 0.52), m_lamp_glow, col=col_world)
        add_box(f"StreetLampCapSnow_{lx}", (lx, ly, 4.04), (0.58, 0.58, 0.16), m_snow, bevel=0.04, col=col_world)
        bpy.ops.object.light_add(type="POINT", location=(lx, ly, 3.62))
        sl = bpy.context.active_object
        sl.data.energy = 140.0 if lx == -2.65 else 95.0
        sl.data.color = (1.0, 0.80, 0.44)
        link_to_collection(sl, col_world)

    # Cozy festive warm string lights draped overhead between the plaza lamps!
    for si in range(9):
        u = si / 8.0
        fx = lerp(-5.20, 5.20, u)
        fy = lerp(4.60, 4.80, u)
        fz = 3.75 - math.sin(u * math.pi) * 0.48
        add_sphere(f"FestoonBulb_{si}", (fx, fy, fz), 0.07, m_festoon_glow, segments=8, col=col_world)

    # ---------------- RJUKAN TORG PLAZA, CLEAR PLOWED ASPHALT ROAD (Y in [6.6..11.4]) & CURB SNOWBANKS ----------------
    add_box("RjukanPlazaCobble", (0.0, 0.0, -0.25), (68.0, 56.0, 0.5), m_cobble, col=col_world)
    add_box("SunlitWetCobble", (0.45, 0.80, 0.008), (5.8, 5.4, 0.02), m_cobble_wet, col=col_world)
    square_patch = add_box("SunlitSquareOverlay", (0.45, 0.80, 0.020), (5.5, 5.1, 0.01), m_spotlight_patch, col=col_world)
    square_patch.visible_shadow = False

    # Wide snow-plowed Norwegian main street completely unobstructed from X=-34 to X=+34!
    add_box("RjukanPlowedRoad", (0.0, 9.0, 0.008), (72.0, 4.8, 0.02), m_asphalt, col=col_world)
    for rx in range(-28, 30, 4):
        add_box(f"RoadDash_{rx}", (rx, 9.0, 0.022), (1.8, 0.14, 0.01), m_road_line, col=col_world)

    # Sculpted roadside snowbanks STRICTLY OUTSIDE the road corridor (Y <= 6.2 or Y >= 12.2 -> ZERO buried cars!)
    add_box("SnowBankL", (-8.8, -1.0, 0.12), (4.6, 13.5, 0.26), m_snow, bevel=0.06, col=col_world)
    add_box("SnowBankR", (8.8, -1.0, 0.12), (4.6, 13.5, 0.26), m_snow, bevel=0.06, col=col_world)
    add_box("SnowBankNorthCurb", (0.0, 12.4, 0.18), (64.0, 1.4, 0.36), m_snow, bevel=0.06, col=col_world)
    add_box("SnowBankSouthCurb", (-5.4, -6.2, 0.12), (6.4, 3.6, 0.24), m_snow, bevel=0.05, col=col_world)

    # ---------------- TEXTURED ALPINE NORWEGIAN MOUNTAIN CLIFFS (CRACKED GRANITE + SNOW LEDGES!) ----------------
    build_jagged_mountain_ridge("RjukanMountainNorth", (0.0, 43.0, -1.0), 124.0, 26.0, 50.0, m_cliff_alpine, seed=31, col=col_world)
    build_jagged_mountain_ridge("GaustatoppenPeak", (16.0, 74.0, -1.0), 104.0, 34.0, 68.0, m_cliff_alpine, seed=36, col=col_world)
    build_jagged_mountain_ridge("ValleyWallWest", (-42.0, 8.0, -1.0), 28.0, 78.0, 40.0, m_cliff_alpine, seed=33, col=col_world)
    build_jagged_mountain_ridge("ValleyWallEast", (42.0, 8.0, -1.0), 28.0, 78.0, 40.0, m_cliff_alpine, seed=34, col=col_world)

    # Loc 2A: Astrid's Open-Air Cliffside Steel Observation Deck (Y in [20.4, 26.8], Z = CLIFF_DECK_Z = 24.0m!)
    add_box("HeliostatDeck", (0.0, 23.6, CLIFF_DECK_Z - 0.15), (16.8, 6.4, 0.30), m_steel, bevel=0.03, col=col_world)
    for sx in (-6.0, 0.0, 6.0):
        add_box(f"DeckStrut_{sx}", (sx, 25.4, CLIFF_DECK_Z - 2.2), (0.35, 5.8, 0.35), m_iron, rot=(math.radians(38), 0, 0), col=col_world)
    for rx in (-7.2, -4.6, -2.8, 0.6, 3.8, 7.2):
        add_cylinder(f"DeckPost_{rx}", (rx, 20.5, CLIFF_DECK_Z + 0.42), 0.05, 0.84, m_iron, verts=8, col=col_world)
    add_box("DeckRailTop", (0.0, 20.5, CLIFF_DECK_Z + 0.82), (14.8, 0.06, 0.06), m_iron, col=col_world)

    # Heliostat electrical control cabinet with status LEDs + solar panel + spinning wind turbine!
    add_box("HeliostatControlBox", (-5.4, 22.8, CLIFF_DECK_Z + 0.72), (0.95, 0.55, 1.44), m_steel, bevel=0.03, col=col_world)
    add_sphere("ControlBoxLed1", (-5.55, 22.50, CLIFF_DECK_Z + 1.15), 0.045, m_led_green, segments=8, col=col_world)
    add_sphere("ControlBoxLed2", (-5.35, 22.50, CLIFF_DECK_Z + 1.15), 0.045, m_lamp_glow, segments=8, col=col_world)
    add_box("SolarPanelL", (-7.4, 24.0, CLIFF_DECK_Z + 1.0), (2.4, 0.12, 1.5), m_solar, rot=(math.radians(55), 0, 0), col=col_world)
    add_cylinder("WindTurbinePole", (7.6, 23.8, CLIFF_DECK_Z + 2.2), 0.09, 4.4, m_steel, verts=10, col=col_world)
    turbine_hub = bpy.data.objects.new("WindTurbineHub", None)
    turbine_hub.location = (7.6, 23.65, CLIFF_DECK_Z + 4.3)
    col_world.objects.link(turbine_hub)
    for bi in range(3):
        blade = add_box(f"TurbineBlade_{bi}", (0, 0, 0), (0.14, 0.04, 1.85), m_nordic_white, rot=(0, math.radians(bi * 120), 0), col=col_world)
        blade.parent = turbine_hub

    add_box("AstridTabletBody", (-1.15, 21.72, CLIFF_DECK_Z + 1.06), (0.50, 0.06, 0.35), m_orange_rubber, rot=(math.radians(-26), 0, math.radians(14)), bevel=0.02, col=col_world)
    add_decal_plane("AstridTabletScreen", (-1.15, 21.68, CLIFF_DECK_Z + 1.075), 0.44, 0.29, (math.radians(64), 0, math.radians(14)), m_tablet_ui, col=col_world)

    # 3 SPOTLESS SOLSPEILET HELIOSTAT MIRRORS (Rear-mounted pistons -> ZERO rods poking through mirror glass!)
    mirror_pivots: List[bpy.types.Object] = []
    for mi, mx in enumerate((-3.85, 0.0, 3.85)):
        _, piv = build_solspeilet_heliostat(
            f"Solspeilet_{mi}", (mx, 25.8, CLIFF_DECK_Z + 2.22), m_steel, m_mirror_surface, m_orange_rubber, col=col_world
        )
        mirror_pivots.append(piv)

    # SILKY ADDITIVE VOLUMETRIC GOD RAY CONE (NO END CAPS, NO SHADOWS, ZERO MUDDY GREY!)
    beam_start = Vector((0.0, 25.4, CLIFF_DECK_Z + 2.2))
    beam_end = Vector((0.45, 0.80, 0.0))
    beam_vec = beam_end - beam_start
    beam_len = beam_vec.length
    bpy.ops.mesh.primitive_cone_add(vertices=28, radius1=2.9, radius2=1.30, depth=beam_len, end_fill_type="NOTHING", location=(beam_start + beam_end) * 0.5)
    god_ray_cone = bpy.context.active_object
    god_ray_cone.name = "VolumetricGodRayCone"
    god_ray_cone.rotation_euler = beam_vec.to_track_quat("-Z", "Y").to_euler()
    god_ray_cone.data.materials.append(m_godray_soft)
    god_ray_cone.visible_shadow = False
    link_to_collection(god_ray_cone, col_world)

    # ---------------- 12 RICH EARLY-1900s NORWEGIAN RJUKAN TOWN BUILDINGS (100% CLEAR OF ROAD Y[6.6..11.4]!) ----------------
    house_specs = [
        # West & East plaza wings (Y <= 5.0 -> completely south of road!)
        (-13.2, -5.0, (6.4, 5.2, 6.4), m_nordic_red,   m_nordic_ochre, "+X"),
        (-13.2,  2.2, (6.8, 5.2, 7.2), m_nordic_ochre, m_nordic_red,   "+X"),
        ( 13.2, -4.6, (6.4, 5.2, 6.6), m_nordic_slate, m_nordic_ochre, "-X"),
        ( 13.2,  2.4, (6.8, 5.2, 7.4), m_nordic_red,   m_nordic_white, "-X"),
        # South town row facing +Y
        (-6.6, -14.2, (6.2, 5.2, 6.6), m_nordic_white, m_nordic_red,   "+Y"),
        ( 0.4, -14.5, (6.6, 5.2, 7.4), m_nordic_red,   m_nordic_ochre, "+Y"),
        ( 7.4, -14.2, (6.2, 5.2, 6.4), m_nordic_ochre, m_nordic_slate, "+Y"),
        # North town row across the plowed street facing -Y (south facade at Y >= 13.4 -> 2m clear of road!)
        (-14.2, 16.0, (6.6, 5.2, 6.8), m_nordic_slate, m_nordic_red,   "-Y"),
        ( -7.0, 16.2, (6.8, 5.2, 7.4), m_nordic_red,   m_nordic_ochre, "-Y"),
        (  0.4, 16.2, (6.8, 5.2, 6.6), m_nordic_white, m_nordic_slate, "-Y"),
        (  7.8, 16.2, (6.8, 5.2, 7.2), m_nordic_ochre, m_nordic_red,   "-Y"),
        ( 15.0, 16.0, (6.4, 5.2, 6.6), m_nordic_red,   m_nordic_white, "-Y"),
    ]
    for bi, (bx, by, bsz, bmat, am, face) in enumerate(house_specs):
        build_norwegian_rjukan_house(
            f"RjukanBldg_{bi}", (bx, by, 0.0), bsz, bmat, m_white_trim, m_roof_dark, m_win_warm, m_snow, m_icicle, m_wood_warm, mat_awning=am, facing=face, col=col_world
        )

    # ---------------- HERO PROPS + RICH BUSY RJUKAN SET DRESSING (ZERO FLOATING BENCHES!) ----------------
    build_striped_beach_chair("HenrikBeachChair", (0.98, 1.32, 0.0), math.radians(-14), m_wood_warm, m_chair_blue, m_chair_white, col=col_world)
    build_thermos_and_mug("HenrikThermosSet", (1.65, 0.90, 0.0), m_steel, m_iron, m_nordic_red, col=col_world)

    # Real wrought-iron-legged wooden plaza benches (NEVER floating!)
    build_plaza_bench_with_legs("RjukanBench_L", (-5.4, 2.2, 0.0), math.radians(24), m_wood_warm, m_iron, m_snow, col=col_world)
    build_plaza_bench_with_legs("RjukanBench_R", (5.6, 2.6, 0.0), math.radians(-26), m_wood_warm, m_iron, m_snow, col=col_world)
    # Cozy glowing Norwegian winter waffle & hot-cocoa kiosk + snowman + red Norwegian postbox + Rjukan Torg sign!
    build_nordic_waffle_kiosk("RjukanWaffleKiosk", (6.0, -2.5, 0.0), math.radians(-24), m_nordic_red, m_white_trim, m_wood_warm, m_snow, m_win_warm, col=col_world)
    build_snowman("PlazaSnowman", (-5.5, -3.5, 0.0), m_snow, m_nordic_red, m_iron, m_orange_rubber, col=col_world)
    add_box("NordicPostboxPost", (-4.4, 4.9, 0.55), (0.10, 0.10, 1.10), m_iron, col=col_world)
    add_box("NordicPostboxBody", (-4.4, 4.9, 1.18), (0.38, 0.28, 0.52), m_nordic_red, bevel=0.02, col=col_world)
    add_box("RjukanSignStand", (-5.0, 5.4, 1.35), (0.14, 0.14, 2.7), m_iron, col=col_world)
    add_decal_plane("RjukanSignFace", (-5.0, 5.28, 2.15), 1.9, 0.95, (math.radians(90), 0, math.radians(12)), m_sign_rjukan, col=col_world)

    pines = []
    for pi, (px, py, ph) in enumerate([(-7.4, 4.8, 5.4), (7.6, 4.8, 5.6), (-7.8, -4.6, 4.8), (8.2, 0.6, 5.0), (-9.6, 12.6, 5.2), (10.4, 12.6, 5.4)]):
        p_root = build_snowy_pine_tree(f"NordicPine_{pi}", (px, py, 0.0), ph, m_wood_warm, m_pine, m_snow, seed=50 + pi, col=col_world)
        pines.append((p_root, pi * 1.4))

    # ---------------- 6 UNIFIED 2.5D BEAN-HEAD NPCs + 3 GROUNDED 3D WHEELED CARS ON OPEN ROAD! ----------------
    npc_dir = os.path.join(sprites_dir, "npcs")
    # Strictly positioned on open cobblestone plaza away from benches & road!
    npc_starts = [(-4.2, -0.6), (-3.8, 4.2), (4.0, 4.0), (4.6, -0.6), (-3.4, -4.6), (4.9, -3.4)]
    town_npcs = []
    for spec, (nx, ny) in zip(NPC_ROSTER["rjukan"], npc_starts):
        nid = spec["id"]
        p0 = os.path.join(npc_dir, nid, "pose_0.png")
        n_obj, n_tex, n_tint = create_character_card(nid, spec["height"], p0, ambient_tint=(0.74, 0.84, 1.0), col=col_world)
        n_obj.location = Vector((nx, ny, 0.0))
        town_npcs.append((n_obj, n_tint, nx, ny))

    # 3 Real 3D Wheeled Cars driving smoothly on CLEAR PLOWED ASPHALT ROAD (Y=7.9 & Y=10.1, Z=0.018 — ZERO SINKING, ZERO WALL CLIP!)
    cars = [
        (build_3d_car("NordicCar_0", (-12.0, 7.9, 0.018), m_car_blue, m_car_glass, m_tire, m_steel, m_lamp_glow, m_tail_red, m_snow, 1.0, col=col_world), 7.9, 1.0, 4.0),
        (build_3d_car("NordicCar_1", (14.0, 10.1, 0.018), m_car_red, m_car_glass, m_tire, m_steel, m_lamp_glow, m_tail_red, m_snow, -1.0, col=col_world), 10.1, -1.0, 14.0),
        (build_3d_car("NordicCar_2", (-24.0, 7.9, 0.018), m_car_cream, m_car_glass, m_tire, m_steel, m_lamp_glow, m_tail_red, m_snow, 1.0, col=col_world), 7.9, 1.0, 32.0),
    ]

    # 95 Falling Snow Particles isolated in COL_02_SnowParticles
    rng = random.Random(202)
    snow_flakes = []
    for si in range(95):
        sx = rng.uniform(-10.0, 10.0)
        sy = rng.uniform(-9.0, 10.0)
        sz = rng.uniform(0.6, 9.5)
        fl = add_sphere(f"RjuSnow_{si}", (sx, sy, sz), rng.uniform(0.014, 0.030), m_snow_flake, segments=6, col=col_snow)
        fl.visible_shadow = False
        snow_flakes.append((fl, sx, sy, sz, rng.uniform(0.6, 1.3), rng.uniform(0, 6.28)))

    # ---------------- HERO PYTHON 2.5D CHARACTERS (Arka, Astrid, Kakek Henrik) ----------------
    char_cards: Dict[str, Any] = {}
    for cid in ("arka", "astrid", "kakek_henrik"):
        first_png = os.path.join(sprites_dir, cid, f"frame_{start_frame:04d}.png")
        obj, tex_node, tint_node = create_character_card(cid, CHAR_HEIGHTS_M[cid], first_png, ambient_tint=(0.76, 0.85, 1.0), col=col_world)
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

        hero_spot.data.energy = 7800.0 * lit_u
        bounce_light.data.energy = 200.0 * lit_u
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
                set_mix_rgba_b(tint_node, (1.03, 0.98, 0.92, 1.0))
            else:
                set_mix_rgba_b(tint_node, (lerp(0.72, 1.05, lit_u), lerp(0.82, 0.98, lit_u), lerp(1.00, 0.86, lit_u), 1.0))
            png_path = os.path.join(sprites_dir, cid, f"frame_{f:04d}.png")
            if os.path.exists(png_path):
                tex_node.image = bpy.data.images.load(png_path, check_existing=True)

        for idx, (n_obj, n_tint, nx, ny) in enumerate(town_npcs):
            cx = lerp(nx, nx * 0.78 + 0.18, lit_u) + math.sin(t * 0.85 + idx) * 0.25
            cy = lerp(ny, ny * 0.78 + 0.30, lit_u) + math.cos(t * 0.75 + idx) * 0.20
            n_obj.location = Vector((cx, cy, abs(math.sin(t * 4.5 + idx)) * 0.035))
            n_obj.rotation_euler = (0.0, 0.0, compute_billboard_rot_z((cx, cy, 0.0), cam_pos))
            set_mix_rgba_b(n_tint, (lerp(0.72, 0.98, lit_u), lerp(0.82, 0.95, lit_u), lerp(1.00, 0.88, lit_u), 1.0))

        # Cars cruise smoothly along wide unobstructed plowed road X in [-28, +28]!
        for c_root, cy, dir_s, ph in cars:
            cx = ((t * 4.2 * dir_s + ph + 28.0) % 56.0) - 28.0
            c_root.location = Vector((cx, cy, 0.018))

        for p_root, ph in pines:
            p_root.rotation_euler = (math.sin(t * 1.4 + ph) * 0.025, math.cos(t * 1.2 + ph) * 0.02, 0.0)

        for fl, sx, sy, sz, spd, ph in snow_flakes:
            nx = sx + math.sin(t * 1.8 + ph) * 0.40
            nz = 0.4 + ((sz - t * 1.2 * spd) % 9.0)
            fl.location = Vector((nx, sy, nz))

        set_transition_flash(scn, (dyn["match_flash"] ** 1.4) * 0.72, (1.0, 0.96, 0.86))

    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(update_rjukan_frame)
    scene.frame_start = start_frame
    scene.frame_end = end_frame - 1
    scene.frame_set(start_frame)
    update_rjukan_frame(scene)
    return scene
