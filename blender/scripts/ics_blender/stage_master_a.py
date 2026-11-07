"""Rota A do Character Master Prototype. Abre o bundle CC0 e salva um .blend próprio."""

import bpy
import numpy as np
from mathutils import Matrix

from . import master_body as mb
from . import master_costume as costume


def _isolate(keep):
    remove = [o for o in bpy.data.objects if o not in keep]
    bpy.data.batch_remove(remove)
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)


def _subdivide(obj, levels=1):
    modifier = obj.modifiers.new("subdiv", "SUBSURF")
    modifier.levels = levels
    modifier.render_levels = levels
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))
    obj.modifiers.clear()
    obj.data = mesh


def run(payload):
    body = bpy.data.objects["GEO-body_male_stylized"]
    eyes = [bpy.data.objects[f"GEO-body_male_stylized.eye.{side}"] for side in "LR"]
    _isolate({body, *eyes})
    scene = bpy.context.scene
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)
    for obj in (body, *eyes):
        if obj.name not in scene.collection.objects:
            scene.collection.objects.link(obj)
        obj.parent = None
    # Coordenadas locais: o offset do bundle (-0.27 em X) não faz parte do personagem.
    eye_world = {obj: np.array(obj.matrix_world) for obj in eyes}
    body_offset = np.array(body.matrix_world)[:3, 3]
    body.matrix_world = Matrix.Identity(4)

    points = mb.to_canonical(mb.read_co(body.data))
    target = mb.remap_proportions(points, mb.SEGMENTS)
    edges = mb.edge_array(body.data)
    delta = mb.smooth_field(target - points, edges, payload.get("smooth", 12), 0.5)
    body_points = points + delta

    eye_points = {}
    for obj in eyes:
        local = np.array([tuple(v.co) for v in obj.data.vertices])
        matrix = eye_world[obj]
        world = local @ matrix[:3, :3].T + matrix[:3, 3] - body_offset
        canonical = mb.to_canonical(world)
        moved = mb.remap_proportions(canonical, mb.SEGMENTS)
        # A esfera do olho da base salta na cabeça maior: recua para dentro da órbita.
        center = moved.mean(axis=0)
        moved = center + (moved - center) * .96 + np.array([0, -.02, 0])
        eye_points[obj] = moved

    centers = [p.mean(axis=0) for p in eye_points.values()]
    mb.write_co(body.data, mb.apply_warps(body_points, costume.FACE_WARPS, centers))
    for obj, moved in eye_points.items():
        obj.matrix_world = Matrix.Identity(4)
        warped = mb.apply_warps(moved, costume.FACE_WARPS, centers)
        # Globo liso: os anéis de íris da base viram ruído em argila.
        center = warped.mean(axis=0)
        radius = np.linalg.norm(warped - center, axis=1).max()
        direction = (warped - center) / np.maximum(np.linalg.norm(warped - center, axis=1, keepdims=True), 1e-9)
        mb.write_co(obj.data, center + direction * radius)
        obj.data.shade_smooth()

    _subdivide(body, payload.get("subdiv", 1))
    edges = mb.edge_array(body.data)
    topology = mb.mesh_topology(body.data)
    co = mb.read_co(body.data)
    # Pernas: relaxa os degraus criados pela compressão antes de esculpir.
    legs = np.clip((.33 - co[:, 2]) / .06, 0, 1) * np.clip((co[:, 2] - .07) / .03, 0, 1)
    relaxed = mb.smooth_field(co, edges, 60, .5)
    co = co + (relaxed - co) * legs[:, None]
    sculpted = mb.apply_brushes(co, costume.BODY_BRUSHES, topology, edges)
    mb.write_co(body.data, sculpted)
    body.data.shade_smooth()
    body.name = "master_body"

    parts = costume.build_all(scene, payload.get("skip", []), sculpted)
    collection = bpy.data.collections.new("MASTER")
    scene.collection.children.link(collection)
    for obj in (body, *eyes, *parts):
        if obj.name in scene.collection.objects:
            scene.collection.objects.unlink(obj)
        collection.objects.link(obj)
    bpy.ops.wm.save_as_mainfile(filepath=payload["blend_path"], compress=True)
    z = sculpted[:, 2]
    return {
        "blender_version": bpy.app.version_string,
        "body_vertices": len(body.data.vertices),
        "body_faces": len(body.data.polygons),
        "height_m": float(z.max() - z.min()),
        "parts": [{"name": p.name, "vertices": len(p.data.vertices)} for p in parts],
    }
