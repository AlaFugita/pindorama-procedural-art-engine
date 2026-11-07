"""Render em lote: câmera fixa, root gira. Saída: frames/<clip>/<dir>/<clip>_<dir>_NNNN.png."""

import json
import math
import os
import time

import bpy

from . import animation as anim
from . import scene as scene_utils


def run(payload):
    scene = bpy.context.scene
    armature = bpy.data.objects["ICS_Rig"]
    render = payload["render"]
    scene_utils.configure_render(scene, render)
    armature.rotation_mode = "XYZ"
    root = payload["output_dir"]
    index = {}
    started = time.monotonic()
    progress = payload.get("progress_file")
    total = sum(clip["frame_count"] for clip in payload["clips"]) * len(render["direction_order"])
    done = 0
    for clip in payload["clips"]:
        anim.use_action(armature, f"clip_{clip['animation_id']}")
        scene.render.fps = clip["fps"]
        clip_index = {}
        for direction in render["direction_order"]:
            armature.rotation_euler = (0, 0, -math.radians(render["headings_deg"][direction]))
            folder = os.path.join(root, clip["animation_id"], direction)
            os.makedirs(folder, exist_ok=True)
            files = []
            for frame in range(clip["frame_count"]):
                scene.frame_set(frame)
                path = os.path.join(folder, f"{clip['animation_id']}_{direction}_{frame:04d}.png")
                scene_utils.render_to(scene, path)
                files.append(path)
                done += 1
                if progress:
                    with open(progress, "w", encoding="utf-8") as stream:
                        json.dump({"done": done, "total": total}, stream)
            clip_index[direction] = files
        index[clip["animation_id"]] = clip_index
    return {"frames": index, "seconds": time.monotonic() - started, "rendered": done}
