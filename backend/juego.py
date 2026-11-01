"""
Demo jugable de Q*bert con las máquinas del informe (ventana con pygame).
Toda la lógica está en partida.py; este archivo solo dibuja.

Controles:  W arriba-derecha   A arriba-izquierda
            S abajo-izquierda  D abajo-derecha
            ENTER siguiente nivel   R reiniciar   ESC salir
"""

import sys

import pygame

from automatas import CANTIDAD_CUBOS, Partida, fila_columna

ANCHO, ALTO = 1100, 680
LADO = 72          # ancho de la cara superior de un cubo
ALTO_CARA = 40     # alto de las caras laterales

FONDO = (18, 20, 34)
TEXTO = (230, 230, 240)
TENUE = (140, 145, 170)
RESALTE = (255, 196, 70)
PANEL = (28, 31, 52)

COLORES = {"A": (232, 200, 90), "B": (70, 140, 230), "C": (80, 200, 120)}
CARA_IZQ = (56, 92, 110)
CARA_DER = (34, 58, 74)
QBERT = (245, 120, 40)

ORIGEN_X, ORIGEN_Y = 330, 70  # centro de la cara superior del cubo de la cima


def centro(i):
    r, k = fila_columna(i)
    x = ORIGEN_X + (k - r / 2) * LADO
    y = ORIGEN_Y + r * (LADO / 2 + ALTO_CARA)
    return x, y


def dibujar_cubo(pantalla, i, color):
    x, y = centro(i)
    m, h = LADO / 2, LADO / 4
    arriba = [(x, y - h), (x + m, y), (x, y + h), (x - m, y)]
    izq = [(x - m, y), (x, y + h), (x, y + h + ALTO_CARA), (x - m, y + ALTO_CARA)]
    der = [(x + m, y), (x, y + h), (x, y + h + ALTO_CARA), (x + m, y + ALTO_CARA)]
    pygame.draw.polygon(pantalla, CARA_IZQ, izq)
    pygame.draw.polygon(pantalla, CARA_DER, der)
    pygame.draw.polygon(pantalla, color, arriba)
    pygame.draw.polygon(pantalla, FONDO, arriba, 1)


def dibujar_qbert(pantalla, i):
    x, y = centro(i)
    y -= 14
    pygame.draw.circle(pantalla, QBERT, (x, y), 15)
    pygame.draw.circle(pantalla, QBERT, (x + 13, y + 6), 7)  # trompa
    pygame.draw.circle(pantalla, (255, 255, 255), (x + 2, y - 4), 5)
    pygame.draw.circle(pantalla, (0, 0, 0), (x + 4, y - 4), 2)


def texto(pantalla, fuente, contenido, x, y, color=TEXTO):
    pantalla.blit(fuente.render(contenido, True, color), (x, y))


def dibujar_panel(pantalla, fuentes, partida):
    grande, normal, chica = fuentes
    x0 = 680
    pygame.draw.rect(pantalla, PANEL, (x0 - 20, 0, ANCHO - x0 + 20, ALTO))

    texto(pantalla, grande, f"Nivel {partida.nivel}", x0, 24)
    texto(pantalla, normal, f"Vidas: {partida.cantidad_vidas()}", x0, 70)
    texto(pantalla, normal, f"Cubos en el color objetivo: {partida.cubos_en_objetivo()}/{CANTIDAD_CUBOS}", x0, 100)

    texto(pantalla, normal, "Colores de este nivel:", x0, 145)
    y = 175
    for q, c in partida.cubo.g.items():
        pygame.draw.rect(pantalla, COLORES[c], (x0, y, 18, 18))
        final = "  (objetivo)" if q in partida.cubo.finales else ""
        texto(pantalla, chica, f"{q}/{c}{final}", x0 + 28, y)
        y += 26

    texto(pantalla, normal, "Último salto:", x0, 270)
    if partida.ultimo_paso:
        for n, linea in enumerate(partida.ultimo_paso.lineas()):
            texto(pantalla, chica, linea, x0, 300 + n * 24, RESALTE)
    else:
        texto(pantalla, chica, "(todavía ninguno)", x0, 300, TENUE)

    ayuda = [
        "W  arriba-derecha     A  arriba-izquierda",
        "S  abajo-izquierda    D  abajo-derecha",
        "ENTER siguiente nivel   R reiniciar   ESC salir",
    ]
    for n, linea in enumerate(ayuda):
        texto(pantalla, chica, linea, x0, ALTO - 90 + n * 24, TENUE)


def dibujar_mensaje(pantalla, fuente, mensaje):
    render = fuente.render(mensaje, True, RESALTE)
    rect = render.get_rect(center=(ORIGEN_X, ALTO - 50))
    pantalla.blit(render, rect)


def dibujar(pantalla, fuentes, partida):
    pantalla.fill(FONDO)
    for i in range(CANTIDAD_CUBOS):
        dibujar_cubo(pantalla, i, COLORES[partida.color(i)])
    if not partida.game_over():
        dibujar_qbert(pantalla, partida.posicion())
    dibujar_panel(pantalla, fuentes, partida)

    if partida.game_over():
        dibujar_mensaje(pantalla, fuentes[0], "GAME OVER  -  R para reiniciar")
    elif partida.nivel_completo():
        if partida.ultimo_nivel():
            dibujar_mensaje(pantalla, fuentes[0], "¡Ganaste todos los niveles!  R para reiniciar")
        else:
            dibujar_mensaje(pantalla, fuentes[0], "¡Nivel completo!  ENTER para seguir")


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Q*bert con autómatas - FTI Grupo 1")
    fuentes = (pygame.font.SysFont(None, 40), pygame.font.SysFont(None, 28),
               pygame.font.SysFont(None, 23))
    reloj = pygame.time.Clock()
    partida = Partida()
    teclas = {pygame.K_w: "w", pygame.K_a: "a", pygame.K_s: "s", pygame.K_d: "d"}

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type != pygame.KEYDOWN:
                continue
            if evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif evento.key in teclas:
                partida.saltar(teclas[evento.key])
            elif evento.key == pygame.K_RETURN and partida.nivel_completo() and not partida.ultimo_nivel():
                partida.pasar_de_nivel()
            elif evento.key == pygame.K_r:
                partida = Partida()

        dibujar(pantalla, fuentes, partida)
        pygame.display.flip()
        reloj.tick(30)


if __name__ == "__main__":
    main()
