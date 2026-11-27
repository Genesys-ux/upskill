"""Dedicated Real-Reference Mid-Poly 3D Hero Prop & Architectural Asset Module (v3: Rich City Detail, Binoculars, Busy Set Dressing)."""
from __future__ import annotations

import math
import random
from typing import Optional, Tuple

import bmesh
import bpy

from blender_scenes.materials_lib import add_box, add_cylinder, add_decal_plane, add_sphere, link_to_collection


def _parent_all(parts: list[bpy.types.Object], root: bpy.types.Object, col: Optional[bpy.types.Collection]) -> bpy.types.Object:
    for p in parts:
        p.parent = root
        if col is not None:
            link_to_collection(p, col)
    if col is not None:
        link_to_collection(root, col)
    return root


# ============================================================================
# 1. ORGANIC JAGGED ROCKS, ALPINE CLIFFS & BERING SEA-ICE FLOES (BMESH)
# ============================================================================

def build_jagged_ice_floe(
    name: str,
    loc: Tuple[float, float, float],
    radius: float,
    thickness: float,
    mat: bpy.types.Material,
    seed: int = 1,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Authentic jagged polygonal Bering Strait sea-ice floe with fractured outer rim & snow ridge."""
    rng = random.Random(seed)
    bm = bmesh.new()
    n_verts = rng.randint(9, 14)
    bot_ring = []
    top_ring = []
    for i in range(n_verts):
        ang = (2.0 * math.pi * i) / n_verts + rng.uniform(-0.18, 0.18)
        r = radius * rng.uniform(0.60, 1.28)
        x = math.cos(ang) * r
        y = math.sin(ang) * r
        bot_ring.append(bm.verts.new((x * 1.07, y * 1.07, -thickness * 0.5)))
        top_ring.append(bm.verts.new((x * 0.95, y * 0.95, thickness * 0.5 + rng.uniform(-0.03, 0.06))))
    bm.faces.new(top_ring)
    bm.faces.new(list(reversed(bot_ring)))
    for i in range(n_verts):
        ni = (i + 1) % n_verts
        bm.faces.new((bot_ring[i], bot_ring[ni], top_ring[ni], top_ring[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.data.materials.append(mat)
    (col or bpy.context.collection).objects.link(obj)
    return obj


def build_jagged_mountain_ridge(
    name: str,
    loc: Tuple[float, float, float],
    width: float,
    depth: float,
    height: float,
    mat: bpy.types.Material,
    seed: int = 7,
    flat_top: bool = False,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """High-detail craggy multi-peak granite mountain ridge with natural stepped ledges for slope-based alpine snow."""
    rng = random.Random(seed)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=26, y_subdivisions=16, size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for v in bm.verts:
        nx = v.co.x * 2.0  # -1..1
        ny = v.co.y * 2.0  # -1..1
        edge_fade = max(0.0, 1.0 - max(abs(nx), abs(ny)) ** 2.6)
        # Multi-frequency alpine peaks & sharp rocky spurs!
        ridge = (
            math.sin(nx * 4.5 + seed * 0.7) * 0.18
            + math.cos(ny * 5.2 + seed * 1.1) * 0.14
            + math.sin((nx + ny) * 8.5 + seed) * 0.08
        )
        if flat_top:
            # Big Diomede volcanic mesa plateau with rugged coastal cliffs
            z_norm = min(1.0, edge_fade * 2.25) * (0.88 + 0.12 * math.sin(nx * 6.0 + seed) + rng.uniform(-0.06, 0.06))
        else:
            raw = (edge_fade ** 0.65) * (0.84 + ridge + rng.uniform(-0.11, 0.11))
            # Subtle geological terracing creates natural flat ledges where alpine snow catches light!
            z_norm = raw + math.sin(raw * 14.0) * 0.035
        v.co.x *= width
        v.co.y *= depth
        v.co.z = max(0.0, z_norm) * height
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.materials.append(mat)
    if col is not None:
        link_to_collection(obj, col)
    return obj


# ============================================================================
# 2. LITTLE DIOMEDE HERO PROPS (DETAILED BINOCULARS, IGNALUK VILLAGE, BOATHOUSE, SNOWMOBILE)
# ============================================================================

def build_detailed_brass_binoculars(
    name: str,
    mat_brass: bpy.types.Material,
    mat_leather: bpy.types.Material,
    mat_dark: bpy.types.Material,
    mat_lens: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Real-reference vintage maritime brass binoculars: tapered twin barrels, leather grip, focus wheel, eyecups & sapphire lenses."""
    root = bpy.data.objects.new(name, None)
    parts = []
    # Local orientation: front objective lenses face -Y (toward camera when Soren raises them!), ocular eyecups at +Y
    for sx in (-0.068, 0.068):
        # Rear ocular eyepiece + rubber eyecup
        parts.append(add_cylinder(f"{name}_eyecup_{sx}", (sx, 0.135, 0), 0.028, 0.032, mat_dark, rot=(math.radians(90), 0, 0), verts=16))
        parts.append(add_cylinder(f"{name}_ocular_{sx}", (sx, 0.095, 0), 0.032, 0.055, mat_brass, rot=(math.radians(90), 0, 0), verts=16))
        # Mid prism body wrapped in textured black marine leather + brass collars
        parts.append(add_cylinder(f"{name}_grip_{sx}", (sx, 0.015, 0), 0.044, 0.115, mat_leather, rot=(math.radians(90), 0, 0), verts=18))
        parts.append(add_cylinder(f"{name}_ringB_{sx}", (sx, 0.072, 0), 0.047, 0.014, mat_brass, rot=(math.radians(90), 0, 0), verts=18))
        parts.append(add_cylinder(f"{name}_ringF_{sx}", (sx, -0.045, 0), 0.050, 0.016, mat_brass, rot=(math.radians(90), 0, 0), verts=18))
        # Front flared brass objective housing + protective dark hood + gleaming coated glass lens!
        parts.append(add_cylinder(f"{name}_obj_{sx}", (sx, -0.095, 0), 0.054, 0.090, mat_brass, rot=(math.radians(90), 0, 0), verts=20))
        parts.append(add_cylinder(f"{name}_hood_{sx}", (sx, -0.142, 0), 0.057, 0.018, mat_dark, rot=(math.radians(90), 0, 0), verts=20))
        parts.append(add_cylinder(f"{name}_lens_{sx}", (sx, -0.144, 0), 0.046, 0.008, mat_lens, rot=(math.radians(90), 0, 0), verts=20))
    # Central articulated hinge axle, cross-bridges & grooved brass focus wheel!
    parts += [
        add_cylinder(f"{name}_axle", (0, 0.01, 0), 0.014, 0.18, mat_brass, rot=(math.radians(90), 0, 0), verts=12),
        add_box(f"{name}_bridgeF", (0, -0.045, 0), (0.14, 0.022, 0.026), mat_dark, bevel=0.004),
        add_box(f"{name}_bridgeB", (0, 0.070, 0), (0.13, 0.020, 0.022), mat_dark, bevel=0.004),
        add_cylinder(f"{name}_focusWheel", (0, 0.025, 0.012), 0.024, 0.036, mat_brass, rot=(math.radians(90), 0, 0), verts=14),
        add_cylinder(f"{name}_focusKnurl", (0, 0.025, 0.012), 0.026, 0.018, mat_dark, rot=(math.radians(90), 0, 0), verts=14),
    ]
    return _parent_all(parts, root, col)


def build_dock_bollard_and_rope(
    name: str,
    loc: Tuple[float, float, float],
    mat_iron: bpy.types.Material,
    mat_rope: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    root = bpy.data.objects.new(name, None)
    root.location = loc
    parts = [
        add_cylinder(f"{name}_base", (0, 0, 0.04), 0.21, 0.08, mat_iron, verts=12),
        add_cylinder(f"{name}_post", (0, 0, 0.26), 0.11, 0.42, mat_iron, verts=12),
        add_cylinder(f"{name}_cap", (0, 0, 0.48), 0.16, 0.08, mat_iron, verts=12),
        add_cylinder(f"{name}_horn", (0, 0, 0.36), 0.04, 0.38, mat_iron, rot=(0, math.radians(90), 0), verts=10),
    ]
    for ri in range(3):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.20 + ri * 0.04, minor_radius=0.025, location=(0.14, -0.06, 0.03 + ri * 0.026))
        r_obj = bpy.context.active_object
        r_obj.name = f"{name}_rope_{ri}"
        r_obj.data.materials.append(mat_rope)
        parts.append(r_obj)
    return _parent_all(parts, root, col)


def build_ignaluk_stilt_house(
    name: str,
    loc: Tuple[float, float, float],
    mat_wall: bpy.types.Material,
    mat_wood: bpy.types.Material,
    mat_trim: bpy.types.Material,
    mat_roof: bpy.types.Material,
    mat_win: bpy.types.Material,
    mat_snow: bpy.types.Material,
    mat_metal: bpy.types.Material,
    rot_z: float = 0.0,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Authentic Little Diomede (Ignaluk) wooden stilt cabin with cross-braced pilings, porch railings, stairs & dish."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (0, 0, rot_z)
    parts = []
    for sx in (-1.45, 1.45):
        for sy in (-1.15, 1.15):
            parts.append(add_cylinder(f"{name}_stilt_{sx}_{sy}", (sx, sy, -2.0), 0.11, 4.2, mat_wood, verts=8))
    parts.append(add_box(f"{name}_brace1", (0, 1.15, -1.5), (3.5, 0.09, 0.11), mat_wood, rot=(0, math.radians(28), 0)))
    parts.append(add_box(f"{name}_brace2", (0, 1.15, -1.5), (3.5, 0.09, 0.11), mat_wood, rot=(0, math.radians(-28), 0)))
    # Elevated timber platform deck + front porch rail
    parts.append(add_box(f"{name}_deck", (0, 0.35, 0.06), (4.0, 3.4, 0.16), mat_wood))
    parts.append(add_box(f"{name}_pRail", (0, 1.95, 0.96), (3.9, 0.08, 0.08), mat_wood))
    for rx in (-1.85, -0.65, 0.65, 1.85):
        parts.append(add_box(f"{name}_pPost_{rx}", (rx, 1.95, 0.52), (0.08, 0.08, 0.90), mat_wood))
    # Main cabin walls + gable roof + overhanging snow slab
    parts.append(add_box(f"{name}_body", (0, -0.05, 1.20), (3.5, 2.55, 2.20), mat_wall))
    parts.append(add_box(f"{name}_roofL", (-0.95, -0.05, 2.60), (2.25, 3.0, 0.14), mat_roof, rot=(0, math.radians(-22), 0)))
    parts.append(add_box(f"{name}_roofR", (0.95, -0.05, 2.60), (2.25, 3.0, 0.14), mat_roof, rot=(0, math.radians(22), 0)))
    parts.append(add_box(f"{name}_snowL", (-0.95, -0.05, 2.74), (2.15, 2.95, 0.16), mat_snow, rot=(0, math.radians(-22), 0), bevel=0.04))
    parts.append(add_box(f"{name}_snowR", (0.95, -0.05, 2.74), (2.15, 2.95, 0.16), mat_snow, rot=(0, math.radians(22), 0), bevel=0.04))
    # Glowing multi-pane windows + paneled door + stove pipe chimney + tiny satellite dish!
    for wx in (-0.98, 0.98):
        parts.append(add_box(f"{name}_wframe_{wx}", (wx, 1.25, 1.28), (0.78, 0.08, 0.86), mat_trim))
        parts.append(add_box(f"{name}_wglass_{wx}", (wx, 1.28, 1.28), (0.64, 0.04, 0.72), mat_win))
        parts.append(add_box(f"{name}_wmullV_{wx}", (wx, 1.30, 1.28), (0.04, 0.04, 0.74), mat_trim))
        parts.append(add_box(f"{name}_wmullH_{wx}", (wx, 1.30, 1.28), (0.66, 0.04, 0.04), mat_trim))
    parts.append(add_box(f"{name}_door", (0, 1.25, 0.96), (0.70, 0.08, 1.66), mat_wood))
    parts.append(add_cylinder(f"{name}_chimney", (0.98, -0.55, 3.15), 0.12, 1.25, mat_metal, verts=8))
    parts.append(add_cylinder(f"{name}_dish", (-1.35, 1.25, 2.15), 0.26, 0.06, mat_trim, rot=(math.radians(55), 0, math.radians(20)), verts=12))
    return _parent_all(parts, root, col)


def build_wooden_dory_boat(
    name: str,
    loc: Tuple[float, float, float],
    rot_z: float,
    mat_hull: bpy.types.Material,
    mat_trim: bpy.types.Material,
    mat_snow: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (0, 0, rot_z)
    parts = [
        add_box(f"{name}_hull_mid", (0, 0, 0.28), (2.4, 1.25, 0.56), mat_hull, bevel=0.12),
        add_box(f"{name}_bow", (1.45, 0, 0.24), (0.95, 0.82, 0.46), mat_hull, rot=(0, math.radians(14), 0), bevel=0.10),
        add_box(f"{name}_keel", (0.1, 0, 0.58), (3.1, 0.12, 0.12), mat_trim),
        add_box(f"{name}_gunwaleL", (0, 0.63, 0.06), (2.5, 0.09, 0.10), mat_trim),
        add_box(f"{name}_gunwaleR", (0, -0.63, 0.06), (2.5, 0.09, 0.10), mat_trim),
        add_box(f"{name}_snow", (0.05, 0, 0.62), (2.5, 0.95, 0.12), mat_snow, bevel=0.04),
    ]
    return _parent_all(parts, root, col)


def build_snowmobile(
    name: str,
    loc: Tuple[float, float, float],
    rot_z: float,
    mat_body: bpy.types.Material,
    mat_dark: bpy.types.Material,
    mat_glass: bpy.types.Material,
    mat_head: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Arctic utility snowmobile parked on Little Diomede dock."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (0, 0, rot_z)
    parts = [
        add_box(f"{name}_track", (-0.35, 0, 0.18), (1.35, 0.52, 0.28), mat_dark, bevel=0.04),
        add_box(f"{name}_chassis", (0.05, 0, 0.46), (1.75, 0.68, 0.36), mat_body, bevel=0.06),
        add_box(f"{name}_seat", (-0.42, 0, 0.72), (0.85, 0.48, 0.22), mat_dark, bevel=0.05),
        add_box(f"{name}_hood", (0.65, 0, 0.58), (0.72, 0.62, 0.32), mat_body, rot=(0, math.radians(16), 0), bevel=0.05),
        add_box(f"{name}_wind", (0.48, 0, 0.88), (0.08, 0.54, 0.36), mat_glass, rot=(0, math.radians(-26), 0)),
        add_cylinder(f"{name}_hbar", (0.28, 0, 0.86), 0.02, 0.72, mat_dark, rot=(math.radians(90), 0, 0), verts=8),
        add_box(f"{name}_hl", (1.00, 0, 0.56), (0.06, 0.26, 0.14), mat_head),
        add_box(f"{name}_skiL", (0.85, 0.36, 0.05), (0.95, 0.14, 0.05), mat_dark),
        add_box(f"{name}_skiR", (0.85, -0.36, 0.05), (0.95, 0.14, 0.05), mat_dark),
    ]
    return _parent_all(parts, root, col)


def build_navigation_buoy(
    name: str,
    loc: Tuple[float, float, float],
    mat_red: bpy.types.Material,
    mat_steel: bpy.types.Material,
    mat_glow: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Floating Arctic maritime harbor navigation buoy with lattice cage & flashing beacon."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    parts = [
        add_cylinder(f"{name}_float", (0, 0, 0.28), 0.65, 0.68, mat_red, verts=14),
        add_cylinder(f"{name}_collar", (0, 0, 0.66), 0.42, 0.14, mat_steel, verts=12),
        add_box(f"{name}_towerL", (-0.18, 0, 1.35), (0.07, 0.07, 1.35), mat_red, rot=(0, math.radians(8), 0)),
        add_box(f"{name}_towerR", (0.18, 0, 1.35), (0.07, 0.07, 1.35), mat_red, rot=(0, math.radians(-8), 0)),
        add_box(f"{name}_topPlat", (0, 0, 2.02), (0.36, 0.36, 0.08), mat_steel),
        add_sphere(f"{name}_light", (0, 0, 2.22), 0.14, mat_glow, segments=10),
    ]
    return _parent_all(parts, root, col)


# ============================================================================
# 3. RJUKAN REAL-REFERENCE ASSETS (SPOTLESS SOLSPEILET, RICH NORWEGIAN TOWN, BENCHES, KIOSK, CARS)
# ============================================================================

def build_solspeilet_heliostat(
    name: str,
    loc: Tuple[float, float, float],
    mat_steel: bpy.types.Material,
    mat_mirror: bpy.types.Material,
    mat_accent: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> Tuple[bpy.types.Object, bpy.types.Object]:
    """Authentic 2013 Rjukan Solspeilet heliostat: A-frame truss + rear-mounted pistons (ZERO poking through glass!)."""
    base = bpy.data.objects.new(f"{name}_Base", None)
    base.location = loc
    base_parts = [
        add_box(f"{name}_footL", (-1.15, 0.25, -2.1), (0.55, 0.90, 0.24), mat_steel),
        add_box(f"{name}_footR", (1.15, 0.25, -2.1), (0.55, 0.90, 0.24), mat_steel),
        add_cylinder(f"{name}_legFL", (-1.10, 0.08, -1.0), 0.09, 2.35, mat_steel, rot=(math.radians(6), 0, 0), verts=8),
        add_cylinder(f"{name}_legFR", (1.10, 0.08, -1.0), 0.09, 2.35, mat_steel, rot=(math.radians(6), 0, 0), verts=8),
        add_cylinder(f"{name}_legBL", (-1.10, 0.68, -1.0), 0.09, 2.45, mat_steel, rot=(math.radians(-16), 0, 0), verts=8),
        add_cylinder(f"{name}_legBR", (1.10, 0.68, -1.0), 0.09, 2.45, mat_steel, rot=(math.radians(-16), 0, 0), verts=8),
        add_box(f"{name}_crossBar", (0, 0.38, -0.95), (2.35, 0.14, 0.14), mat_steel),
        add_cylinder(f"{name}_gearbox", (0, 0.28, 0.0), 0.24, 2.4, mat_steel, rot=(0, math.radians(90), 0), verts=12),
        # Hydraulic actuator pistons strictly BEHIND mirror (y >= +0.55, angled away from glass!)
        add_cylinder(f"{name}_hydL", (-0.75, 0.62, -0.85), 0.075, 1.9, mat_accent, rot=(math.radians(-18), 0, 0), verts=10),
        add_cylinder(f"{name}_hydR", (0.75, 0.62, -0.85), 0.075, 1.9, mat_accent, rot=(math.radians(-18), 0, 0), verts=10),
    ]
    _parent_all(base_parts, base, col)

    piv = bpy.data.objects.new(f"{name}_Pivot", None)
    piv.location = (loc[0], loc[1] - 0.12, loc[2])
    piv_parts = [
        add_box(f"{name}_frameBack", (0, 0.10, 0), (3.55, 0.14, 4.55), mat_steel, bevel=0.03),
        add_box(f"{name}_glassMain", (0, -0.02, 0), (3.30, 0.04, 4.30), mat_mirror),
    ]
    for gx in (-0.55, 0.55):
        piv_parts.append(add_box(f"{name}_divV_{gx}", (gx, -0.05, 0), (0.045, 0.04, 4.32), mat_steel))
    for gz in (-1.08, 0.0, 1.08):
        piv_parts.append(add_box(f"{name}_divH_{gz}", (0, -0.05, gz), (3.32, 0.04, 0.045), mat_steel))
    _parent_all(piv_parts, piv, col)
    return base, piv


def build_norwegian_rjukan_house(
    name: str,
    loc: Tuple[float, float, float],
    size: Tuple[float, float, float],
    mat_wall: bpy.types.Material,
    mat_trim: bpy.types.Material,
    mat_roof: bpy.types.Material,
    mat_win: bpy.types.Material,
    mat_snow: bpy.types.Material,
    mat_ice: bpy.types.Material,
    mat_door: bpy.types.Material,
    mat_awning: Optional[bpy.types.Material] = None,
    facing: str = "+X",  # "+X", "-X", "+Y", or "-Y"
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Rich early-1900s Rjukan Torg Norwegian building: shopfront awning, balcony, pediments, dormer, snow eaves & icicles!"""
    w, d, h = size
    root = bpy.data.objects.new(name, None)
    root.location = loc
    rot_map = {"+Y": 0.0, "-Y": math.pi, "-X": math.radians(90), "+X": math.radians(-90)}
    root.rotation_euler = (0, 0, rot_map.get(facing, 0.0))
    awn_m = mat_awning or mat_door
    fy = d * 0.5 + 0.03

    parts = [
        # Textured granite plinth + main horizontal clapboard facade + white corner boards + mid-story cornice molding
        add_box(f"{name}_plinth", (0, 0, 0.38), (w + 0.16, d + 0.16, 0.76), mat_roof),
        add_box(f"{name}_body", (0, 0, h * 0.5 + 0.34), (w, d, h), mat_wall),
        add_box(f"{name}_corniceMid", (0, fy + 0.06, 3.18), (w + 0.24, 0.20, 0.16), mat_trim),
        add_box(f"{name}_corniceTop", (0, fy + 0.08, h + 0.28), (w + 0.34, 0.28, 0.20), mat_trim),
        add_box(f"{name}_cornerFL", (-w * 0.5, d * 0.5, h * 0.5 + 0.34), (0.20, 0.20, h), mat_trim),
        add_box(f"{name}_cornerFR", (w * 0.5, d * 0.5, h * 0.5 + 0.34), (0.20, 0.20, h), mat_trim),
        # Pitched slate gable roof + thick sculpted snow overhang + brick chimney + roof dormer!
        add_box(f"{name}_roofF", (0, d * 0.28, h + 1.00), (w + 0.72, d * 0.68, 0.18), mat_roof, rot=(math.radians(28), 0, 0)),
        add_box(f"{name}_roofB", (0, -d * 0.28, h + 1.00), (w + 0.72, d * 0.68, 0.18), mat_roof, rot=(math.radians(-28), 0, 0)),
        add_box(f"{name}_snowF", (0, d * 0.28, h + 1.18), (w + 0.62, d * 0.65, 0.24), mat_snow, rot=(math.radians(28), 0, 0), bevel=0.05),
        add_box(f"{name}_snowB", (0, -d * 0.28, h + 1.18), (w + 0.62, d * 0.65, 0.24), mat_snow, rot=(math.radians(-28), 0, 0), bevel=0.05),
        add_box(f"{name}_chim", (w * 0.28, -d * 0.12, h + 2.05), (0.68, 0.68, 1.65), mat_door),
        add_box(f"{name}_chimSnow", (w * 0.28, -d * 0.12, h + 2.92), (0.76, 0.76, 0.14), mat_snow),
        # Charming attic dormer window on front roof slope!
        add_box(f"{name}_dormBody", (0, d * 0.26, h + 1.48), (1.35, 1.10, 1.05), mat_trim),
        add_box(f"{name}_dormWin", (0, d * 0.26 + 0.56, h + 1.48), (0.82, 0.06, 0.72), mat_win),
        add_box(f"{name}_dormRoof", (0, d * 0.26, h + 2.08), (1.56, 1.32, 0.18), mat_snow, bevel=0.04),
    ]
    # Hanging crystalline icicles along front snow eaves!
    eave_y = d * 0.5 + 0.28
    eave_z = h + 0.36
    for ix in range(-3, 4):
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.048, depth=0.36 + (abs(ix) % 2) * 0.16, location=(ix * (w * 0.14), eave_y, eave_z), rotation=(math.radians(180), 0, 0))
        ic = bpy.context.active_object
        ic.name = f"{name}_icicle_{ix}"
        ic.data.materials.append(mat_ice)
        parts.append(ic)

    # Ground-floor shopfront door + warm glowing fascia sign + angled fabric shop awning + balcony above!
    parts += [
        add_box(f"{name}_doorFrame", (0, fy, 1.40), (1.42, 0.14, 2.30), mat_trim),
        add_box(f"{name}_doorLeaf", (0, fy + 0.04, 1.34), (1.16, 0.08, 2.12), mat_door),
        add_box(f"{name}_shopAwning", (0, fy + 0.52, 2.66), (w * 0.86, 1.02, 0.12), awn_m, rot=(math.radians(20), 0, 0)),
        add_box(f"{name}_shopAwningSnow", (0, fy + 0.52, 2.75), (w * 0.84, 0.96, 0.10), mat_snow, rot=(math.radians(20), 0, 0), bevel=0.03),
        # 2nd-floor timber balcony with white railing
        add_box(f"{name}_balcDeck", (0, fy + 0.42, 3.32), (2.25, 0.84, 0.14), mat_door),
        add_box(f"{name}_balcRail", (0, fy + 0.80, 4.02), (2.25, 0.08, 0.08), mat_trim),
    ]
    for bx in (-1.05, -0.35, 0.35, 1.05):
        parts.append(add_box(f"{name}_balcPost_{bx}", (bx, fy + 0.80, 3.68), (0.07, 0.07, 0.68), mat_trim))

    # Crisp white-framed multi-pane windows with decorative Norwegian header pediments & snowy sills!
    for floor_z in (1.75, 4.65):
        if floor_z + 0.8 > h:
            continue
        xs = [-w * 0.31, w * 0.31] if floor_z < 3.0 else [-w * 0.31, 0.0, w * 0.31]
        for wx in xs:
            ww = 1.32 if floor_z < 3.0 else 1.12
            wh = 1.45 if floor_z < 3.0 else 1.34
            parts += [
                add_box(f"{name}_wf_{floor_z}_{wx}", (wx, fy, floor_z), (ww, 0.12, wh), mat_trim),
                add_box(f"{name}_wg_{floor_z}_{wx}", (wx, fy + 0.04, floor_z), (ww - 0.18, 0.05, wh - 0.18), mat_win),
                add_box(f"{name}_mv_{floor_z}_{wx}", (wx, fy + 0.07, floor_z), (0.05, 0.04, wh - 0.16), mat_trim),
                add_box(f"{name}_mh_{floor_z}_{wx}", (wx, fy + 0.07, floor_z), (ww - 0.16, 0.04, 0.05), mat_trim),
                add_box(f"{name}_wped_{floor_z}_{wx}", (wx, fy + 0.08, floor_z + wh * 0.5 + 0.08), (ww + 0.18, 0.18, 0.14), mat_trim),
                add_box(f"{name}_wsill_{floor_z}_{wx}", (wx, fy + 0.10, floor_z - wh * 0.5 - 0.04), (ww + 0.14, 0.24, 0.10), mat_snow),
            ]
    return _parent_all(parts, root, col)


def build_plaza_bench_with_legs(
    name: str,
    loc: Tuple[float, float, float],
    rot_z: float,
    mat_wood: bpy.types.Material,
    mat_iron: bpy.types.Material,
    mat_snow: Optional[bpy.types.Material] = None,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Real European park/plaza wooden bench with solid cast-iron legs, armrests & slatted backrest (NEVER floats!)."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (0, 0, rot_z)
    parts = [
        # Cast-iron side leg frames grounded at Z=0.0!
        add_box(f"{name}_legFL", (-0.78, -0.20, 0.24), (0.08, 0.08, 0.48), mat_iron),
        add_box(f"{name}_legFR", (0.78, -0.20, 0.24), (0.08, 0.08, 0.48), mat_iron),
        add_box(f"{name}_legBL", (-0.78, 0.20, 0.46), (0.08, 0.08, 0.92), mat_iron),
        add_box(f"{name}_legBR", (0.78, 0.20, 0.46), (0.08, 0.08, 0.92), mat_iron),
        add_box(f"{name}_armL", (-0.80, 0.0, 0.64), (0.07, 0.46, 0.06), mat_iron),
        add_box(f"{name}_armR", (0.80, 0.0, 0.64), (0.07, 0.46, 0.06), mat_iron),
        # Slatted timber seat & backrest
        add_box(f"{name}_seat1", (0, -0.10, 0.46), (1.76, 0.22, 0.06), mat_wood, bevel=0.01),
        add_box(f"{name}_seat2", (0, 0.14, 0.46), (1.76, 0.20, 0.06), mat_wood, bevel=0.01),
        add_box(f"{name}_back1", (0, 0.23, 0.72), (1.76, 0.06, 0.16), mat_wood, bevel=0.01),
        add_box(f"{name}_back2", (0, 0.24, 0.90), (1.76, 0.06, 0.16), mat_wood, bevel=0.01),
    ]
    if mat_snow is not None:
        parts.append(add_box(f"{name}_snowSeat", (0, 0.0, 0.51), (1.68, 0.36, 0.06), mat_snow, bevel=0.02))
        parts.append(add_box(f"{name}_snowTop", (0, 0.24, 1.00), (1.72, 0.10, 0.06), mat_snow, bevel=0.02))
    return _parent_all(parts, root, col)


def build_nordic_waffle_kiosk(
    name: str,
    loc: Tuple[float, float, float],
    rot_z: float,
    mat_red: bpy.types.Material,
    mat_trim: bpy.types.Material,
    mat_wood: bpy.types.Material,
    mat_snow: bpy.types.Material,
    mat_glow: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Cozy glowing Rjukan Torg wooden winter coffee & waffle kiosk with pitched snow roof & counter."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (0, 0, rot_z)
    parts = [
        add_box(f"{name}_base", (0, 0, 0.52), (2.2, 1.45, 1.04), mat_red, bevel=0.02),
        add_box(f"{name}_counter", (0, -0.76, 1.06), (2.35, 0.42, 0.08), mat_wood, bevel=0.015),
        add_box(f"{name}_back", (0, 0.58, 1.72), (2.2, 0.28, 1.40), mat_red),
        add_box(f"{name}_postL", (-1.04, -0.66, 1.72), (0.12, 0.12, 1.40), mat_trim),
        add_box(f"{name}_postR", (1.04, -0.66, 1.72), (0.12, 0.12, 1.40), mat_trim),
        add_box(f"{name}_innerGlow", (0, 0.36, 1.65), (1.92, 0.12, 1.05), mat_glow),
        add_box(f"{name}_roofL", (-0.72, 0, 2.75), (1.65, 1.85, 0.14), mat_wood, rot=(0, math.radians(-22), 0)),
        add_box(f"{name}_roofR", (0.72, 0, 2.75), (1.65, 1.85, 0.14), mat_wood, rot=(0, math.radians(22), 0)),
        add_box(f"{name}_snowL", (-0.72, 0, 2.88), (1.62, 1.82, 0.16), mat_snow, rot=(0, math.radians(-22), 0), bevel=0.04),
        add_box(f"{name}_snowR", (0.72, 0, 2.88), (1.62, 1.82, 0.16), mat_snow, rot=(0, math.radians(22), 0), bevel=0.04),
    ]
    return _parent_all(parts, root, col)


def build_snowman(
    name: str,
    loc: Tuple[float, float, float],
    mat_snow: bpy.types.Material,
    mat_scarf: bpy.types.Material,
    mat_dark: bpy.types.Material,
    mat_orange: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    root = bpy.data.objects.new(name, None)
    root.location = loc
    parts = [
        add_sphere(f"{name}_b", (0, 0, 0.42), 0.46, mat_snow, segments=12),
        add_sphere(f"{name}_m", (0, 0, 1.02), 0.34, mat_snow, segments=12),
        add_sphere(f"{name}_h", (0, 0, 1.50), 0.24, mat_snow, segments=12),
        add_cylinder(f"{name}_scarf", (0, 0, 1.28), 0.24, 0.10, mat_scarf, verts=12),
        add_box(f"{name}_nose", (0, -0.26, 1.50), (0.06, 0.22, 0.06), mat_orange),
        add_cylinder(f"{name}_hatBrim", (0, 0, 1.70), 0.26, 0.04, mat_dark, verts=12),
        add_cylinder(f"{name}_hatTop", (0, 0, 1.86), 0.16, 0.28, mat_dark, verts=12),
    ]
    return _parent_all(parts, root, col)


def build_3d_car(
    name: str,
    loc: Tuple[float, float, float],
    mat_body: bpy.types.Material,
    mat_glass: bpy.types.Material,
    mat_tire: bpy.types.Material,
    mat_rim: bpy.types.Material,
    mat_head: bpy.types.Material,
    mat_tail: bpy.types.Material,
    mat_snow: Optional[bpy.types.Material] = None,
    dir_sign: float = 1.0,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Real stylized 3D hatchback/SUV strictly grounded on tires at Z=0.00 (center Z=0.34, radius=0.34)."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (0, 0, 0.0 if dir_sign >= 0 else math.pi)
    parts = [
        add_box(f"{name}_chassis", (0, 0, 0.56), (3.55, 1.68, 0.60), mat_body, bevel=0.09),
        add_box(f"{name}_bumperF", (1.78, 0, 0.36), (0.16, 1.66, 0.22), mat_tire, bevel=0.04),
        add_box(f"{name}_bumperR", (-1.78, 0, 0.36), (0.16, 1.66, 0.22), mat_tire, bevel=0.04),
        add_box(f"{name}_grille", (1.80, 0, 0.56), (0.06, 0.72, 0.20), mat_tire),
        add_box(f"{name}_cabin", (-0.22, 0, 1.12), (1.96, 1.48, 0.58), mat_body, bevel=0.08),
        add_box(f"{name}_windF", (0.72, 0, 1.10), (0.12, 1.36, 0.48), mat_glass, rot=(0, math.radians(-28), 0)),
        add_box(f"{name}_windR", (-1.16, 0, 1.10), (0.12, 1.34, 0.46), mat_glass, rot=(0, math.radians(24), 0)),
        add_box(f"{name}_sideWin", (-0.22, 0, 1.12), (1.58, 1.51, 0.40), mat_glass),
        add_box(f"{name}_mirL", (0.58, 0.88, 0.90), (0.12, 0.16, 0.10), mat_body),
        add_box(f"{name}_mirR", (0.58, -0.88, 0.90), (0.12, 0.16, 0.10), mat_body),
        add_box(f"{name}_hlL", (1.79, 0.56, 0.60), (0.06, 0.32, 0.18), mat_head),
        add_box(f"{name}_hlR", (1.79, -0.56, 0.60), (0.06, 0.32, 0.18), mat_head),
        add_box(f"{name}_tlL", (-1.79, 0.56, 0.60), (0.06, 0.30, 0.18), mat_tail),
        add_box(f"{name}_tlR", (-1.79, -0.56, 0.60), (0.06, 0.30, 0.18), mat_tail),
    ]
    if mat_snow is not None:
        parts.append(add_box(f"{name}_roofSnow", (-0.22, 0, 1.44), (1.76, 1.34, 0.09), mat_snow, bevel=0.03))
    for wx in (-1.08, 1.08):
        for wy in (-0.82, 0.82):
            parts.append(add_cylinder(f"{name}_tire_{wx}_{wy}", (wx, wy, 0.34), 0.34, 0.22, mat_tire, rot=(math.radians(90), 0, 0), verts=16))
            parts.append(add_cylinder(f"{name}_rim_{wx}_{wy}", (wx, wy + (0.03 if wy > 0 else -0.03), 0.34), 0.19, 0.20, mat_rim, rot=(math.radians(90), 0, 0), verts=12))
    return _parent_all(parts, root, col)


def build_snowy_pine_tree(
    name: str,
    loc: Tuple[float, float, float],
    height: float,
    mat_trunk: bpy.types.Material,
    mat_pine: bpy.types.Material,
    mat_snow: bpy.types.Material,
    seed: int = 11,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Multi-branched layered Nordic spruce/pine with irregular snow-covered boughs."""
    rng = random.Random(seed)
    root = bpy.data.objects.new(name, None)
    root.location = loc
    parts = [add_cylinder(f"{name}_trunk", (0, 0, height * 0.25), 0.16, height * 0.50, mat_trunk, verts=8)]
    tiers = 5
    for t_i in range(tiers):
        u = t_i / float(tiers - 1)
        z = height * (0.28 + u * 0.64)
        rad = (1.55 - u * 1.05) * (height / 5.0)
        n_boughs = 6 if t_i < 3 else 4
        for bi in range(n_boughs):
            ang = (2.0 * math.pi * bi) / n_boughs + t_i * 0.55 + rng.uniform(-0.2, 0.2)
            bx = math.cos(ang) * rad * 0.42
            by = math.sin(ang) * rad * 0.42
            parts.append(add_box(f"{name}_b_{t_i}_{bi}", (bx, by, z), (rad * 0.95, rad * 0.52, 0.34), mat_pine, rot=(math.radians(16), 0, ang), bevel=0.05))
            parts.append(add_box(f"{name}_s_{t_i}_{bi}", (bx, by, z + 0.17), (rad * 0.85, rad * 0.44, 0.14), mat_snow, rot=(math.radians(16), 0, ang), bevel=0.04))
    return _parent_all(parts, root, col)


def build_striped_beach_chair(
    name: str,
    loc: Tuple[float, float, float],
    rot_z: float,
    mat_wood: bpy.types.Material,
    mat_blue: bpy.types.Material,
    mat_white: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Authentic wooden-frame folding blue-and-white striped deck/beach chair with armrests & canvas sling."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (0, 0, rot_z)
    parts = [
        add_box(f"{name}_legFL", (-0.42, -0.05, 0.48), (0.055, 1.15, 0.055), mat_wood, rot=(math.radians(52), 0, 0)),
        add_box(f"{name}_legFR", (0.42, -0.05, 0.48), (0.055, 1.15, 0.055), mat_wood, rot=(math.radians(52), 0, 0)),
        add_box(f"{name}_legBL", (-0.42, 0.05, 0.38), (0.055, 0.95, 0.055), mat_wood, rot=(math.radians(-40), 0, 0)),
        add_box(f"{name}_legBR", (0.42, 0.05, 0.38), (0.055, 0.95, 0.055), mat_wood, rot=(math.radians(-40), 0, 0)),
        add_box(f"{name}_armL", (-0.44, -0.04, 0.62), (0.08, 0.72, 0.045), mat_wood),
        add_box(f"{name}_armR", (0.44, -0.04, 0.62), (0.08, 0.72, 0.045), mat_wood),
        add_cylinder(f"{name}_topBar", (0, 0.32, 0.96), 0.032, 0.88, mat_wood, rot=(0, math.radians(90), 0), verts=10),
        add_cylinder(f"{name}_frontBar", (0, -0.40, 0.30), 0.032, 0.88, mat_wood, rot=(0, math.radians(90), 0), verts=10),
    ]
    for si in range(7):
        sx = -0.33 + si * 0.11
        sm = mat_blue if si % 2 == 0 else mat_white
        parts.append(add_box(f"{name}_slingB_{si}", (sx, 0.14, 0.66), (0.11, 0.72, 0.03), sm, rot=(math.radians(52), 0, 0)))
        parts.append(add_box(f"{name}_slingS_{si}", (sx, -0.18, 0.34), (0.11, 0.48, 0.03), sm, rot=(math.radians(-10), 0, 0)))
    return _parent_all(parts, root, col)


def build_thermos_and_mug(
    name: str,
    loc: Tuple[float, float, float],
    mat_steel: bpy.types.Material,
    mat_dark: bpy.types.Material,
    mat_red: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    root = bpy.data.objects.new(name, None)
    root.location = loc
    parts = [
        add_cylinder(f"{name}_body", (0, 0, 0.18), 0.075, 0.34, mat_steel, verts=16),
        add_cylinder(f"{name}_collar", (0, 0, 0.37), 0.062, 0.06, mat_dark, verts=16),
        add_cylinder(f"{name}_cap", (0, 0, 0.44), 0.068, 0.09, mat_steel, verts=16),
        add_box(f"{name}_handle", (0.09, 0, 0.22), (0.035, 0.03, 0.22), mat_dark, bevel=0.01),
        add_cylinder(f"{name}_cup", (-0.18, -0.06, 0.065), 0.055, 0.12, mat_red, verts=14),
    ]
    return _parent_all(parts, root, col)


# ============================================================================
# 4. BAARLE REAL-REFERENCE ASSETS (ESPRESSO, PASTRY, BISTRO SETS, PLANTS, DUAL-FLAG & ROW HOUSES)
# ============================================================================

def build_italian_espresso_machine(
    name: str,
    loc: Tuple[float, float, float],
    mat_chrome: bpy.types.Material,
    mat_brass: bpy.types.Material,
    mat_dark: bpy.types.Material,
    mat_white: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Commercial Italian café espresso machine + coffee bean grinder beside it!"""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    parts = [
        add_box(f"{name}_base", (0, 0, 0.05), (0.86, 0.56, 0.10), mat_dark, bevel=0.01),
        add_box(f"{name}_body", (0, 0.06, 0.32), (0.84, 0.44, 0.46), mat_chrome, bevel=0.03),
        add_box(f"{name}_topTray", (0, 0.06, 0.56), (0.82, 0.42, 0.03), mat_brass),
        add_box(f"{name}_drip", (0, -0.18, 0.08), (0.78, 0.18, 0.04), mat_chrome),
        add_box(f"{name}_railL", (-0.39, 0.06, 0.62), (0.02, 0.40, 0.08), mat_chrome),
        add_box(f"{name}_railR", (0.39, 0.06, 0.62), (0.02, 0.40, 0.08), mat_chrome),
        add_box(f"{name}_railB", (0, 0.25, 0.62), (0.80, 0.02, 0.08), mat_chrome),
        # Espresso bean grinder right beside the machine!
        add_cylinder(f"{name}_grindBase", (0.60, 0.05, 0.16), 0.11, 0.30, mat_dark, verts=14),
        add_cylinder(f"{name}_grindHopper", (0.60, 0.05, 0.42), 0.10, 0.22, mat_brass, verts=14),
    ]
    for cx in (-0.26, -0.10, 0.06, 0.22):
        parts.append(add_cylinder(f"{name}_topCup_{cx}", (cx, 0.08, 0.61), 0.042, 0.08, mat_white, verts=12))
    for gx in (-0.18, 0.18):
        parts.append(add_cylinder(f"{name}_grp_{gx}", (gx, -0.18, 0.34), 0.072, 0.11, mat_chrome, verts=14))
        parts.append(add_cylinder(f"{name}_pf_{gx}", (gx, -0.18, 0.26), 0.056, 0.06, mat_brass, verts=14))
        parts.append(add_cylinder(f"{name}_pfh_{gx}", (gx, -0.32, 0.24), 0.018, 0.20, mat_dark, rot=(math.radians(82), 0, 0), verts=10))
    parts.append(add_cylinder(f"{name}_knob", (-0.34, -0.17, 0.46), 0.032, 0.05, mat_brass, rot=(math.radians(90), 0, 0), verts=12))
    parts.append(add_cylinder(f"{name}_wand", (-0.34, -0.22, 0.26), 0.011, 0.28, mat_chrome, rot=(math.radians(24), math.radians(-16), 0), verts=8))
    for dx in (0.0, 0.32):
        parts.append(add_cylinder(f"{name}_dialRim_{dx}", (dx, -0.165, 0.45), 0.048, 0.025, mat_brass, rot=(math.radians(90), 0, 0), verts=16))
        parts.append(add_cylinder(f"{name}_dialFace_{dx}", (dx, -0.175, 0.45), 0.038, 0.015, mat_white, rot=(math.radians(90), 0, 0), verts=16))
    return _parent_all(parts, root, col)


def build_pastry_display_case(
    name: str,
    loc: Tuple[float, float, float],
    mat_glass: bpy.types.Material,
    mat_metal: bpy.types.Material,
    mat_oak: bpy.types.Material,
    mat_pastry: bpy.types.Material,
    mat_waffle: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    root = bpy.data.objects.new(name, None)
    root.location = loc
    parts = [
        add_box(f"{name}_base", (0, 0, 0.03), (1.05, 0.56, 0.06), mat_oak),
        add_box(f"{name}_shelfMid", (0, 0, 0.26), (0.98, 0.48, 0.02), mat_glass),
        add_box(f"{name}_glassTop", (0, 0.04, 0.50), (1.04, 0.46, 0.02), mat_glass),
        add_box(f"{name}_glassFront", (0, -0.23, 0.27), (1.04, 0.02, 0.48), mat_glass, rot=(math.radians(-12), 0, 0)),
    ]
    for mx in (-0.51, 0.51):
        parts.append(add_box(f"{name}_postB_{mx}", (mx, 0.26, 0.27), (0.03, 0.03, 0.48), mat_metal))
        parts.append(add_box(f"{name}_postF_{mx}", (mx, -0.22, 0.27), (0.03, 0.03, 0.48), mat_metal, rot=(math.radians(-12), 0, 0)))
    for ci in range(4):
        cx = -0.34 + ci * 0.22
        parts.append(add_sphere(f"{name}_crM_{ci}", (cx, -0.02, 0.10), 0.055, mat_pastry, scale=(1.35, 0.78, 0.65), segments=10))
        parts.append(add_sphere(f"{name}_crL_{ci}", (cx - 0.06, -0.05, 0.09), 0.038, mat_pastry, scale=(1.1, 0.75, 0.65), segments=8))
        parts.append(add_sphere(f"{name}_crR_{ci}", (cx + 0.06, -0.05, 0.09), 0.038, mat_pastry, scale=(1.1, 0.75, 0.65), segments=8))
    for wi in range(3):
        wx = -0.28 + wi * 0.28
        for st in range(3):
            parts.append(add_cylinder(f"{name}_sw_{wi}_{st}", (wx, 0.02, 0.285 + st * 0.022), 0.068, 0.018, mat_waffle, verts=14))
    return _parent_all(parts, root, col)


def build_edison_pendant(
    name: str,
    loc: Tuple[float, float, float],
    mat_iron: bpy.types.Material,
    mat_brass: bpy.types.Material,
    mat_bulb: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    root = bpy.data.objects.new(name, None)
    root.location = loc
    bpy.ops.mesh.primitive_cone_add(vertices=18, radius1=0.26, radius2=0.07, depth=0.22, location=(0, 0, 0.08))
    shade = bpy.context.active_object
    shade.name = f"{name}_shade"
    shade.data.materials.append(mat_iron)
    parts = [
        add_cylinder(f"{name}_cord", (0, 0, 0.62), 0.012, 0.96, mat_iron, verts=8),
        add_cylinder(f"{name}_socket", (0, 0, 0.20), 0.042, 0.08, mat_brass, verts=12),
        shade,
        add_sphere(f"{name}_bulb", (0, 0, -0.03), 0.065, mat_bulb, scale=(0.85, 0.85, 1.25), segments=12),
    ]
    return _parent_all(parts, root, col)


def build_cafe_bistro_set(
    name: str,
    loc: Tuple[float, float, float],
    mat_iron: bpy.types.Material,
    mat_oak: bpy.types.Material,
    mat_rattan: bpy.types.Material,
    mat_cup: bpy.types.Material,
    mat_umbrella: Optional[bpy.types.Material] = None,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Complete European café bistro table + 2 chairs + coffee cups (+ optional patio sun umbrella!)."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    parts = [
        add_cylinder(f"{name}_tBase", (0, 0, 0.03), 0.28, 0.05, mat_iron, verts=14),
        add_cylinder(f"{name}_tPost", (0, 0, 0.39), 0.042, 0.74, mat_iron, verts=10),
        add_cylinder(f"{name}_tTop", (0, 0, 0.77), 0.48, 0.045, mat_oak, verts=18),
        add_cylinder(f"{name}_cup1", (-0.16, -0.08, 0.84), 0.05, 0.09, mat_cup, verts=12),
        add_cylinder(f"{name}_cup2", (0.18, 0.06, 0.84), 0.05, 0.09, mat_cup, verts=12),
    ]
    for sx in (-0.72, 0.72):
        parts += [
            add_cylinder(f"{name}_cSeat_{sx}", (sx, 0, 0.46), 0.24, 0.04, mat_rattan, verts=14),
            add_box(f"{name}_cBack_{sx}", (sx + (0.20 if sx > 0 else -0.20), 0, 0.74), (0.05, 0.42, 0.50), mat_rattan),
            add_cylinder(f"{name}_cLeg1_{sx}", (sx - 0.16, -0.16, 0.23), 0.02, 0.46, mat_iron, verts=8),
            add_cylinder(f"{name}_cLeg2_{sx}", (sx + 0.16, 0.16, 0.23), 0.02, 0.46, mat_iron, verts=8),
            add_cylinder(f"{name}_cLeg3_{sx}", (sx - 0.16, 0.16, 0.23), 0.02, 0.46, mat_iron, verts=8),
            add_cylinder(f"{name}_cLeg4_{sx}", (sx + 0.16, -0.16, 0.23), 0.02, 0.46, mat_iron, verts=8),
        ]
    if mat_umbrella is not None:
        parts.append(add_cylinder(f"{name}_umbPole", (0, 0, 1.45), 0.026, 2.35, mat_oak, verts=10))
        bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=1.22, radius2=0.06, depth=0.45, location=(0, 0, 2.55))
        umb = bpy.context.active_object
        umb.name = f"{name}_umbTop"
        umb.data.materials.append(mat_umbrella)
        parts.append(umb)
    return _parent_all(parts, root, col)


def build_potted_plant(
    name: str,
    loc: Tuple[float, float, float],
    mat_pot: bpy.types.Material,
    mat_leaf: bpy.types.Material,
    mat_flower: Optional[bpy.types.Material] = None,
    scale_h: float = 1.0,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.scale = (scale_h, scale_h, scale_h)
    parts = [
        add_cylinder(f"{name}_pot", (0, 0, 0.22), 0.20, 0.44, mat_pot, verts=12),
        add_cylinder(f"{name}_rim", (0, 0, 0.44), 0.23, 0.06, mat_pot, verts=12),
        add_sphere(f"{name}_bush0", (0, 0, 0.68), 0.28, mat_leaf, scale=(1.0, 1.0, 1.15), segments=10),
        add_sphere(f"{name}_bush1", (-0.16, 0.10, 0.84), 0.20, mat_leaf, segments=8),
        add_sphere(f"{name}_bush2", (0.16, -0.08, 0.88), 0.19, mat_leaf, segments=8),
    ]
    if mat_flower is not None:
        for fx, fy, fz in [(-0.14, -0.14, 0.78), (0.15, -0.12, 0.86), (0.0, -0.18, 0.66)]:
            parts.append(add_sphere(f"{name}_fl_{fx}", (fx, fy, fz), 0.065, mat_flower, segments=8))
    return _parent_all(parts, root, col)


def build_dutch_bicycle(
    name: str,
    loc: Tuple[float, float, float],
    rot_z: float,
    mat_frame: bpy.types.Material,
    mat_tire: bpy.types.Material,
    mat_iron: bpy.types.Material,
    mat_rattan: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (0, 0, rot_z)
    parts = []
    for wx in (-0.52, 0.52):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.33, minor_radius=0.034, location=(wx, 0, 0.35), rotation=(math.radians(90), 0, 0))
        t_obj = bpy.context.active_object
        t_obj.name = f"{name}_tire_{wx}"
        t_obj.data.materials.append(mat_tire)
        parts.append(t_obj)
        parts.append(add_cylinder(f"{name}_hub_{wx}", (wx, 0, 0.35), 0.04, 0.08, mat_iron, rot=(math.radians(90), 0, 0), verts=10))
        for sp in range(3):
            parts.append(add_cylinder(f"{name}_sp_{wx}_{sp}", (wx, 0, 0.35), 0.008, 0.62, mat_iron, rot=(0, math.radians(sp * 60), 0), verts=6))
    parts += [
        add_cylinder(f"{name}_barTop", (0.0, 0, 0.72), 0.022, 0.86, mat_frame, rot=(0, math.radians(82), 0), verts=8),
        add_cylinder(f"{name}_seatPost", (0.16, 0, 0.64), 0.022, 0.62, mat_frame, rot=(0, math.radians(-16), 0), verts=8),
        add_cylinder(f"{name}_forkF", (-0.42, 0, 0.68), 0.022, 0.74, mat_frame, rot=(0, math.radians(-18), 0), verts=8),
        add_cylinder(f"{name}_handlebar", (-0.34, 0, 1.02), 0.018, 0.56, mat_iron, rot=(math.radians(90), 0, 0), verts=8),
        add_box(f"{name}_saddle", (0.20, 0, 0.96), (0.24, 0.14, 0.06), mat_tire, bevel=0.02),
        add_box(f"{name}_basket", (-0.54, 0, 0.82), (0.28, 0.34, 0.24), mat_rattan, bevel=0.02),
    ]
    return _parent_all(parts, root, col)


def build_baarle_dual_flag_house(
    name: str,
    loc: Tuple[float, float, float],
    mat_brick: bpy.types.Material,
    mat_trim: bpy.types.Material,
    mat_door: bpy.types.Material,
    mat_brass: bpy.types.Material,
    mat_glass: bpy.types.Material,
    mat_curtain: bpy.types.Material,
    mat_plaque_b: bpy.types.Material,
    mat_plaque_nl: bpy.types.Material,
    mat_lantern: bpy.types.Material,
    mat_pot: bpy.types.Material,
    mat_leaf: bpy.types.Material,
    mat_flower: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Iconic Baarle stepped-gable brick border house with dark-green shutters, limestone keystones, flower boxes & dual NL/BE plaques!"""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    fy = 1.24
    parts = [
        add_box(f"{name}_plinth", (0, 0, 0.30), (6.95, 2.58, 0.60), mat_trim),
        add_box(f"{name}_body", (0, 0, 3.45), (6.8, 2.45, 6.2), mat_brick),
        add_box(f"{name}_quoinL", (-3.38, fy - 0.04, 3.45), (0.24, 0.16, 6.2), mat_trim),
        add_box(f"{name}_quoinR", (3.38, fy - 0.04, 3.45), (0.24, 0.16, 6.2), mat_trim),
        # Decorative limestone string-course band between stories!
        add_box(f"{name}_bandMid", (0, fy + 0.04, 3.42), (6.92, 0.14, 0.16), mat_trim),
    ]
    for si, (sw, sz) in enumerate([(5.8, 6.95), (4.4, 7.75), (3.0, 8.55), (1.5, 9.35)]):
        parts.append(add_box(f"{name}_gable_{si}", (0, 1.02, sz), (sw, 0.44, 0.82), mat_brick))
        parts.append(add_box(f"{name}_cap_{si}", (0, 1.05, sz + 0.42), (sw + 0.20, 0.52, 0.10), mat_trim))
    # Attic round bullseye window in gable peak!
    parts.append(add_cylinder(f"{name}_gableOculusFrame", (0, fy + 0.02, 7.35), 0.46, 0.12, mat_trim, rot=(math.radians(90), 0, 0), verts=18))
    parts.append(add_cylinder(f"{name}_gableOculusGlass", (0, fy + 0.06, 7.35), 0.36, 0.08, mat_glass, rot=(math.radians(90), 0, 0), verts=18))

    # Recessed paneled green front door + stone steps + brass knob + mail slot + transom fanlight + wrought-iron wall lantern!
    parts += [
        add_box(f"{name}_step", (0, fy + 0.24, 0.12), (2.0, 0.52, 0.24), mat_trim),
        add_box(f"{name}_doorCasing", (0, fy + 0.02, 1.56), (1.62, 0.18, 2.90), mat_trim),
        add_box(f"{name}_doorPediment", (0, fy + 0.10, 3.04), (1.92, 0.28, 0.18), mat_trim),
        add_box(f"{name}_doorLeaf", (0, fy + 0.06, 1.32), (1.24, 0.10, 2.26), mat_door),
        add_box(f"{name}_doorPanelT", (0, fy + 0.12, 1.82), (0.86, 0.03, 0.72), mat_trim),
        add_box(f"{name}_doorPanelB", (0, fy + 0.12, 0.82), (0.86, 0.03, 0.72), mat_trim),
        add_sphere(f"{name}_knob", (0.44, fy + 0.16, 1.24), 0.055, mat_brass, segments=10),
        add_box(f"{name}_mailSlot", (0, fy + 0.14, 1.32), (0.34, 0.03, 0.07), mat_brass),
        add_box(f"{name}_transom", (0, fy + 0.08, 2.66), (1.24, 0.06, 0.36), mat_curtain),
        add_box(f"{name}_lanternCap", (0, fy + 0.24, 3.24), (0.28, 0.28, 0.08), mat_brass),
        add_sphere(f"{name}_lanternGlow", (0, fy + 0.24, 3.10), 0.12, mat_lantern, segments=10),
    ]

    # OFFICIAL DUAL-COUNTRY PLAQUES: Screen LEFT (+X) = BELGIUM 2; Screen RIGHT (-X) = NETHERLANDS 19!
    parts += [
        add_box(f"{name}_plaqueBackB", (1.28, fy + 0.05, 2.04), (0.94, 0.06, 0.70), mat_trim),
        add_decal_plane(f"{name}_plaqueFaceB", (1.28, fy + 0.10, 2.04), 0.88, 0.64, (math.radians(90), 0, math.radians(180)), mat_plaque_b),
        add_box(f"{name}_plaqueBackNL", (-1.28, fy + 0.05, 2.04), (0.94, 0.06, 0.70), mat_trim),
        add_decal_plane(f"{name}_plaqueFaceNL", (-1.28, fy + 0.10, 2.04), 0.88, 0.64, (math.radians(90), 0, math.radians(180)), mat_plaque_nl),
    ]

    # 4 Recessed Multi-Pane Windows with DARK-GREEN WOODEN SHUTTERS, Limestone Keystones, Curtains & Geranium Flower Boxes!
    win_coords = [(-2.52, 1.96), (2.52, 1.96), (-1.82, 4.78), (1.82, 4.78)]
    for wi, (wx, wz) in enumerate(win_coords):
        parts += [
            add_box(f"{name}_wf_{wi}", (wx, fy + 0.02, wz), (1.26, 0.14, 1.54), mat_trim),
            add_box(f"{name}_wlintel_{wi}", (wx, fy + 0.08, wz + 0.82), (1.44, 0.18, 0.16), mat_trim),
            add_box(f"{name}_wg_{wi}", (wx, fy + 0.07, wz), (1.04, 0.05, 1.32), mat_glass),
            add_box(f"{name}_curtL_{wi}", (wx - 0.33, fy + 0.05, wz), (0.32, 0.04, 1.28), mat_curtain),
            add_box(f"{name}_curtR_{wi}", (wx + 0.33, fy + 0.05, wz), (0.32, 0.04, 1.28), mat_curtain),
            add_box(f"{name}_mv_{wi}", (wx, fy + 0.11, wz), (0.06, 0.05, 1.34), mat_trim),
            add_box(f"{name}_mh_{wi}", (wx, fy + 0.11, wz + 0.14), (1.06, 0.05, 0.06), mat_trim),
            add_box(f"{name}_wsill_{wi}", (wx, fy + 0.14, wz - 0.78), (1.40, 0.26, 0.12), mat_trim),
            # Authentic dark-green European louvered shutters flanking window!
            add_box(f"{name}_shutL_{wi}", (wx - 0.80, fy + 0.07, wz), (0.32, 0.06, 1.48), mat_door, bevel=0.01),
            add_box(f"{name}_shutR_{wi}", (wx + 0.80, fy + 0.07, wz), (0.32, 0.06, 1.48), mat_door, bevel=0.01),
            # Blooming red geranium window flower box on sill!
            add_box(f"{name}_fbox_{wi}", (wx, fy + 0.24, wz - 0.64), (1.12, 0.22, 0.20), mat_pot),
            add_sphere(f"{name}_flL_{wi}", (wx - 0.32, fy + 0.26, wz - 0.46), 0.13, mat_leaf, segments=8),
            add_sphere(f"{name}_flM_{wi}", (wx, fy + 0.26, wz - 0.44), 0.15, mat_leaf, segments=8),
            add_sphere(f"{name}_flR_{wi}", (wx + 0.32, fy + 0.26, wz - 0.46), 0.13, mat_leaf, segments=8),
            add_sphere(f"{name}_fp1_{wi}", (wx - 0.22, fy + 0.32, wz - 0.38), 0.07, mat_flower, segments=8),
            add_sphere(f"{name}_fp2_{wi}", (wx + 0.18, fy + 0.32, wz - 0.37), 0.07, mat_flower, segments=8),
        ]
    return _parent_all(parts, root, col)


def build_baarle_row_house(
    name: str,
    loc: Tuple[float, float, float],
    mat_brick: bpy.types.Material,
    mat_trim: bpy.types.Material,
    mat_awning: bpy.types.Material,
    mat_glass: bpy.types.Material,
    mat_door: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Detailed flanking Dutch/Belgian stepped-gable row-house with shopfront awning & multi-pane windows (NOT blank brick block!)."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    fy = 1.32
    parts = [
        add_box(f"{name}_body", (0, 0, 3.25), (6.5, 2.6, 6.5), mat_brick),
        add_box(f"{name}_band", (0, fy + 0.02, 3.20), (6.6, 0.12, 0.14), mat_trim),
        add_box(f"{name}_shopWin", (0, fy + 0.02, 1.55), (4.6, 0.10, 2.15), mat_trim),
        add_box(f"{name}_shopGlass", (0, fy + 0.06, 1.55), (4.2, 0.06, 1.85), mat_glass),
        add_box(f"{name}_shopAwn", (0, fy + 0.48, 2.72), (5.2, 0.96, 0.10), mat_awning, rot=(math.radians(-18), 0, 0)),
    ]
    for si, (sw, sz) in enumerate([(5.2, 6.85), (3.6, 7.65), (2.0, 8.45)]):
        parts.append(add_box(f"{name}_g_{si}", (0, 1.10, sz), (sw, 0.40, 0.80), mat_brick))
        parts.append(add_box(f"{name}_gc_{si}", (0, 1.12, sz + 0.40), (sw + 0.16, 0.46, 0.08), mat_trim))
    for wx in (-1.75, 0.0, 1.75):
        parts += [
            add_box(f"{name}_wf_{wx}", (wx, fy + 0.02, 4.75), (1.15, 0.12, 1.48), mat_trim),
            add_box(f"{name}_wg_{wx}", (wx, fy + 0.06, 4.75), (0.95, 0.05, 1.28), mat_glass),
            add_box(f"{name}_shL_{wx}", (wx - 0.70, fy + 0.05, 4.75), (0.24, 0.05, 1.42), mat_door),
        ]
    return _parent_all(parts, root, col)
