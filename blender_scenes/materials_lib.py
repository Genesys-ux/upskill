"""Blender 4.2 EEVEE Next Mid-Poly Cel-Shaded World-Space PBR Shader Library, 2.5D Hero/NPC Cards & Compositor (v2)."""
from __future__ import annotations

import math
import os
from typing import Any, Optional, Tuple

import bpy
from mathutils import Euler, Vector


def set_in(node: Any, name: str, val: Any) -> None:
    if name in node.inputs:
        node.inputs[name].default_value = val


def make_mix_rgba(nt: bpy.types.NodeTree, blend_type: str = "MIX", factor: float = 0.5, name: str = "") -> Tuple[Any, Any, Any, Any, Any]:
    """Blender 4.0-4.4 safe RGBA Mix node helper returning (node, fac_in, a_in, b_in, result_out)."""
    n = nt.nodes.new("ShaderNodeMix")
    if name:
        n.name = name
    n.data_type = "RGBA"
    n.blend_type = blend_type
    fac_in = n.inputs[0]
    rgba_ins = [inp for inp in n.inputs if inp.type == "RGBA"]
    rgba_outs = [out for out in n.outputs if out.type == "RGBA"]
    a_in = rgba_ins[0]
    b_in = rgba_ins[1]
    res_out = rgba_outs[0]
    fac_in.default_value = factor
    return n, fac_in, a_in, b_in, res_out


def set_mix_rgba_b(node: Any, color_rgba: Tuple[float, float, float, float]) -> None:
    rgba_ins = [inp for inp in node.inputs if inp.type == "RGBA"]
    if len(rgba_ins) >= 2:
        rgba_ins[1].default_value = color_rgba


def clear_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def get_or_create_collection(name: str) -> bpy.types.Collection:
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def link_to_collection(obj: bpy.types.Object, col: bpy.types.Collection) -> None:
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)


def configure_render_eevee(
    width: int = 720,
    height: int = 1280,
    fps: int = 30,
    samples: int = 8,
    use_motion_blur: bool = True,
) -> bpy.types.Scene:
    scene = bpy.context.scene
    engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"

    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 15

    ee = scene.eevee
    if hasattr(ee, "taa_render_samples"):
        ee.taa_render_samples = samples
    if hasattr(ee, "use_motion_blur"):
        ee.use_motion_blur = use_motion_blur
    if hasattr(ee, "motion_blur_shutter"):
        ee.motion_blur_shutter = 0.42
    if hasattr(ee, "motion_blur_steps"):
        ee.motion_blur_steps = 1
    if hasattr(ee, "use_volumetric_shadows"):
        ee.use_volumetric_shadows = False
    if hasattr(ee, "volumetric_tile_size"):
        ee.volumetric_tile_size = "8"
    if hasattr(ee, "volumetric_samples"):
        ee.volumetric_samples = 20
    if hasattr(ee, "volumetric_end"):
        ee.volumetric_end = 135.0
    if hasattr(ee, "shadow_resolution_scale"):
        ee.shadow_resolution_scale = 0.70 if width <= 720 else 0.90
    if hasattr(ee, "use_bloom"):
        ee.use_bloom = True
        ee.bloom_threshold = 2.0
        ee.bloom_intensity = 0.06
    if hasattr(ee, "use_raytracing"):
        ee.use_raytracing = False
    if hasattr(scene.render, "use_persistent_data"):
        scene.render.use_persistent_data = True

    scene.view_settings.view_transform = "AgX" if "AgX" in [
        v.identifier for v in scene.view_settings.bl_rna.properties["view_transform"].enum_items
    ] else "Filmic"
    if hasattr(scene.view_settings, "look"):
        looks = [l.identifier for l in scene.view_settings.bl_rna.properties["look"].enum_items]
        for preferred in ["AgX - Punchy", "AgX - Medium High Contrast", "Medium High Contrast", "None"]:
            if preferred in looks:
                scene.view_settings.look = preferred
                break
    scene.view_settings.exposure = 0.05

    # Controlled Compositor: Gentle Glare (prevents white-out on Rjukan!) + Crisp Transition Flash node
    scene.use_nodes = True
    nt = scene.node_tree
    nt.nodes.clear()
    n_rl = nt.nodes.new("CompositorNodeRLayers")
    n_glare = nt.nodes.new("CompositorNodeGlare")
    n_glare.glare_type = "FOG_GLOW"
    n_glare.quality = "MEDIUM"
    n_glare.threshold = 2.35  # High threshold keeps snow & 2.5D ink outlines razor sharp!
    n_glare.mix = -0.68
    n_glare.size = 6

    n_flash_col = nt.nodes.new("CompositorNodeRGB")
    n_flash_col.name = "TransitionFlashColor"
    n_flash_col.outputs[0].default_value = (1.0, 0.94, 0.78, 1.0)

    n_flash_mix = nt.nodes.new("CompositorNodeMixRGB")
    n_flash_mix.name = "TransitionFlashMix"
    n_flash_mix.blend_type = "MIX"
    n_flash_mix.inputs[0].default_value = 0.0

    n_out = nt.nodes.new("CompositorNodeComposite")
    nt.links.new(n_rl.outputs["Image"], n_glare.inputs["Image"])
    nt.links.new(n_glare.outputs["Image"], n_flash_mix.inputs[1])
    nt.links.new(n_flash_col.outputs["RGBA"], n_flash_mix.inputs[2])
    nt.links.new(n_flash_mix.outputs["Image"], n_out.inputs["Image"])
    return scene


def set_transition_flash(scene: bpy.types.Scene, strength: float, color: Tuple[float, float, float] = (1.0, 0.94, 0.76)) -> None:
    if not scene.use_nodes or not scene.node_tree:
        return
    mix_n = scene.node_tree.nodes.get("TransitionFlashMix")
    col_n = scene.node_tree.nodes.get("TransitionFlashColor")
    if col_n:
        col_n.outputs[0].default_value = (color[0], color[1], color[2], 1.0)
    if mix_n:
        mix_n.inputs[0].default_value = max(0.0, min(0.85, float(strength)))


# ============================================================================
# WORLD-SPACE PBR + CEL-SHADED SEMI-REALISTIC MATERIALS (NO STRETCHING!)
# ============================================================================

def make_cel_pbr_material(
    name: str,
    base_color: Tuple[float, float, float],
    shadow_tint: Tuple[float, float, float] = (0.28, 0.38, 0.58),
    roughness: float = 0.55,
    metallic: float = 0.0,
    bump_scale: float = 2.5,
    bump_strength: float = 0.20,
    pattern: str = "noise",  # noise | wood | brick | cobble | snow | water | metal
    color_b: Optional[Tuple[float, float, float]] = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    """Mid-poly Cel-Shaded Semi-Realistic material using World-Space Position so bricks/wood/cobble NEVER stretch."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    n_out = nt.nodes.new("ShaderNodeOutputMaterial")
    n_bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    # TRUE WORLD-SPACE COORDINATES (meters) so bricks & wood planks stay uniform on EVERY building/wall!
    n_geom = nt.nodes.new("ShaderNodeNewGeometry")
    n_map = nt.nodes.new("ShaderNodeMapping")
    nt.links.new(n_geom.outputs["Position"], n_map.inputs["Vector"])

    col2 = color_b or (base_color[0] * 0.76, base_color[1] * 0.76, base_color[2] * 0.78)
    n_bump = nt.nodes.new("ShaderNodeBump")
    n_bump.inputs["Strength"].default_value = bump_strength
    n_bump.inputs["Distance"].default_value = 0.035

    if pattern == "brick":
        # Project X+Y onto U and Z onto V so bricks wrap cleanly on ALL vertical walls (X-facing & Y-facing)!
        n_sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        n_add = nt.nodes.new("ShaderNodeMath")
        n_add.operation = "ADD"
        n_comb = nt.nodes.new("ShaderNodeCombineXYZ")
        nt.links.new(n_geom.outputs["Position"], n_sep.inputs["Vector"])
        nt.links.new(n_sep.outputs["X"], n_add.inputs[0])
        nt.links.new(n_sep.outputs["Y"], n_add.inputs[1])
        nt.links.new(n_add.outputs["Value"], n_comb.inputs["X"])
        nt.links.new(n_sep.outputs["Z"], n_comb.inputs["Y"])

        n_tex = nt.nodes.new("ShaderNodeTexBrick")
        n_tex.inputs["Scale"].default_value = max(1.2, bump_scale * 0.25)
        n_tex.inputs["Brick Width"].default_value = 0.42
        n_tex.inputs["Row Height"].default_value = 0.16
        n_tex.inputs["Mortar Size"].default_value = 0.018
        n_tex.inputs["Mortar Smooth"].default_value = 0.15
        n_tex.inputs["Color1"].default_value = (*base_color, 1.0)
        n_tex.inputs["Color2"].default_value = (*col2, 1.0)
        n_tex.inputs["Mortar"].default_value = (0.58, 0.54, 0.48, 1.0)
        nt.links.new(n_comb.outputs["Vector"], n_tex.inputs["Vector"])
        albedo_out = n_tex.outputs["Color"]
        height_out = n_tex.outputs["Fac"]
    elif pattern == "wood":
        n_map.inputs["Scale"].default_value = (0.8, 3.2, 1.8)
        n_tex = nt.nodes.new("ShaderNodeTexNoise")
        n_tex.inputs["Scale"].default_value = max(1.5, bump_scale * 0.35)
        n_tex.inputs["Detail"].default_value = 8.0
        n_tex.inputs["Distortion"].default_value = 1.6
        nt.links.new(n_map.outputs["Vector"], n_tex.inputs["Vector"])
        _, fac_i, a_i, b_i, res_o = make_mix_rgba(nt, "MIX", 0.5)
        a_i.default_value = (*col2, 1.0)
        b_i.default_value = (*base_color, 1.0)
        nt.links.new(n_tex.outputs["Fac"], fac_i)
        albedo_out = res_o
        height_out = n_tex.outputs["Fac"]
    elif pattern == "cobble":
        n_tex = nt.nodes.new("ShaderNodeTexVoronoi")
        n_tex.feature = "DISTANCE_TO_EDGE"
        n_tex.inputs["Scale"].default_value = max(2.2, bump_scale * 0.28)
        nt.links.new(n_map.outputs["Vector"], n_tex.inputs["Vector"])
        _, fac_i, a_i, b_i, res_o = make_mix_rgba(nt, "MIX", 0.5)
        a_i.default_value = (col2[0] * 0.60, col2[1] * 0.60, col2[2] * 0.64, 1.0)
        b_i.default_value = (*base_color, 1.0)
        nt.links.new(n_tex.outputs["Distance"], fac_i)
        albedo_out = res_o
        height_out = n_tex.outputs["Distance"]
    else:
        n_tex = nt.nodes.new("ShaderNodeTexNoise")
        n_tex.inputs["Scale"].default_value = max(0.8, bump_scale * 0.22)
        n_tex.inputs["Detail"].default_value = 6.0 if pattern != "water" else 4.0
        n_tex.inputs["Roughness"].default_value = 0.62
        nt.links.new(n_map.outputs["Vector"], n_tex.inputs["Vector"])
        _, fac_i, a_i, b_i, res_o = make_mix_rgba(nt, "MIX", 0.5)
        a_i.default_value = (*col2, 1.0)
        b_i.default_value = (*base_color, 1.0)
        nt.links.new(n_tex.outputs["Fac"], fac_i)
        albedo_out = res_o
        height_out = n_tex.outputs["Fac"]

    nt.links.new(height_out, n_bump.inputs["Height"])
    nt.links.new(albedo_out, n_bsdf.inputs["Base Color"])
    nt.links.new(n_bump.outputs["Normal"], n_bsdf.inputs["Normal"])

    n_rmap = nt.nodes.new("ShaderNodeMapRange")
    n_rmap.inputs["From Min"].default_value = 0.25
    n_rmap.inputs["From Max"].default_value = 0.78
    n_rmap.inputs["To Min"].default_value = max(0.06, roughness - 0.16)
    n_rmap.inputs["To Max"].default_value = min(0.96, roughness + 0.14)
    nt.links.new(height_out, n_rmap.inputs["Value"])
    nt.links.new(n_rmap.outputs["Result"], n_bsdf.inputs["Roughness"])

    set_in(n_bsdf, "Metallic", metallic)
    set_in(n_bsdf, "Specular IOR Level", 0.55 if pattern in ("water", "snow", "metal") else 0.42)
    if emission_strength > 0.0:
        set_in(n_bsdf, "Emission Color", (*base_color, 1.0))
        set_in(n_bsdf, "Emission Strength", emission_strength)

    if emission_strength > 0.5 or metallic > 0.78:
        nt.links.new(n_bsdf.outputs["BSDF"], n_out.inputs["Surface"])
    else:
        n_s2r = nt.nodes.new("ShaderNodeShaderToRGB")
        n_ramp = nt.nodes.new("ShaderNodeValToRGB")
        n_ramp.color_ramp.interpolation = "EASE"
        el0 = n_ramp.color_ramp.elements[0]
        el0.position = 0.08
        el0.color = (shadow_tint[0], shadow_tint[1], shadow_tint[2], 1.0)
        el1 = n_ramp.color_ramp.elements[1]
        el1.position = 0.50
        el1.color = (0.94, 0.94, 0.95, 1.0)
        el2 = n_ramp.color_ramp.elements.new(0.88)
        el2.color = (1.06, 1.04, 1.00, 1.0)

        _, _, m_a, m_b, m_res = make_mix_rgba(nt, "MULTIPLY", 0.85)
        _, _, b_a, b_b, b_res = make_mix_rgba(nt, "MIX", 0.62)

        n_emit = nt.nodes.new("ShaderNodeEmission")
        n_emit.inputs["Strength"].default_value = 1.0

        nt.links.new(n_bsdf.outputs["BSDF"], n_s2r.inputs["Shader"])
        nt.links.new(n_s2r.outputs["Color"], n_ramp.inputs["Fac"])
        nt.links.new(albedo_out, m_a)
        nt.links.new(n_ramp.outputs["Color"], m_b)
        nt.links.new(n_s2r.outputs["Color"], b_a)
        nt.links.new(m_res, b_b)
        nt.links.new(b_res, n_emit.inputs["Color"])
        nt.links.new(n_emit.outputs["Emission"], n_out.inputs["Surface"])

    return mat


def make_emissive_material(
    name: str,
    color: Tuple[float, float, float],
    strength: float = 3.0,
    alpha: float = 1.0,
) -> bpy.types.Material:
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    n_out = nt.nodes.new("ShaderNodeOutputMaterial")
    n_emit = nt.nodes.new("ShaderNodeEmission")
    n_emit.inputs["Color"].default_value = (*color, 1.0)
    n_emit.inputs["Strength"].default_value = strength
    if alpha < 0.99:
        n_trans = nt.nodes.new("ShaderNodeBsdfTransparent")
        n_mix = nt.nodes.new("ShaderNodeMixShader")
        n_mix.inputs["Fac"].default_value = alpha
        nt.links.new(n_trans.outputs["BSDF"], n_mix.inputs[1])
        nt.links.new(n_emit.outputs["Emission"], n_mix.inputs[2])
        nt.links.new(n_mix.outputs["Shader"], n_out.inputs["Surface"])
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = "BLENDED"
        elif hasattr(mat, "blend_method"):
            mat.blend_method = "BLEND"
    else:
        nt.links.new(n_emit.outputs["Emission"], n_out.inputs["Surface"])
    return mat


def make_soft_godray_material(
    name: str = "SoftVolumetricGodRay",
    color: Tuple[float, float, float] = (1.0, 0.84, 0.42),
    strength: float = 0.38,
    max_opacity: float = 0.28,
) -> bpy.types.Material:
    """Layer-Weight (Facing) feathered volumetric god-ray cone — soft golden glow with ZERO white-out or solid plastic edge!"""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    n_out = nt.nodes.new("ShaderNodeOutputMaterial")
    n_lw = nt.nodes.new("ShaderNodeLayerWeight")
    n_lw.inputs["Blend"].default_value = 0.35

    # Facing is 1.0 at grazing edges, 0.0 at center -> invert so edges fade cleanly to 0.0 transparent!
    n_ramp = nt.nodes.new("ShaderNodeValToRGB")
    n_ramp.color_ramp.interpolation = "EASE"
    el0 = n_ramp.color_ramp.elements[0]
    el0.position = 0.0
    el0.color = (max_opacity, max_opacity, max_opacity, 1.0)
    el1 = n_ramp.color_ramp.elements[1]
    el1.position = 0.72
    el1.color = (0.0, 0.0, 0.0, 1.0)

    n_trans = nt.nodes.new("ShaderNodeBsdfTransparent")
    n_emit = nt.nodes.new("ShaderNodeEmission")
    n_emit.inputs["Color"].default_value = (*color, 1.0)
    n_emit.inputs["Strength"].default_value = strength
    n_mix = nt.nodes.new("ShaderNodeMixShader")

    nt.links.new(n_lw.outputs["Facing"], n_ramp.inputs["Fac"])
    nt.links.new(n_ramp.outputs["Color"], n_mix.inputs["Fac"])
    nt.links.new(n_trans.outputs["BSDF"], n_mix.inputs[1])
    nt.links.new(n_emit.outputs["Emission"], n_mix.inputs[2])
    nt.links.new(n_mix.outputs["Shader"], n_out.inputs["Surface"])

    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "BLENDED"
    elif hasattr(mat, "blend_method"):
        mat.blend_method = "BLEND"
    return mat


def make_hologram_curtain_material(name: str = "ThinHoloDateLineCurtain") -> bpy.types.Material:
    """Thin, crisp translucent holographic International Date Line curtain (never opaque neon wall!)."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    n_out = nt.nodes.new("ShaderNodeOutputMaterial")
    n_geom = nt.nodes.new("ShaderNodeNewGeometry")
    n_wave = nt.nodes.new("ShaderNodeTexWave")
    n_wave.wave_type = "BANDS"
    n_wave.bands_direction = "Z"
    n_wave.inputs["Scale"].default_value = 3.5
    nt.links.new(n_geom.outputs["Position"], n_wave.inputs["Vector"])

    n_ramp = nt.nodes.new("ShaderNodeValToRGB")
    n_ramp.color_ramp.elements[0].position = 0.35
    n_ramp.color_ramp.elements[0].color = (0.03, 0.03, 0.03, 1.0)
    n_ramp.color_ramp.elements[1].position = 0.85
    n_ramp.color_ramp.elements[1].color = (0.16, 0.16, 0.16, 1.0)

    n_trans = nt.nodes.new("ShaderNodeBsdfTransparent")
    n_emit = nt.nodes.new("ShaderNodeEmission")
    n_emit.inputs["Color"].default_value = (1.0, 0.22, 0.16, 1.0)
    n_emit.inputs["Strength"].default_value = 3.5
    n_mix = nt.nodes.new("ShaderNodeMixShader")

    nt.links.new(n_wave.outputs["Fac"], n_ramp.inputs["Fac"])
    nt.links.new(n_ramp.outputs["Color"], n_mix.inputs["Fac"])
    nt.links.new(n_trans.outputs["BSDF"], n_mix.inputs[1])
    nt.links.new(n_emit.outputs["Emission"], n_mix.inputs[2])
    nt.links.new(n_mix.outputs["Shader"], n_out.inputs["Surface"])

    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "BLENDED"
    elif hasattr(mat, "blend_method"):
        mat.blend_method = "BLEND"
    return mat


def make_decal_material(
    name: str,
    image_path: str,
    emissive: float = 0.0,
    use_alpha: bool = False,
    roughness: float = 0.45,
) -> bpy.types.Material:
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    n_out = nt.nodes.new("ShaderNodeOutputMaterial")
    n_tex = nt.nodes.new("ShaderNodeTexImage")
    if os.path.exists(image_path):
        n_tex.image = bpy.data.images.load(image_path, check_existing=True)

    if emissive > 0.0 and use_alpha:
        n_emit = nt.nodes.new("ShaderNodeEmission")
        n_emit.inputs["Strength"].default_value = emissive
        n_trans = nt.nodes.new("ShaderNodeBsdfTransparent")
        n_mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(n_tex.outputs["Color"], n_emit.inputs["Color"])
        nt.links.new(n_tex.outputs["Alpha"], n_mix.inputs["Fac"])
        nt.links.new(n_trans.outputs["BSDF"], n_mix.inputs[1])
        nt.links.new(n_emit.outputs["Emission"], n_mix.inputs[2])
        nt.links.new(n_mix.outputs["Shader"], n_out.inputs["Surface"])
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = "BLENDED"
        elif hasattr(mat, "blend_method"):
            mat.blend_method = "BLEND"
    else:
        n_bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        set_in(n_bsdf, "Roughness", roughness)
        nt.links.new(n_tex.outputs["Color"], n_bsdf.inputs["Base Color"])
        if emissive > 0.0:
            nt.links.new(n_tex.outputs["Color"], n_bsdf.inputs["Emission Color"])
            set_in(n_bsdf, "Emission Strength", emissive)
        if use_alpha:
            nt.links.new(n_tex.outputs["Alpha"], n_bsdf.inputs["Alpha"])
            if hasattr(mat, "surface_render_method"):
                mat.surface_render_method = "BLENDED"
            elif hasattr(mat, "blend_method"):
                mat.blend_method = "BLEND"
        nt.links.new(n_bsdf.outputs["BSDF"], n_out.inputs["Surface"])
    return mat


# ============================================================================
# 2.5D HERO & UNIFIED BEAN-HEAD NPC CARDS (GROUND-ANCHORED AT FEET Z=0)
# ============================================================================

def create_character_card(
    char_id: str,
    height_m: float,
    initial_png_path: str,
    ambient_tint: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    col: Optional[bpy.types.Collection] = None,
) -> Tuple[bpy.types.Object, bpy.types.ShaderNodeTexImage, Any]:
    """Create 3D vertical 2.5D character card anchored precisely at feet baseline (y=478/520)."""
    width_m = height_m * (240.0 / 520.0)
    z_bottom = -height_m * (42.0 / 520.0)
    z_top = z_bottom + height_m
    hw = width_m * 0.5

    mesh = bpy.data.meshes.new(f"CharMesh_{char_id}")
    verts = [(-hw, 0.0, z_bottom), (hw, 0.0, z_bottom), (hw, 0.0, z_top), (-hw, 0.0, z_top)]
    faces = [(0, 1, 2, 3)]
    mesh.from_pydata(verts, [], faces)
    uv_layer = mesh.uv_layers.new(name="UVMap")
    uvs = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    for i, loop in enumerate(mesh.loops):
        uv_layer.data[i].uv = uvs[i]
    mesh.update()

    obj = bpy.data.objects.new(f"Char_{char_id}", mesh)
    (col or bpy.context.collection).objects.link(obj)

    mat = bpy.data.materials.new(name=f"CharMat_{char_id}")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    n_out = nt.nodes.new("ShaderNodeOutputMaterial")
    n_tex = nt.nodes.new("ShaderNodeTexImage")
    n_tex.name = "CharSpriteTex"
    n_tex.extension = "CLIP"
    if os.path.exists(initial_png_path):
        n_tex.image = bpy.data.images.load(initial_png_path, check_existing=True)

    n_tint, _, tint_a, tint_b, tint_res = make_mix_rgba(nt, "MULTIPLY", 1.0, name="SceneLightTint")
    tint_b.default_value = (*ambient_tint, 1.0)

    n_bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    set_in(n_bsdf, "Roughness", 0.85)
    set_in(n_bsdf, "Specular IOR Level", 0.10)
    n_s2r = nt.nodes.new("ShaderNodeShaderToRGB")

    # 80% crisp stylized sprite (protects dark outlines!) + 20% live directional shading
    _, _, lit_a, lit_b, lit_res = make_mix_rgba(nt, "MIX", 0.20)

    n_emit = nt.nodes.new("ShaderNodeEmission")
    n_emit.inputs["Strength"].default_value = 1.0

    n_trans = nt.nodes.new("ShaderNodeBsdfTransparent")
    n_alpha_mix = nt.nodes.new("ShaderNodeMixShader")

    nt.links.new(n_tex.outputs["Color"], tint_a)
    nt.links.new(tint_res, n_bsdf.inputs["Base Color"])
    nt.links.new(n_bsdf.outputs["BSDF"], n_s2r.inputs["Shader"])
    nt.links.new(tint_res, lit_a)
    nt.links.new(n_s2r.outputs["Color"], lit_b)
    nt.links.new(lit_res, n_emit.inputs["Color"])
    nt.links.new(n_tex.outputs["Alpha"], n_alpha_mix.inputs["Fac"])
    nt.links.new(n_trans.outputs["BSDF"], n_alpha_mix.inputs[1])
    nt.links.new(n_emit.outputs["Emission"], n_alpha_mix.inputs[2])
    nt.links.new(n_alpha_mix.outputs["Shader"], n_out.inputs["Surface"])

    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "DITHERED"
    elif hasattr(mat, "blend_method"):
        mat.blend_method = "HASHED"
    if hasattr(mat, "shadow_method"):
        mat.shadow_method = "HASHED"

    obj.data.materials.append(mat)
    return obj, n_tex, n_tint


# ============================================================================
# GEOMETRY, WORLD & CAMERA HELPERS
# ============================================================================

def add_box(
    name: str,
    loc: Tuple[float, float, float],
    scale: Tuple[float, float, float],
    mat: bpy.types.Material,
    rot: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel: float = 0.0,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if bevel > 0.0:
        mod = obj.modifiers.new(name="Bevel", type="BEVEL")
        mod.width = bevel
        mod.segments = 2
    obj.data.materials.append(mat)
    if col is not None:
        link_to_collection(obj, col)
    return obj


def add_cylinder(
    name: str,
    loc: Tuple[float, float, float],
    radius: float,
    depth: float,
    mat: bpy.types.Material,
    rot: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    verts: int = 16,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    if col is not None:
        link_to_collection(obj, col)
    return obj


def add_sphere(
    name: str,
    loc: Tuple[float, float, float],
    radius: float,
    mat: bpy.types.Material,
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    segments: int = 16,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=10, radius=radius, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    if col is not None:
        link_to_collection(obj, col)
    return obj


def add_decal_plane(
    name: str,
    loc: Tuple[float, float, float],
    width: float,
    height: float,
    rot: Tuple[float, float, float],
    mat: bpy.types.Material,
    col: Optional[bpy.types.Collection] = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (width, height, 1.0)
    obj.data.materials.append(mat)
    if col is not None:
        link_to_collection(obj, col)
    return obj


def setup_world_sky(
    zenith_color: Tuple[float, float, float],
    horizon_color: Tuple[float, float, float],
    strength: float = 0.8,
    haze_density: float = 0.003,
    haze_color: Tuple[float, float, float] = (0.55, 0.72, 0.90),
) -> bpy.types.World:
    world = bpy.data.worlds.new("StoryWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()

    n_out = nt.nodes.new("ShaderNodeOutputWorld")
    n_bg = nt.nodes.new("ShaderNodeBackground")
    n_bg.name = "WorldBG"
    n_bg.inputs["Strength"].default_value = strength

    n_tc = nt.nodes.new("ShaderNodeTexCoord")
    n_sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    n_ramp = nt.nodes.new("ShaderNodeValToRGB")
    n_ramp.color_ramp.elements[0].position = 0.0
    n_ramp.color_ramp.elements[0].color = (*horizon_color, 1.0)
    n_ramp.color_ramp.elements[1].position = 0.45
    n_ramp.color_ramp.elements[1].color = (*zenith_color, 1.0)

    nt.links.new(n_tc.outputs["Generated"], n_sep.inputs["Vector"])
    nt.links.new(n_sep.outputs["Z"], n_ramp.inputs["Fac"])
    nt.links.new(n_ramp.outputs["Color"], n_bg.inputs["Color"])
    nt.links.new(n_bg.outputs["Background"], n_out.inputs["Surface"])

    if haze_density > 0.0:
        n_vol = nt.nodes.new("ShaderNodeVolumeScatter")
        n_vol.name = "WorldHaze"
        n_vol.inputs["Color"].default_value = (*haze_color, 1.0)
        n_vol.inputs["Density"].default_value = haze_density
        n_vol.inputs["Anisotropy"].default_value = 0.55
        nt.links.new(n_vol.outputs["Volume"], n_out.inputs["Volume"])
    return world


def point_camera_at(cam_obj: bpy.types.Object, pos: Tuple[float, float, float], target: Tuple[float, float, float], lens: float, roll_deg: float) -> None:
    cam_obj.location = Vector(pos)
    direction = Vector(target) - Vector(pos)
    if direction.length < 1e-5:
        direction = Vector((0.0, 1.0, 0.0))
    rot_quat = direction.to_track_quat("-Z", "Y")
    roll_quat = Euler((0.0, 0.0, math.radians(roll_deg)), "XYZ").to_quaternion()
    cam_obj.rotation_mode = "QUATERNION"
    cam_obj.rotation_quaternion = rot_quat @ roll_quat
    cam_obj.data.lens = lens
