"""Tests de la Moore de la bola (enemigo)."""

import pytest

from automatas import CAIDA, CANTIDAD_CUBOS, FUERA, crear_bola, crear_movimiento


def test_empieza_fuera_y_entra_por_la_cima():
    b = crear_bola()
    assert b.q0 == "bF" and b.g["bF"] == FUERA
    assert b.paso("bF", "s") == ("b0", "0")
    assert b.paso("bF", "d") == ("b0", "0")


def test_coincide_con_la_mealy_de_movimiento_restringida_a_s_y_d():
    """Donde Q*bert baja sin caerse, la bola hace exactamente lo mismo."""
    mov, bola = crear_movimiento(), crear_bola()
    for i in range(CANTIDAD_CUBOS):
        for e in "sd":
            destino_qbert, salida = mov.paso(f"q{i}", e)
            destino_bola, _ = bola.paso(f"b{i}", e)
            if salida == CAIDA:
                assert destino_bola == "bF", f"(b{i}, {e})"
            else:
                assert destino_bola == "b" + destino_qbert[1:], f"(b{i}, {e})"


def test_salida_es_el_cubo_del_estado():
    b = crear_bola()
    assert all(b.g[f"b{i}"] == str(i) for i in range(CANTIDAD_CUBOS))


def test_solo_baja_o_se_retira():
    assert crear_bola().sigma_e == {"s", "d", CAIDA}


def test_con_x_sale_de_la_piramide_desde_cualquier_estado():
    b = crear_bola()
    assert all(b.paso(q, CAIDA) == ("bF", FUERA) for q in b.Q)


@pytest.mark.parametrize("palabra, salida", [
    ("s", ["0"]),
    ("sss", ["0", "1", "3"]),
    ("sdd", ["0", "2", "5"]),
    # entra, baja 6 filas, sale, vuelve a entrar
    ("ssssssss", ["0", "1", "3", "6", "10", "15", "21", FUERA]),
    ("sssssssss", ["0", "1", "3", "6", "10", "15", "21", FUERA, "0"]),
])
def test_traducciones(palabra, salida):
    assert crear_bola().traducir(palabra)[0] == salida


def test_moore_misma_longitud():
    salida, _ = crear_bola().traducir("sdsdsdsdsd")
    assert len(salida) == 10
