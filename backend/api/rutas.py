"""
Rutas HTTP. Cada una busca o crea objetos de automatas/, llama a sus métodos
y devuelve el resultado convertido a esquema. No hay lógica de autómatas acá.
"""

from __future__ import annotations

import random
import uuid

from fastapi import APIRouter, HTTPException

from automatas import FILAS, CANTIDAD_CUBOS, MAQUINAS, NIVELES, Partida, fila_columna

from . import conversion as conv
from .esquemas import (Cubo, EstadoPartida, Maquina, NombreMaquina, NuevaPartida, Piramide,
                       ResultadoSalto, ResultadoTic, ResultadoTicCoily, ResultadoTraduccion,
                       ResumenMaquina, Salto, Tic, Traduccion)

assert set(NombreMaquina.__args__) == set(MAQUINAS)


router = APIRouter(prefix="/api")

# Partidas en curso, por id. En memoria: si se reinicia el servidor, se pierden.
partidas: dict[str, Partida] = {}


def _buscar(id_: str) -> Partida:
    if id_ not in partidas:
        raise HTTPException(404, f"no existe la partida '{id_}'")
    return partidas[id_]


@router.post("/partidas", status_code=201, response_model=EstadoPartida,
             operation_id="crearPartida", tags=["partidas"])
def crear_partida(pedido: NuevaPartida | None = None):
    nivel = (pedido or NuevaPartida()).nivel
    if nivel not in NIVELES:
        raise HTTPException(400, f"nivel debe ser uno de {list(NIVELES)}")
    id_ = uuid.uuid4().hex
    partidas[id_] = Partida(nivel)
    return conv.estado(id_, partidas[id_])


@router.get("/partidas/{id}", response_model=EstadoPartida,
            operation_id="obtenerPartida", tags=["partidas"])
def obtener_partida(id: str):
    return conv.estado(id, _buscar(id))


@router.delete("/partidas/{id}", status_code=204, operation_id="borrarPartida", tags=["partidas"])
def borrar_partida(id: str):
    _buscar(id)
    del partidas[id]


@router.post("/partidas/{id}/saltos", response_model=ResultadoSalto,
             operation_id="saltar", tags=["partidas"])
def saltar(id: str, salto: Salto):
    p = _buscar(id)
    paso = p.saltar(salto.tecla)
    return ResultadoSalto(paso=conv.paso(paso) if paso else None, estado=conv.estado(id, p))


@router.post("/partidas/{id}/tic", response_model=ResultadoTic,
             operation_id="tic", tags=["partidas"])
def tic(id: str, pedido: Tic | None = None):
    p = _buscar(id)
    # La moneda que escribe la palabra de entrada de la bola. Está acá, fuera de
    # automatas/, porque no es parte de ninguna máquina.
    direccion = (pedido.direccion if pedido else None) or random.choice("sd")
    paso = p.tic(direccion)
    return ResultadoTic(paso=conv.paso_tic(paso) if paso else None, estado=conv.estado(id, p))


@router.post("/partidas/{id}/tic-coily", response_model=ResultadoTicCoily,
             operation_id="ticCoily", tags=["partidas"])
def tic_coily(id: str, pedido: Tic | None = None):
    p = _buscar(id)
    # La elección aleatoria de la bajada y la espera hasta el spawn pertenecen al juego,
    # no a la MEF de Coily.
    direccion = (pedido.direccion if pedido else None) or random.choice("sd")
    paso = p.tic_coily(direccion)
    return ResultadoTicCoily(
        paso=conv.paso_tic_coily(paso) if paso else None,
        estado=conv.estado(id, p),
    )


@router.post("/partidas/{id}/nivel-siguiente", response_model=EstadoPartida,
             operation_id="pasarDeNivel", tags=["partidas"])
def pasar_de_nivel(id: str):
    p = _buscar(id)
    try:
        p.pasar_de_nivel()
    except ValueError as e:
        raise HTTPException(409, str(e))
    return conv.estado(id, p)


@router.get("/maquinas", response_model=list[ResumenMaquina],
            operation_id="listarMaquinas", tags=["maquinas"])
def listar_maquinas():
    return [conv.resumen(nombre, crear()) for nombre, crear in MAQUINAS.items()]


@router.get("/maquinas/{nombre}", response_model=Maquina,
            operation_id="obtenerMaquina", tags=["maquinas"])
def obtener_maquina(nombre: str):
    if nombre not in MAQUINAS:
        raise HTTPException(404, f"no existe la máquina '{nombre}'")
    return conv.maquina(nombre, MAQUINAS[nombre]())


@router.post("/maquinas/{nombre}/traducir", response_model=ResultadoTraduccion,
             operation_id="traducir", tags=["maquinas"])
def traducir(nombre: str, pedido: Traduccion):
    if nombre not in MAQUINAS:
        raise HTTPException(404, f"no existe la máquina '{nombre}'")
    m = MAQUINAS[nombre]()
    try:
        pasos = m.traza(pedido.palabra, pedido.estado_inicial)
    except ValueError as e:
        raise HTTPException(400, str(e))
    final = pasos[-1].q_nuevo if pasos else (pedido.estado_inicial or m.q0)
    return ResultadoTraduccion(pasos=[conv.transicion(t) for t in pasos],
                               salida=[t.s for t in pasos], estado_final=final)


@router.get("/piramide", response_model=Piramide, operation_id="obtenerPiramide",
            tags=["piramide"])
def obtener_piramide():
    cubos = []
    for i in range(CANTIDAD_CUBOS):
        r, k = fila_columna(i)
        cubos.append(Cubo(numero=i, fila=r, columna=k))
    return Piramide(filas=FILAS, cubos=cubos)
