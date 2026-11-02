"""
Traducción de los objetos de automatas/ a los esquemas JSON de la API.
Es el único lugar donde se juntan las dos cosas.
"""

from __future__ import annotations

import automatas
from automatas import MEF, Mealy, Partida

from .esquemas import (ColorNivel, EstadoPartida, Maquina, Paso, PasoCubo, PasoTic,
                       ResumenMaquina, Transicion)


def orden_simbolos(s: str):
    return (0, int(s)) if s.isdigit() else (1, s)


def transicion(t: automatas.Transicion) -> Transicion:
    return Transicion(**t._asdict())


def estado(id_: str, p: Partida) -> EstadoPartida:
    return EstadoPartida(
        id=id_,
        nivel=p.nivel,
        ultimo_nivel=p.ultimo_nivel(),
        estado_movimiento=p.estado_mov,
        posicion=p.posicion(),
        estados_cubos=list(p.estados_cubos),
        colores=[p.color(i) for i in range(automatas.CANTIDAD_CUBOS)],
        colores_nivel=[ColorNivel(estado=q, color=p.cubo.g[q], objetivo=q in p.cubo.finales)
                       for q in p.cubo.orden],
        cubos_en_objetivo=p.cubos_en_objetivo(),
        estado_vidas=p.estado_vidas,
        vidas=p.cantidad_vidas(),
        estado_bola=p.estado_bola,
        posicion_bola=p.posicion_bola(),
        salida_mealy=list(p.salida_mealy),
        nivel_completo=p.nivel_completo(),
        game_over=p.game_over(),
    )


def paso(p: automatas.Paso) -> Paso:
    return Paso(
        movimiento=transicion(p.mov),
        cubo=PasoCubo(**p.cubo._asdict()) if p.cubo else None,
        choque=p.choque,
        vidas=transicion(p.vidas),
        retiro_bola=transicion(p.retiro_bola) if p.retiro_bola else None,
    )


def paso_tic(p: automatas.PasoTic) -> PasoTic:
    return PasoTic(
        bola=transicion(p.bola),
        choque=p.choque,
        vidas=transicion(p.vidas) if p.vidas else None,
        retiro_bola=transicion(p.retiro_bola) if p.retiro_bola else None,
    )


def resumen(nombre: str, m: MEF) -> ResumenMaquina:
    return ResumenMaquina(nombre=nombre, tipo=m.tipo, cantidad_estados=len(m.Q),
                          sigma_e=m.simbolos, sigma_s=sorted(m.sigma_s, key=orden_simbolos))


def maquina(nombre: str, m: MEF) -> Maquina:
    return Maquina(
        nombre=nombre,
        tipo=m.tipo,
        Q=m.orden,
        sigma_e=m.simbolos,
        sigma_s=sorted(m.sigma_s, key=orden_simbolos),
        q0=m.q0,
        finales=[q for q in m.orden if q in m.finales],
        f={q: {e: m.f.transitions[q][e] for e in m.simbolos} for q in m.orden},
        g={q: (dict(m.g[q]) if isinstance(m, Mealy) else m.g[q]) for q in m.orden},
        tabla=m.tabla(),
    )
