"""Inferência local do TripoSG (MIT) sem RMBG e sem diso.

Roda no ambiente isolado tools/route_b/.venv. ``diso`` exige compilação com CUDA; a extração da
superfície é trocada por marching cubes do scikit-image, sem alterar o repositório clonado.

Uso: tools/route_b/.venv/Scripts/python.exe scripts/route_b_infer.py <rgba.png> <base.glb> [seed]
Gera <base>_hier.glb, com relatório JSON.
"""

import json
import sys
import time
import types
from pathlib import Path

import numpy as np
import torch
from PIL import Image

REPO = Path(__file__).resolve().parents[1] / "tools/route_b/TripoSG"
sys.path.insert(0, str(REPO))


class SkimageDMC(torch.nn.Module):
    """Substituto de diso.DiffDMC: mesma interface usada em inference_utils."""

    def __init__(self, dtype=torch.float32):
        super().__init__()

    def forward(self, sdf, deform=None, return_quads=False, normalize=False):
        from scipy import ndimage
        from skimage import measure

        # O decodificador só avalia uma faixa em torno da superfície; o resto vem NaN. Preencher
        # com um valor único cria casca falsa e degraus de voxel (provado em esfera sintética:
        # erro de 1,03 voxel contra 0,0008). O sinal do preenchimento precisa ser preservado:
        # NaN ligado à borda do volume é exterior; o restante é interior.
        grid = sdf.detach().float().cpu().numpy()
        holes = np.isnan(grid)
        labels, _ = ndimage.label(holes)
        faces_of_volume = (labels[0], labels[-1], labels[:, 0], labels[:, -1], labels[:, :, 0], labels[:, :, -1])
        border = np.unique(np.concatenate([face.ravel() for face in faces_of_volume]))
        outside = np.isin(labels, border[border != 0])
        grid[holes] = -1.0
        grid[outside] = 1.0
        vertices, faces, _, _ = measure.marching_cubes(grid, level=0.0)
        return torch.from_numpy(vertices.copy()).float(), torch.from_numpy(faces.copy()).long()


sys.modules["diso"] = types.SimpleNamespace(DiffDMC=SkimageDMC)

import trimesh

# O diffusers atual só resolve componentes do repositório se os módulos já estiverem importados.
import triposg.models.autoencoders.autoencoder_kl_triposg
import triposg.models.transformers.triposg_transformer
import triposg.schedulers.scheduling_rectified_flow  # noqa: F401
from huggingface_hub import snapshot_download
from triposg.pipelines.pipeline_triposg import TripoSGPipeline

source, output = Path(sys.argv[1]), Path(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 42
weights = REPO / "pretrained_weights/TripoSG"
snapshot_download(repo_id="VAST-AI/TripoSG", local_dir=weights)

rgba = Image.open(source).convert("RGBA")
white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
white.alpha_composite(rgba)
image = white.convert("RGB").resize((512, 512), Image.LANCZOS)

pipe = TripoSGPipeline.from_pretrained(str(weights)).to("cuda", torch.float16)
# Decodificador em float32: em float16 as coordenadas perdem precisão antes do embedding de
# frequência, e o campo sai em patamares (malha com 30% das faces alinhadas à grade).
pipe.vae.to(torch.float32)
original_decode = pipe.vae._decode


def decode_float32(z, sampled_points, **kwargs):
    if next(pipe.transformer.parameters()).device.type == "cuda":
        pipe.transformer.to("cpu")  # libera VRAM: a difusão já acabou
        torch.cuda.empty_cache()
    return original_decode(z.float(), sampled_points.float(), **kwargs)


pipe.vae._decode = decode_float32


def run(name, use_flash):
    pipe.transformer.to("cuda")
    torch.cuda.reset_peak_memory_stats()
    started = time.monotonic()
    with torch.no_grad():
        result = pipe(
            image=image,
            generator=torch.Generator(device=pipe.device).manual_seed(seed),
            num_inference_steps=50,
            guidance_scale=7.0,
            use_flash_decoder=use_flash,
        ).samples[0]
    mesh = trimesh.Trimesh(result[0].astype(np.float32), np.ascontiguousarray(result[1]))
    path = output.with_name(f"{output.stem}_{name}.glb")
    path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(path)
    report = {
        "variant": name, "seed": seed, "seconds": round(time.monotonic() - started, 1),
        "faces": len(mesh.faces), "vertices": len(mesh.vertices),
        "peak_vram_mib": torch.cuda.max_memory_allocated() // 2**20,
        "watertight": bool(mesh.is_watertight), "components": len(mesh.split(only_watertight=False)),
        "axis_aligned_faces": round(float((np.abs(mesh.face_normals).max(axis=1) > .999).mean()), 4),
        "torch": torch.__version__,
    }
    path.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(report, flush=True)


# Só o caminho hierárquico: o rápido falha por conflito de dtype com o decodificador em float32.
for name, use_flash in (("hier", False),):
    try:
        run(name, use_flash)
    except Exception as error:  # uma variante não deve impedir a outra
        print(f"FALHOU {name}: {type(error).__name__}: {error}", flush=True)
        torch.cuda.empty_cache()
