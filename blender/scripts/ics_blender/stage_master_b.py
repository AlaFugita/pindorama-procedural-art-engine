"""Rota B: importa o GLB gerado e o normaliza para o mesmo estúdio da Rota A.

Só escala, centraliza e gira. Nenhuma limpeza ou escultura: a comparação precisa mostrar a saída
da IA como ela é. Remesh ou decimação, se vierem, são outra tentativa, registrada à parte.
"""

import math

import bmesh
import bpy
import numpy as np
from mathutils import Matrix

from . import master_body as mb


def _clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def _components(mesh):
    edges = mb.edge_array(mesh)
    parent = np.arange(len(mesh.vertices))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for a, b in edges.tolist():
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    return len({find(i) for i in range(len(parent))})


def _quality(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    result = {
        "vertices": len(bm.verts), "faces": len(bm.faces),
        "quads": sum(1 for f in bm.faces if len(f.verts) == 4),
        "tris": sum(1 for f in bm.faces if len(f.verts) == 3),
        "open_edges": sum(1 for e in bm.edges if e.is_boundary),
        "non_manifold_edges": sum(1 for e in bm.edges if not e.is_manifold and not e.is_boundary),
    }
    bm.free()
    result["components"] = _components(mesh)
    result["uv_layers"] = len(mesh.uv_layers)
    return result


def run(payload):
    scene = _clear()
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=payload["glb_path"])
    meshes = [o for o in set(bpy.data.objects) - before if o.type == "MESH"]
    if len(meshes) != 1:
        raise RuntimeError(f"esperada uma malha, vieram {len(meshes)}")
    obj = meshes[0]
    obj.parent = None
    depsgraph = bpy.context.evaluated_depsgraph_get()
    matrix = np.array(obj.evaluated_get(depsgraph).matrix_world)
    co = mb.read_co(obj.data)
    co = co @ matrix[:3, :3].T + matrix[:3, 3]
    obj.matrix_world = Matrix.Identity(4)
    span = co[:, 2].max() - co[:, 2].min()
    co *= payload["target_height_m"] / span
    yaw = math.radians(payload.get("yaw_deg", 0.0))
    rotation = np.array([[math.cos(yaw), -math.sin(yaw), 0], [math.sin(yaw), math.cos(yaw), 0], [0, 0, 1]])
    co = co @ rotation.T
    center = (co.max(axis=0) + co.min(axis=0)) / 2
    co[:, 0] -= center[0]
    co[:, 1] -= center[1]
    co[:, 2] -= co[:, 2].min()
    mb.write_co(obj.data, co)
    obj.data.shade_smooth()
    obj.name = "master_body"
    for other in list(bpy.data.objects):
        if other is not obj:
            bpy.data.objects.remove(other)
    collection = bpy.data.collections.new("MASTER")
    scene.collection.children.link(collection)
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    bpy.ops.wm.save_as_mainfile(filepath=payload["blend_path"], compress=True)
    return {"quality": _quality(obj.data), "source_span": float(span)}
