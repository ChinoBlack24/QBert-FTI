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
