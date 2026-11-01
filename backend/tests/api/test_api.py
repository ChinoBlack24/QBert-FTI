"""La API usada como la usaría el frontend."""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from automatas import CAIDA

cliente = TestClient(app)


@pytest.fixture
def partida():
    r = cliente.post("/api/partidas", json={"nivel": 1})
    assert r.status_code == 201
    return r.json()


def test_partida_nueva(partida):
    assert partida["posicion"] == 0 and partida["vidas"] == 3
    assert partida["colores"] == ["A"] * 28
    assert partida["colores_nivel"][-1] == {"estado": "q1", "color": "B", "objetivo": True}


def test_crear_sin_cuerpo_usa_nivel_1():
    assert cliente.post("/api/partidas").json()["nivel"] == 1


def test_salto(partida):
    r = cliente.post(f"/api/partidas/{partida['id']}/saltos", json={"tecla": "s"}).json()
    assert r["paso"]["movimiento"] == {"q": "q0", "e": "s", "q_nuevo": "q1", "s": "1"}
    assert r["paso"]["cubo"] == {"cubo": 1, "q": "q0", "q_nuevo": "q1", "color": "B"}
    assert r["estado"]["colores"][1] == "B" and r["estado"]["posicion"] == 1


def test_caida(partida):
    r = cliente.post(f"/api/partidas/{partida['id']}/saltos", json={"tecla": "w"}).json()
    assert r["paso"]["cubo"] is None
    assert r["paso"]["vidas"]["e"] == CAIDA
    assert r["estado"]["vidas"] == 2


def test_game_over_devuelve_paso_null(partida):
    url = f"/api/partidas/{partida['id']}/saltos"
    for _ in range(3):
        cliente.post(url, json={"tecla": "w"})
    r = cliente.post(url, json={"tecla": "s"}).json()
    assert r["paso"] is None and r["estado"]["game_over"]


def test_tecla_invalida(partida):
    r = cliente.post(f"/api/partidas/{partida['id']}/saltos", json={"tecla": "x"})
    assert r.status_code == 422


def test_nivel_invalido():
    assert cliente.post("/api/partidas", json={"nivel": 9}).status_code == 400


def test_partida_inexistente():
    assert cliente.get("/api/partidas/nada").status_code == 404


def test_nivel_siguiente_sin_completar(partida):
    r = cliente.post(f"/api/partidas/{partida['id']}/nivel-siguiente")
    assert r.status_code == 409


def test_borrar(partida):
    assert cliente.delete(f"/api/partidas/{partida['id']}").status_code == 204
    assert cliente.get(f"/api/partidas/{partida['id']}").status_code == 404


def test_maquinas():
    nombres = [m["nombre"] for m in cliente.get("/api/maquinas").json()]
    assert nombres == ["mov", "cubo1", "cubo2", "cubo3", "vidas"]


def test_quintupla_mealy():
    m = cliente.get("/api/maquinas/mov").json()
    assert m["tipo"] == "Mealy" and m["q0"] == "q0" and len(m["Q"]) == 28
    assert m["sigma_e"] == ["w", "a", "s", "d"]
    assert m["f"]["q1"]["a"] == "q0" and m["g"]["q1"]["a"] == CAIDA


def test_quintupla_moore():
    m = cliente.get("/api/maquinas/cubo2").json()
    assert m["g"] == {"q0": "A", "q1": "B", "q2": "C"}
    assert m["finales"] == ["q2"]


def test_traducir():
    r = cliente.post("/api/maquinas/vidas/traducir", json={"palabra": "pXpXX"}).json()
    assert r["salida"] == ["3", "2", "2", "1", "0"] and r["estado_final"] == "GO"


def test_traducir_simbolo_invalido():
    r = cliente.post("/api/maquinas/mov/traducir", json={"palabra": "sz"})
    assert r.status_code == 400


def test_piramide():
    p = cliente.get("/api/piramide").json()
    assert p["filas"] == 7 and len(p["cubos"]) == 28
    assert p["cubos"][4] == {"numero": 4, "fila": 2, "columna": 1}
