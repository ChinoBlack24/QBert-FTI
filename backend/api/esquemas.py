"""
Esquemas JSON de la API (pydantic). Tienen los mismos nombres y campos que
components/schemas de contrato-api/openapi.yaml; tests/api/test_contrato.py
lo verifica.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

NombreMaquina = Literal["mov", "cubo1", "cubo2", "cubo3", "vidas"]


class NuevaPartida(BaseModel):
    nivel: int = 1


class Salto(BaseModel):
    tecla: Literal["w", "a", "s", "d"]


class Traduccion(BaseModel):
    palabra: str
    estado_inicial: str | None = None


class Transicion(BaseModel):
    q: str
    e: str
    q_nuevo: str
    s: str


class ResumenMaquina(BaseModel):
    nombre: str
    tipo: Literal["Mealy", "Moore"]
    cantidad_estados: int
    sigma_e: list[str]
    sigma_s: list[str]


class Maquina(BaseModel):
    nombre: str
    tipo: Literal["Mealy", "Moore"]
    Q: list[str]
    sigma_e: list[str]
    sigma_s: list[str]
    q0: str
    finales: list[str]
    f: dict[str, dict[str, str]]
    g: dict[str, str | dict[str, str]]
    tabla: str


class ResultadoTraduccion(BaseModel):
    pasos: list[Transicion]
    salida: list[str]
    estado_final: str


class ColorNivel(BaseModel):
    estado: str
    color: str
    objetivo: bool


class EstadoPartida(BaseModel):
    id: str
    nivel: int
    ultimo_nivel: bool
    estado_movimiento: str
    posicion: int
    estados_cubos: list[str]
    colores: list[str]
    colores_nivel: list[ColorNivel]
    cubos_en_objetivo: int
    estado_vidas: str
    vidas: int
    salida_mealy: list[str]
    nivel_completo: bool
    game_over: bool


class PasoCubo(BaseModel):
    cubo: int
    q: str
    q_nuevo: str
    color: str


class Paso(BaseModel):
    movimiento: Transicion
    cubo: PasoCubo | None
    vidas: Transicion


class ResultadoSalto(BaseModel):
    paso: Paso | None
    estado: EstadoPartida


class Cubo(BaseModel):
    numero: int
    fila: int
    columna: int


class Piramide(BaseModel):
    filas: int
    cubos: list[Cubo]
