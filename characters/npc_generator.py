"""Unified 2.5D Bean-Head NPC Generator (v3: 18 Distinct Living Background NPCs using exact Character25D engine)."""
from __future__ import annotations

import os
import sys
from typing import Any, Dict, List

CHAR_DIR = os.path.dirname(os.path.abspath(__file__))
if CHAR_DIR not in sys.path:
    sys.path.insert(0, CHAR_DIR)

from character_engine_25d import Character25D, DEFAULT_CONFIG

# 18 distinct background NPCs matching exact 2.5D bean-head thick-outline studio style (5 Diomede, 6 Rjukan, 7 Baarle)
NPC_ROSTER: Dict[str, List[Dict[str, Any]]] = {
    "diomede": [
        {
            "id": "npc_dio_1", "height": 1.84,
            "config": {
                **DEFAULT_CONFIG, "name": "Nelayan Diomede 1",
                "headShape": "wide", "ears": True, "skinColor": "#E5B89B", "blush": True, "blushColor": "#CA8274",
                "eyes": "chill", "eyebrows": "flat", "nose": "upturned_tiny", "mouth": "smirk", "beard": "stubble",
                "hat": "beanie", "hatPrimary": "#2E4057", "hatAccent": "#E09F3E", "backHair": "short", "hairColor": "#3A2D28",
                "outfit": "safari_explorer", "robeColor": "#284B63", "innerColor": "#D9D9D9", "sashColor": "#1F2933", "trimColor": "#E09F3E",
                "beltStyle": "buckle", "cape": "none", "pose": "ready", "limbColor": "#22262E",
            },
        },
        {
            "id": "npc_dio_2", "height": 1.78,
            "config": {
                **DEFAULT_CONFIG, "name": "Nelayan Diomede 2",
                "headShape": "round", "ears": True, "skinColor": "#DDA988", "blush": True, "blushColor": "#C47D6E",
                "eyes": "focused", "eyebrows": "thick_arch", "nose": "upturned_tiny", "mouth": "flat", "beard": "mustache",
                "hat": "beanie", "hatPrimary": "#B84A39", "hatAccent": "#E8DCC6", "backHair": "short", "hairColor": "#2B2220",
                "outfit": "hoodie", "robeColor": "#C46D28", "innerColor": "#2E3A48", "sashColor": "#2E3A48", "trimColor": "#EAE4D8",
                "beltStyle": "plain", "cape": "scarf", "capeColor": "#33475B", "pose": "akimbo", "limbColor": "#242933",
            },
        },
        {
            "id": "npc_dio_3", "height": 1.80,
            "config": {
                **DEFAULT_CONFIG, "name": "Warga Ignaluk 1",
                "headShape": "chubby_oval", "ears": True, "skinColor": "#D8A482", "blush": True, "blushColor": "#BE796B",
                "eyes": "happy", "eyebrows": "happy", "nose": "upturned_tiny", "mouth": "smirk", "beard": "none",
                "hat": "beanie", "hatPrimary": "#4A5859", "hatAccent": "#F4F1EA", "backHair": "short", "hairColor": "#231B1A",
                "outfit": "safari_explorer", "robeColor": "#4A6B5D", "innerColor": "#E8E2D6", "sashColor": "#2C3A38", "trimColor": "#D6A848",
                "beltStyle": "utility_belt", "cape": "backpack", "capeColor": "#4D3B2E", "pose": "ready", "limbColor": "#232830",
            },
        },
        {
            "id": "npc_dio_4", "height": 1.76,
            "config": {
                **DEFAULT_CONFIG, "name": "Warga Ignaluk 2",
                "headShape": "round", "ears": True, "skinColor": "#E0B294", "blush": True, "blushColor": "#C88072",
                "eyes": "honey_oval", "eyebrows": "happy", "nose": "upturned_tiny", "mouth": "grin_teeth", "beard": "none",
                "hat": "beanie", "hatPrimary": "#2F5D62", "hatAccent": "#F4D35E", "backHair": "short", "hairColor": "#1E1918",
                "outfit": "trench_coat", "robeColor": "#8E3B46", "innerColor": "#F2E9DC", "sashColor": "#5E242C", "trimColor": "#E6B84C",
                "beltStyle": "buckle", "cape": "scarf", "capeColor": "#E8DFCE", "pose": "wave", "limbColor": "#242830",
            },
        },
        {
            "id": "npc_dio_5", "height": 1.86,
            "config": {
                **DEFAULT_CONFIG, "name": "Pelaut Bering",
                "headShape": "tall", "ears": True, "skinColor": "#E6BE9E", "blush": False, "blushColor": "#CA8676",
                "eyes": "chill", "eyebrows": "raised", "nose": "upturned_tiny", "mouth": "smirk", "beard": "full_beard",
                "hat": "beanie", "hatPrimary": "#D4882A", "hatAccent": "#24303C", "backHair": "short", "hairColor": "#4C3A2C",
                "outfit": "hoodie", "robeColor": "#2B4158", "innerColor": "#E4DED2", "sashColor": "#1C2B3A", "trimColor": "#E6A83A",
                "beltStyle": "plain", "cape": "none", "pose": "ready", "limbColor": "#202630",
            },
        },
    ],
    "rjukan": [
        {
            "id": "npc_rju_1", "height": 1.78,
            "config": {
                **DEFAULT_CONFIG, "name": "Warga Rjukan 1",
                "headShape": "round", "ears": True, "skinColor": "#FCE9DD", "blush": True, "blushColor": "#E8B0A8",
                "eyes": "happy", "eyebrows": "happy", "nose": "upturned_tiny", "mouth": "smirk", "beard": "none",
                "hat": "beanie", "hatPrimary": "#9E2A2B", "hatAccent": "#F2E9DC", "backHair": "short", "hairColor": "#D9B45C",
                "outfit": "trench_coat", "robeColor": "#2D4F6C", "innerColor": "#F2E9DC", "sashColor": "#213A50", "trimColor": "#E0B654",
                "beltStyle": "buckle", "cape": "scarf", "capeColor": "#9E2A2B", "pose": "ready", "limbColor": "#242A34",
            },
        },
        {
            "id": "npc_rju_2", "height": 1.84,
            "config": {
                **DEFAULT_CONFIG, "name": "Warga Rjukan 2",
                "headShape": "tall", "ears": True, "skinColor": "#F9E4D6", "blush": True, "blushColor": "#E2A9A0",
                "eyes": "chill", "eyebrows": "raised", "nose": "upturned_tiny", "mouth": "grin_teeth", "beard": "stubble",
                "hat": "beanie", "hatPrimary": "#354F52", "hatAccent": "#CAD2C5", "backHair": "short", "hairColor": "#7A5838",
                "outfit": "safari_explorer", "robeColor": "#8C4A32", "innerColor": "#E8DEC8", "sashColor": "#4E2B1E", "trimColor": "#D4A84E",
                "beltStyle": "buckle", "cape": "scarf", "capeColor": "#D9C7A8", "pose": "wave", "limbColor": "#26282E",
            },
        },
        {
            "id": "npc_rju_3", "height": 1.74,
            "config": {
                **DEFAULT_CONFIG, "name": "Warga Rjukan 3",
                "headShape": "chubby_oval", "ears": True, "skinColor": "#FDECE2", "blush": True, "blushColor": "#ECBAB2",
                "eyes": "starry", "eyebrows": "happy", "nose": "upturned_tiny", "mouth": "happy_open", "beard": "none",
                "hat": "beanie", "hatPrimary": "#D4A034", "hatAccent": "#FAF6EC", "backHair": "short", "hairColor": "#C49746",
                "outfit": "hoodie", "robeColor": "#3A5A40", "innerColor": "#F2E8CF", "sashColor": "#2A4230", "trimColor": "#F2E8CF",
                "beltStyle": "plain", "cape": "scarf", "capeColor": "#F2E8CF", "pose": "ready", "limbColor": "#262A30",
            },
        },
        {
            "id": "npc_rju_4", "height": 1.82,
            "config": {
                **DEFAULT_CONFIG, "name": "Warga Rjukan 4",
                "headShape": "potato", "ears": True, "skinColor": "#F5DFCE", "blush": True, "blushColor": "#DFABA2",
                "eyes": "honey_oval", "eyebrows": "happy", "nose": "upturned_tiny", "mouth": "smirk", "beard": "mustache",
                "hat": "beanie", "hatPrimary": "#4A4E69", "hatAccent": "#C9ADA7", "backHair": "short", "hairColor": "#A8B0BC",
                "outfit": "trench_coat", "robeColor": "#5C4D42", "innerColor": "#EAE0D2", "sashColor": "#3D322B", "trimColor": "#C9A25B",
                "beltStyle": "buckle", "cape": "scarf", "capeColor": "#588157", "pose": "akimbo", "limbColor": "#28262C",
            },
        },
        {
            "id": "npc_rju_5", "height": 1.76,
            "config": {
                **DEFAULT_CONFIG, "name": "Turis Norwegia 1",
                "headShape": "round", "ears": True, "skinColor": "#FCE7DA", "blush": True, "blushColor": "#E8B0A6",
                "eyes": "happy", "eyebrows": "raised", "nose": "upturned_tiny", "mouth": "grin_teeth", "beard": "none",
                "hat": "beanie", "hatPrimary": "#C85A32", "hatAccent": "#FAF0DC", "backHair": "short", "hairColor": "#8C5834",
                "outfit": "hoodie", "robeColor": "#3D5A80", "innerColor": "#F4EDE2", "sashColor": "#293E58", "trimColor": "#EE6C4D",
                "beltStyle": "plain", "cape": "backpack", "capeColor": "#5E3A28", "pose": "ready", "limbColor": "#242A34",
            },
        },
        {
            "id": "npc_rju_6", "height": 1.80,
            "config": {
                **DEFAULT_CONFIG, "name": "Penjual Wafel Rjukan",
                "headShape": "wide", "ears": True, "skinColor": "#F9E2D2", "blush": True, "blushColor": "#E2A49C",
                "eyes": "honey_oval", "eyebrows": "happy", "nose": "upturned_tiny", "mouth": "happy_open", "beard": "stubble",
                "hat": "beanie", "hatPrimary": "#7A2E2E", "hatAccent": "#F6E8CC", "backHair": "short", "hairColor": "#6A4B30",
                "outfit": "chef_apron", "robeColor": "#B84A39", "innerColor": "#FAF6EC", "sashColor": "#3B2820", "trimColor": "#E2B448",
                "beltStyle": "knot", "cape": "none", "pose": "wave", "limbColor": "#2A2424",
            },
        },
    ],
    "baarle": [
        {
            "id": "npc_baa_1", "height": 1.78,
            "config": {
                **DEFAULT_CONFIG, "name": "Pelanggan Kafe 1",
                "headShape": "round", "ears": True, "skinColor": "#FBE7D8", "blush": True, "blushColor": "#E8B0A6",
                "eyes": "happy", "eyebrows": "happy", "nose": "upturned_tiny", "mouth": "smirk", "beard": "none",
                "hat": "none", "backHair": "short", "hairColor": "#6B442A",
                "outfit": "trench_coat", "robeColor": "#34597C", "innerColor": "#F4ECD8", "sashColor": "#25405A", "trimColor": "#D9A84C",
                "beltStyle": "buckle", "cape": "scarf", "capeColor": "#D8B98E", "pose": "ready", "limbColor": "#24344D",
            },
        },
        {
            "id": "npc_baa_2", "height": 1.84,
            "config": {
                **DEFAULT_CONFIG, "name": "Pelanggan Kafe 2",
                "headShape": "tall", "ears": True, "skinColor": "#F7DFCE", "blush": False, "blushColor": "#E2B2A4",
                "eyes": "chill", "eyebrows": "flat", "nose": "upturned_tiny", "mouth": "smirk", "beard": "goatee",
                "faceAccessory": "round_glasses", "hat": "none", "backHair": "side_part", "hairColor": "#3B281E",
                "outfit": "suit_tie", "robeColor": "#4B5D52", "innerColor": "#F5EFE4", "sashColor": "#A84A32", "trimColor": "#D9A84C",
                "beltStyle": "buckle", "cape": "none", "pose": "think", "limbColor": "#25262B",
            },
        },
        {
            "id": "npc_baa_3", "height": 1.76,
            "config": {
                **DEFAULT_CONFIG, "name": "Pejalan Kaki Baarle 1",
                "headShape": "chubby_oval", "ears": True, "skinColor": "#FCE9DA", "blush": True, "blushColor": "#EAB4AA",
                "eyes": "honey_oval", "eyebrows": "happy", "nose": "upturned_tiny", "mouth": "grin_teeth", "beard": "none",
                "hat": "beret", "hatPrimary": "#7D303A", "hatAccent": "#F2E8D8", "hatTilt": -5, "backHair": "short", "hairColor": "#4E3224",
                "outfit": "trench_coat", "robeColor": "#C48F44", "innerColor": "#F7F1E4", "sashColor": "#8C632B", "trimColor": "#423228",
                "beltStyle": "buckle", "cape": "none", "pose": "ready", "limbColor": "#2A364B",
            },
        },
        {
            "id": "npc_baa_4", "height": 1.82,
            "config": {
                **DEFAULT_CONFIG, "name": "Pejalan Kaki Baarle 2",
                "headShape": "potato", "ears": True, "skinColor": "#F2D5BE", "blush": False, "blushColor": "#DCAD9C",
                "eyes": "chill", "eyebrows": "happy", "nose": "upturned_tiny", "mouth": "smirk", "beard": "stubble",
                "hat": "none", "backHair": "side_part", "hairColor": "#2E2420",
                "outfit": "street_varsity", "robeColor": "#3A4E6C", "innerColor": "#F2ECE0", "sashColor": "#222E42", "trimColor": "#E5B44A",
                "beltStyle": "plain", "cape": "backpack", "capeColor": "#6B4E38", "pose": "ready", "limbColor": "#242A36",
            },
        },
        {
            "id": "npc_baa_5", "height": 1.74,
            "config": {
                **DEFAULT_CONFIG, "name": "Tamu Patio Kiri",
                "headShape": "round", "ears": True, "skinColor": "#FCE9DB", "blush": True, "blushColor": "#E8B0A6",
                "eyes": "happy", "eyebrows": "happy", "nose": "upturned_tiny", "mouth": "happy_open", "beard": "none",
                "hat": "beret", "hatPrimary": "#2C5545", "hatAccent": "#F4EBD6", "hatTilt": 4, "backHair": "short", "hairColor": "#B8843E",
                "outfit": "hoodie", "robeColor": "#B85C3C", "innerColor": "#F8F2E6", "sashColor": "#7E3C24", "trimColor": "#F4EBD6",
                "beltStyle": "plain", "cape": "scarf", "capeColor": "#F4EBD6", "pose": "wave", "limbColor": "#2C303A",
            },
        },
        {
            "id": "npc_baa_6", "height": 1.80,
            "config": {
                **DEFAULT_CONFIG, "name": "Tamu Patio Kanan",
                "headShape": "wide", "ears": True, "skinColor": "#F6DFCE", "blush": False, "blushColor": "#DFAC9E",
                "eyes": "honey_oval", "eyebrows": "raised", "nose": "upturned_tiny", "mouth": "smirk", "beard": "mustache",
                "hat": "fedora", "hatPrimary": "#4A3A2E", "hatAccent": "#C89B4C", "backHair": "short", "hairColor": "#423228",
                "outfit": "suit_tie", "robeColor": "#5E4B3C", "innerColor": "#F4EFE4", "sashColor": "#2A584A", "trimColor": "#D4A84E",
                "beltStyle": "buckle", "cape": "none", "pose": "ready", "limbColor": "#2A2626",
            },
        },
        {
            "id": "npc_baa_7", "height": 1.78,
            "config": {
                **DEFAULT_CONFIG, "name": "Pelanggan Kafe 3",
                "headShape": "chubby_oval", "ears": True, "skinColor": "#F9E3D4", "blush": True, "blushColor": "#E4A8A0",
                "eyes": "happy", "eyebrows": "happy", "nose": "upturned_tiny", "mouth": "grin_teeth", "beard": "none",
                "hat": "none", "backHair": "curly", "hairColor": "#5A3824",
                "outfit": "trench_coat", "robeColor": "#3B6B58", "innerColor": "#F5EFE0", "sashColor": "#26483B", "trimColor": "#E0B44E",
                "beltStyle": "buckle", "cape": "none", "pose": "ready", "limbColor": "#242C34",
            },
        },
    ],
}


def render_scene_npc_sprites(scene_name: str, out_root: str, scale: float = 1.25) -> Dict[str, str]:
    """Render 4-frame lightweight cycle PNGs for every 2.5D bean-head NPC in scene_name."""
    os.makedirs(out_root, exist_ok=True)
    result: Dict[str, str] = {}
    for spec in NPC_ROSTER.get(scene_name, []):
        nid = spec["id"]
        npc_dir = os.path.join(out_root, nid)
        os.makedirs(npc_dir, exist_ok=True)
        char = Character25D(spec["config"], scale=scale, fps=30, default_animation="idle")
        for idx, ang in enumerate([0.0, 22.0, -22.0, 12.0]):
            out_png = os.path.join(npc_dir, f"pose_{idx}.png")
            if not os.path.exists(out_png) or os.path.getsize(out_png) < 200:
                char.save_frame(out_png, frame=idx * 6, fps=30, angle=ang, animation="idle", blink=0.0, ground_shadow=False)
        result[nid] = npc_dir
    return result
