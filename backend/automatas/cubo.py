"""
4.3 Máquina de color de cubo (Moore). Hay una por cubo, todas iguales dentro
de un nivel.

    ΣE = {p}        "me pisaron"
    ΣS = colores    A, B (y C en el nivel 2)

El estado del color objetivo es final (*): el apunte (6 Máquinas Secuenciales)
muestra que una Moore puede funcionar como AF si se asocian estados finales a
ciertas salidas.
"""

from .mef import Moore, leer_tabla_moore

TABLA_NIVEL_1 = """
Q/ΣS    p
→q0/A   q1
q1/B*   q1
"""

TABLA_NIVEL_2 = """
Q/ΣS    p
→q0/A   q1
q1/B    q2
q2/C*   q2
"""

TABLA_NIVEL_3 = """
Q/ΣS    p
→q0/A   q1
q1/B*   q0
"""

NIVELES_CUBO = {
    1: ("una pisada alcanza (A -> B -> B)", TABLA_NIVEL_1),
    2: ("hacen falta dos pisadas (A -> B -> C -> C)", TABLA_NIVEL_2),
    3: ("pisar un cubo terminado lo revierte (A <-> B)", TABLA_NIVEL_3),
}
NIVELES = tuple(NIVELES_CUBO)


def descripcion_nivel(nivel: int) -> str:
    return NIVELES_CUBO[nivel][0]


def crear_cubo(nivel: int) -> Moore:
    """MEF_cubo^(nivel) del informe."""
    if nivel not in NIVELES_CUBO:
        raise ValueError(f"nivel debe ser uno de {NIVELES}")
    f, g, q0, finales = leer_tabla_moore(NIVELES_CUBO[nivel][1])
    return Moore(f"cubo nivel {nivel}", f, g, set(g.values()), q0, finales)
