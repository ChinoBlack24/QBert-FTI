"""Tests de la Moore de vidas (4.4)."""

from automatas import CAIDA, crear_vidas


def test_salida_es_la_cantidad_de_vidas():
    v = crear_vidas()
    assert v.g[v.q0] == "3"
    assert v.traducir("pXpXX")[0] == ["3", "2", "2", "1", "0"]


def test_pisar_no_cambia_las_vidas():
    v = crear_vidas()
    assert v.traducir("pppp") == (["3"] * 4, "V3")


def test_game_over_es_absorbente():
    v = crear_vidas()
    _, q = v.traducir(CAIDA * 3)
    assert q == "GO"
    assert v.traducir("pXpX" * 3, q)[1] == "GO"
