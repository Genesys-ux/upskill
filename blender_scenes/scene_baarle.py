"""World 3: Baarle-Nassau / Baarle-Hertog White Cross Border, Café de Grens & Golden Afternoon Street."""
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


def build_and_bind_baarle(
    sprites_dir: str,
    start_frame: int,
    end_frame: int,
    width: int = 720,
    height: int = 1280,
    samples: int = 22,
) -> bpy.types.Scene:
    clear_scene()
    scene = configure_render_eevee(width=width, height=height, fps=30, samples=samples, use_motion_blur=True)

    # Golden Afternoon European Low Sun Sky + Warm Atmospheric Haze (total warm contrast from Diomede & Rjukan!)
    setup_world_sky(
        zenith_color=(0.24, 0.46, 0.78),
        horizon_color=(1.00, 0.72, 0.42),
        strength=0.95,
        haze_density=0.0028,
        haze_color=(1.0, 0.86, 0.66),
    )

    # ---------------- MATERIALS ----------------
    m_clinker = make_cel_pbr_material("BaarleClinkerPave", (0.50, 0.34, 0.26), (0.28, 0.24, 0.36), roughness=0.62, bump_scale=20.0, bump_strength=0.22, pattern="brick", color_b=(0.40, 0.27, 0.21))
    m_brick_red = make_cel_pbr_material("DutchRedBrick", (0.56, 0.24, 0.18), (0.28, 0.20, 0.32), roughness=0.72, bump_scale=16.0, bump_strength=0.28, pattern="brick", color_b=(0.44, 0.18, 0.14))
    m_brick_warm = make_cel_pbr_material("BelgianOchreBrick", (0.68, 0.48, 0.32), (0.32, 0.26, 0.36), roughness=0.72, bump_scale=16.0, bump_strength=0.25, pattern="brick")
    m_oak_gloss = make_cel_pbr_material("VarnishedOakBar", (0.44, 0.26, 0.14), (0.22, 0.16, 0.24), roughness=0.24, bump_scale=14.0, bump_strength=0.14, pattern="wood")
    m_cafe_floor = make_cel_pbr_material("CafeWarmTile", (0.72, 0.62, 0.48), (0.36, 0.32, 0.42), roughness=0.35, bump_scale=18.0, pattern="cobble")
    m_cafe_wall = make_cel_pbr_material("CafePlasterCream", (0.90, 0.84, 0.72), (0.46, 0.42, 0.52), roughness=0.68)
    m_green_frame = make_cel_pbr_material("CafeForestGreen", (0.10, 0.28, 0.20), (0.06, 0.16, 0.18), roughness=0.38)
    m_brass = make_cel_pbr_material("InlaidBrass", (0.88, 0.68, 0.24), (0.42, 0.32, 0.18), roughness=0.18, metallic=0.92)
    m_chrome = make_cel_pbr_material("EspressoChrome", (0.85, 0.88, 0.92), (0.38, 0.44, 0.56), roughness=0.12, metallic=0.94)
    m_white_cross = make_cel_pbr_material("BorderWhiteStone", (0.95, 0.94, 0.90), (0.56, 0.54, 0.62), roughness=0.42)
    m_rattan = make_cel_pbr_material("RattanChair", (0.68, 0.50, 0.28), (0.34, 0.26, 0.30), roughness=0.65, pattern="wood")
    m_ceramic_w = make_cel_pbr_material("LatteCeramic", (0.96, 0.95, 0.92), (0.58, 0.56, 0.62), roughness=0.16)
    m_coffee = make_cel_pbr_material("LatteFoam", (0.62, 0.40, 0.24), (0.30, 0.20, 0.16), roughness=0.35)
    m_pastry = make_cel_pbr_material("CroissantGold", (0.84, 0.56, 0.22), (0.44, 0.28, 0.18), roughness=0.45)
    m_geranium = make_cel_pbr_material("GeraniumRed", (0.86, 0.14, 0.16), (0.40, 0.12, 0.18), roughness=0.55)
    m_leaf = make_cel_pbr_material("LeafGreen", (0.16, 0.44, 0.18), (0.08, 0.24, 0.18), roughness=0.6)
    m_dark_iron = make_cel_pbr_material("BikeIron", (0.14, 0.15, 0.18), (0.08, 0.10, 0.16), roughness=0.38, metallic=0.75)
    m_car_mint = make_cel_pbr_material("EuroCarMint", (0.28, 0.62, 0.56), (0.14, 0.32, 0.38), roughness=0.22, metallic=0.45)
    m_car_mustard = make_cel_pbr_material("EuroCarMustard", (0.84, 0.64, 0.18), (0.38, 0.28, 0.22), roughness=0.22, metallic=0.45)
    m_npc_skin = make_cel_pbr_material("NpcSkinB", (0.90, 0.76, 0.66), (0.46, 0.38, 0.44), roughness=0.58)
    m_flag_r = make_cel_pbr_material("FlagRed", (0.82, 0.14, 0.16), (0.40, 0.12, 0.16), roughness=0.6)
    m_flag_b = make_cel_pbr_material("FlagBlue", (0.12, 0.26, 0.62), (0.08, 0.14, 0.36), roughness=0.6)
    m_flag_y = make_cel_pbr_material("FlagYellow", (0.95, 0.78, 0.12), (0.48, 0.36, 0.12), roughness=0.6)

    m_edison = make_emissive_material("EdisonWarmBulb", (1.0, 0.78, 0.36), strength=9.0)
    m_dust_mote = make_emissive_material("GoldenDustMote", (1.0, 0.90, 0.60), strength=2.6, alpha=0.7)
    m_steam = make_emissive_material("EspressoSteam", (0.98, 0.96, 0.92), strength=1.1, alpha=0.42)
    m_glass = make_emissive_material("CafeGlassPane", (0.82, 0.92, 0.98), strength=0.4, alpha=0.18)

    m_border_tile = make_decal_material("BaarleCrossTileMat", os.path.join(DECALS_DIR, "baarle_border_cross_tile.png"), roughness=0.48)
    m_menu_decal = make_decal_material("BaarleMenuMat", os.path.join(DECALS_DIR, "baarle_cafe_menu.png"), roughness=0.62)
    m_plaque_b = make_decal_material("PlaqueBelgiumMat", os.path.join(DECALS_DIR, "plaque_belgium_2.png"), roughness=0.35)
    m_plaque_nl = make_decal_material("PlaqueNLMat", os.path.join(DECALS_DIR, "plaque_netherlands_19.png"), roughness=0.35)

    # ---------------- GOLDEN AFTERNOON LOW-SUN LIGHTING ----------------
    bpy.ops.object.light_add(type="SUN", location=(-24.0, -18.0, 10.0), rotation=(math.radians(74), math.radians(-18), math.radians(-42)))
    sun = bpy.context.active_object
    sun.name = "GoldenAfternoonLowSun"
    sun.data.energy = 6.2
    sun.data.color = (1.0, 0.78, 0.48)
    sun.data.angle = math.radians(1.8)

    # Warm Edison pendant lights inside Café de Grens
    for ex in (-1.8, 0.0, 1.8):
        bpy.ops.object.light_add(type="POINT", location=(ex, 4.4, 2.75))
        el = bpy.context.active_object
        el.data.energy = 190.0
        el.data.color = (1.0, 0.74, 0.36)
        add_cylinder(f"EdisonCord_{ex}", (ex, 4.4, 3.35), 0.015, 1.0, m_dark_iron, verts=6)
        add_sphere(f"EdisonBulb_{ex}", (ex, 4.4, 2.82), 0.11, m_edison, segments=12)

    # Soft sky fill inside cafe so characters look vibrant & cozy
    bpy.ops.object.light_add(type="AREA", location=(0.0, 1.5, 2.6), rotation=(math.radians(55), 0, 0))
    c_fill = bpy.context.active_object
    c_fill.data.energy = 420.0
    c_fill.data.color = (1.0, 0.90, 0.76)
    c_fill.data.size = 5.5

    # ---------------- SIDEWALK, STREET & ICONIC WHITE CROSS (+) B|NL BORDER ----------------
    # Street & Sidewalk outside café (Y < 0)
    add_box("BaarleStreetClinker", (0.0, -7.5, -0.25), (42.0, 16.0, 0.5), m_clinker)
    # Café interior floor (Y in [0, 9])
    add_box("CafeFloorBase", (0.0, 4.5, -0.24), (10.6, 9.2, 0.48), m_cafe_floor)

    # ICONIC B | NL WHITE CROSS BORDER TILES marching straight down X = 0.0 from street -> sidewalk -> café floor!
    for ti in range(-10, 6):
        ty = ti * 1.05
        add_decal_plane(f"BorderCrossTile_{ti}", (0.0, ty, 0.012), 1.02, 1.02, (0, 0, 0), m_border_tile)

    # ---------------- CAFÉ DE GRENS (CORNER EUROPEAN CAFÉ, Y in [0, 9]) ----------------
    # Back wall, left/right walls, warm ceiling (open front glass facade at Y = 0!)
    add_box("CafeBackWall", (0.0, 8.6, 2.1), (10.6, 0.35, 4.2), m_cafe_wall)
    add_box("CafeLeftWall", (-5.2, 4.3, 2.1), (0.35, 8.8, 4.2), m_brick_red)
    add_box("CafeRightWall", (5.2, 4.3, 2.1), (0.35, 8.8, 4.2), m_brick_red)
    add_box("CafeCeiling", (0.0, 4.3, 4.05), (10.8, 9.0, 0.25), m_oak_gloss)
    # Upper exterior European brick facade above café storefront
    add_box("CafeUpperFacade", (0.0, 0.0, 5.8), (11.2, 0.45, 3.6), m_brick_red)
    # Dark-green classic wooden storefront pillars framing WIDE OPEN double-doors (X in [-1.9, +1.9]) & large windows!
    for fx in (-4.8, -2.0, 2.0, 4.8):
        add_box(f"FrontPillar_{fx}", (fx, 0.0, 2.0), (0.28, 0.32, 4.0), m_green_frame)
    add_box("FrontHeaderBeam", (0.0, 0.0, 3.75), (10.2, 0.36, 0.48), m_green_frame)
    # Side glass window panels with low brick sill + potted red geranium boxes!
    for wx in (-3.4, 3.4):
        add_box(f"WindowSill_{wx}", (wx, 0.0, 0.45), (2.55, 0.34, 0.90), m_green_frame)
        add_box(f"WindowGlass_{wx}", (wx, 0.0, 2.25), (2.5, 0.04, 2.65), m_glass)
        # Potted red geranium flowers outside windows
        add_box(f"FlowerBox_{wx}", (wx, -0.35, 0.96), (1.8, 0.32, 0.24), m_oak_gloss)
        for gi in range(5):
            add_sphere(f"Leaf_{wx}_{gi}", (wx - 0.7 + gi * 0.35, -0.35, 1.14), 0.14, m_leaf, segments=8)
            add_sphere(f"Flower_{wx}_{gi}", (wx - 0.7 + gi * 0.35, -0.35, 1.24), 0.09, m_geranium, segments=8)
    # Striped green-cream café awning + fluttering Dutch & Belgian mini flags at corners!
    add_box("CafeAwning", (0.0, -0.95, 3.62), (9.8, 1.85, 0.14), m_green_frame, rot=(math.radians(-18), 0, 0))
    # Mini Belgian flag on LEFT (B) corner of awning & Dutch flag on RIGHT (NL) corner!
    flag_be_root = bpy.data.objects.new("MiniFlagBelgium", None)
    flag_be_root.location = (-4.6, -1.75, 3.55)
    bpy.context.collection.objects.link(flag_be_root)
    add_box("FlagBE_Blk", (-0.18, 0, 0), (0.18, 0.03, 0.36), m_dark_iron).parent = flag_be_root
    add_box("FlagBE_Yel", (0.0, 0, 0), (0.18, 0.03, 0.36), m_flag_y).parent = flag_be_root
    add_box("FlagBE_Red", (0.18, 0, 0), (0.18, 0.03, 0.36), m_flag_r).parent = flag_be_root

    flag_nl_root = bpy.data.objects.new("MiniFlagNetherlands", None)
    flag_nl_root.location = (4.6, -1.75, 3.55)
    bpy.context.collection.objects.link(flag_nl_root)
    add_box("FlagNL_Red", (0, 0, 0.12), (0.54, 0.03, 0.12), m_flag_r).parent = flag_nl_root
    add_box("FlagNL_Wht", (0, 0, 0.0), (0.54, 0.03, 0.12), m_white_cross).parent = flag_nl_root
    add_box("FlagNL_Blu", (0, 0, -0.12), (0.54, 0.03, 0.12), m_flag_b).parent = flag_nl_root

    # ---------------- HERO OAK BAR COUNTER SPLIT BY BRASS BORDER STRIP (Y = 5.2m) ----------------
    add_box("OakBarBody", (0.0, 5.25, 0.50), (5.8, 0.88, 1.00), m_oak_gloss)
    add_box("OakBarTop", (0.0, 5.20, 1.03), (6.0, 1.04, 0.07), m_oak_gloss)
    # Gleaming INLAID BRASS BORDER STRIP running straight down X = 0.0 across bar front & bar top!
    add_box("BrassBarBorderTop", (0.0, 5.20, 1.068), (0.06, 1.06, 0.014), m_brass)
    add_box("BrassBarBorderFront", (0.0, 4.78, 0.52), (0.06, 0.02, 1.02), m_brass)

    # Classic Chrome Espresso Machine on NL side (+X) + Animated Steam Puffs
    add_box("EspressoBase", (1.85, 5.32, 1.34), (0.82, 0.54, 0.54), m_chrome)
    add_cylinder("EspressoGroupHead", (1.65, 5.05, 1.38), 0.09, 0.18, m_brass, verts=12)
    steam_puffs = []
    for spi in range(4):
        sp = add_sphere(f"EspressoSteam_{spi}", (1.65, 5.05, 1.6 + spi * 0.2), 0.09, m_steam, segments=8)
        steam_puffs.append((sp, 1.65, 5.05, 1.55, spi * 0.65))

    # Glass Pastry Display Case with Croissants & Stroopwafels on Belgium side (-X)
    add_box("PastryCaseGlass", (-1.85, 5.25, 1.32), (1.15, 0.62, 0.52), m_glass)
    for pi in range(4):
        add_sphere(f"Croissant_{pi}", (-2.18 + pi * 0.22, 5.25, 1.15), 0.08, m_pastry, scale=(1.3, 0.8, 0.6), segments=10)
        add_cylinder(f"Stroopwafel_{pi}", (-2.15 + pi * 0.22, 5.38, 1.32), 0.07, 0.025, m_pastry, verts=12)

    # Chalkboard Menu on back wall (baarle_cafe_menu.png!)
    add_decal_plane("BaarleChalkboard", (-1.55, 8.38, 2.25), 1.45, 1.82, (math.radians(90), 0, 0), m_menu_decal)

    # HERO SLIDING LATTE CUP (slides 30cm across X=0 brass border from Bram NL -> Clara B!)
    latte_root = bpy.data.objects.new("HeroSlidingLatte", None)
    bpy.context.collection.objects.link(latte_root)
    add_cylinder("LatteSaucer", (0, 0, 0.012), 0.11, 0.02, m_ceramic_w, verts=16).parent = latte_root
    add_cylinder("LatteCup", (0, 0, 0.07), 0.075, 0.11, m_ceramic_w, verts=16).parent = latte_root
    add_cylinder("LatteFoamTop", (0, 0, 0.122), 0.068, 0.015, m_coffee, verts=16).parent = latte_root

    # Arka's Finale Coffee Cup (outside on street at 70..75s)
    arka_cup = add_cylinder("ArkaFinaleCup", (-0.28, -2.72, 1.18), 0.06, 0.12, m_ceramic_w, verts=12)

    # ---------------- CLARA'S BORDER BISTRO TABLE & RATTAN CHAIR (X = -0.55, Y = 3.85) ----------------
    # Chair firmly in Belgium (X = -0.55) with cross-rung clearly visible for Clara's feet-lift comedy gag!
    cx_c, cy_c = -0.55, 3.85
    add_cylinder("ClaraChairSeat", (cx_c, cy_c, 0.48), 0.28, 0.05, m_rattan, verts=14)
    add_box("ClaraChairBack", (cx_c - 0.12, cy_c + 0.22, 0.78), (0.48, 0.05, 0.55), m_rattan, rot=(0, 0, math.radians(-18)))
    for lx, ly in [(-0.20, -0.20), (0.20, -0.20), (-0.20, 0.20), (0.20, 0.20)]:
        add_cylinder(f"ClaraChairLeg_{lx}_{ly}", (cx_c + lx, cy_c + ly, 0.24), 0.024, 0.48, m_oak_gloss, verts=8)
    add_box("ClaraChairRung", (cx_c, cy_c - 0.18, 0.22), (0.44, 0.035, 0.035), m_oak_gloss)
    # Round Bistro Table right beside Clara
    add_cylinder("BistroTablePost", (-1.15, 3.60, 0.38), 0.05, 0.76, m_dark_iron, verts=10)
    add_cylinder("BistroTableTop", (-1.15, 3.60, 0.78), 0.46, 0.05, m_oak_gloss, verts=18)
    add_box("ClaraNotebook", (-1.02, 3.55, 0.82), (0.24, 0.18, 0.025), m_white_cross, rot=(0, 0, math.radians(15)))

    # Additional café bistro tables + animated chatting patrons!
    patron_coats = [m_flag_b, m_brick_red, m_green_frame, m_car_mustard, m_rattan]
    patrons = []
    for ti, (tx, ty) in enumerate([(-3.2, 2.6), (3.1, 2.8), (-3.3, 6.2), (3.4, 6.4)]):
        add_cylinder(f"TablePost_{ti}", (tx, ty, 0.38), 0.045, 0.76, m_dark_iron, verts=10)
        add_cylinder(f"TableTop_{ti}", (tx, ty, 0.78), 0.48, 0.045, m_oak_gloss, verts=16)
        p_npc = add_stylized_npc(f"CafePatron_{ti}", (tx + (0.65 if tx < 0 else -0.65), ty, 0.0), patron_coats[ti], m_npc_skin, m_oak_gloss, m_dark_iron, 0.90)
        patrons.append((p_npc, ti * 1.5))

    # ---------------- OPPOSITE STEPPED-GABLE DUTCH-BELGIAN HOUSE WITH DUAL FLAG PLAQUES (Y = -11.5m) ----------------
    add_box("DualDoorHouseBody", (0.0, -12.6, 3.2), (6.6, 2.4, 6.4), m_brick_red)
    # Iconic Dutch-Belgian STEPPED GABLE ROOFLINE (real architecture reference!)
    for step_i, (sw, sz) in enumerate([(5.6, 6.8), (4.2, 7.6), (2.8, 8.4), (1.4, 9.2)]):
        add_box(f"SteppedGable_{step_i}", (0.0, -11.55, sz), (sw, 0.38, 0.82), m_brick_red)
        add_box(f"SteppedCap_{step_i}", (0.0, -11.55, sz + 0.42), (sw + 0.14, 0.44, 0.08), m_white_cross)
    # Painted Front Door right on the border + BOTH Belgian (2) & Dutch (19) Flag House Plaques!
    add_box("DualHouseDoorFrame", (0.0, -11.38, 1.38), (1.42, 0.16, 2.72), m_white_cross)
    add_box("DualHouseDoorLeaf", (0.0, -11.34, 1.32), (1.16, 0.12, 2.54), m_green_frame)
    # Large crisp legible house plaques flanking the front door (facing +Y toward the café window!)
    add_decal_plane("PlaqueBelgium2", (-1.18, -11.32, 2.02), 0.82, 0.62, (math.radians(90), 0, math.radians(180)), m_plaque_b)
    add_decal_plane("PlaqueNetherlands19", (1.18, -11.32, 2.02), 0.82, 0.62, (math.radians(90), 0, math.radians(180)), m_plaque_nl)
    # Flanking European stepped-gable townhouses along the street
    for sx, hmat in [(-7.4, m_brick_warm), (7.4, m_brick_warm), (-14.2, m_brick_red), (14.2, m_brick_red)]:
        add_box(f"RowHouse_{sx}", (sx, -12.8, 3.0), (6.4, 2.6, 6.0), hmat)
        for si, (sw, sz) in enumerate([(5.0, 6.4), (3.4, 7.2), (1.8, 8.0)]):
            add_box(f"RowGable_{sx}_{si}", (sx, -11.6, sz), (sw, 0.35, 0.8), hmat)

    # Parked classic Dutch city bicycles in iron rack outside café
    for bi, bx in enumerate((-5.8, -6.5, 5.9)):
        add_cylinder(f"BikeWheelF_{bi}", (bx - 0.42, -1.8, 0.34), 0.34, 0.06, m_dark_iron, rot=(math.radians(90), 0, 0), verts=14)
        add_cylinder(f"BikeWheelR_{bi}", (bx + 0.42, -1.8, 0.34), 0.34, 0.06, m_dark_iron, rot=(math.radians(90), 0, 0), verts=14)
        add_box(f"BikeFrame_{bi}", (bx, -1.8, 0.56), (0.86, 0.06, 0.08), m_flag_b if bi % 2 == 0 else m_brick_red)
        add_box(f"BikeBasket_{bi}", (bx - 0.44, -1.8, 0.78), (0.28, 0.34, 0.24), m_rattan)

    # ---------------- LIVING BUSY ANIMATED STREET & GOLDEN DUST MOTES ----------------
    # 1) 4 Walking Sidewalk Pedestrians stepping across the B | NL street border
    peds = []
    for pi, (py, dir_s) in enumerate([(-4.4, 1.0), (-5.6, -1.0), (-8.8, 1.0), (-9.6, -1.0)]):
        ped = add_stylized_npc(f"BaarlePed_{pi}", (0.0, py, 0.0), patron_coats[pi % len(patron_coats)], m_npc_skin, m_oak_gloss, m_dark_iron, 0.94)
        peds.append((ped, py, dir_s, pi * 4.5))

    # 2) 2 Passing Vintage European Compact Cars + 2 Dutch Cyclists gliding down golden street!
    vehicles = []
    for vi, (vy, vmat, spd) in enumerate([(-6.8, m_car_mint, 3.6), (-8.2, m_car_mustard, -3.2)]):
        v_root = bpy.data.objects.new(f"EuroCar_{vi}", None)
        bpy.context.collection.objects.link(v_root)
        add_box(f"ECarBody_{vi}", (0, 0, 0.52), (3.2, 1.5, 0.78), vmat).parent = v_root
        add_box(f"ECarTop_{vi}", (-0.1, 0, 1.12), (1.7, 1.32, 0.58), m_white_cross).parent = v_root
        vehicles.append((v_root, vy, spd, vi * 8.0))

    # 3) 80 Golden Sunlit Dust Motes dancing lazily in the warm afternoon sunbeams!
    rng = random.Random(303)
    dust_motes = []
    for di in range(80):
        dx = rng.uniform(-4.5, 4.5)
        dy = rng.uniform(-5.5, 6.5)
        dz = rng.uniform(0.4, 3.4)
        m_obj = add_sphere(f"DustMote_{di}", (dx, dy, dz), rng.uniform(0.012, 0.026), m_dust_mote, segments=6)
        dust_motes.append((m_obj, dx, dy, dz, rng.uniform(0, 6.28)))

    # ---------------- PYTHON 2.5D CHARACTERS (Arka, Bram, Clara) ----------------
    char_cards: Dict[str, Any] = {}
    for cid in ("arka", "bram", "clara"):
        first_png = os.path.join(sprites_dir, cid, f"frame_{start_frame:04d}.png")
        obj, tex_node, tint_node = create_character_card(cid, CHAR_HEIGHTS_M[cid], first_png, ambient_tint=(1.08, 1.00, 0.88))
        char_cards[cid] = (obj, tex_node, tint_node)

    # ---------------- CAMERA ----------------
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.clip_start = 0.08
    cam_data.clip_end = 260.0
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
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

        for cid, (obj, tex_node, _) in char_cards.items():
            st = chars[cid]
            obj.location = Vector(st["pos"])
            obj.rotation_euler = (0.0, 0.0, st["rot_z"])
            obj.hide_render = not st["visible"]
            png_path = os.path.join(sprites_dir, cid, f"frame_{f:04d}.png")
            if os.path.exists(png_path):
                tex_node.image = bpy.data.images.load(png_path, check_existing=True)

        # Sliding latte cup across NL -> B brass border line!
        latte_root.location = Vector(dyn["latte_pos"])
        arka_cup.hide_render = not dyn["arka_finale_cup_visible"]
        arka_cup.location = Vector(dyn["arka_finale_cup_pos"])

        # Fluttering mini NL & BE flags
        flag_be_root.rotation_euler = (0.0, 0.0, math.sin(t * 5.2) * 0.14)
        flag_nl_root.rotation_euler = (0.0, 0.0, math.cos(t * 5.0) * 0.14)

        # Espresso steam plumes
        for sp, sx, sy, sz, ph in steam_puffs:
            cyc = (t * 0.9 + ph) % 2.0
            sp.location = Vector((sx + math.sin(cyc * 3.0) * 0.05, sy, sz + cyc * 0.55))
            sc = 0.6 + cyc * 0.55
            sp.scale = (sc, sc, sc)

        # Chatting café patrons
        for p_npc, ph in patrons:
            p_npc.rotation_euler.z = math.sin(t * 1.4 + ph) * 0.25
            p_npc.location.z = abs(math.sin(t * 2.2 + ph)) * 0.025

        # Walking street pedestrians (never cross directly in front of Arka at finale 70..75s!)
        for ped, py, dir_s, ph in peds:
            px = ((t * 1.4 * dir_s + ph) % 26.0) - 13.0
            ped.location = Vector((px, py, abs(math.sin(t * 6.5 + ph)) * 0.05))
            ped.rotation_euler.z = 0.0 if dir_s > 0 else math.pi

        for v_root, vy, spd, ph in vehicles:
            vx = ((t * spd + ph) % 34.0) - 17.0
            v_root.location = Vector((vx, vy, 0.0))

        for m_obj, dx, dy, dz, ph in dust_motes:
            m_obj.location = Vector((dx + math.sin(t * 0.8 + ph) * 0.22, dy + math.cos(t * 0.6 + ph) * 0.18, dz + math.sin(t * 0.9 + ph) * 0.15))

        # Match-cut fade-in at 49.0-49.35s & glitch flash at 74.55-75.0s!
        enter_flash = max(0.0, 1.0 - (t - 49.0) / 0.32) if t < 49.35 else 0.0
        outro_glitch = dyn["glitch_outro"]
        set_transition_flash(scn, max(enter_flash * 0.85, outro_glitch * 0.72), (0.98, 0.96, 0.92) if enter_flash > outro_glitch else (0.55, 0.92, 1.0))

    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(update_baarle_frame)
    scene.frame_start = start_frame
    scene.frame_end = end_frame - 1
    scene.frame_set(start_frame)
    update_baarle_frame(scene)
    return scene
