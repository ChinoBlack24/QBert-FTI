"""Tests de la integración (4.5) y de la intersección (3.3)."""

import random

import pytest

from automatas import (CAIDA, CANTIDAD_CUBOS, DESPLAZAMIENTOS, NIVELES, Partida,
                       crear_cubo_sobre_salida, fila_columna, numero_cubo)

INVERSA = {"w": "s", "s": "w", "a": "d", "d": "a"}


def recorrido_cerrado():
    """Recorrido en profundidad que pisa todos los cubos sin caerse y vuelve a la cima."""
    visitados, teclas = {0}, []

    def dfs(i):
        r, k = fila_columna(i)
        for e, (dr, dk) in DESPLAZAMIENTOS.items():
            j = numero_cubo(r + dr, k + dk)
            if j is not None and j not in visitados:
                visitados.add(j)
                teclas.append(e)
                dfs(j)
                teclas.append(INVERSA[e])

    dfs(0)
    return "".join(teclas)


def test_saltar_actualiza_las_tres_maquinas():
    p = Partida()
    paso = p.saltar("s")
    assert paso.mov == ("q0", "s", "q1", "1")
    assert paso.cubo == (1, "q0", "q1", "B")
    assert paso.vidas == ("V3", "p", "V3", "3")
    assert p.color(1) == "B" and p.posicion() == 1


def test_caida_no_pinta_y_resta_vida():
    p = Partida()
    paso = p.saltar("w")  # desde la cima, arriba-derecha: se cae
    assert paso.cubo is None
    assert paso.vidas == ("V3", CAIDA, "V2", "2")
    assert p.posicion() == 0
    assert all(p.color(i) == "A" for i in range(CANTIDAD_CUBOS))


def test_tres_caidas_es_game_over_y_no_acepta_mas_saltos():
    p = Partida()
    p.jugar("www")
    assert p.game_over()
    assert p.saltar("s") is None


def test_tecla_invalida():
    with pytest.raises(ValueError):
        Partida().saltar("x")


def test_nivel_1_se_completa_con_un_recorrido():
    p = Partida(1)
    p.jugar(recorrido_cerrado())
    assert p.nivel_completo()
    assert p.cantidad_vidas() == 3


def test_nivel_2_necesita_dos_recorridos():
    p = Partida(2)
    r = recorrido_cerrado()
    p.jugar(r)
    assert not p.nivel_completo()
    p.jugar(r)
    assert p.nivel_completo()


def test_nivel_3_pisar_dos_veces_revierte():
    p = Partida(3)
    p.jugar("sw")  # pisa 1 y después 0
    assert p.color(1) == "B"
    p.jugar("ss")  # vuelve a pisar 1 y baja a 3
    assert p.color(1) == "A"


def test_vidas_se_conservan_entre_niveles():
    p = Partida(1)
    p.saltar("w")
    p.jugar(recorrido_cerrado())
    assert p.nivel_completo()
    p.empezar_nivel(2)
    assert p.cantidad_vidas() == 2 and p.cubos_en_objetivo() == 0


@pytest.mark.parametrize("nivel", NIVELES)
def test_integracion_equivale_a_cubos_sobre_la_salida_de_la_mealy(nivel):
    """
    Lo que hace Partida (solo el cubo s lee p) da el mismo estado que el AF_i de
    4.5 leyendo la palabra completa de salida de la Mealy.
    """
    azar = random.Random(nivel)
    for _ in range(20):
        p = Partida(nivel)
        p.jugar("".join(azar.choice("wasd") for _ in range(150)))
        for i in range(CANTIDAD_CUBOS):
            af = crear_cubo_sobre_salida(nivel, i)
            *_, final = af.read_input_stepwise(p.salida_mealy, ignore_rejection=True)
            assert final == p.estados_cubos[i]


@pytest.mark.parametrize("nivel", NIVELES)
def test_interseccion_de_automata_lib_equivale_a_revisar_cada_cubo(nivel):
    cubos = [0, 1, 2, 4]
    afds = [crear_cubo_sobre_salida(nivel, i) for i in cubos]
    producto = afds[0]
    for a in afds[1:]:
        producto = producto & a
    azar = random.Random(100 + nivel)
    for _ in range(200):
        palabra = [azar.choice(["0", "1", "2", "4", "7", CAIDA]) for _ in range(azar.randint(0, 12))]
        assert producto.accepts_input(palabra) == all(a.accepts_input(palabra) for a in afds)


# --- bola (eventos tic) -------------------------------------------------------
def test_la_bola_empieza_fuera():
    p = Partida()
    assert p.estado_bola == "bF" and p.posicion_bola() is None


def test_tic_mueve_solo_la_bola():
    p = Partida()
    p.saltar("s")                    # Q*bert al cubo 1
    paso = p.tic("d")                # la bola entra a la cima
    assert paso.bola == ("bF", "d", "b0", "0")
    assert not paso.choque and paso.vidas is None
    assert p.posicion() == 1 and p.posicion_bola() == 0
    assert p.salida_mealy == ["1"]   # la Mealy no leyó nada en el tic


def test_choque_porque_la_bola_cae_sobre_qbert():
    p = Partida()
    p.saltar("s")                    # Q*bert en 1
    p.tic("s")                       # bola en 0
    paso = p.tic("s")                # bola baja a 1
    assert paso.choque
    assert paso.vidas == ("V3", CAIDA, "V2", "2")
    assert p.posicion() == 1         # nadie se reinicia


def test_choque_porque_qbert_salta_al_cubo_de_la_bola():
    p = Partida()
    p.jugar("sd")                    # Q*bert en 4
    p.tic("s")                       # bola en 0
    p.tic("d")                       # bola en 2
    paso = p.saltar("w")             # Q*bert de 4 a 2
    assert paso.choque and paso.vidas.e == CAIDA
    assert p.cantidad_vidas() == 2
    assert p.color(2) == "B"         # el cubo igual se pinta


def test_la_bola_que_entra_cae_sobre_qbert_si_esta_en_la_cima():
    p = Partida()
    paso = p.tic("s")                # Q*bert sigue en 0 y la bola entra a 0
    assert paso.choque and p.cantidad_vidas() == 2


def test_el_choque_retira_la_bola():
    p = Partida()
    p.saltar("s")                    # Q*bert en 1
    p.tic("s")                       # bola en 0
    paso = p.tic("s")                # bola cae en 1: choque
    assert paso.retiro_bola == ("b1", CAIDA, "bF", "F")
    assert p.estado_bola == "bF" and p.posicion_bola() is None
    p.tic("s")                       # vuelve a entrar por la cima, lejos de Q*bert
    assert p.cantidad_vidas() == 2


def test_saltar_sobre_la_bola_la_retira():
    p = Partida()
    p.jugar("sd")                    # Q*bert en 4
    p.tic("s")
    p.tic("d")                       # bola en 2
    paso = p.saltar("w")             # Q*bert a 2: choque
    assert paso.retiro_bola is not None and p.estado_bola == "bF"


def test_una_caida_tambien_retira_la_bola():
    p = Partida()
    p.saltar("s")
    p.tic("s")                       # bola en 0
    paso = p.saltar("a")             # se cae
    assert paso.retiro_bola == ("b0", CAIDA, "bF", "F")
    assert p.estado_bola == "bF"


def test_sin_perder_vida_la_bola_no_se_retira():
    p = Partida()
    p.saltar("s")
    p.tic("d")                       # bola en 0
    paso = p.saltar("d")             # Q*bert a 4, sin choque
    assert paso.retiro_bola is None and p.estado_bola == "b0"


def test_el_reloj_no_puede_mandar_x():
    with pytest.raises(ValueError):
        Partida().tic(CAIDA)


def test_caida_y_bola_en_el_mismo_lugar_resta_una_sola_vida():
    p = Partida()
    p.saltar("s")                    # Q*bert en 1
    p.tic("s")                       # bola en 0
    paso = p.saltar("a")             # Q*bert se cae y vuelve a q0, donde está la bola
    assert not paso.choque           # su salida es X, no el cubo 0
    assert p.cantidad_vidas() == 2


def test_tic_con_la_partida_terminada():
    p = Partida()
    p.jugar("www")
    assert p.game_over() and p.tic("s") is None


def test_tic_direccion_invalida():
    with pytest.raises(ValueError):
        Partida().tic("w")


def test_el_nivel_nuevo_saca_a_la_bola():
    p = Partida(1)
    p.saltar("s")
    p.tic("s")
    p.jugar("w" + recorrido_cerrado())
    p.pasar_de_nivel()
    assert p.estado_bola == "bF"


def test_sin_tics_la_bola_no_molesta():
    """Las pruebas de nivel de arriba no usan tics: la bola queda fuera."""
    p = Partida(2)
    p.jugar(recorrido_cerrado() * 2)
    assert p.nivel_completo() and p.cantidad_vidas() == 3
