/**
 * Estado del juego en el frontend. No decide nada: manda cada acción al
 * backend y guarda lo que responde.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import * as api from "../api/cliente";
import type { EstadoPartida, Paso, Piramide, Tecla } from "../api/cliente";

export function useJuego() {
  const [piramide, setPiramide] = useState<Piramide | null>(null);
  const [estado, setEstado] = useState<EstadoPartida | null>(null);
  const [ultimoPaso, setUltimoPaso] = useState<Paso | null>(null);
  const [error, setError] = useState<string | null>(null);

  const idPartida = useRef<string | null>(null);
  // Las acciones se encolan para que lleguen al backend en orden,
  // aunque se aprieten varias teclas antes de que vuelva la respuesta.
  const cola = useRef<Promise<void>>(Promise.resolve());

  const encolar = useCallback((accion: () => Promise<void>) => {
    cola.current = cola.current.then(accion).catch((e: Error) => setError(e.message));
  }, []);

  const nuevaPartida = useCallback(() => encolar(async () => {
    const anterior = idPartida.current;
    const nueva = await api.crearPartida(1);
    idPartida.current = nueva.id;
    setEstado(nueva);
    setUltimoPaso(null);
    setError(null);
    if (anterior) api.borrarPartida(anterior).catch(() => {});
  }), [encolar]);

  const saltar = useCallback((tecla: Tecla) => encolar(async () => {
    if (!idPartida.current) return;
    const { paso, estado } = await api.saltar(idPartida.current, tecla);
    setEstado(estado);
    if (paso) setUltimoPaso(paso);
  }), [encolar]);

  const siguienteNivel = useCallback(() => encolar(async () => {
    if (!idPartida.current) return;
    try {
      setEstado(await api.pasarDeNivel(idPartida.current));
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

  return { piramide, estado, ultimoPaso, error, saltar, siguienteNivel, nuevaPartida };
}
