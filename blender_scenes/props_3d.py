"""Dedicated Real-Reference Mid-Poly 3D Hero Prop & Architectural Asset Module (Beveled, Multi-Part, PBR)."""
from __future__ import annotations

import math
import random
from typing import Optional, Tuple

import bmesh
import bpy
from mathutils import Vector

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
# 1. ORGANIC JAGGED ROCKS, CLIFFS & BERING SEA-ICE FLOES (BMESH DISPLACED)
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
    """Authentic jagged polygonal Bering Strait sea-ice floe with fractured outer rim."""
    rng = random.Random(seed)
    bm = bmesh.new()
    n_verts = rng.randint(8, 13)
    bot_ring = []
    top_ring = []
    for i in range(n_verts):
        ang = (2.0 * math.pi * i) / n_verts + rng.uniform(-0.18, 0.18)
        r = radius * rng.uniform(0.62, 1.25)
        x = math.cos(ang) * r
        y = math.sin(ang) * r
        bot_ring.append(bm.verts.new((x * 1.06, y * 1.06, -thickness * 0.5)))
        top_ring.append(bm.verts.new((x * 0.96, y * 0.96, thickness * 0.5 + rng.uniform(-0.03, 0.05))))
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
    """Multi-faceted rugged granite mountain / volcanic mesa silhouette (Little Diomede, Big Diomede, Rjukan cliff)."""
    rng = random.Random(seed)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=14, y_subdivisions=10, size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for v in bm.verts:
        nx = v.co.x * 2.0  # -1..1
        ny = v.co.y * 2.0  # -1..1
        edge_fade = max(0.0, 1.0 - max(abs(nx), abs(ny)) ** 2.4)
        ridge = math.sin(nx * 3.8 + seed) * 0.16 + math.cos(ny * 4.2 + seed) * 0.14
        if flat_top:
            # Big Diomede iconic steep flat-topped mesa silhouette!
            z_norm = min(1.0, edge_fade * 2.1) * (0.90 + 0.10 * rng.uniform(-1, 1))
        else:
            z_norm = (edge_fade ** 0.72) * (0.85 + ridge + rng.uniform(-0.14, 0.14))
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
# 2. LITTLE DIOMEDE HERO PROPS (IGNALUK STILT HOUSE, BOLLARDS, DORY BOAT)
# ============================================================================

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
        add_cylinder(f"{name}_base", (0, 0, 0.04), 0.20, 0.08, mat_iron, verts=12),
        add_cylinder(f"{name}_post", (0, 0, 0.26), 0.11, 0.42, mat_iron, verts=12),
        add_cylinder(f"{name}_cap", (0, 0, 0.48), 0.16, 0.08, mat_iron, verts=12),
        add_cylinder(f"{name}_horn", (0, 0, 0.36), 0.04, 0.38, mat_iron, rot=(0, math.radians(90), 0), verts=10),
    ]
    # Coiled mooring rope around bollard base
    for ri in range(3):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.19 + ri * 0.04, minor_radius=0.024, location=(0.14, -0.06, 0.03 + ri * 0.025))
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
    """Authentic Little Diomede (Ignaluk) wooden stilt house with cross-braced pilings, white window frames & porch."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (0, 0, rot_z)
    parts = []
    # 4 tall timber stilts + diagonal X-braces
    for sx in (-1.4, 1.4):
        for sy in (-1.1, 1.1):
            parts.append(add_cylinder(f"{name}_stilt_{sx}_{sy}", (sx, sy, -1.9), 0.11, 4.0, mat_wood, verts=8))
    parts.append(add_box(f"{name}_brace1", (0, 1.1, -1.5), (3.4, 0.09, 0.11), mat_wood, rot=(0, math.radians(28), 0)))
    parts.append(add_box(f"{name}_brace2", (0, 1.1, -1.5), (3.4, 0.09, 0.11), mat_wood, rot=(0, math.radians(-28), 0)))
    # Elevated timber platform deck
    parts.append(add_box(f"{name}_deck", (0, 0.25, 0.06), (3.8, 3.2, 0.16), mat_wood))
    # Main cabin walls + gable roof + overhanging snow slab
    parts.append(add_box(f"{name}_body", (0, -0.05, 1.18), (3.4, 2.5, 2.15), mat_wall))
    parts.append(add_box(f"{name}_roofL", (-0.92, -0.05, 2.56), (2.2, 2.9, 0.14), mat_roof, rot=(0, math.radians(-22), 0)))
    parts.append(add_box(f"{name}_roofR", (0.92, -0.05, 2.56), (2.2, 2.9, 0.14), mat_roof, rot=(0, math.radians(22), 0)))
    parts.append(add_box(f"{name}_snowL", (-0.92, -0.05, 2.70), (2.1, 2.85, 0.14), mat_snow, rot=(0, math.radians(-22), 0)))
    parts.append(add_box(f"{name}_snowR", (0.92, -0.05, 2.70), (2.1, 2.85, 0.14), mat_snow, rot=(0, math.radians(22), 0)))
    # White-trimmed multi-pane glowing windows + paneled entry door
    for wx in (-0.95, 0.95):
        parts.append(add_box(f"{name}_wframe_{wx}", (wx, 1.22, 1.25), (0.76, 0.08, 0.84), mat_trim))
        parts.append(add_box(f"{name}_wglass_{wx}", (wx, 1.25, 1.25), (0.62, 0.04, 0.70), mat_win))
        parts.append(add_box(f"{name}_wmullV_{wx}", (wx, 1.27, 1.25), (0.04, 0.04, 0.72), mat_trim))
        parts.append(add_box(f"{name}_wmullH_{wx}", (wx, 1.27, 1.25), (0.64, 0.04, 0.04), mat_trim))
    parts.append(add_box(f"{name}_door", (0, 1.22, 0.95), (0.68, 0.08, 1.62), mat_wood))
    parts.append(add_cylinder(f"{name}_chimney", (0.95, -0.55, 3.10), 0.12, 1.2, mat_metal, verts=8))
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


# ============================================================================
# 3. RJUKAN REAL-REFERENCE ASSETS (SOLSPEILET MIRRORS, NORWEGIAN FACADES, CARS, PINES, BEACH CHAIR)
# ============================================================================

def build_solspeilet_heliostat(
    name: str,
    loc: Tuple[float, float, float],
    mat_steel: bpy.types.Material,
    mat_mirror: bpy.types.Material,
    mat_accent: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> Tuple[bpy.types.Object, bpy.types.Object]:
    """Authentic 2013 Rjukan Solspeilet heliostat: A-frame steel lattice truss + hydraulic pistons + 3x4 paneled mirror."""
    base = bpy.data.objects.new(f"{name}_Base", None)
    base.location = loc
    base_parts = [
        add_box(f"{name}_footL", (-1.15, 0, -2.1), (0.55, 0.85, 0.24), mat_steel),
        add_box(f"{name}_footR", (1.15, 0, -2.1), (0.55, 0.85, 0.24), mat_steel),
        add_cylinder(f"{name}_legFL", (-1.10, -0.25, -1.0), 0.09, 2.4, mat_steel, rot=(math.radians(10), 0, 0), verts=8),
        add_cylinder(f"{name}_legFR", (1.10, -0.25, -1.0), 0.09, 2.4, mat_steel, rot=(math.radians(10), 0, 0), verts=8),
        add_cylinder(f"{name}_legBL", (-1.10, 0.45, -1.0), 0.09, 2.5, mat_steel, rot=(math.radians(-16), 0, 0), verts=8),
        add_cylinder(f"{name}_legBR", (1.10, 0.45, -1.0), 0.09, 2.5, mat_steel, rot=(math.radians(-16), 0, 0), verts=8),
        add_box(f"{name}_crossBar", (0, 0.10, -0.95), (2.35, 0.14, 0.14), mat_steel),
        add_cylinder(f"{name}_gearbox", (0, 0.08, 0.0), 0.24, 2.4, mat_steel, rot=(0, math.radians(90), 0), verts=12),
        add_cylinder(f"{name}_hydL", (-0.75, 0.42, -0.85), 0.075, 2.0, mat_accent, rot=(math.radians(22), 0, 0), verts=10),
        add_cylinder(f"{name}_hydR", (0.75, 0.42, -0.85), 0.075, 2.0, mat_accent, rot=(math.radians(22), 0, 0), verts=10),
    ]
    _parent_all(base_parts, base, col)

    # Pivoting mirror assembly (3x4 real glass sub-panels on brushed aluminum frame!)
    piv = bpy.data.objects.new(f"{name}_Pivot", None)
    piv.location = (loc[0], loc[1] - 0.15, loc[2])
    piv_parts = [
        add_box(f"{name}_frameBack", (0, 0.08, 0), (3.55, 0.14, 4.55), mat_steel, bevel=0.03),
        add_box(f"{name}_glassMain", (0, -0.02, 0), (3.30, 0.04, 4.30), mat_mirror),
    ]
    # Real panel mullion dividers (3 cols x 4 rows matching real Solspeilet!)
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
    facing: str = "+X",  # "+X", "-X", or "+Y"
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Authentic Rjukan Torg Norwegian wooden/brick building: white window casings, shop door, thick snow eaves & icicles."""
    w, d, h = size
    root = bpy.data.objects.new(name, None)
    root.location = loc
    rot_map = {"+Y": 0.0, "-X": math.radians(90), "+X": math.radians(-90)}
    root.rotation_euler = (0, 0, rot_map.get(facing, 0.0))

    parts = [
        # Stone plinth foundation
        add_box(f"{name}_plinth", (0, 0, 0.35), (w + 0.12, d + 0.12, 0.70), mat_roof),
        # Main facade body
        add_box(f"{name}_body", (0, 0, h * 0.5 + 0.30), (w, d, h), mat_wall),
        # White corner trim boards (signature Norwegian timber house detail!)
        add_box(f"{name}_cornerFL", (-w * 0.5, d * 0.5, h * 0.5 + 0.30), (0.18, 0.18, h), mat_trim),
        add_box(f"{name}_cornerFR", (w * 0.5, d * 0.5, h * 0.5 + 0.30), (0.18, 0.18, h), mat_trim),
        # Pitched gable roof + thick snow overhang!
        add_box(f"{name}_roofF", (0, d * 0.28, h + 0.95), (w + 0.65, d * 0.66, 0.18), mat_roof, rot=(math.radians(26), 0, 0)),
        add_box(f"{name}_roofB", (0, -d * 0.28, h + 0.95), (w + 0.65, d * 0.66, 0.18), mat_roof, rot=(math.radians(-26), 0, 0)),
        add_box(f"{name}_snowF", (0, d * 0.28, h + 1.12), (w + 0.55, d * 0.64, 0.22), mat_snow, rot=(math.radians(26), 0, 0), bevel=0.05),
        add_box(f"{name}_snowB", (0, -d * 0.28, h + 1.12), (w + 0.55, d * 0.64, 0.22), mat_snow, rot=(math.radians(-26), 0, 0), bevel=0.05),
        # Brick chimney
        add_box(f"{name}_chim", (w * 0.28, -d * 0.15, h + 1.85), (0.65, 0.65, 1.5), mat_door),
    ]
    # Hanging crystalline icicles along front snow eaves!
    eave_y = d * 0.5 + 0.24
    eave_z = h + 0.42
    for ix in range(-2, 3):
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.05, depth=0.38 + (abs(ix) % 2) * 0.14, location=(ix * (w * 0.19), eave_y, eave_z), rotation=(math.radians(180), 0, 0))
        ic = bpy.context.active_object
        ic.name = f"{name}_icicle_{ix}"
        ic.data.materials.append(mat_ice)
        parts.append(ic)

    # Recessed front shop door with awning + multi-pane white-cased windows!
    fy = d * 0.5 + 0.03
    parts.append(add_box(f"{name}_doorFrame", (0, fy, 1.38), (1.35, 0.12, 2.25), mat_trim))
    parts.append(add_box(f"{name}_doorLeaf", (0, fy + 0.03, 1.32), (1.10, 0.08, 2.08), mat_door))
    parts.append(add_box(f"{name}_doorAwning", (0, fy + 0.35, 2.52), (1.65, 0.65, 0.14), mat_snow, rot=(math.radians(14), 0, 0)))

    # 2 stories of crisp white-framed multi-pane windows!
    win_xs = [-w * 0.30, w * 0.30]
    for floor_z in (2.05, 4.45):
        if floor_z + 0.8 > h:
            continue
        xs = win_xs if floor_z < 3.0 else [-w * 0.30, 0.0, w * 0.30]
        for wx in xs:
            parts.append(add_box(f"{name}_wf_{floor_z}_{wx}", (wx, fy, floor_z), (1.12, 0.10, 1.32), mat_trim))
            parts.append(add_box(f"{name}_wg_{floor_z}_{wx}", (wx, fy + 0.03, floor_z), (0.94, 0.05, 1.14), mat_win))
            parts.append(add_box(f"{name}_mv_{floor_z}_{wx}", (wx, fy + 0.06, floor_z), (0.05, 0.04, 1.15), mat_trim))
            parts.append(add_box(f"{name}_mh_{floor_z}_{wx}", (wx, fy + 0.06, floor_z), (0.95, 0.04, 0.05), mat_trim))
            parts.append(add_box(f"{name}_wsill_{floor_z}_{wx}", (wx, fy + 0.10, floor_z - 0.66), (1.22, 0.22, 0.09), mat_snow))

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
    """Real stylized 3D hatchback/SUV with beveled body, tinted windshields, 4 rubber wheels & alloy rims, headlights/taillights."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (0, 0, 0.0 if dir_sign >= 0 else math.pi)
    parts = [
        add_box(f"{name}_chassis", (0, 0, 0.56), (3.55, 1.68, 0.62), mat_body, bevel=0.09),
        add_box(f"{name}_bumperF", (1.78, 0, 0.36), (0.16, 1.66, 0.22), mat_tire, bevel=0.04),
        add_box(f"{name}_bumperR", (-1.78, 0, 0.36), (0.16, 1.66, 0.22), mat_tire, bevel=0.04),
        add_box(f"{name}_cabin", (-0.22, 0, 1.12), (1.95, 1.48, 0.58), mat_body, bevel=0.08),
        # Front & Rear sloped tinted windshields + side windows
        add_box(f"{name}_windF", (0.72, 0, 1.10), (0.12, 1.36, 0.48), mat_glass, rot=(0, math.radians(-28), 0)),
        add_box(f"{name}_windR", (-1.16, 0, 1.10), (0.12, 1.34, 0.46), mat_glass, rot=(0, math.radians(24), 0)),
        add_box(f"{name}_sideWin", (-0.22, 0, 1.12), (1.58, 1.51, 0.40), mat_glass),
        # Headlights & Red Taillights
        add_box(f"{name}_hlL", (1.79, 0.56, 0.60), (0.06, 0.32, 0.18), mat_head),
        add_box(f"{name}_hlR", (1.79, -0.56, 0.60), (0.06, 0.32, 0.18), mat_head),
        add_box(f"{name}_tlL", (-1.79, 0.56, 0.60), (0.06, 0.30, 0.18), mat_tail),
        add_box(f"{name}_tlR", (-1.79, -0.56, 0.60), (0.06, 0.30, 0.18), mat_tail),
    ]
    if mat_snow is not None:
        parts.append(add_box(f"{name}_roofSnow", (-0.22, 0, 1.44), (1.75, 1.34, 0.09), mat_snow, bevel=0.03))
    # 4 real rubber tires with metallic alloy rims!
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
    """Multi-branched layered Nordic spruce/pine with irregular snow-covered boughs (not 3 plain cones)."""
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
        # Crossed folding timber side rails & armrests
        add_box(f"{name}_legFL", (-0.42, -0.05, 0.48), (0.055, 1.15, 0.055), mat_wood, rot=(math.radians(52), 0, 0)),
        add_box(f"{name}_legFR", (0.42, -0.05, 0.48), (0.055, 1.15, 0.055), mat_wood, rot=(math.radians(52), 0, 0)),
        add_box(f"{name}_legBL", (-0.42, 0.05, 0.38), (0.055, 0.95, 0.055), mat_wood, rot=(math.radians(-40), 0, 0)),
        add_box(f"{name}_legBR", (0.42, 0.05, 0.38), (0.055, 0.95, 0.055), mat_wood, rot=(math.radians(-40), 0, 0)),
        add_box(f"{name}_armL", (-0.44, -0.04, 0.62), (0.08, 0.72, 0.045), mat_wood),
        add_box(f"{name}_armR", (0.44, -0.04, 0.62), (0.08, 0.72, 0.045), mat_wood),
        add_cylinder(f"{name}_topBar", (0, 0.32, 0.96), 0.032, 0.88, mat_wood, rot=(0, math.radians(90), 0), verts=10),
        add_cylinder(f"{name}_frontBar", (0, -0.40, 0.30), 0.032, 0.88, mat_wood, rot=(0, math.radians(90), 0), verts=10),
    ]
    # 7-stripe blue & white canvas sling backrest + seat
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
# 4. BAARLE REAL-REFERENCE ASSETS (ESPRESSO MACHINE, PASTRY CASE, OAK BAR, EDISON LAMP, BICYCLE, DUAL-FLAG HOUSE)
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
    """Commercial Italian café espresso machine: curved chrome chassis, cup rail, dual portafilters, steam wand & pressure dials."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    parts = [
        add_box(f"{name}_base", (0, 0, 0.05), (0.86, 0.56, 0.10), mat_dark, bevel=0.01),
        add_box(f"{name}_body", (0, 0.06, 0.32), (0.84, 0.44, 0.46), mat_chrome, bevel=0.03),
        add_box(f"{name}_topTray", (0, 0.06, 0.56), (0.82, 0.42, 0.03), mat_brass),
        # Drip grate tray in front
        add_box(f"{name}_drip", (0, -0.18, 0.08), (0.78, 0.18, 0.04), mat_chrome),
        # Top cup-warmer guard rails + stacked ceramic espresso cups
        add_box(f"{name}_railL", (-0.39, 0.06, 0.62), (0.02, 0.40, 0.08), mat_chrome),
        add_box(f"{name}_railR", (0.39, 0.06, 0.62), (0.02, 0.40, 0.08), mat_chrome),
        add_box(f"{name}_railB", (0, 0.25, 0.62), (0.80, 0.02, 0.08), mat_chrome),
    ]
    for cx in (-0.26, -0.10, 0.06, 0.22):
        parts.append(add_cylinder(f"{name}_topCup_{cx}", (cx, 0.08, 0.61), 0.042, 0.08, mat_white, verts=12))
    # Dual group-heads + brass portafilters + angled black handles!
    for gx in (-0.18, 0.18):
        parts.append(add_cylinder(f"{name}_grp_{gx}", (gx, -0.18, 0.34), 0.072, 0.11, mat_chrome, verts=14))
        parts.append(add_cylinder(f"{name}_pf_{gx}", (gx, -0.18, 0.26), 0.056, 0.06, mat_brass, verts=14))
        parts.append(add_cylinder(f"{name}_pfh_{gx}", (gx, -0.32, 0.24), 0.018, 0.20, mat_dark, rot=(math.radians(82), 0, 0), verts=10))
    # Angled stainless steam wand + brass steam knob
    parts.append(add_cylinder(f"{name}_knob", (-0.34, -0.17, 0.46), 0.032, 0.05, mat_brass, rot=(math.radians(90), 0, 0), verts=12))
    parts.append(add_cylinder(f"{name}_wand", (-0.34, -0.22, 0.26), 0.011, 0.28, mat_chrome, rot=(math.radians(24), math.radians(-16), 0), verts=8))
    # 2 circular white pressure-gauge dials with brass bezels!
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
    """Detailed glass café bakery vitrine with metal corner mullions, 2 trays, curved croissants & Dutch stroopwafels."""
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
    # Bottom tray: curved croissants (3 segmented crescent arcs each)
    for ci in range(4):
        cx = -0.34 + ci * 0.22
        parts.append(add_sphere(f"{name}_crM_{ci}", (cx, -0.02, 0.10), 0.055, mat_pastry, scale=(1.35, 0.78, 0.65), segments=10))
        parts.append(add_sphere(f"{name}_crL_{ci}", (cx - 0.06, -0.05, 0.09), 0.038, mat_pastry, scale=(1.1, 0.75, 0.65), segments=8))
        parts.append(add_sphere(f"{name}_crR_{ci}", (cx + 0.06, -0.05, 0.09), 0.038, mat_pastry, scale=(1.1, 0.75, 0.65), segments=8))
    # Top shelf: Dutch stroopwafel stacks & Belgian waffles
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
    """Classic Dutch city omafiets bicycle with torus rubber tires, spoked rims, tubular frame, handlebars & wicker basket."""
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
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    """Iconic real-reference Baarle-Nassau / Baarle-Hertog stepped-gable brick border house with dual NL & BE house plaques!"""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    # House front facade faces +Y (toward Café de Grens window at Y > -11.2)
    fy = 1.24
    parts = [
        # Dark limestone plinth + main textured Dutch red-brick facade
        add_box(f"{name}_plinth", (0, 0, 0.28), (6.9, 2.55, 0.56), mat_trim),
        add_box(f"{name}_body", (0, 0, 3.45), (6.8, 2.45, 6.2), mat_brick),
        # White limestone corner quoins
        add_box(f"{name}_quoinL", (-3.38, fy - 0.04, 3.45), (0.22, 0.14, 6.2), mat_trim),
        add_box(f"{name}_quoinR", (3.38, fy - 0.04, 3.45), (0.22, 0.14, 6.2), mat_trim),
    ]
    # Iconic 4-tier Dutch-Belgian stepped gable with crisp white limestone coping caps!
    for si, (sw, sz) in enumerate([(5.8, 6.95), (4.4, 7.75), (3.0, 8.55), (1.5, 9.35)]):
        parts.append(add_box(f"{name}_gable_{si}", (0, 1.02, sz), (sw, 0.42, 0.82), mat_brick))
        parts.append(add_box(f"{name}_cap_{si}", (0, 1.05, sz + 0.42), (sw + 0.18, 0.50, 0.10), mat_trim))

    # Recessed central dark-green wooden paneled front door with stone step, transom fanlight, brass handle & wall lantern!
    parts += [
        add_box(f"{name}_step", (0, fy + 0.22, 0.12), (1.95, 0.48, 0.24), mat_trim),
        add_box(f"{name}_doorCasing", (0, fy + 0.02, 1.56), (1.58, 0.16, 2.86), mat_trim),
        add_box(f"{name}_doorLeaf", (0, fy + 0.06, 1.32), (1.24, 0.10, 2.26), mat_door),
        add_box(f"{name}_doorPanelT", (0, fy + 0.12, 1.82), (0.86, 0.03, 0.72), mat_trim),
        add_box(f"{name}_doorPanelB", (0, fy + 0.12, 0.82), (0.86, 0.03, 0.72), mat_trim),
        # Brass door handle + letterbox slot
        add_sphere(f"{name}_knob", (0.44, fy + 0.16, 1.24), 0.055, mat_brass, segments=10),
        add_box(f"{name}_mailSlot", (0, fy + 0.14, 1.32), (0.34, 0.03, 0.07), mat_brass),
        # Transom fanlight glass above door + warm wall sconce lantern
        add_box(f"{name}_transom", (0, fy + 0.08, 2.66), (1.24, 0.06, 0.36), mat_curtain),
        add_box(f"{name}_lanternCap", (0, fy + 0.22, 3.16), (0.26, 0.26, 0.08), mat_brass),
        add_sphere(f"{name}_lanternGlow", (0, fy + 0.22, 3.04), 0.11, mat_lantern, segments=10),
    ]

    # TWO HUGE, CRISP, BRIGHTLY-LIT OFFICIAL DUAL-COUNTRY HOUSE PLAQUES!
    # Standing inside Café looking -Y -> screen LEFT is +X (Belgium 2!), screen RIGHT is -X (Netherlands 19!)
    # WAIT — VERIFY LEFT/RIGHT WHEN CAMERA LOOKS -Y!!
    # Camera at (0, -4.6) looking toward (0, -11.2) [direction = -Y]:
    # Camera UP = +Z; Camera RIGHT = (-Y) x (+Z) = (-1, 0, 0) = -X!! Camera LEFT = +X!!
    # OH!! THANK GOODNESS WE VERIFIED THAT CROSS PRODUCT!!
    # Screen LEFT (Belgia) = +X (+1.36); Screen RIGHT (Belanda) = -X (-1.36)!!
    parts += [
        add_box(f"{name}_plaqueBackB", (1.28, fy + 0.05, 2.02), (0.92, 0.06, 0.68), mat_trim),
        add_decal_plane(f"{name}_plaqueFaceB", (1.28, fy + 0.10, 2.02), 0.86, 0.62, (math.radians(90), 0, math.radians(180)), mat_plaque_b),
        add_box(f"{name}_plaqueBackNL", (-1.28, fy + 0.05, 2.02), (0.92, 0.06, 0.68), mat_trim),
        add_decal_plane(f"{name}_plaqueFaceNL", (-1.28, fy + 0.10, 2.02), 0.86, 0.62, (math.radians(90), 0, math.radians(180)), mat_plaque_nl),
    ]

    # 4 Authentic Recessed Multi-Pane Windows with White Frames, Sills & Soft Cream Curtains!
    win_coords = [(-2.45, 1.95), (2.45, 1.95), (-1.75, 4.55), (1.75, 4.55)]
    for wi, (wx, wz) in enumerate(win_coords):
        parts += [
            add_box(f"{name}_wf_{wi}", (wx, fy + 0.02, wz), (1.28, 0.14, 1.56), mat_trim),
            add_box(f"{name}_wg_{wi}", (wx, fy + 0.07, wz), (1.06, 0.05, 1.34), mat_glass),
            # Soft cream curtains inside edges of glass
            add_box(f"{name}_curtL_{wi}", (wx - 0.34, fy + 0.05, wz), (0.34, 0.04, 1.30), mat_curtain),
            add_box(f"{name}_curtR_{wi}", (wx + 0.34, fy + 0.05, wz), (0.34, 0.04, 1.30), mat_curtain),
            # Crisp white window cross mullions & stone sill
            add_box(f"{name}_mv_{wi}", (wx, fy + 0.11, wz), (0.06, 0.05, 1.36), mat_trim),
            add_box(f"{name}_mh_{wi}", (wx, fy + 0.11, wz + 0.14), (1.08, 0.05, 0.06), mat_trim),
            add_box(f"{name}_wsill_{wi}", (wx, fy + 0.12, wz - 0.78), (1.42, 0.24, 0.12), mat_trim),
        ]

    return _parent_all(parts, root, col)
