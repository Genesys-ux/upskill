"""Blender 4.2 EEVEE Next Mid-Poly Cel-Shaded World-Space PBR Shader Library (v3: Rich Shadows, Highlights, Alpine Cliffs & Lush Skies)."""
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
        ee.motion_blur_shutter = 0.38
    if hasattr(ee, "motion_blur_steps"):
        ee.motion_blur_steps = 1
    if hasattr(ee, "use_shadows"):
        ee.use_shadows = True
    if hasattr(ee, "shadow_resolution_scale"):
        ee.shadow_resolution_scale = 0.95 if width <= 720 else 1.0
    if hasattr(ee, "shadow_ray_count"):
        ee.shadow_ray_count = 2
    if hasattr(ee, "shadow_step_count"):
        ee.shadow_step_count = 6
    if hasattr(ee, "use_volumetric_shadows"):
        ee.use_volumetric_shadows = False
    if hasattr(ee, "use_bloom"):
        ee.use_bloom = True
        ee.bloom_threshold = 2.1
        ee.bloom_intensity = 0.08
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
    scene.view_settings.exposure = 0.08

    # Controlled Compositor: Crisp specular/lantern glow (protects outlines!) + short transition flash node
    scene.use_nodes = True
    nt = scene.node_tree
    nt.nodes.clear()
    n_rl = nt.nodes.new("CompositorNodeRLayers")
    n_glare = nt.nodes.new("CompositorNodeGlare")
    n_glare.glare_type = "FOG_GLOW"
    n_glare.quality = "MEDIUM"
    n_glare.threshold = 2.20
    n_glare.mix = -0.62
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
# WORLD-SPACE PBR + CEL-SHADED MATERIALS (CRISP BLUE SHADOWS + WARM HIGHLIGHTS!)
# ============================================================================

def make_cel_pbr_material(
    name: str,
    base_color: Tuple[float, float, float],
    shadow_tint: Tuple[float, float, float] = (0.18, 0.28, 0.50),
    roughness: float = 0.45,
    metallic: float = 0.0,
    bump_scale: float = 2.5,
    bump_strength: float = 0.24,
    pattern: str = "noise",  # noise | wood | brick | cobble | snow | water | metal | clapboard
    color_b: Optional[Tuple[float, float, float]] = None,
    emission_strength: float = 0.0,
    rim_strength: float = 0.20,
    highlight_tint: Tuple[float, float, float] = (1.18, 1.13, 1.04),
) -> bpy.types.Material:
    """Mid-poly Cel-Shaded Semi-Realistic material with crisp cast shadows, rich blue-shade shadows & sunlit rim highlights."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    n_out = nt.nodes.new("ShaderNodeOutputMaterial")
    n_bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    n_geom = nt.nodes.new("ShaderNodeNewGeometry")
    n_map = nt.nodes.new("ShaderNodeMapping")
    nt.links.new(n_geom.outputs["Position"], n_map.inputs["Vector"])

    col2 = color_b or (base_color[0] * 0.72, base_color[1] * 0.72, base_color[2] * 0.75)
    n_bump = nt.nodes.new("ShaderNodeBump")
    n_bump.inputs["Strength"].default_value = bump_strength
    n_bump.inputs["Distance"].default_value = 0.04

    if pattern == "brick":
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
        n_tex.inputs["Scale"].default_value = max(1.2, bump_scale * 0.26)
        n_tex.inputs["Brick Width"].default_value = 0.42
        n_tex.inputs["Row Height"].default_value = 0.16
        n_tex.inputs["Mortar Size"].default_value = 0.018
        n_tex.inputs["Mortar Smooth"].default_value = 0.12
        n_tex.inputs["Color1"].default_value = (*base_color, 1.0)
        n_tex.inputs["Color2"].default_value = (*col2, 1.0)
        n_tex.inputs["Mortar"].default_value = (0.64, 0.60, 0.54, 1.0)
        nt.links.new(n_comb.outputs["Vector"], n_tex.inputs["Vector"])
        albedo_out = n_tex.outputs["Color"]
        height_out = n_tex.outputs["Fac"]
    elif pattern == "clapboard":
        # Authentic horizontal Norwegian timber planks (real Rjukan Torg architecture!)
        n_wave = nt.nodes.new("ShaderNodeTexWave")
        n_wave.wave_type = "BANDS"
        n_wave.bands_direction = "Z"
        n_wave.wave_profile = "SAW"
        n_wave.inputs["Scale"].default_value = max(2.0, bump_scale * 0.65)
        n_wave.inputs["Distortion"].default_value = 0.35
        nt.links.new(n_map.outputs["Vector"], n_wave.inputs["Vector"])
        _, fac_i, a_i, b_i, res_o = make_mix_rgba(nt, "MIX", 0.5)
        a_i.default_value = (*col2, 1.0)
        b_i.default_value = (*base_color, 1.0)
        nt.links.new(n_wave.outputs["Fac"], fac_i)
        albedo_out = res_o
        height_out = n_wave.outputs["Fac"]
    elif pattern == "wood":
        n_map.inputs["Scale"].default_value = (0.8, 3.4, 1.8)
        n_tex = nt.nodes.new("ShaderNodeTexNoise")
        n_tex.inputs["Scale"].default_value = max(1.6, bump_scale * 0.38)
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
        n_tex.inputs["Scale"].default_value = max(2.4, bump_scale * 0.30)
        nt.links.new(n_map.outputs["Vector"], n_tex.inputs["Vector"])
        _, fac_i, a_i, b_i, res_o = make_mix_rgba(nt, "MIX", 0.5)
        a_i.default_value = (col2[0] * 0.55, col2[1] * 0.55, col2[2] * 0.60, 1.0)
        b_i.default_value = (*base_color, 1.0)
        nt.links.new(n_tex.outputs["Distance"], fac_i)
        albedo_out = res_o
        height_out = n_tex.outputs["Distance"]
    else:
        n_tex = nt.nodes.new("ShaderNodeTexNoise")
        n_tex.inputs["Scale"].default_value = max(0.8, bump_scale * 0.25)
        n_tex.inputs["Detail"].default_value = 7.0 if pattern != "water" else 4.0
        n_tex.inputs["Roughness"].default_value = 0.64
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
    n_rmap.inputs["From Min"].default_value = 0.22
    n_rmap.inputs["From Max"].default_value = 0.78
    n_rmap.inputs["To Min"].default_value = max(0.06, roughness - 0.18)
    n_rmap.inputs["To Max"].default_value = min(0.92, roughness + 0.12)
    nt.links.new(height_out, n_rmap.inputs["Value"])
    nt.links.new(n_rmap.outputs["Result"], n_bsdf.inputs["Roughness"])

    set_in(n_bsdf, "Metallic", metallic)
    set_in(n_bsdf, "Specular IOR Level", 0.72 if pattern in ("water", "snow", "metal") else 0.56)
    if emission_strength > 0.0:
        set_in(n_bsdf, "Emission Color", (*base_color, 1.0))
        set_in(n_bsdf, "Emission Strength", emission_strength)

    if emission_strength > 0.5 or metallic > 0.75:
        nt.links.new(n_bsdf.outputs["BSDF"], n_out.inputs["Surface"])
    else:
        # 3-BAND CINEMATIC CEL-SHADE WITH REAL SHADOW CONTRAST, SPECULAR & SUNLIT FRESNEL RIM HIGHLIGHT!
        n_s2r = nt.nodes.new("ShaderNodeShaderToRGB")
        n_lum = nt.nodes.new("ShaderNodeRGBToBW")
        n_ramp = nt.nodes.new("ShaderNodeValToRGB")
        n_ramp.color_ramp.interpolation = "EASE"

        # Band 0: Deep rich cool blue-violet shadow (clearly differentiates cast shadows & shadow faces!)
        el0 = n_ramp.color_ramp.elements[0]
        el0.position = 0.04
        el0.color = (shadow_tint[0] * 0.78, shadow_tint[1] * 0.85, min(1.0, shadow_tint[2] * 1.10), 1.0)
        # Band 1: Shadow terminator transition
        el1 = n_ramp.color_ramp.elements[1]
        el1.position = 0.26
        el1.color = (0.86, 0.88, 0.92, 1.0)
        # Band 2: Sunlit key face
        el2 = n_ramp.color_ramp.elements.new(0.62)
        el2.color = (1.04, 1.02, 0.98, 1.0)
        # Band 3: Crisp warm specular highlight band!
        el3 = n_ramp.color_ramp.elements.new(0.86)
        el3.color = (highlight_tint[0], highlight_tint[1], highlight_tint[2], 1.0)

        # Multiply albedo by 3-band lighting ramp, then blend 55% cel + 45% live PBR specular/shadow!
        _, _, m_a, m_b, m_res = make_mix_rgba(nt, "MULTIPLY", 0.92)
        _, _, b_a, b_b, b_res = make_mix_rgba(nt, "MIX", 0.56)

        # Add subtle Fresnel sunlit rim highlight modulated by live lighting (dark in shadows, crisp bright rim in sun!)
        n_lw = nt.nodes.new("ShaderNodeLayerWeight")
        n_lw.inputs["Blend"].default_value = 0.22
        n_rim_ramp = nt.nodes.new("ShaderNodeValToRGB")
        n_rim_ramp.color_ramp.elements[0].position = 0.58
        n_rim_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
        n_rim_ramp.color_ramp.elements[1].position = 0.90
        n_rim_ramp.color_ramp.elements[1].color = (rim_strength, rim_strength, rim_strength, 1.0)
        n_rim_gate = nt.nodes.new("ShaderNodeMath")
        n_rim_gate.operation = "MULTIPLY"
        _, rim_fac, rim_a, rim_b, rim_res = make_mix_rgba(nt, "ADD", 0.0)
        rim_b.default_value = (highlight_tint[0] * 0.72, highlight_tint[1] * 0.70, highlight_tint[2] * 0.65, 1.0)

        n_emit = nt.nodes.new("ShaderNodeEmission")
        n_emit.inputs["Strength"].default_value = 1.0

        nt.links.new(n_bsdf.outputs["BSDF"], n_s2r.inputs["Shader"])
        nt.links.new(n_s2r.outputs["Color"], n_lum.inputs["Color"])
        nt.links.new(n_lum.outputs["Val"], n_ramp.inputs["Fac"])
        nt.links.new(albedo_out, m_a)
        nt.links.new(n_ramp.outputs["Color"], m_b)
        nt.links.new(n_s2r.outputs["Color"], b_a)
        nt.links.new(m_res, b_b)

        nt.links.new(n_lw.outputs["Facing"], n_rim_ramp.inputs["Fac"])
        nt.links.new(n_rim_ramp.outputs["Color"], n_rim_gate.inputs[0])
        nt.links.new(n_lum.outputs["Val"], n_rim_gate.inputs[1])
        nt.links.new(n_rim_gate.outputs["Value"], rim_fac)
        nt.links.new(b_res, rim_a)
        nt.links.new(rim_res, n_emit.inputs["Color"])
        nt.links.new(n_emit.outputs["Emission"], n_out.inputs["Surface"])

    return mat


def make_snowy_cliff_material(
    name: str = "NorwegianAlpineCliff",
    rock_light: Tuple[float, float, float] = (0.34, 0.40, 0.50),
    rock_dark: Tuple[float, float, float] = (0.16, 0.21, 0.30),
    snow_color: Tuple[float, float, float] = (0.86, 0.92, 0.99),
    snow_slope_threshold: float = 0.54,
) -> bpy.types.Material:
    """Rich textured Norwegian / Arctic granite cliff with fractured rock strata + automatic snow on ledges!"""
    if name in bpy.data.materials:
        return bpy.data.materials[name]

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    n_out = nt.nodes.new("ShaderNodeOutputMaterial")
    n_bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    n_geom = nt.nodes.new("ShaderNodeNewGeometry")

    # 1. Fractured rocky granite strata (Voronoi crevices + ridged multi-scale Noise)
    n_map_rock = nt.nodes.new("ShaderNodeMapping")
    n_map_rock.inputs["Scale"].default_value = (0.28, 0.28, 0.52)
    nt.links.new(n_geom.outputs["Position"], n_map_rock.inputs["Vector"])

    n_vor = nt.nodes.new("ShaderNodeTexVoronoi")
    n_vor.feature = "DISTANCE_TO_EDGE"
    n_vor.inputs["Scale"].default_value = 1.6
    nt.links.new(n_map_rock.outputs["Vector"], n_vor.inputs["Vector"])

    n_noise = nt.nodes.new("ShaderNodeTexNoise")
    n_noise.inputs["Scale"].default_value = 0.95
    n_noise.inputs["Detail"].default_value = 9.0
    n_noise.inputs["Roughness"].default_value = 0.68
    nt.links.new(n_map_rock.outputs["Vector"], n_noise.inputs["Vector"])

    n_rock_h = nt.nodes.new("ShaderNodeMath")
    n_rock_h.operation = "MULTIPLY_ADD"
    n_rock_h.inputs[1].default_value = 0.55
    nt.links.new(n_vor.outputs["Distance"], n_rock_h.inputs[0])
    nt.links.new(n_noise.outputs["Fac"], n_rock_h.inputs[2])

    _, rock_fac, rock_a, rock_b, rock_col = make_mix_rgba(nt, "MIX", 0.5)
    rock_a.default_value = (*rock_dark, 1.0)
    rock_b.default_value = (*rock_light, 1.0)
    nt.links.new(n_rock_h.outputs["Value"], rock_fac)

    # 2. Automatic alpine snow accumulation on upward-facing ledges (Normal.Z + noise breakup)
    n_sep_n = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(n_geom.outputs["Normal"], n_sep_n.inputs["Vector"])

    n_snow_mix_v = nt.nodes.new("ShaderNodeMath")
    n_snow_mix_v.operation = "ADD"
    n_noise_snow = nt.nodes.new("ShaderNodeMath")
    n_noise_snow.operation = "MULTIPLY"
    n_noise_snow.inputs[1].default_value = 0.28
    nt.links.new(n_noise.outputs["Fac"], n_noise_snow.inputs[0])
    nt.links.new(n_sep_n.outputs["Z"], n_snow_mix_v.inputs[0])
    nt.links.new(n_noise_snow.outputs["Value"], n_snow_mix_v.inputs[1])

    n_snow_ramp = nt.nodes.new("ShaderNodeValToRGB")
    n_snow_ramp.color_ramp.elements[0].position = max(0.15, snow_slope_threshold - 0.08)
    n_snow_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    n_snow_ramp.color_ramp.elements[1].position = min(0.95, snow_slope_threshold + 0.14)
    n_snow_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(n_snow_mix_v.outputs["Value"], n_snow_ramp.inputs["Fac"])

    _, sn_fac, sn_a, sn_b, final_albedo = make_mix_rgba(nt, "MIX", 0.0)
    sn_b.default_value = (*snow_color, 1.0)
    nt.links.new(n_snow_ramp.outputs["Color"], sn_fac)
    nt.links.new(rock_col, sn_a)

    # Strong rocky bump normal + subtle cool ambient glow so cliff NEVER crushes to pure black!
    n_bump = nt.nodes.new("ShaderNodeBump")
    n_bump.inputs["Strength"].default_value = 0.62
    n_bump.inputs["Distance"].default_value = 0.18
    nt.links.new(n_rock_h.outputs["Value"], n_bump.inputs["Height"])

    nt.links.new(final_albedo, n_bsdf.inputs["Base Color"])
    nt.links.new(n_bump.outputs["Normal"], n_bsdf.inputs["Normal"])
    set_in(n_bsdf, "Roughness", 0.68)
    set_in(n_bsdf, "Specular IOR Level", 0.45)

    # Cel-tinted live lighting + minimum 24% atmospheric fill so granite rock detail is ALWAYS visible!
    n_s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    _, _, amb_a, amb_b, amb_res = make_mix_rgba(nt, "MULTIPLY", 1.0)
    amb_b.default_value = (0.36, 0.46, 0.68, 1.0)
    _, _, out_a, out_b, out_col = make_mix_rgba(nt, "ADD", 0.32)
    n_emit = nt.nodes.new("ShaderNodeEmission")
    n_emit.inputs["Strength"].default_value = 1.0

    nt.links.new(n_bsdf.outputs["BSDF"], n_s2r.inputs["Shader"])
    nt.links.new(final_albedo, amb_a)
    nt.links.new(n_s2r.outputs["Color"], out_a)
    nt.links.new(amb_res, out_b)
    nt.links.new(out_col, n_emit.inputs["Color"])
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
    color: Tuple[float, float, float] = (1.0, 0.86, 0.42),
    strength: float = 0.24,
    max_opacity: float = 0.28,
) -> bpy.types.Material:
    """Silky pure ADDITIVE golden volumetric god-ray cone (ZERO muddy grey/brown darkening, ZERO white-out!)."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    n_out = nt.nodes.new("ShaderNodeOutputMaterial")
    n_lw = nt.nodes.new("ShaderNodeLayerWeight")
    n_lw.inputs["Blend"].default_value = 0.40

    # Facing=0 at center -> bright feather; Facing->1 at grazing cone edges -> 0.0 completely invisible edge!
    n_ramp = nt.nodes.new("ShaderNodeValToRGB")
    n_ramp.color_ramp.interpolation = "EASE"
    n_ramp.color_ramp.elements[0].position = 0.0
    n_ramp.color_ramp.elements[0].color = (strength, strength, strength, 1.0)
    n_ramp.color_ramp.elements[1].position = 0.68
    n_ramp.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0)

    n_trans = nt.nodes.new("ShaderNodeBsdfTransparent")
    n_emit = nt.nodes.new("ShaderNodeEmission")
    n_emit.inputs["Color"].default_value = (*color, 1.0)

    # Pure Additive Shader (Transparent + feathered Emission) = true glowing golden sunbeam with ZERO muddiness!
    n_add = nt.nodes.new("ShaderNodeAddShader")

    nt.links.new(n_lw.outputs["Facing"], n_ramp.inputs["Fac"])
    nt.links.new(n_ramp.outputs["Color"], n_emit.inputs["Strength"])
    nt.links.new(n_trans.outputs["BSDF"], n_add.inputs[0])
    nt.links.new(n_emit.outputs["Emission"], n_add.inputs[1])
    nt.links.new(n_add.outputs["Shader"], n_out.inputs["Surface"])

    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "BLENDED"
    elif hasattr(mat, "blend_method"):
        mat.blend_method = "BLEND"
    return mat


def make_hologram_curtain_material(name: str = "ThinHoloDateLineCurtain") -> bpy.types.Material:
    """Ultra-sheer additive holographic International Date Line veil — Big Diomede & sky stay 100% visible behind it!"""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    n_out = nt.nodes.new("ShaderNodeOutputMaterial")
    n_geom = nt.nodes.new("ShaderNodeNewGeometry")
    n_sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(n_geom.outputs["Position"], n_sep.inputs["Vector"])

    # Height fade: subtle glow near water (Z=0..6m), fades cleanly to 0 above Z=8m!
    n_hmap = nt.nodes.new("ShaderNodeMapRange")
    n_hmap.inputs["From Min"].default_value = 0.5
    n_hmap.inputs["From Max"].default_value = 8.5
    n_hmap.inputs["To Min"].default_value = 0.16
    n_hmap.inputs["To Max"].default_value = 0.0
    n_hmap.clamp = True
    nt.links.new(n_sep.outputs["Z"], n_hmap.inputs["Value"])

    # Fine vertical holographic scan-bars
    n_wave = nt.nodes.new("ShaderNodeTexWave")
    n_wave.wave_type = "BANDS"
    n_wave.bands_direction = "X"
    n_wave.inputs["Scale"].default_value = 1.4
    nt.links.new(n_geom.outputs["Position"], n_wave.inputs["Vector"])

    n_mult = nt.nodes.new("ShaderNodeMath")
    n_mult.operation = "MULTIPLY"
    nt.links.new(n_hmap.outputs["Result"], n_mult.inputs[0])
    nt.links.new(n_wave.outputs["Fac"], n_mult.inputs[1])

    n_trans = nt.nodes.new("ShaderNodeBsdfTransparent")
    n_emit = nt.nodes.new("ShaderNodeEmission")
    n_emit.inputs["Color"].default_value = (0.32, 0.88, 1.0, 1.0)  # Crisp icy-cyan holo glow!
    n_add = nt.nodes.new("ShaderNodeAddShader")

    nt.links.new(n_mult.outputs["Value"], n_emit.inputs["Strength"])
    nt.links.new(n_trans.outputs["BSDF"], n_add.inputs[0])
    nt.links.new(n_emit.outputs["Emission"], n_add.inputs[1])
    nt.links.new(n_add.outputs["Shader"], n_out.inputs["Surface"])

    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "BLENDED"
    elif hasattr(mat, "blend_method"):
        mat.blend_method = "BLEND"
    return mat


def make_contact_shadow_material(name: str = "SoftContactShadow", opacity: float = 0.42) -> bpy.types.Material:
    """Soft radial ground contact shadow disc anchoring every 2.5D character and prop solidly to the ground."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    n_out = nt.nodes.new("ShaderNodeOutputMaterial")
    n_tc = nt.nodes.new("ShaderNodeTexCoord")
    n_grad = nt.nodes.new("ShaderNodeTexGradient")
    n_grad.gradient_type = "QUADRATIC_SPHERE"
    n_map = nt.nodes.new("ShaderNodeMapping")
    n_map.inputs["Location"].default_value = (-1.0, -1.0, 0.0)
    n_map.inputs["Scale"].default_value = (2.0, 2.0, 1.0)
    nt.links.new(n_tc.outputs["UV"], n_map.inputs["Vector"])
    nt.links.new(n_map.outputs["Vector"], n_grad.inputs["Vector"])

    n_mul = nt.nodes.new("ShaderNodeMath")
    n_mul.operation = "MULTIPLY"
    n_mul.inputs[1].default_value = opacity
    nt.links.new(n_grad.outputs["Fac"], n_mul.inputs[0])

    n_trans = nt.nodes.new("ShaderNodeBsdfTransparent")
    n_dark = nt.nodes.new("ShaderNodeEmission")
    n_dark.inputs["Color"].default_value = (0.04, 0.07, 0.16, 1.0)  # Cool blue-shade contact shadow!
    n_dark.inputs["Strength"].default_value = 0.08
    n_mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(n_mul.outputs["Value"], n_mix.inputs["Fac"])
    nt.links.new(n_trans.outputs["BSDF"], n_mix.inputs[1])
    nt.links.new(n_dark.outputs["Emission"], n_mix.inputs[2])
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
    roughness: float = 0.42,
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
# 2.5D HERO & UNIFIED BEAN-HEAD NPC CARDS (WITH LIVE GROUNDED CONTACT SHADOW!)
# ============================================================================

def create_character_card(
    char_id: str,
    height_m: float,
    initial_png_path: str,
    ambient_tint: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    col: Optional[bpy.types.Collection] = None,
    with_contact_shadow: bool = True,
) -> Tuple[bpy.types.Object, bpy.types.ShaderNodeTexImage, Any]:
    """Create 3D vertical 2.5D character card anchored at feet baseline (y=478/520) + soft blue-shade contact shadow!"""
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
    set_in(n_bsdf, "Roughness", 0.72)
    set_in(n_bsdf, "Specular IOR Level", 0.22)
    n_s2r = nt.nodes.new("ShaderNodeShaderToRGB")

    # 76% crisp stylized sprite (protects dark outlines!) + 24% live directional highlight/shadow
    _, _, lit_a, lit_b, lit_res = make_mix_rgba(nt, "MIX", 0.24)

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

    if with_contact_shadow:
        sh_mat = make_contact_shadow_material()
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, 0.0, 0.014))
        sh = bpy.context.active_object
        sh.name = f"CharShadow_{char_id}"
        sh.scale = (width_m * 1.15, width_m * 0.72, 1.0)
        sh.data.materials.append(sh_mat)
        sh.visible_shadow = False
        sh.parent = obj
        if col is not None:
            link_to_collection(sh, col)

    return obj, n_tex, n_tint


# ============================================================================
# GEOMETRY, LUSH GRADIENT SKY & CAMERA HELPERS
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
    strength: float = 0.85,
    mid_color: Optional[Tuple[float, float, float]] = None,
    haze_density: float = 0.0,  # Kept 0 on World Volume in EEVEE Next so infinite sky NEVER turns pitch black!
    haze_color: Tuple[float, float, float] = (0.55, 0.72, 0.90),
) -> bpy.types.World:
    """Lush multi-stop atmospheric World Sky that NEVER renders pitch black in Blender 4.2 EEVEE Next."""
    world = bpy.data.worlds.new("StoryWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()

    n_out = nt.nodes.new("ShaderNodeOutputWorld")
    n_bg = nt.nodes.new("ShaderNodeBackground")
    n_bg.name = "WorldBG"
    n_bg.inputs["Strength"].default_value = strength

    # Generated.Z is [-1..+1] (0 at horizon, +1 at zenith) -> remap [-0.05..0.55] -> [0..1] for vivid horizon-to-zenith gradient!
    n_tc = nt.nodes.new("ShaderNodeTexCoord")
    n_sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    n_mapr = nt.nodes.new("ShaderNodeMapRange")
    n_mapr.inputs["From Min"].default_value = -0.04
    n_mapr.inputs["From Max"].default_value = 0.58
    n_mapr.inputs["To Min"].default_value = 0.0
    n_mapr.inputs["To Max"].default_value = 1.0
    n_mapr.clamp = True

    mid = mid_color or (
        (horizon_color[0] + zenith_color[0]) * 0.52,
        (horizon_color[1] + zenith_color[1]) * 0.54,
        (horizon_color[2] + zenith_color[2]) * 0.58,
    )
    n_ramp = nt.nodes.new("ShaderNodeValToRGB")
    n_ramp.color_ramp.interpolation = "EASE"
    n_ramp.color_ramp.elements[0].position = 0.0
    n_ramp.color_ramp.elements[0].color = (*horizon_color, 1.0)
    n_ramp.color_ramp.elements[1].position = 1.0
    n_ramp.color_ramp.elements[1].color = (*zenith_color, 1.0)
    el_m = n_ramp.color_ramp.elements.new(0.36)
    el_m.color = (*mid, 1.0)

    # Subtle wispy cloud texture blended into upper sky for true atmospheric depth!
    n_cnoise = nt.nodes.new("ShaderNodeTexNoise")
    n_cnoise.inputs["Scale"].default_value = 3.6
    n_cnoise.inputs["Detail"].default_value = 5.0
    n_cnoise.inputs["Roughness"].default_value = 0.55
    n_cmap = nt.nodes.new("ShaderNodeMapping")
    n_cmap.inputs["Scale"].default_value = (1.0, 1.0, 3.8)
    nt.links.new(n_tc.outputs["Generated"], n_cmap.inputs["Vector"])
    nt.links.new(n_cmap.outputs["Vector"], n_cnoise.inputs["Vector"])

    n_cramp = nt.nodes.new("ShaderNodeValToRGB")
    n_cramp.color_ramp.elements[0].position = 0.56
    n_cramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    n_cramp.color_ramp.elements[1].position = 0.80
    n_cramp.color_ramp.elements[1].color = (0.28, 0.28, 0.28, 1.0)
    nt.links.new(n_cnoise.outputs["Fac"], n_cramp.inputs["Fac"])

    _, c_fac, c_a, c_b, c_res = make_mix_rgba(nt, "MIX", 0.0)
    c_b.default_value = (
        min(1.0, horizon_color[0] * 1.15 + 0.14),
        min(1.0, horizon_color[1] * 1.15 + 0.14),
        min(1.0, horizon_color[2] * 1.12 + 0.16),
        1.0,
    )

    nt.links.new(n_tc.outputs["Generated"], n_sep.inputs["Vector"])
    nt.links.new(n_sep.outputs["Z"], n_mapr.inputs["Value"])
    nt.links.new(n_mapr.outputs["Result"], n_ramp.inputs["Fac"])
    nt.links.new(n_cramp.outputs["Color"], c_fac)
    nt.links.new(n_ramp.outputs["Color"], c_a)
    nt.links.new(c_res, n_bg.inputs["Color"])
    nt.links.new(n_bg.outputs["Background"], n_out.inputs["Surface"])
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
