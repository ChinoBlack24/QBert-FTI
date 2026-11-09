"""
Lógica de los autómatas del proyecto Q*bert (FTI, Grupo 1).

Este paquete es el modelo teórico del informe y nada más: no sabe que existe
una API, una consola ni un frontend. Solo depende de automata-lib.

    mef.py          MEF = <Q, ΣE, ΣS, f, g>, Mealy y Moore
    movimiento.py   4.2 Mealy de movimiento
    cubo.py         4.3 Moore de color de cubo (una tabla por nivel)
    vidas.py        4.4 Moore de vidas
    bola.py         Moore del enemigo (la bola)
    partida.py      4.5 conexión entre las máquinas (h', AF_i): saltos y tics
    piramide.py     geometría de la pirámide (no es una máquina)

Quien use la lógica (api/, juego.py) importa desde acá:

    from automatas import Partida, crear_movimiento
"""

from .bola import FUERA, crear_bola
from .cubo import NIVELES, crear_cubo, descripcion_nivel
from .mef import MEF, Mealy, Moore, Transicion
from .movimiento import (CAIDA, CUBO_DEL_ESTADO, ESTADO_DEL_CUBO, SIGMA_S_MOVIMIENTO,
                         crear_movimiento)
from .partida import Partida, Paso, PasoCubo, PasoTic, crear_cubo_sobre_salida, entrada_vidas
from .piramide import (CANTIDAD_CUBOS, DESPLAZAMIENTOS, FILAS, fila_columna,
                       numero_cubo)
from .vidas import crear_vidas

# Las máquinas por nombre corto (las usa la API).
MAQUINAS = {
    "mov": crear_movimiento,
    "cubo1": lambda: crear_cubo(1),
    "cubo2": lambda: crear_cubo(2),
    "cubo3": lambda: crear_cubo(3),
    "vidas": crear_vidas,
    "bola": crear_bola,
}

__all__ = [
    # MEF genérica
    "MEF", "Mealy", "Moore", "Transicion",
    # 4.2
    "CAIDA", "SIGMA_S_MOVIMIENTO", "ESTADO_DEL_CUBO", "CUBO_DEL_ESTADO", "crear_movimiento",
    # 4.3
    "NIVELES", "crear_cubo", "descripcion_nivel",
    # 4.4
    "crear_vidas",
    # bola
    "FUERA", "crear_bola",
    # 4.5
    "Partida", "Paso", "PasoCubo", "PasoTic", "entrada_vidas", "crear_cubo_sobre_salida",
    # pirámide
    "FILAS", "CANTIDAD_CUBOS", "DESPLAZAMIENTOS", "fila_columna", "numero_cubo",
    "MAQUINAS",
]
