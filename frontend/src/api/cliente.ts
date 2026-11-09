/**
 * Cliente de la API. Es el único archivo del frontend que conoce las URLs:
 * los componentes llaman a estas funciones y reciben objetos tipados.
 *
 * Los tipos salen de contrato-api/openapi.yaml (`npm run tipos` regenera
 * esquema.d.ts). Si el contrato cambia y este archivo no, no compila.
 */

import type { components, operations } from "./esquema";

export type Esquemas = components["schemas"];
export type EstadoPartida = Esquemas["EstadoPartida"];
export type ResultadoSalto = Esquemas["ResultadoSalto"];
export type Paso = Esquemas["Paso"];
export type ResultadoTic = Esquemas["ResultadoTic"];
export type PasoTic = Esquemas["PasoTic"];
export type Transicion = Esquemas["Transicion"];
export type Maquina = Esquemas["Maquina"];
export type ResumenMaquina = Esquemas["ResumenMaquina"];
export type ResultadoTraduccion = Esquemas["ResultadoTraduccion"];
export type Piramide = Esquemas["Piramide"];
export type Tecla = Esquemas["Salto"]["tecla"];
export type Direccion = NonNullable<Esquemas["Tic"]["direccion"]>;
export type NombreMaquina = operations["obtenerMaquina"]["parameters"]["path"]["nombre"];

/** Prefijo de la API (servers[0].url del contrato). En desarrollo Vite lo redirige al backend. */
const BASE = "/api";

/** Error devuelto por la API: código HTTP y mensaje de `detail`. */
export class ErrorApi extends Error {
  readonly status: number;

  constructor(status: number, mensaje: string) {
    super(mensaje);
    this.name = "ErrorApi";
    this.status = status;
  }
}

async function pedir<T>(metodo: string, ruta: string, cuerpo?: unknown): Promise<T> {
  const respuesta = await fetch(BASE + ruta, {
    method: metodo,
    headers: cuerpo === undefined ? undefined : { "Content-Type": "application/json" },
    body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
  });
  if (!respuesta.ok) {
    let mensaje = respuesta.statusText;
    try {
      const { detail } = await respuesta.json();
      mensaje = typeof detail === "string" ? detail : JSON.stringify(detail);
    } catch {
      // la respuesta no era JSON; queda statusText
    }
    throw new ErrorApi(respuesta.status, mensaje);
  }
  return (respuesta.status === 204 ? undefined : await respuesta.json()) as T;
}

// --- partidas --------------------------------------------------------------
export const crearPartida = (nivel = 1) =>
  pedir<EstadoPartida>("POST", "/partidas", { nivel });

export const obtenerPartida = (id: string) =>
  pedir<EstadoPartida>("GET", `/partidas/${id}`);

export const borrarPartida = (id: string) =>
  pedir<void>("DELETE", `/partidas/${id}`);

export const saltar = (id: string, tecla: Tecla) =>
  pedir<ResultadoSalto>("POST", `/partidas/${id}/saltos`, { tecla });

/** Pasa el tiempo: la bola baja. Sin dirección, el backend tira una moneda. */
export const tic = (id: string, direccion?: Direccion) =>
  pedir<ResultadoTic>("POST", `/partidas/${id}/tic`, { direccion: direccion ?? null });

export const pasarDeNivel = (id: string) =>
  pedir<EstadoPartida>("POST", `/partidas/${id}/nivel-siguiente`);

// --- máquinas --------------------------------------------------------------
export const listarMaquinas = () =>
  pedir<ResumenMaquina[]>("GET", "/maquinas");

export const obtenerMaquina = (nombre: NombreMaquina) =>
  pedir<Maquina>("GET", `/maquinas/${nombre}`);

export const traducir = (nombre: NombreMaquina, palabra: string, estadoInicial?: string) =>
  pedir<ResultadoTraduccion>("POST", `/maquinas/${nombre}/traducir`,
    { palabra, estado_inicial: estadoInicial ?? null });

// --- pirámide --------------------------------------------------------------
export const obtenerPiramide = () =>
  pedir<Piramide>("GET", "/piramide");
