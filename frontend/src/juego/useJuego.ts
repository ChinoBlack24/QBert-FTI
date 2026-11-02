/**
 * Estado del juego en el frontend. No decide nada: manda cada acción al
 * backend y guarda lo que responde.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import * as api from "../api/cliente";
import type { EstadoPartida, Paso, Piramide, Tecla } from "../api/cliente";

const CLAVE_MEJOR_PUNTAJE = "qbert-mejor-puntaje";

function leerMejorPuntaje(): { puntaje: number; error: string | null } {
  try {
    const guardado = window.localStorage.getItem(CLAVE_MEJOR_PUNTAJE);
    const puntaje = guardado === null ? 0 : Number(guardado);
    if (!Number.isSafeInteger(puntaje) || puntaje < 0) {
      throw new Error("el valor guardado no es un puntaje válido");
    }
    return { puntaje, error: null };
  } catch (e) {
    return {
      puntaje: 0,
      error: `No se pudo leer el récord guardado: ${e instanceof Error ? e.message : String(e)}`,
    };
  }
}

export function useJuego() {
  const [puntajeGuardado] = useState(leerMejorPuntaje);
  const [piramide, setPiramide] = useState<Piramide | null>(null);
  const [estado, setEstado] = useState<EstadoPartida | null>(null);
  const [ultimoPaso, setUltimoPaso] = useState<Paso | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [puntaje, setPuntaje] = useState(0);
  const [mejorPuntaje, setMejorPuntaje] = useState(puntajeGuardado.puntaje);
  const [errorPuntaje, setErrorPuntaje] = useState<string | null>(puntajeGuardado.error);

  const idPartida = useRef<string | null>(null);
  const estadoActual = useRef<EstadoPartida | null>(null);
  const puntajeActual = useRef(0);
  const mejorPuntajeActual = useRef(puntajeGuardado.puntaje);
  // Las acciones se encolan para que lleguen al backend en orden,
  // aunque se aprieten varias teclas antes de que vuelva la respuesta.
  const cola = useRef<Promise<void>>(Promise.resolve());

  const sumarPuntos = useCallback((puntos: number) => {
    const nuevoPuntaje = puntajeActual.current + puntos;
    puntajeActual.current = nuevoPuntaje;
    setPuntaje(nuevoPuntaje);

    if (nuevoPuntaje > mejorPuntajeActual.current) {
      mejorPuntajeActual.current = nuevoPuntaje;
      setMejorPuntaje(nuevoPuntaje);
      try {
        window.localStorage.setItem(CLAVE_MEJOR_PUNTAJE, String(nuevoPuntaje));
        setErrorPuntaje(null);
      } catch (e) {
        setErrorPuntaje(`No se pudo guardar el récord: ${e instanceof Error ? e.message : String(e)}`);
      }
    }
  }, []);

  const encolar = useCallback((accion: () => Promise<void>) => {
    cola.current = cola.current.then(accion).catch((e: Error) => setError(e.message));
  }, []);

  const nuevaPartida = useCallback(() => encolar(async () => {
    const anterior = idPartida.current;
    const nueva = await api.crearPartida(1);
    idPartida.current = nueva.id;
    estadoActual.current = nueva;
    setEstado(nueva);
    puntajeActual.current = 0;
    setPuntaje(0);
    setUltimoPaso(null);
    setError(null);
    if (anterior) api.borrarPartida(anterior).catch(() => {});
  }), [encolar]);

  const saltar = useCallback((tecla: Tecla) => encolar(async () => {
    if (!idPartida.current) return;
    const anterior = estadoActual.current;
    const { paso, estado: nuevoEstado } = await api.saltar(idPartida.current, tecla);
    estadoActual.current = nuevoEstado;
    setEstado(nuevoEstado);
    if (paso) setUltimoPaso(paso);

    if (paso?.cubo && anterior?.colores[paso.cubo.cubo] !== nuevoEstado.colores[paso.cubo.cubo]) {
      sumarPuntos(30);
    }
    if (anterior && !anterior.nivel_completo && nuevoEstado.nivel_completo) {
      sumarPuntos(100);
    }
  }), [encolar, sumarPuntos]);

  const siguienteNivel = useCallback(() => encolar(async () => {
    if (!idPartida.current) return;
    try {
      const nuevoEstado = await api.pasarDeNivel(idPartida.current);
      estadoActual.current = nuevoEstado;
      setEstado(nuevoEstado);
      setUltimoPaso(null);
    } catch (e) {
      // 409: el nivel no está completo o es el último; no es un error del usuario.
      if (!(e instanceof api.ErrorApi && e.status === 409)) throw e;
    }
  }), [encolar]);

  useEffect(() => {
    api.obtenerPiramide().then(setPiramide).catch((e: Error) => setError(e.message));
    nuevaPartida();
  }, [nuevaPartida]);

  return {
    piramide, estado, ultimoPaso, error, puntaje, mejorPuntaje, errorPuntaje,
    saltar, siguienteNivel, nuevaPartida,
  };
}
