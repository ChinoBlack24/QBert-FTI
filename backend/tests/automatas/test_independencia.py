"""
automatas/ es la lógica pura: no puede depender de la API, de FastAPI ni de
nada de presentación. Si alguien agrega un import así, este test falla.
"""

import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2]
PROHIBIDOS = ("api", "fastapi", "pydantic", "starlette", "uvicorn", "pygame")


def test_importar_automatas_no_carga_nada_de_la_api():
    codigo = (
        "import sys, automatas\n"
        f"malos = sorted(m for m in sys.modules if m.split('.')[0] in {PROHIBIDOS!r})\n"
        "print(','.join(malos))\n"
    )
    r = subprocess.run([sys.executable, "-c", codigo], cwd=BACKEND,
                       capture_output=True, text=True, check=True)
    assert r.stdout.strip() == "", f"automatas importa: {r.stdout.strip()}"


def test_ningun_archivo_de_automatas_importa_cosas_de_afuera():
    for archivo in (BACKEND / "automatas").glob("*.py"):
        for linea in archivo.read_text().splitlines():
            if linea.startswith(("import ", "from ")):
                modulo = linea.split()[1].lstrip(".").split(".")[0]
                assert modulo not in PROHIBIDOS, f"{archivo.name}: {linea}"
