"""GLB de intercâmbio (opcional). O conversor oficial aplica +Y up ao exportar."""

import bpy


def run(payload):
    bpy.ops.export_scene.gltf(
        filepath=payload["glb_path"],
        export_format="GLB",
        export_yup=True,
        export_animations=True,
        export_force_sampling=True,
        use_selection=False,
    )
    return {"glb_path": payload["glb_path"]}
