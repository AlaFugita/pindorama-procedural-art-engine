"""Montagem do personagem: CharacterSpec resolvido → cena Blender com rig e materiais."""

import hashlib

import bpy

from . import BUILDER_VERSION
from . import chibi_components as chibi
from . import chibi_detail
from . import components as comp
from . import materials as mats
from . import rig as rig_utils
from . import scene as scene_utils


def _make_mesh(part, collection):
    verts, faces = part["mesh"]
    mesh = bpy.data.meshes.new(part["name"])
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(part["name"], mesh)
    collection.objects.link(obj)
    if part.get("remesh"):
        remesh = obj.modifiers.new("remesh", "REMESH")
        remesh.mode = "VOXEL"
        remesh.voxel_size = part["remesh"]
        remesh.use_smooth_shade = True
        smooth = obj.modifiers.new("smooth", "SMOOTH")
        smooth.iterations = 6
        smooth.factor = 0.6
        depsgraph = bpy.context.evaluated_depsgraph_get()
        applied = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))
        obj.modifiers.clear()
        obj.data = applied
        bpy.data.meshes.remove(mesh)
        applied.name = part["name"]
    obj.data.shade_smooth()
    return obj


def _add_outline(obj, material, art):
    if art["outline_thickness_m"] <= 0:
        return
    obj.data.materials.append(material)
    solidify = obj.modifiers.new("ICS_Outline", "SOLIDIFY")
    solidify.thickness = art["outline_thickness_m"]
    solidify.offset = 1.0
    solidify.use_flip_normals = True
    solidify.use_rim = False
    solidify.material_offset = 1


def run(payload):
    scene = scene_utils.clear_scene()
    art, rig, render = payload["art"], payload["rig"], payload["render"]
    spec = payload["character"]
    scene_utils.configure_render(scene, render)
    scene_utils.add_camera(scene, render)
    scene_utils.add_lights(scene, art)

    armature = rig_utils.build_armature(scene, rig)
    rig_utils.setup_ik(armature, rig)
    deform = [b["blender_name"] for b in rig["bones"] if b["deform"]]
    head_params = next(c["params"] for c in payload["components"] if c["kind"] == "head")
    context = {"deform_bones": deform, "head_params": head_params}
    palette = dict(spec["palette"])
    palette["skin"] = payload["skin_color"]
    palette["hair"] = payload.get("hair_color") or palette["secondary"]

    collection = bpy.data.collections.new("ICS_Character")
    scene.collection.children.link(collection)
    material_cache = {}

    def material_pair(key):
        color = mats.resolve_color(key, palette)
        if color not in material_cache:
            material_cache[color] = (
                mats.toon_material(f"ICS_{key}_{color[1:]}", color, art),
                mats.outline_material(f"ICS_outline_{color[1:]}", color, art),
            )
        return material_cache[color]

    objects = []
    for component in payload["components"]:
        generator = {**comp.GENERATORS, **chibi.GENERATORS, **chibi_detail.GENERATORS}[component["generator"]]
        for part in generator(component["params"], context):
            obj = _make_mesh(part, collection)
            base, outline = material_pair(part["material"])
            obj.data.materials.append(base)
            obj["ics_component"] = component["id"]
            obj["ics_color"] = mats.resolve_color(part["material"], palette)
            rig_utils.skin_weights(obj, armature, part["skin"], rig)
            if part["outline"]:
                _add_outline(obj, outline, art)
            coords = [round(c, 5) for v in obj.data.vertices for c in v.co]
            objects.append({
                "mesh_sha": hashlib.sha256(repr(coords).encode()).hexdigest()[:16],
                "name": obj.name, "component": component["id"], "vertices": len(obj.data.vertices),
                "faces": len(obj.data.polygons), "material": part["material"],
                "skin": part["skin"].get("rigid", "smooth"),
            })

    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=payload["blend_path"], compress=True)
    return {
        "blender_version": bpy.app.version_string,
        "builder_version": BUILDER_VERSION,
        "objects": objects,
        "materials": sorted(m.name for m in bpy.data.materials),
        "blend_path": payload["blend_path"],
    }
