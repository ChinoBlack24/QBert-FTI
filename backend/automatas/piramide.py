"""
Geometría de la pirámide: 7 filas, 28 cubos.

No es una máquina. La usan la consola y la ventana para dibujar, y los tests
para comprobar que la tabla de movimiento es correcta.

Numeración: la fila r (0..6) tiene r+1 cubos y el cubo 0 es la cima.

            0
          1   2
        3   4   5
      6   7   8   9
    ...
"""

FILAS = 7
CANTIDAD_CUBOS = FILAS * (FILAS + 1) // 2  # 1 + 2 + ... + 7 = 28

# Cómo cambia (fila, columna) con cada tecla.
#     w: arriba-derecha   a: arriba-izquierda   s: abajo-izquierda   d: abajo-derecha
DESPLAZAMIENTOS = {"w": (-1, 0), "a": (-1, -1), "s": (1, 0), "d": (1, 1)}


def fila_columna(i: int) -> tuple[int, int]:
    """Número de cubo -> (fila, columna)."""
    r = 0
    while i > r:
        i -= r + 1
        r += 1
    return r, i


def numero_cubo(r: int, k: int) -> int | None:
    """(fila, columna) -> número de cubo, o None si está fuera de la pirámide."""
    if 0 <= r < FILAS and 0 <= k <= r:
        return r * (r + 1) // 2 + k
    return None
