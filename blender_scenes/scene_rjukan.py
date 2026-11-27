"""World 2: Rjukan Steep Dark Valley, Cliffside Solspeilet 3-Mirror Heliostat & Volumetric Golden God Ray Plaza."""
from __future__ import annotations

import math
import os
import random
from typing import Any, Dict, List

import bpy
from mathutils import Vector

from animation.storyboard import get_camera_at_frame, get_characters_at_frame, get_scene_dynamic_state, lerp
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
    set_mix_rgba_b,
    set_transition_flash,
    setup_world_sky,
)
from project_config import CHAR_HEIGHTS_M, DECALS_DIR


def build_and_bind_rjukan(
    sprites_dir: str,
    start_frame: int,
    end_frame: int,
    width: int = 720,
    height: int = 1280,
    samples: int = 22,
) -> bpy.types.Scene:
    clear_scene()
    scene = configure_render_eevee(width=width, height=height, fps=30, samples=samples, use_motion_blur=True)

    # Deep Freezing Nordic Blue-Violet Shadow Sky at 12:00 Noon + Atmospheric Snow Haze
    setup_world_sky(
        zenith_color=(0.04, 0.08, 0.22),
        horizon_color=(0.14, 0.22, 0.42),
        strength=0.45,
        haze_density=0.0055,
        haze_color=(0.35, 0.48, 0.72),
    )

    # ---------------- MATERIALS ----------------
    m_cobble = make_cel_pbr_material("RjukanCobble", (0.34, 0.36, 0.40), (0.14, 0.20, 0.38), roughness=0.58, bump_scale=22.0, bump_strength=0.25, pattern="cobble")
    m_cobble_wet = make_cel_pbr_material("RjukanCobbleWet", (0.46, 0.42, 0.36), (0.28, 0.28, 0.38), roughness=0.14, bump_scale=22.0, bump_strength=0.18, pattern="cobble")
    m_snow = make_cel_pbr_material("RjukanSnow", (0.86, 0.91, 0.98), (0.24, 0.38, 0.68), roughness=0.36, bump_scale=20.0, pattern="snow")
    m_cliff = make_cel_pbr_material("RjukanBlackCliff", (0.12, 0.13, 0.18), (0.05, 0.08, 0.18), roughness=0.86, bump_scale=6.0, bump_strength=0.35, pattern="noise")
    m_nordic_red = make_cel_pbr_material("NordicRedWood", (0.58, 0.14, 0.14), (0.16, 0.18, 0.36), roughness=0.62, bump_scale=16.0, pattern="wood")
    m_nordic_ochre = make_cel_pbr_material("NordicOchreWood", (0.76, 0.56, 0.18), (0.22, 0.24, 0.38), roughness=0.62, bump_scale=16.0, pattern="wood")
    m_nordic_white = make_cel_pbr_material("NordicWhiteWood", (0.86, 0.85, 0.82), (0.26, 0.34, 0.56), roughness=0.62, bump_scale=16.0, pattern="wood")
    m_roof_dark = make_cel_pbr_material("NordicSlateRoof", (0.16, 0.18, 0.24), (0.08, 0.12, 0.24), roughness=0.55)
    m_iron = make_cel_pbr_material("ClassicBlackIron", (0.12, 0.13, 0.16), (0.06, 0.08, 0.15), roughness=0.36, metallic=0.82)
    m_steel = make_cel_pbr_material("HeliostatSteel", (0.52, 0.56, 0.62), (0.20, 0.28, 0.44), roughness=0.32, metallic=0.85)
    m_solar = make_cel_pbr_material("SolarCellBlue", (0.08, 0.16, 0.38), (0.04, 0.10, 0.24), roughness=0.14, metallic=0.65)
    m_pine = make_cel_pbr_material("NordicPine", (0.10, 0.24, 0.16), (0.06, 0.14, 0.22), roughness=0.78)
    m_chair_blue = make_cel_pbr_material("BeachChairBlue", (0.12, 0.44, 0.84), (0.08, 0.22, 0.48), roughness=0.52)
    m_chair_white = make_cel_pbr_material("BeachChairWhite", (0.94, 0.94, 0.92), (0.36, 0.44, 0.62), roughness=0.52)
    m_wood_warm = make_cel_pbr_material("WarmBenchWood", (0.48, 0.30, 0.18), (0.18, 0.20, 0.34), roughness=0.55, pattern="wood")
    m_orange_rubber = make_cel_pbr_material("TabletRubberOrange", (0.92, 0.42, 0.10), (0.36, 0.22, 0.24), roughness=0.48)
    m_car_blue = make_cel_pbr_material("NordicCarBlue", (0.16, 0.36, 0.58), (0.08, 0.18, 0.36), roughness=0.22, metallic=0.45)
    m_car_red = make_cel_pbr_material("NordicCarRed", (0.68, 0.18, 0.18), (0.24, 0.16, 0.30), roughness=0.22, metallic=0.45)
    m_npc_skin = make_cel_pbr_material("NpcSkinR", (0.92, 0.78, 0.70), (0.38, 0.42, 0.60), roughness=0.58)

    m_win_warm = make_emissive_material("RjukanWinWarm", (1.0, 0.78, 0.34), strength=4.2)
    m_lamp_glow = make_emissive_material("StreetLampGlow", (1.0, 0.84, 0.48), strength=7.5)
    m_mirror_surface = make_emissive_material("SolspeiletMirrorGlow", (1.0, 0.92, 0.68), strength=2.2)
    m_godray_mat = make_emissive_material("VolumetricGodRayShaft", (1.0, 0.84, 0.44), strength=3.4, alpha=0.24)
    m_spotlight_patch = make_emissive_material("SunlitSquarePatch", (1.0, 0.88, 0.52), strength=2.2, alpha=0.45)
    m_snow_flake = make_emissive_material("SnowFlakeR", (0.88, 0.94, 1.0), strength=1.1)

    m_tablet_ui = make_decal_material("AstridTabletUI", os.path.join(DECALS_DIR, "tablet_heliostat_ui.png"), emissive=2.8)
    m_sign_rjukan = make_decal_material("RjukanSignMat", os.path.join(DECALS_DIR, "sign_rjukan_torg.png"), roughness=0.42)

    # ---------------- DYNAMIC STORY LIGHTING RIG ----------------
    # 1) Cold Nordic deep-shadow ambient fill (always present in surrounding snow!)
    bpy.ops.object.light_add(type="SUN", location=(-20.0, -20.0, 35.0), rotation=(math.radians(52), math.radians(15), math.radians(-30)))
    cold_sun = bpy.context.active_object
    cold_sun.name = "NordicShadowFill"
    cold_sun.data.energy = 1.15
    cold_sun.data.color = (0.42, 0.60, 1.0)

    # 2) Dramatic High-Altitude Golden Sun hitting ONLY the 3 cliff mirrors on the mountain peak!
    bpy.ops.object.light_add(type="SPOT", location=(-14.0, 10.0, 42.0))
    peak_sun = bpy.context.active_object
    peak_sun.name = "PeakHeliostatSun"
    peak_sun.data.energy = 28000.0
    peak_sun.data.color = (1.0, 0.84, 0.52)
    peak_sun.data.spot_size = math.radians(52)
    peak_sun.data.spot_blend = 0.4
    direction_p = Vector((0.0, 25.5, 31.0)) - peak_sun.location
    peak_sun.rotation_euler = direction_p.to_track_quat("-Z", "Y").to_euler()

    # 3) HERO DYNAMIC STORY SPOTLIGHT: Reflected Golden Beam blasting 450m down onto Rjukan Torg!
    bpy.ops.object.light_add(type="SPOT", location=(0.0, 24.5, 30.8))
    hero_spot = bpy.context.active_object
    hero_spot.name = "SolspeiletGoldenSpot"
    hero_spot.data.energy = 0.0  # Starts OFF at 00:25 -> blasts to 95,000W at 00:39.5!
    hero_spot.data.color = (1.0, 0.80, 0.40)
    hero_spot.data.spot_size = math.radians(16.5)
    hero_spot.data.spot_blend = 0.22
    hero_spot.data.shadow_soft_size = 0.6
    dir_sp = Vector((0.5, 0.8, 0.0)) - hero_spot.location
    hero_spot.rotation_euler = dir_sp.to_track_quat("-Z", "Y").to_euler()

    # 4) Warm Golden Ground Bounce Light illuminating Kakek Henrik & Arka when beam lands!
    bpy.ops.object.light_add(type="POINT", location=(0.45, 0.4, 1.1))
    bounce_light = bpy.context.active_object
    bounce_light.name = "PlazaWarmBounce"
    bounce_light.data.energy = 0.0  # Starts 0 -> rises to 1400W when beam hits!
    bounce_light.data.color = (1.0, 0.78, 0.36)

    # 5) Streetlamp practical warm point light
    bpy.ops.object.light_add(type="POINT", location=(-2.2, -2.4, 3.65))
    sl_light = bpy.context.active_object
    sl_light.data.energy = 160.0
    sl_light.data.color = (1.0, 0.82, 0.48)

    # ---------------- RJUKAN TORG PLAZA & SNOW BANKS (Z = 0.0) ----------------
    add_box("RjukanPlazaCobble", (0.0, 0.0, -0.25), (44.0, 44.0, 0.5), m_cobble)
    # Wet melting cobblestone inside the sunlit square patch!
    add_box("SunlitWetCobble", (0.45, 0.75, 0.008), (5.8, 5.4, 0.02), m_cobble_wet)
    # Glowing warm square highlight overlay (fades in when beam slams down!)
    square_patch = add_box("SunlitSquareOverlay", (0.45, 0.75, 0.022), (5.6, 5.2, 0.01), m_spotlight_patch)
    # Thick winter snow banks surrounding the central square
    add_box("SnowBankL", (-8.5, 1.0, 0.14), (10.0, 26.0, 0.32), m_snow)
    add_box("SnowBankR", (9.2, 1.0, 0.14), (10.0, 26.0, 0.32), m_snow)
    add_box("SnowBankBack", (0.0, 12.0, 0.25), (26.0, 10.0, 0.55), m_snow)
    add_box("SnowBankFront", (-4.8, -5.8, 0.12), (8.0, 5.2, 0.26), m_snow)

    # ---------------- STEEP NORTHERN MOUNTAIN WALL & SOLSPEILET CLIFF DECK (Z = 28m) ----------------
    add_box("MountainWallMain", (0.0, 34.0, 24.0), (110.0, 24.0, 62.0), m_cliff, rot=(math.radians(14), 0, 0))
    add_box("MountainSnowShoulder", (0.0, 28.5, 48.0), (104.0, 18.0, 6.0), m_snow)
    add_box("ValleyWallWest", (-38.0, 6.0, 18.0), (24.0, 72.0, 44.0), m_cliff, rot=(0, math.radians(-18), 0))
    add_box("ValleyWallEast", (38.0, 6.0, 18.0), (24.0, 72.0, 44.0), m_cliff, rot=(0, math.radians(18), 0))

    # Loc 2A: Astrid's Cliffside Steel Heliostat Observation Platform (Z = 28.0m)
    add_box("HeliostatDeck", (0.0, 22.8, 27.85), (15.0, 4.4, 0.30), m_steel)
    for rx in (-6.8, -4.0, -1.2, 1.6, 4.4, 6.8):
        add_cylinder(f"DeckPost_{rx}", (rx, 20.7, 28.55), 0.05, 1.15, m_iron, verts=8)
    add_box("DeckRailTop", (0.0, 20.7, 29.10), (14.2, 0.08, 0.08), m_iron)
    # Solar power panels & animated mini wind turbine beside the mirrors (real Solspeilet detail!)
    add_box("SolarPanelL", (-7.6, 24.2, 29.0), (2.4, 0.12, 1.5), m_solar, rot=(math.radians(55), 0, 0))
    add_cylinder("WindTurbinePole", (7.6, 24.0, 30.2), 0.09, 4.4, m_steel, verts=10)
    turbine_hub = bpy.data.objects.new("WindTurbineHub", None)
    turbine_hub.location = (7.6, 23.85, 32.3)
    bpy.context.collection.objects.link(turbine_hub)
    for bi in range(3):
        blade = add_box(f"TurbineBlade_{bi}", (0, 0, 0), (0.14, 0.04, 1.8), m_nordic_white, rot=(0, math.radians(bi * 120), 0))
        blade.parent = turbine_hub

    # Astrid's glowing industrial orange tablet in front of her at Z = 28m
    astrid_tab_body = add_box("AstridTabletBody", (-1.52, 21.42, 29.12), (0.48, 0.06, 0.34), m_orange_rubber, rot=(math.radians(-28), 0, math.radians(10)))
    astrid_tab_screen = add_decal_plane("AstridTabletScreen", (-1.52, 21.385, 29.135), 0.42, 0.28, (math.radians(62), 0, math.radians(10)), m_tablet_ui)

    # 3 GIANT SOLSPEILET MIRRORS (Real-world 3 rectangular heliostats on steel lattice A-frame trusses!)
    mirror_pivots: List[bpy.types.Object] = []
    for mi, mx in enumerate((-4.4, 0.0, 4.4)):
        # Steel A-frame mount posts
        add_cylinder(f"MirrorPylonL_{mi}", (mx - 1.1, 25.4, 29.8), 0.14, 3.8, m_steel, rot=(math.radians(-12), 0, 0), verts=8)
        add_cylinder(f"MirrorPylonR_{mi}", (mx + 1.1, 25.4, 29.8), 0.14, 3.8, m_steel, rot=(math.radians(-12), 0, 0), verts=8)
        add_cylinder(f"HydraulicActuator_{mi}", (mx, 25.9, 30.1), 0.10, 2.8, m_orange_rubber, rot=(math.radians(24), 0, 0), verts=8)
        piv = bpy.data.objects.new(f"SolspeiletMirrorPivot_{mi}", None)
        piv.location = (mx, 25.1, 31.4)
        bpy.context.collection.objects.link(piv)
        frame_b = add_box(f"MirrorFrame_{mi}", (0, 0, 0), (3.5, 0.22, 4.6), m_steel)
        glass_f = add_box(f"MirrorGlass_{mi}", (0, -0.13, 0), (3.25, 0.05, 4.35), m_mirror_surface)
        frame_b.parent = piv
        glass_f.parent = piv
        mirror_pivots.append(piv)

    # EPIC 450m VOLUMETRIC GOLDEN GOD RAY SHAFT (connecting cliff mirrors -> Rjukan Torg!)
    beam_start = Vector((0.0, 24.8, 31.0))
    beam_end = Vector((0.45, 0.75, 0.0))
    beam_vec = beam_end - beam_start
    beam_len = beam_vec.length
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=3.2, radius2=1.4, depth=beam_len, location=(beam_start + beam_end) * 0.5)
    god_ray_cone = bpy.context.active_object
    god_ray_cone.name = "VolumetricGodRayCone"
    god_ray_cone.rotation_euler = beam_vec.to_track_quat("-Z", "Y").to_euler()
    god_ray_cone.data.materials.append(m_godray_mat)

    # ---------------- HISTORIC NORWEGIAN BUILDINGS AROUND RJUKAN TORG ----------------
    bldg_specs = [
        (-12.5, -5.0, 5.2, 6.5, 6.2, m_nordic_red),
        (-12.8, 2.5, 5.4, 7.2, 7.4, m_nordic_ochre),
        (-12.2, 10.5, 5.0, 6.8, 6.0, m_nordic_white),
        (12.5, -4.5, 5.4, 6.6, 6.6, m_nordic_ochre),
        (12.8, 3.2, 5.2, 7.4, 7.8, m_nordic_red),
        (12.2, 11.0, 5.0, 6.4, 6.2, m_nordic_white),
        (-6.2, -13.5, 6.2, 5.2, 6.4, m_nordic_white),
        (0.5, -13.8, 6.8, 5.2, 7.2, m_nordic_red),
        (7.2, -13.5, 6.2, 5.2, 6.2, m_nordic_ochre),
    ]
    for bi, (bx, by, bw, bd, bh, bmat) in enumerate(bldg_specs):
        add_box(f"RjukanBldg_{bi}", (bx, by, bh * 0.5), (bw, bd, bh), bmat)
        # Pitched Nordic roof with snow blanket
        add_box(f"RjukanRoof_{bi}", (bx, by, bh + 0.75), (bw + 0.5, bd + 0.5, 1.5), m_roof_dark, rot=(0, math.radians(18 if bx < 0 else -18), 0))
        add_box(f"RjukanRoofSnow_{bi}", (bx, by, bh + 1.52), (bw + 0.35, bd + 0.35, 0.25), m_snow, rot=(0, math.radians(18 if bx < 0 else -18), 0))
        # Tiny cozy warm glowing Nordic windows facing the square
        face_x = bx + (bw * 0.5 + 0.04 if bx < 0 else -bw * 0.5 - 0.04)
        for wz in (2.0, 4.4):
            if abs(bx) > 9.0:
                for wy in (by - 1.6, by + 1.6):
                    add_box(f"RWin_{bi}_{wz}_{wy}", (face_x, wy, wz), (0.06, 0.95, 1.15), m_win_warm)
            else:
                for wx in (bx - 1.5, bx + 1.5):
                    add_box(f"RWinF_{bi}_{wz}_{wx}", (wx, by + bd * 0.5 + 0.04, wz), (0.95, 0.06, 1.15), m_win_warm)

    # ---------------- FOREGROUND & HERO PROPS ----------------
    # Classic Black Iron Streetlamp (snow-covered top) where Arka peeks out!
    add_cylinder("StreetLampPole", (-2.2, -2.4, 1.85), 0.08, 3.7, m_iron, verts=12)
    add_cylinder("StreetLampBase", (-2.2, -2.4, 0.32), 0.18, 0.65, m_iron, verts=12)
    add_box("StreetLampLantern", (-2.2, -2.4, 3.72), (0.42, 0.42, 0.52), m_lamp_glow)
    add_box("StreetLampCapSnow", (-2.2, -2.4, 4.04), (0.56, 0.56, 0.16), m_snow)

    # Kakek Henrik's iconic Blue-White Striped Folding Beach Chair in the snow + thermos & hot cocoa!
    chair_x, chair_y = 0.92, 0.92
    add_box("BeachChairFrameL", (chair_x - 0.38, chair_y, 0.48), (0.05, 0.92, 0.05), m_wood_warm, rot=(math.radians(32), 0, math.radians(-14)))
    add_box("BeachChairFrameR", (chair_x + 0.38, chair_y, 0.48), (0.05, 0.92, 0.05), m_wood_warm, rot=(math.radians(32), 0, math.radians(-14)))
    for si in range(5):
        s_mat = m_chair_blue if si % 2 == 0 else m_chair_white
        add_box(f"ChairStripe_{si}", (chair_x - 0.28 + si * 0.14, chair_y + 0.12, 0.52), (0.14, 0.85, 0.04), s_mat, rot=(math.radians(-58), 0, math.radians(-14)))
    add_box("BeachChairSeat", (chair_x, chair_y - 0.14, 0.34), (0.74, 0.52, 0.05), m_chair_blue, rot=(math.radians(-12), 0, math.radians(-14)))
    # Thermos & steaming hot cocoa beside chair
    add_cylinder("HenrikThermos", (chair_x + 0.62, chair_y - 0.22, 0.19), 0.075, 0.38, m_steel, verts=12)
    henrik_mug = add_cylinder("HenrikCocoaMug", (chair_x - 0.34, chair_y - 0.26, 0.92), 0.065, 0.12, m_nordic_red, verts=12)

    # Frosted wooden benches, Rjukan municipal sign, street coffee cart, snowy pine trees
    for bx, by, rz in [(-4.2, 2.2, 22), (4.6, 2.5, -24)]:
        add_box(f"BenchSeat_{bx}", (bx, by, 0.48), (1.8, 0.52, 0.08), m_wood_warm, rot=(0, 0, math.radians(rz)))
        add_box(f"BenchSnow_{bx}", (bx, by, 0.54), (1.76, 0.48, 0.06), m_snow, rot=(0, 0, math.radians(rz)))
    add_box("RjukanSignStand", (-4.8, 5.2, 1.35), (0.14, 0.14, 2.7), m_iron)
    add_decal_plane("RjukanSignFace", (-4.8, 5.08, 2.15), 1.9, 0.95, (math.radians(90), 0, math.radians(12)), m_sign_rjukan)
    # Street warm coffee cart
    add_box("CoffeeCartBody", (5.4, -2.6, 0.72), (1.7, 0.95, 1.1), m_nordic_red, rot=(0, 0, math.radians(-20)))
    add_box("CoffeeCartAwning", (5.4, -2.6, 2.25), (1.9, 1.15, 0.14), m_nordic_ochre, rot=(math.radians(10), 0, math.radians(-20)))

    # Swaying snow-laden Nordic pine trees
    pines = []
    for pi, (px, py, ph) in enumerate([(-6.8, 6.2, 5.4), (6.8, 6.8, 5.8), (-7.2, -4.2, 4.6), (7.6, 0.4, 5.0)]):
        p_root = bpy.data.objects.new(f"NordicPine_{pi}", None)
        p_root.location = (px, py, 0.0)
        bpy.context.collection.objects.link(p_root)
        tr = add_cylinder(f"PineTrunk_{pi}", (0, 0, ph * 0.2), 0.16, ph * 0.4, m_wood_warm, verts=8)
        tr.parent = p_root
        for tier in range(3):
            bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=1.35 - tier * 0.32, depth=1.8, location=(0, 0, ph * 0.36 + tier * 1.15))
            cn = bpy.context.active_object
            cn.name = f"PineTier_{pi}_{tier}"
            cn.data.materials.append(m_pine if tier % 2 == 0 else m_snow)
            cn.parent = p_root
        pines.append((p_root, pi * 1.4))

    # ---------------- LIVING BUSY ANIMATED SET DRESSING ----------------
    # 1) 8 Bundled-up Norwegian Townspeople NPCs walking & flocking toward sunlit square when beam lands!
    coat_mats = [m_nordic_red, m_car_blue, m_nordic_ochre, m_pine, m_nordic_white]
    town_npcs = []
    npc_starts = [(-5.8, -0.8), (-4.5, 4.8), (5.5, 4.2), (6.2, -0.5), (-3.5, 7.2), (3.8, 7.6), (-6.2, 3.0), (4.8, -4.5)]
    for ni, (nx, ny) in enumerate(npc_starts):
        npc = add_stylized_npc(f"RjukanNPC_{ni}", (nx, ny, 0.0), coat_mats[ni % len(coat_mats)], m_npc_skin, m_roof_dark, m_iron, 0.92 + (ni % 3) * 0.05)
        town_npcs.append((npc, nx, ny, ni * 0.9))

    # 2) 2 Nordic Winter Cars driving smoothly along the perimeter road behind the square
    cars = []
    for ci, (cy, cmat, dir_s) in enumerate([(8.8, m_car_blue, 1.0), (-8.6, m_car_red, -1.0)]):
        c_root = bpy.data.objects.new(f"NordicCar_{ci}", None)
        bpy.context.collection.objects.link(c_root)
        add_box(f"CarBody_{ci}", (0, 0, 0.58), (3.6, 1.65, 0.85), cmat).parent = c_root
        add_box(f"CarCab_{ci}", (-0.15, 0, 1.25), (1.9, 1.45, 0.65), m_snow).parent = c_root
        add_box(f"CarHeadL_{ci}", (1.82 * dir_s, -0.52, 0.62), (0.08, 0.28, 0.20), m_lamp_glow).parent = c_root
        add_box(f"CarHeadR_{ci}", (1.82 * dir_s, 0.52, 0.62), (0.08, 0.28, 0.20), m_lamp_glow).parent = c_root
        cars.append((c_root, cy, dir_s))

    # 3) 120 Falling Snow Particles drifting through blue shade & golden god ray!
    rng = random.Random(202)
    snow_flakes = []
    for si in range(120):
        sx = rng.uniform(-10.0, 10.0)
        sy = rng.uniform(-9.0, 10.0)
        sz = rng.uniform(0.5, 9.5)
        fl = add_sphere(f"RjuSnow_{si}", (sx, sy, sz), rng.uniform(0.018, 0.042), m_snow_flake, segments=6)
        snow_flakes.append((fl, sx, sy, sz, rng.uniform(0.6, 1.3), rng.uniform(0, 6.28)))

    # ---------------- PYTHON 2.5D CHARACTERS (Arka, Astrid, Kakek Henrik) ----------------
    char_cards: Dict[str, Any] = {}
    for cid in ("arka", "astrid", "kakek_henrik"):
        first_png = os.path.join(sprites_dir, cid, f"frame_{start_frame:04d}.png")
        obj, tex_node, tint_node = create_character_card(cid, CHAR_HEIGHTS_M[cid], first_png, ambient_tint=(0.68, 0.78, 1.0))
        char_cards[cid] = (obj, tex_node, tint_node)

    # ---------------- CAMERA ----------------
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.clip_start = 0.08
    cam_data.clip_end = 260.0
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
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

        piv_u = dyn["mirror_pivot"]
        beam_u = dyn["beam_shoot"]
        lit_u = dyn["square_lit"]

        # DYNAMIC STORY LIGHTING TURN!
        # Cold blue shadow (0.65, 0.76, 1.0) snaps to warm golden bounce light (1.16, 1.04, 0.84) when mirrors illuminate plaza!
        hero_spot.data.energy = 115000.0 * lit_u
        bounce_light.data.energy = 1650.0 * lit_u
        square_patch.hide_render = lit_u < 0.05

        # Mirror hydraulic rotation & golden glow ramp
        for mi, piv in enumerate(mirror_pivots):
            piv.rotation_euler = (math.radians(lerp(-5.0, 26.0, piv_u)), 0.0, math.radians((mi - 1) * 8.0 * (1.0 - piv_u)))
        turbine_hub.rotation_euler = (0.0, t * 4.5, 0.0)

        # God ray shaft extends dynamically from mountain peak (beam_start) down into Rjukan Torg (beam_end)!
        if beam_u < 0.02:
            god_ray_cone.hide_render = True
        else:
            god_ray_cone.hide_render = False
            cur_end = beam_start.lerp(beam_end, beam_u)
            god_ray_cone.location = (beam_start + cur_end) * 0.5
            god_ray_cone.scale = (0.45 + 0.55 * beam_u, 0.45 + 0.55 * beam_u, max(0.05, beam_u))

        # Update characters + dynamic warm/cool light tinting!
        for cid, (obj, tex_node, tint_node) in char_cards.items():
            st = chars[cid]
            obj.location = Vector(st["pos"])
            obj.rotation_euler = (0.0, 0.0, st["rot_z"])
            obj.hide_render = not st["visible"]
            if cid == "astrid":
                # Astrid sits high up on the sunlit cliff rim
                set_mix_rgba_b(tint_node, (1.02, 0.98, 0.92, 1.0))
            else:
                # Arka & Henrik shift dramatically from freezing blue shadow to warm golden sunlight!
                r_c = lerp(0.62, 1.15, lit_u)
                g_c = lerp(0.75, 1.05, lit_u)
                b_c = lerp(1.00, 0.86, lit_u)
                set_mix_rgba_b(tint_node, (r_c, g_c, b_c, 1.0))
            png_path = os.path.join(sprites_dir, cid, f"frame_{f:04d}.png")
            if os.path.exists(png_path):
                tex_node.image = bpy.data.images.load(png_path, check_existing=True)

        # Henrik cocoa mug sip bob
        sip = math.sin(max(0.0, min(1.0, (t - 42.2) / 1.8)) * math.pi)
        henrik_mug.location = Vector((chair_x - 0.30, chair_y - 0.25, 0.90 + sip * 0.22))

        # Animated living Rjukan town NPCs flocking excitedly toward the newly-lit golden square!
        for npc, nx, ny, ph in town_npcs:
            # Move 35% closer toward golden square (0.5, 0.8) once spotlight hits!
            cx = lerp(nx, nx * 0.62 + 0.3, lit_u) + math.sin(t * 0.9 + ph) * 0.45
            cy = lerp(ny, ny * 0.62 + 0.5, lit_u) + math.cos(t * 0.8 + ph) * 0.35
            hop = abs(math.sin(t * 5.2 + ph)) * 0.06
            npc.location = Vector((cx, cy, hop))
            npc.rotation_euler.z = math.atan2(0.8 - cy, 0.5 - cx) - math.pi * 0.5

        for c_root, cy, dir_s in cars:
            cx = ((t * 3.8 * dir_s + 15.0) % 36.0) - 18.0
            c_root.location = Vector((cx, cy, 0.0))

        for p_root, ph in pines:
            p_root.rotation_euler = (math.sin(t * 1.4 + ph) * 0.03, math.cos(t * 1.2 + ph) * 0.025, 0.0)

        for fl, sx, sy, sz, spd, ph in snow_flakes:
            nx = sx + math.sin(t * 1.8 + ph) * 0.45
            nz = 0.4 + ((sz - t * 1.2 * spd) % 9.0)
            fl.location = Vector((nx, sy, nz))

        # Sunglasses golden light bar Match-Cut flash (00:48.35 -> 00:49.0)
        set_transition_flash(scn, dyn["match_flash"] ** 1.3, (1.0, 0.97, 0.88))

    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(update_rjukan_frame)
    scene.frame_start = start_frame
    scene.frame_end = end_frame - 1
    scene.frame_set(start_frame)
    update_rjukan_frame(scene)
    return scene
