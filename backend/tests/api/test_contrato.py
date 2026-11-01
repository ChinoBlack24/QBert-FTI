"""
El backend cumple contrato-api/openapi.yaml.

Compara el contrato escrito a mano con el OpenAPI que genera FastAPI:
mismas rutas, métodos, operationId y códigos de respuesta exitosos, y mismos
campos (y obligatorios) en cada esquema. Si alguien cambia la API sin cambiar
el contrato (o al revés), esto falla.
"""

from pathlib import Path

import pytest
import yaml

from api.main import app

CONTRATO = yaml.safe_load(
    (Path(__file__).resolve().parents[3] / "contrato-api" / "openapi.yaml").read_text())
GENERADO = app.openapi()
PREFIJO = CONTRATO["servers"][0]["url"]  # /api
METODOS = {"get", "post", "put", "patch", "delete"}


def _operaciones(spec, prefijo=""):
    return {(prefijo + ruta, metodo): op
            for ruta, item in spec["paths"].items()
            for metodo, op in item.items() if metodo in METODOS}


OPS_CONTRATO = _operaciones(CONTRATO, PREFIJO)
OPS_GENERADO = _operaciones(GENERADO)


def test_mismas_rutas_y_metodos():
    assert set(OPS_CONTRATO) == set(OPS_GENERADO)


@pytest.mark.parametrize("clave", sorted(OPS_CONTRATO))
def test_operacion(clave):
    contrato, generado = OPS_CONTRATO[clave], OPS_GENERADO[clave]
    assert contrato["operationId"] == generado["operationId"]
    exitos = lambda op: {c for c in op["responses"] if c.startswith("2")}
    assert exitos(contrato) == exitos(generado)


ESQUEMAS = sorted(n for n in CONTRATO["components"]["schemas"]
                  if n not in {"Error", "ErrorValidacion"})


@pytest.mark.parametrize("nombre", ESQUEMAS)
def test_esquema(nombre):
    contrato = CONTRATO["components"]["schemas"][nombre]
    generado = GENERADO["components"]["schemas"].get(nombre)
    assert generado is not None, f"FastAPI no genera el esquema {nombre}"
    assert set(contrato.get("properties", {})) == set(generado.get("properties", {}))
    assert set(contrato.get("required", [])) == set(generado.get("required", []))
