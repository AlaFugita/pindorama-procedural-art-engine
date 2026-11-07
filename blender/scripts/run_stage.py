"""Ponto de entrada único dos estágios Blender.

Uso: blender --background [arquivo.blend] --python run_stage.py -- --stage X --input a --output b

Não depende de pydantic nem de nada fora do Blender: recebe JSON já resolvido pelo backend.
"""

import argparse
import importlib
import json
import os
import sys
import traceback

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :]
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    with open(args.input, encoding="utf-8") as stream:
        payload = json.load(stream)

    try:
        module = importlib.import_module(f"ics_blender.stage_{args.stage}")
        result = module.run(payload)
        result = {"status": "ok", "stage": args.stage, **result}
    except Exception as error:  # manifesto registra a falha; exit code é propagado abaixo
        traceback.print_exc()
        result = {"status": "error", "stage": args.stage, "error": f"{type(error).__name__}: {error}"}
        with open(args.output, "w", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, ensure_ascii=False)
        raise

    with open(args.output, "w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)


main()
