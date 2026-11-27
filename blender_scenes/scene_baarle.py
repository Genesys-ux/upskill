"""World 3 (v2 Audited): Baarle-Nassau / Baarle-Hertog Corner Café, Italian Espresso Bar & Iconic Dual-Flag Brick House."""
from __future__ import annotations

import math
import os
from typing import Any, Dict

import bpy
from mathutils import Vector

from animation.storyboard import BAR_TOP_Z, BRAM_STEP_Z, CAFE_FLOOR_Z, compute_billboard_rot_z, get_camera_at_frame, get_characters_at_frame, get_scene_dynamic_state
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
    set_transition_flash,
    setup_world_sky,
)
from blender_scenes.props_3d import (
    build_3d_car,
    build_baarle_dual_flag_house,
    build_dutch_bicycle,
    build_edison_pendant,
    build_italian_espresso_machine,
    build_pastry_display_case,
)
from characters.npc_generator import NPC_ROSTER
from project_config import CHAR_HEIGHTS_M, DECALS_DIR


def build_and_bind_baarle(
    sprites_dir: str,
    start_frame: int,
    end_frame: int,
    width: int = 720,
    height: int = 1280,
    samples: int = 8,
) -> bpy.types.Scene:
    clear_scene()
    scene = configure_render_eevee(width=width, height=height, fps=30, samples=samples, use_motion_blur=True)

    # STRICT ISOLATION: COL_03_Baarle ONLY (ZERO SNOW PARTICLES ANYWHERE IN THIS SCENE!)
    col_world = get_or_create_collection("COL_03_Baarle")

    # Warm Golden Afternoon European Low Sun Sky
    setup_world_sky(
        zenith_color=(0.24, 0.48, 0.80),
        horizon_color=(1.00, 0.74, 0.44),
        strength=0.92,
        haze_density=0.0018,
        haze_color=(1.0, 0.88, 0.68),
    )

    # ---------------- WORLD-SPACE PBR MATERIALS (CRISP REAL BRICK & WOOD!) ----------------
    m_clinker = make_cel_pbr_material("BaarleClinkerPave", (0.50, 0.34, 0.26), (0.28, 0.24, 0.36), roughness=0.62, bump_scale=8.0, bump_strength=0.22, pattern="cobble", color_b=(0.38, 0.26, 0.20))
    m_brick_red = make_cel_pbr_material("DutchRedBrick", (0.58, 0.24, 0.17), (0.30, 0.20, 0.30), roughness=0.72, bump_scale=5.5, bump_strength=0.30, pattern="brick", color_b=(0.44, 0.18, 0.13))
    m_brick_warm = make_cel_pbr_material("BelgianOchreBrick", (0.68, 0.48, 0.30), (0.34, 0.26, 0.34), roughness=0.72, bump_scale=5.5, bump_strength=0.26, pattern="brick", color_b=(0.56, 0.38, 0.24))
    m_oak_gloss = make_cel_pbr_material("VarnishedOakBar", (0.46, 0.27, 0.14), (0.24, 0.16, 0.22), roughness=0.26, bump_scale=5.0, bump_strength=0.16, pattern="wood")
    m_oak_dark = make_cel_pbr_material("DarkOakPanel", (0.30, 0.18, 0.10), (0.16, 0.12, 0.18), roughness=0.38, bump_scale=5.0, pattern="wood")
    m_cafe_floor = make_cel_pbr_material("CafeWarmTile", (0.72, 0.62, 0.48), (0.38, 0.32, 0.40), roughness=0.36, bump_scale=6.0, pattern="cobble")
    m_cafe_wall = make_cel_pbr_material("CafePlasterCream", (0.90, 0.84, 0.72), (0.48, 0.42, 0.50), roughness=0.68)
    m_green_frame = make_cel_pbr_material("CafeForestGreen", (0.10, 0.30, 0.20), (0.06, 0.16, 0.18), roughness=0.36)
    m_awning_cream = make_cel_pbr_material("AwningCream", (0.95, 0.90, 0.78), (0.50, 0.46, 0.52), roughness=0.72)
    m_brass = make_cel_pbr_material("InlaidBrass", (0.88, 0.68, 0.24), (0.42, 0.32, 0.18), roughness=0.18, metallic=0.92)
    m_chrome = make_cel_pbr_material("EspressoChrome", (0.86, 0.89, 0.93), (0.40, 0.46, 0.58), roughness=0.12, metallic=0.94)
    m_white_stone = make_cel_pbr_material("LimestoneTrim", (0.94, 0.92, 0.88), (0.54, 0.52, 0.58), roughness=0.45)
    m_rattan = make_cel_pbr_material("RattanChair", (0.68, 0.50, 0.28), (0.34, 0.26, 0.30), roughness=0.62, pattern="wood")
    m_ceramic_w = make_cel_pbr_material("LatteCeramic", (0.96, 0.95, 0.92), (0.58, 0.56, 0.62), roughness=0.16)
    m_coffee = make_cel_pbr_material("LatteFoam", (0.62, 0.40, 0.24), (0.30, 0.20, 0.16), roughness=0.35)
    m_pastry = make_cel_pbr_material("CroissantGold", (0.86, 0.56, 0.20), (0.44, 0.28, 0.18), roughness=0.42)
    m_waffle = make_cel_pbr_material("StroopwafelBrown", (0.68, 0.42, 0.18), (0.34, 0.22, 0.16), roughness=0.50)
    m_terracotta = make_cel_pbr_material("TerracottaPot", (0.74, 0.36, 0.22), (0.36, 0.20, 0.22), roughness=0.68)
    m_geranium = make_cel_pbr_material("GeraniumRed", (0.88, 0.14, 0.16), (0.40, 0.12, 0.18), roughness=0.55)
    m_leaf = make_cel_pbr_material("LeafGreen", (0.16, 0.46, 0.18), (0.08, 0.24, 0.18), roughness=0.60)
    m_dark_iron = make_cel_pbr_material("BikeIron", (0.14, 0.15, 0.18), (0.08, 0.10, 0.16), roughness=0.38, metallic=0.75)
    m_tire = make_cel_pbr_material("EuroTire", (0.08, 0.08, 0.10), (0.04, 0.04, 0.06), roughness=0.82)
    m_car_mint = make_cel_pbr_material("EuroCarMint", (0.28, 0.62, 0.56), (0.14, 0.32, 0.38), roughness=0.22, metallic=0.45)
    m_car_mustard = make_cel_pbr_material("EuroCarMustard", (0.84, 0.64, 0.18), (0.38, 0.28, 0.22), roughness=0.22, metallic=0.45)
    m_car_glass = make_cel_pbr_material("EuroCarGlass", (0.12, 0.20, 0.28), (0.06, 0.12, 0.20), roughness=0.08, metallic=0.5)
    m_bottle_g = make_cel_pbr_material("BottleGreen", (0.12, 0.42, 0.22), (0.06, 0.20, 0.14), roughness=0.12, metallic=0.2)
    m_bottle_a = make_cel_pbr_material("BottleAmber", (0.72, 0.36, 0.10), (0.32, 0.16, 0.08), roughness=0.12, metallic=0.2)
    m_curtain = make_cel_pbr_material("HouseCurtainCream", (0.95, 0.92, 0.84), (0.56, 0.52, 0.56), roughness=0.82)
    m_flag_r = make_cel_pbr_material("FlagRed", (0.82, 0.14, 0.16), (0.40, 0.12, 0.16), roughness=0.6)
    m_flag_b = make_cel_pbr_material("FlagBlue", (0.12, 0.26, 0.62), (0.08, 0.14, 0.36), roughness=0.6)
    m_flag_y = make_cel_pbr_material("FlagYellow", (0.95, 0.78, 0.12), (0.48, 0.36, 0.12), roughness=0.6)

    m_edison = make_emissive_material("EdisonWarmBulb", (1.0, 0.78, 0.36), strength=5.5)
    m_head_glow = make_emissive_material("EuroHeadLight", (1.0, 0.94, 0.76), strength=3.0)
    m_tail_glow = make_emissive_material("EuroTailRed", (1.0, 0.14, 0.10), strength=3.0)
    m_steam = make_soft_godray_material("WispyEspressoSteam", (0.98, 0.96, 0.92), strength=0.45, max_opacity=0.22)
    m_glass = make_emissive_material("CafeGlassPane", (0.82, 0.92, 0.98), strength=0.25, alpha=0.14)

    m_border_tile = make_decal_material("BaarleCrossTileMat", os.path.join(DECALS_DIR, "baarle_border_cross_tile.png"), roughness=0.48)
    m_menu_decal = make_decal_material("BaarleMenuMat", os.path.join(DECALS_DIR, "baarle_cafe_menu.png"), emissive=0.18, roughness=0.62)
    # Bright crisp official Dutch & Belgian house-number plaques (emissive=0.42 so they NEVER render dark!)
    m_plaque_b = make_decal_material("PlaqueBelgiumMat", os.path.join(DECALS_DIR, "plaque_belgium_2.png"), emissive=0.42, roughness=0.35)
    m_plaque_nl = make_decal_material("PlaqueNLMat", os.path.join(DECALS_DIR, "plaque_netherlands_19.png"), emissive=0.42, roughness=0.35)

    # ---------------- GOLDEN AFTERNOON LOW-SUN LIGHTING ----------------
    bpy.ops.object.light_add(type="SUN", location=(-24.0, -18.0, 12.0), rotation=(math.radians(72), math.radians(-18), math.radians(-40)))
    sun = bpy.context.active_object
    sun.name = "GoldenAfternoonLowSun"
    sun.data.energy = 5.4
    sun.data.color = (1.0, 0.80, 0.52)
    sun.data.angle = math.radians(1.8)

    # Dedicated warm golden bounce lighting the opposite Baarle dual-flag house (+Y facade!) so brick & plaques pop!
    bpy.ops.object.light_add(type="AREA", location=(0.0, -7.2, 4.2), rotation=(math.radians(76), 0, 0))
    house_fill = bpy.context.active_object
    house_fill.name = "DualHouseFacadeWarmFill"
    house_fill.data.energy = 950.0
    house_fill.data.color = (1.0, 0.86, 0.64)
    house_fill.data.size = 6.5

    # Warm Edison Pendant Lamps with conical black-iron shades inside Café de Grens!
    for ex in (-1.85, 0.0, 1.85):
        bpy.ops.object.light_add(type="POINT", location=(ex, 4.4, 2.75))
        el = bpy.context.active_object
        el.data.energy = 165.0
        el.data.color = (1.0, 0.76, 0.38)
        build_edison_pendant(f"EdisonPendant_{ex}", (ex, 4.4, 2.88), m_dark_iron, m_brass, m_edison, col=col_world)

    bpy.ops.object.light_add(type="AREA", location=(0.0, 1.8, 2.6), rotation=(math.radians(52), 0, 0))
    c_fill = bpy.context.active_object
    c_fill.data.energy = 420.0
    c_fill.data.color = (1.0, 0.90, 0.78)
    c_fill.data.size = 5.5

    # ---------------- SIDEWALK, STREET & ICONIC WHITE CROSS (+) B|NL BORDER ----------------
    add_box("BaarleStreetClinker", (0.0, -7.5, -0.25), (44.0, 16.0, 0.5), m_clinker, col=col_world)
    add_box("CafeFloorBase", (0.0, 4.5, -0.24), (11.2, 9.2, 0.48), m_cafe_floor, col=col_world)

    # ICONIC B | NL WHITE CROSS BORDER TILES running cleanly down X = 0.0 from street -> sidewalk -> café floor!
    for ti in range(-10, 6):
        ty = ti * 1.05
        add_decal_plane(f"BorderCrossTile_{ti}", (0.0, ty, 0.012), 1.02, 1.02, (0, 0, 0), m_border_tile, col=col_world)

    # ---------------- AUTHENTIC EUROPEAN CORNER CAFÉ DE GRENS (Y in [0, 9]) ----------------
    add_box("CafeBackWall", (0.0, 8.6, 2.1), (11.2, 0.35, 4.2), m_cafe_wall, col=col_world)
    add_box("CafeBackWainscot", (0.0, 8.38, 0.68), (11.0, 0.12, 1.36), m_oak_dark, col=col_world)
    add_box("CafeLeftWall", (-5.4, 4.3, 2.1), (0.35, 8.8, 4.2), m_brick_red, col=col_world)
    add_box("CafeRightWall", (5.4, 4.3, 2.1), (0.35, 8.8, 4.2), m_brick_red, col=col_world)
    # Coffered ceiling beams (NOT flat stretched brown plane!)
    add_box("CafeCeiling", (0.0, 4.3, 4.02), (11.2, 9.0, 0.22), m_cafe_wall, col=col_world)
    for by in (1.4, 3.2, 5.0, 6.8):
        add_box(f"CeilingBeam_{by}", (0.0, by, 3.84), (10.8, 0.22, 0.24), m_oak_dark, col=col_world)

    # Brick Exterior Upper Facade + Dark-Green Mullioned Storefront & Wide-Open Double Doors (X in [-2.0, +2.0])
    add_box("CafeUpperBrick", (0.0, 0.0, 5.75), (11.8, 0.48, 3.5), m_brick_red, col=col_world)
    add_box("CafeBrickCornice", (0.0, -0.25, 3.92), (12.0, 0.36, 0.22), m_white_stone, col=col_world)
    for fx in (-5.0, -2.15, 2.15, 5.0):
        add_box(f"FrontPillar_{fx}", (fx, 0.0, 2.0), (0.32, 0.36, 4.0), m_green_frame, bevel=0.02, col=col_world)
    add_box("FrontHeaderBeam", (0.0, 0.0, 3.72), (10.4, 0.38, 0.50), m_green_frame, col=col_world)

    # Mullioned European Café Windows + Terracotta Geranium Flower Boxes
    for wx in (-3.58, 3.58):
        add_box(f"WindowBrickSill_{wx}", (wx, 0.0, 0.44), (2.56, 0.38, 0.88), m_brick_red, col=col_world)
        add_box(f"WindowStoneCap_{wx}", (wx, -0.05, 0.90), (2.64, 0.46, 0.08), m_white_stone, col=col_world)
        add_box(f"WindowGlass_{wx}", (wx, 0.0, 2.24), (2.48, 0.04, 2.55), m_glass, col=col_world)
        add_box(f"WindowMullV_{wx}", (wx, -0.03, 2.24), (0.07, 0.08, 2.56), m_green_frame, col=col_world)
        add_box(f"WindowMullH_{wx}", (wx, -0.03, 2.65), (2.52, 0.08, 0.07), m_green_frame, col=col_world)
        # Detailed terracotta planter box + leafy geranium clusters!
        add_box(f"PlanterBox_{wx}", (wx, -0.38, 1.04), (1.95, 0.34, 0.26), m_terracotta, bevel=0.02, col=col_world)
        for gi in range(6):
            gx = wx - 0.78 + gi * 0.31
            add_sphere(f"GerLeaf_{wx}_{gi}", (gx, -0.38, 1.24), 0.14, m_leaf, scale=(1.1, 0.9, 0.7), segments=8, col=col_world)
            add_sphere(f"GerPetalA_{wx}_{gi}", (gx - 0.04, -0.44, 1.34), 0.075, m_geranium, segments=8, col=col_world)
            add_sphere(f"GerPetalB_{wx}_{gi}", (gx + 0.05, -0.34, 1.37), 0.065, m_geranium, segments=8, col=col_world)

    # Striped Forest-Green & Cream Fabric Café Awning + Iron Support Arms + Fluttering NL & BE Mini Flags!
    for si in range(11):
        sx = -4.5 + si * 0.90
        sm = m_green_frame if si % 2 == 0 else m_awning_cream
        add_box(f"AwningStripe_{si}", (sx, -0.95, 3.60), (0.90, 1.88, 0.09), sm, rot=(math.radians(-18), 0, 0), col=col_world)
        add_box(f"AwningValance_{si}", (sx, -1.84, 3.16), (0.90, 0.05, 0.28), sm, col=col_world)
    for ax in (-4.8, 4.8):
        add_cylinder(f"AwningArm_{ax}", (ax, -0.92, 3.25), 0.025, 1.9, m_dark_iron, rot=(math.radians(78), 0, 0), verts=8, col=col_world)

    flag_be_root = bpy.data.objects.new("MiniFlagBelgium", None)
    flag_be_root.location = (-4.8, -1.85, 3.45)
    col_world.objects.link(flag_be_root)
    for part in [
        add_box("FlagBE_Blk", (-0.18, 0, 0), (0.18, 0.03, 0.36), m_dark_iron, col=col_world),
        add_box("FlagBE_Yel", (0.0, 0, 0), (0.18, 0.03, 0.36), m_flag_y, col=col_world),
        add_box("FlagBE_Red", (0.18, 0, 0), (0.18, 0.03, 0.36), m_flag_r, col=col_world),
    ]:
        part.parent = flag_be_root

    flag_nl_root = bpy.data.objects.new("MiniFlagNetherlands", None)
    flag_nl_root.location = (4.8, -1.85, 3.45)
    col_world.objects.link(flag_nl_root)
    for part in [
        add_box("FlagNL_Red", (0, 0, 0.12), (0.54, 0.03, 0.12), m_flag_r, col=col_world),
        add_box("FlagNL_Wht", (0, 0, 0.0), (0.54, 0.03, 0.12), m_white_stone, col=col_world),
        add_box("FlagNL_Blu", (0, 0, -0.12), (0.54, 0.03, 0.12), m_flag_b, col=col_world),
    ]:
        part.parent = flag_nl_root

    # ---------------- HERO PANELED OAK BAR COUNTER (BAR_TOP_Z = 0.86m) + BACK-BAR SHELVES ----------------
    # Raised wooden duckboard behind bar so Bram (BRAM_STEP_Z = 0.24) clears bar cleanly with full chest & apron!
    add_box("BramDuckboard", (0.8, 5.95, BRAM_STEP_Z * 0.5), (3.8, 0.95, BRAM_STEP_Z), m_oak_dark, col=col_world)
    add_box("OakBarBody", (0.0, 5.20, BAR_TOP_Z * 0.5 - 0.03), (6.2, 0.86, BAR_TOP_Z - 0.06), m_oak_dark, col=col_world)
    add_box("OakBarTop", (0.0, 5.15, BAR_TOP_Z - 0.03), (6.45, 1.04, 0.06), m_oak_gloss, bevel=0.015, col=col_world)
    # Recessed decorative wooden bar front panels + brass footrail!
    for px in (-2.4, -1.2, 1.2, 2.4):
        add_box(f"BarPanel_{px}", (px, 4.76, 0.42), (0.92, 0.05, 0.58), m_oak_gloss, bevel=0.01, col=col_world)
    add_cylinder("BarBrassFootrail", (0.0, 4.62, 0.16), 0.022, 6.0, m_brass, rot=(0, math.radians(90), 0), verts=10, col=col_world)
    # Gleaming INLAID BRASS BORDER STRIP (X = 0.0 across bar top & front!)
    add_box("BrassBarBorderTop", (0.0, 5.15, BAR_TOP_Z + 0.006), (0.055, 1.06, 0.012), m_brass, col=col_world)
    add_box("BrassBarBorderFront", (0.0, 4.76, BAR_TOP_Z * 0.5), (0.055, 0.025, BAR_TOP_Z), m_brass, col=col_world)

    # Rich Cozy Back-Bar Shelves (bottles, stacked ceramic cups, coffee canisters + framed chalkboard menu!)
    for sz in (1.75, 2.45):
        add_box(f"BackShelf_{sz}", (1.75, 8.20, sz), (3.6, 0.34, 0.06), m_oak_gloss, col=col_world)
    for bi in range(8):
        bx = 0.25 + bi * 0.40
        bm = m_bottle_g if bi % 2 == 0 else m_bottle_a
        add_cylinder(f"BackBottle_{bi}", (bx, 8.22, 1.94), 0.052, 0.30, bm, verts=12, col=col_world)
        add_cylinder(f"BackBottleNeck_{bi}", (bx, 8.22, 2.13), 0.022, 0.10, bm, verts=10, col=col_world)
    for ci in range(6):
        cx = 0.35 + ci * 0.52
        add_cylinder(f"BackCupA_{ci}", (cx, 8.22, 2.54), 0.058, 0.10, m_ceramic_w, verts=12, col=col_world)
        add_cylinder(f"BackCupB_{ci}", (cx, 8.22, 2.65), 0.054, 0.10, m_ceramic_w, verts=12, col=col_world)
    add_decal_plane("BaarleChalkboard", (-1.85, 8.38, 2.25), 1.48, 1.85, (math.radians(90), 0, 0), m_menu_decal, col=col_world)

    # Commercial Italian Espresso Machine cleanly on FAR RIGHT (+2.15) & Pastry Case cleanly on FAR LEFT (-2.25) -> ZERO BRAM CLIPPING!
    build_italian_espresso_machine("ItalianEspresso", (2.15, 5.20, BAR_TOP_Z), m_chrome, m_brass, m_dark_iron, m_ceramic_w, col=col_world)
    build_pastry_display_case("PastryVitrine", (-2.25, 5.15, BAR_TOP_Z), m_glass, m_dark_iron, m_oak_gloss, m_pastry, m_waffle, col=col_world)

    # Subtle translucent wispy steam rising from the angled steam wand (NOT solid white balls!)
    steam_wisps = []
    for spi in range(3):
        sp = add_cylinder(f"SteamWisp_{spi}", (1.81, 4.98, BAR_TOP_Z + 0.45 + spi * 0.18), 0.055, 0.18, m_steam, verts=10, col=col_world)
        sp.visible_shadow = False
        steam_wisps.append((sp, 1.81, 4.98, BAR_TOP_Z + 0.36, spi * 0.7))

    # HERO SLIDING LATTE CUP (slides swiftly across brass border at BAR_TOP_Z=0.86!)
    latte_root = bpy.data.objects.new("HeroSlidingLatte", None)
    col_world.objects.link(latte_root)
    for part in [
        add_cylinder("LatteSaucer", (0, 0, 0.012), 0.11, 0.02, m_ceramic_w, verts=16, col=col_world),
        add_cylinder("LatteCup", (0, 0, 0.07), 0.075, 0.11, m_ceramic_w, verts=16, col=col_world),
        add_cylinder("LatteFoamTop", (0, 0, 0.122), 0.068, 0.015, m_coffee, verts=16, col=col_world),
    ]:
        part.parent = latte_root

    arka_cup = add_cylinder("ArkaFinaleCup", (-0.28, -2.56, 1.16), 0.06, 0.12, m_ceramic_w, verts=12, col=col_world)

    # ---------------- CLARA'S BORDER CHAIR & BISTRO TABLE (ZERO CLIPPING CLEARANCES!) ----------------
    # Clara stands/sits at (-0.85, 3.65). Chair placed strictly BEHIND her at (-0.85, 4.02); bistro table clearly LEFT at (-1.88, 3.60)!
    cx_c, cy_c = -0.85, 4.02
    add_cylinder("ClaraChairSeat", (cx_c, cy_c, 0.46), 0.27, 0.045, m_rattan, verts=16, col=col_world)
    add_box("ClaraChairBack", (cx_c, cy_c + 0.24, 0.78), (0.48, 0.05, 0.56), m_rattan, bevel=0.015, col=col_world)
    for lx, ly in [(-0.20, -0.20), (0.20, -0.20), (-0.20, 0.20), (0.20, 0.20)]:
        add_cylinder(f"ClaraChairLeg_{lx}_{ly}", (cx_c + lx, cy_c + ly, 0.23), 0.022, 0.46, m_oak_dark, verts=8, col=col_world)
    add_box("ClaraChairRung", (cx_c, cy_c - 0.18, 0.22), (0.42, 0.032, 0.032), m_oak_dark, col=col_world)

    # Bistro table cleanly left at X = -1.88 (1.03m clear of Clara, 2.98m clear of Arka -> ZERO tabletop slicing!)
    add_cylinder("BistroTableBase", (-1.88, 3.60, 0.03), 0.28, 0.05, m_dark_iron, verts=14, col=col_world)
    add_cylinder("BistroTablePost", (-1.88, 3.60, 0.38), 0.045, 0.74, m_dark_iron, verts=10, col=col_world)
    add_cylinder("BistroTableTop", (-1.88, 3.60, 0.76), 0.44, 0.045, m_oak_gloss, verts=18, col=col_world)
    add_box("ClaraNotebook", (-1.82, 3.55, 0.80), (0.24, 0.18, 0.024), m_white_stone, rot=(0, 0, math.radians(16)), col=col_world)

    # Far-side café bistro tables (|X| >= 3.5 -> 100% clear of central camera aisle!)
    for ti, (tx, ty) in enumerate([(-3.7, 2.5), (3.7, 2.6), (-3.8, 6.2), (3.8, 6.4)]):
        add_cylinder(f"TablePost_{ti}", (tx, ty, 0.38), 0.045, 0.76, m_dark_iron, verts=10, col=col_world)
        add_cylinder(f"TableTop_{ti}", (tx, ty, 0.76), 0.46, 0.045, m_oak_gloss, verts=16, col=col_world)

    # ---------------- ICONIC OPPOSITE BAARLE DUAL-FLAG STEPPED-GABLE BRICK HOUSE (Y = -12.4m) ----------------
    build_baarle_dual_flag_house(
        "DualDoorHouse", (0.0, -12.4, 0.0),
        m_brick_red, m_white_stone, m_green_frame, m_brass, m_car_glass, m_curtain, m_plaque_b, m_plaque_nl, m_edison,
        col=col_world,
    )
    # Flanking European stepped-gable townhouses
    for sx, hmat in [(-7.4, m_brick_warm), (7.4, m_brick_warm), (-14.2, m_brick_red), (14.2, m_brick_red)]:
        add_box(f"RowHouse_{sx}", (sx, -12.6, 3.2), (6.5, 2.6, 6.4), hmat, col=col_world)
        for si, (sw, sz) in enumerate([(5.0, 6.8), (3.4, 7.6), (1.8, 8.4)]):
            add_box(f"RowGable_{sx}_{si}", (sx, -11.4, sz), (sw, 0.38, 0.8), hmat, col=col_world)
            add_box(f"RowCap_{sx}_{si}", (sx, -11.38, sz + 0.40), (sw + 0.14, 0.44, 0.08), m_white_stone, col=col_world)

    # 3 Detailed Classic Dutch City Bicycles parked cleanly outside sides of café
    build_dutch_bicycle("DutchBike_0", (-4.4, -1.8, 0.0), math.radians(12), m_flag_b, m_tire, m_dark_iron, m_rattan, col=col_world)
    build_dutch_bicycle("DutchBike_1", (-5.4, -2.0, 0.0), math.radians(-8), m_brick_red, m_tire, m_dark_iron, m_rattan, col=col_world)
    build_dutch_bicycle("DutchBike_2", (4.5, -1.8, 0.0), math.radians(-14), m_green_frame, m_tire, m_dark_iron, m_rattan, col=col_world)

    # ---------------- 4 UNIFIED 2.5D BEAN-HEAD NPCs + 2 REAL 3D WHEELED EUROPEAN CARS (ZERO CAMERA OBSTRUCTION!) ----------------
    npc_dir = os.path.join(sprites_dir, "npcs")
    # 2 seated café patrons on far left/right tables (|X| = 3.55); 2 pedestrians walking strictly along far street (Y = -8.6 / -9.4)
    npc_specs_pos = [
        (NPC_ROSTER["baarle"][0], -3.55, 3.25, "patron"),
        (NPC_ROSTER["baarle"][1], 3.55, 3.35, "patron"),
        (NPC_ROSTER["baarle"][2], -5.5, -8.6, "walker_pos"),
        (NPC_ROSTER["baarle"][3], 6.5, -9.4, "walker_neg"),
    ]
    baarle_npcs = []
    for spec, nx, ny, role in npc_specs_pos:
        nid = spec["id"]
        p0 = os.path.join(npc_dir, nid, "pose_0.png")
        n_obj, _, _ = create_character_card(nid, spec["height"], p0, ambient_tint=(1.06, 0.99, 0.90), col=col_world)
        n_obj.location = Vector((nx, ny, 0.0))
        baarle_npcs.append((n_obj, nx, ny, role))

    # 2 Real 3D Wheeled European Cars driving smoothly along street Y = -7.6 & Y = -9.6 (kept clear of X=0 at 62..66s house zoom!)
    vehicles = [
        (build_3d_car("EuroCar_0", (-12.0, -7.8, 0.0), m_car_mint, m_car_glass, m_tire, m_chrome, m_head_glow, m_tail_glow, None, 1.0, col=col_world), -7.8, 2.8, 2.0),
        (build_3d_car("EuroCar_1", (14.0, -9.8, 0.0), m_car_mustard, m_car_glass, m_tire, m_chrome, m_head_glow, m_tail_glow, None, -1.0, col=col_world), -9.8, -2.5, 11.0),
    ]

    # ---------------- HERO PYTHON 2.5D CHARACTERS (Arka, Bram, Clara) ----------------
    char_cards: Dict[str, Any] = {}
    for cid in ("arka", "bram", "clara"):
        first_png = os.path.join(sprites_dir, cid, f"frame_{start_frame:04d}.png")
        obj, tex_node, tint_node = create_character_card(cid, CHAR_HEIGHTS_M[cid], first_png, ambient_tint=(1.06, 0.99, 0.89), col=col_world)
        char_cards[cid] = (obj, tex_node, tint_node)

    # ---------------- CAMERA ----------------
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.clip_start = 0.08
    cam_data.clip_end = 260.0
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    col_world.objects.link(cam_obj)
    scene.camera = cam_obj

    for f in range(max(1470, start_frame - 1), end_frame + 2):
        c_st = get_camera_at_frame("baarle", f)
        point_camera_at(cam_obj, c_st["pos"], c_st["target"], c_st["lens"], c_st["roll"])
        cam_obj.keyframe_insert(data_path="location", frame=f)
        cam_obj.keyframe_insert(data_path="rotation_quaternion", frame=f)
        cam_data.keyframe_insert(data_path="lens", frame=f)

    # ---------------- DYNAMIC FRAME UPDATE HANDLER ----------------
    def update_baarle_frame(scn: bpy.types.Scene) -> None:
        f = scn.frame_current
        t = f / 30.0
        dyn = get_scene_dynamic_state("baarle", f)
        chars = get_characters_at_frame("baarle", f)
        cam_pos = get_camera_at_frame("baarle", f)["pos"]

        for cid, (obj, tex_node, _) in char_cards.items():
            st = chars[cid]
            obj.location = Vector(st["pos"])
            obj.rotation_euler = (0.0, 0.0, st["rot_z"])
            obj.hide_render = not st["visible"]
            png_path = os.path.join(sprites_dir, cid, f"frame_{f:04d}.png")
            if os.path.exists(png_path):
                tex_node.image = bpy.data.images.load(png_path, check_existing=True)

        # Unified 2.5D bean-head NPCs (strictly kept out of central camera aisle & house-zoom view!)
        for idx, (n_obj, nx, ny, role) in enumerate(baarle_npcs):
            if role == "patron":
                n_obj.location = Vector((nx, ny, abs(math.sin(t * 2.2 + idx)) * 0.02))
                n_obj.rotation_euler = (0.0, 0.0, compute_billboard_rot_z((nx, ny, 0.0), cam_pos))
            else:
                dir_s = 1.0 if role == "walker_pos" else -1.0
                px = ((t * 1.2 * dir_s + nx + 14.0) % 28.0) - 14.0
                # Gently keep far-street pedestrians outside central dual-house sightline X[-2.5..2.5] during 62..67s
                if 61.5 <= t <= 67.0 and abs(px) < 3.2:
                    px = -4.2 if px < 0 else 4.2
                n_obj.location = Vector((px, ny, abs(math.sin(t * 6.0 + idx)) * 0.04))
                n_obj.rotation_euler = (0.0, 0.0, compute_billboard_rot_z((px, ny, 0.0), cam_pos))

        latte_root.hide_render = not dyn["latte_visible"]
        latte_root.location = Vector(dyn["latte_pos"])
        arka_cup.hide_render = not dyn["arka_finale_cup_visible"]
        arka_cup.location = Vector(dyn["arka_finale_cup_pos"])

        flag_be_root.rotation_euler = (0.0, 0.0, math.sin(t * 5.2) * 0.14)
        flag_nl_root.rotation_euler = (0.0, 0.0, math.cos(t * 5.0) * 0.14)

        for sp, sx, sy, sz, ph in steam_wisps:
            cyc = (t * 0.85 + ph) % 1.8
            sp.location = Vector((sx + math.sin(cyc * 3.0) * 0.04, sy, sz + cyc * 0.45))
            sc = 0.65 + cyc * 0.45
            sp.scale = (sc, sc, sc)

        for v_root, vy, spd, ph in vehicles:
            vx = ((t * spd + ph + 18.0) % 36.0) - 18.0
            # Ensure cars don't photobomb dual-flag door close-up at 62..67s
            if 61.5 <= t <= 67.0 and abs(vx) < 4.5:
                vx = -6.5 if vx < 0 else 6.5
            v_root.location = Vector((vx, vy, 0.0))

        # Crisp short match-cut exit (only first 6 frames 49.0..49.20) & sharp outro glitch (74.68..75.0)
        enter_flash = max(0.0, 1.0 - (t - 49.0) / 0.20) if t < 49.22 else 0.0
        outro_glitch = dyn["glitch_outro"]
        set_transition_flash(scn, max(enter_flash * 0.65, outro_glitch * 0.65), (1.0, 0.96, 0.88) if enter_flash > outro_glitch else (0.55, 0.92, 1.0))

    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(update_baarle_frame)
    scene.frame_start = start_frame
    scene.frame_end = end_frame - 1
    scene.frame_set(start_frame)
    update_baarle_frame(scene)
    return scene
