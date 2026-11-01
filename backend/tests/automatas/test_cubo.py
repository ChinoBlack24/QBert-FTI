"""Tests de la Moore de color de cubo (4.3)."""

import pytest

from automatas import NIVELES, crear_cubo


@pytest.mark.parametrize("nivel, salida", [
    (1, ["B", "B", "B"]),
    (2, ["B", "C", "C"]),
    (3, ["B", "A", "B"]),
])
def test_salida_del_estado_destino(nivel, salida):
    cubo = crear_cubo(nivel)
    assert cubo.g[cubo.q0] == "A"
    assert cubo.traducir("ppp")[0] == salida


@pytest.mark.parametrize("nivel, pisadas_para_objetivo", [(1, 1), (2, 2), (3, 1)])
def test_estado_final_es_el_objetivo(nivel, pisadas_para_objetivo):
    cubo = crear_cubo(nivel)
    assert len(cubo.finales) == 1
    assert not cubo.f.accepts_input("p" * (pisadas_para_objetivo - 1))
    assert cubo.f.accepts_input("p" * pisadas_para_objetivo)


def test_nivel_3_acepta_cantidad_impar_de_pisadas():
    cubo = crear_cubo(3)
    for n in range(10):
        assert cubo.f.accepts_input("p" * n) == (n % 2 == 1)


def test_nivel_inexistente():
    with pytest.raises(ValueError):
        crear_cubo(max(NIVELES) + 1)


@pytest.mark.parametrize("nivel", NIVELES)
def test_tabla_se_imprime(nivel):
    assert "→q0/A" in crear_cubo(nivel).tabla()
