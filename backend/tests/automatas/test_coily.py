"""Tests de las fases y transiciones de la Mealy de Coily."""

from automatas import CAIDA, SALTO_DISCO, crear_coily


def test_aparece_fuera_como_huevo_en_la_cima():
    coily = crear_coily()
    assert coily.q0 == "fuera"
    assert coily.paso("fuera", "S") == ("h0", "H0")
    assert coily.paso("fuera", "D") == ("h0", "H0")


def test_huevo_baja_con_la_misma_geometria_que_la_bola():
    coily = crear_coily()
    estado = coily.paso("fuera", "S")[0]
    for destino in ("h1", "h3", "h6", "h10", "h15"):
        estado, salida = coily.paso(estado, "S")
        assert estado == destino
        assert salida == f"H{destino[1:]}"
    estado, salida = coily.paso(estado, "S")
    assert (estado, salida) == ("c21", "C21")


def test_en_persecucion_copia_la_tecla_desde_su_propia_posicion():
    coily = crear_coily()
    assert coily.paso("c1", "s") == ("c3", "C3")
    assert coily.paso("c1", "w") == ("c0", "C0")


def test_coily_se_cae_si_su_movimiento_sale_de_la_piramide():
    assert crear_coily().paso("c0", "w") == ("fuera", CAIDA)


def test_caida_y_disco_lo_retirarían_desde_cualquier_fase():
    coily = crear_coily()
    for estado in ("fuera", "h4", "c4"):
        assert coily.paso(estado, CAIDA) == ("fuera", "N")
        assert coily.paso(estado, SALTO_DISCO) == ("fuera", "N")
