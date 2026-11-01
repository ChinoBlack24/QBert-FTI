"""Tests de la Mealy de movimiento (4.2)."""

import pytest

from automatas import (CAIDA, CANTIDAD_CUBOS, DESPLAZAMIENTOS, crear_movimiento, fila_columna,
                       numero_cubo)


def test_tabla_coincide_con_la_geometria():
    """Cada una de las 28 x 4 celdas se compara con el desplazamiento en la pirámide."""
    m = crear_movimiento()
    for i in range(CANTIDAD_CUBOS):
        r, k = fila_columna(i)
        for e, (dr, dk) in DESPLAZAMIENTOS.items():
            destino = numero_cubo(r + dr, k + dk)
            esperado = ("q0", CAIDA) if destino is None else (f"q{destino}", str(destino))
            assert m.paso(f"q{i}", e) == esperado, f"celda (q{i}, {e})"


def test_es_completa():
    m = crear_movimiento()
    assert len(m.Q) == CANTIDAD_CUBOS
    assert m.q0 == "q0"
    assert m.sigma_e == {"w", "a", "s", "d"}
    assert all(set(m.f.transitions[q]) == m.sigma_e for q in m.Q)


def test_salida_misma_longitud_que_entrada():
    m = crear_movimiento()
    for palabra in ["", "s", "sdw", "wwww", "ssssssss"]:
        salida, _ = m.traducir(palabra)
        assert len(salida) == len(palabra)


def test_mismo_destino_distinta_salida():
    """El argumento de 4.2: a q0 se llega saltando a la cima o cayéndose."""
    m = crear_movimiento()
    assert m.paso("q1", "w") == ("q0", "0")
    assert m.paso("q1", "a") == ("q0", CAIDA)


@pytest.mark.parametrize("palabra, salida, final", [
    ("sd", ["1", "4"], "q4"),
    ("sdw", ["1", "4", "2"], "q2"),
    ("a", [CAIDA], "q0"),
    ("ssssss", ["1", "3", "6", "10", "15", "21"], "q21"),
    ("sssssss", ["1", "3", "6", "10", "15", "21", CAIDA], "q0"),
])
def test_traducciones(palabra, salida, final):
    assert crear_movimiento().traducir(palabra) == (salida, final)


def test_simbolo_fuera_del_alfabeto():
    with pytest.raises(ValueError):
        crear_movimiento().traducir("sz")
