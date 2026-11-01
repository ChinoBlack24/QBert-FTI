"""Tests de la MEF genérica y de la lectura de tablas."""

import pytest

from automatas import NIVELES, Mealy, Moore, crear_cubo, crear_movimiento, crear_vidas
from automatas.mef import leer_tabla_mealy, leer_tabla_moore

MAQUINAS = [crear_movimiento, crear_vidas] + [lambda n=n: crear_cubo(n) for n in NIVELES]


@pytest.mark.parametrize("crear", MAQUINAS)
def test_tabla_impresa_se_puede_volver_a_leer(crear):
    """tabla() escribe el mismo formato que se usa en el código para definir la máquina."""
    m = crear()
    leer = leer_tabla_mealy if isinstance(m, Mealy) else leer_tabla_moore
    f, g, q0, finales = leer(m.tabla())
    assert f == {q: dict(m.f.transitions[q]) for q in m.Q}
    assert g == m.g
    assert q0 == m.q0
    assert finales == m.finales


def test_falta_una_celda_de_g():
    with pytest.raises(ValueError, match="no está definida"):
        Mealy("rota", f={"q0": {"a": "q0"}}, g={"q0": {}}, sigma_s={"1"}, q0="q0")


def test_salida_fuera_de_sigma_s():
    with pytest.raises(ValueError, match="no pertenece a ΣS"):
        Moore("rota", f={"q0": {"a": "q0"}}, g={"q0": "Z"}, sigma_s={"A"}, q0="q0")


def test_tabla_sin_estado_inicial():
    with pytest.raises(ValueError, match="estado inicial"):
        leer_tabla_moore("Q/ΣS p\nq0/A q0")


def test_estado_inicial_inexistente():
    with pytest.raises(ValueError):
        crear_movimiento().traducir("s", "q99")


def test_explicacion_de_la_salida_segun_el_modelo():
    """Mealy: g(q, e).  Moore: g del estado al que se transiciona."""
    [t] = crear_movimiento().traza("s")
    assert crear_movimiento().explicar_salida(t) == "g(q0, s) = 1"
    [t] = crear_vidas().traza("X")
    assert crear_vidas().explicar_salida(t) == "g(V2) = 2"
