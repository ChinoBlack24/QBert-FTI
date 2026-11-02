/**
 * Estado del juego en el frontend. No decide nada: manda cada evento al
 * backend y guarda lo que responde.
 *
 * Hay dos fuentes de eventos, como en el modelo:
 *   - el teclado  -> saltar(tecla)   (lo lee la Mealy de Q*bert)
 *   - el reloj    -> tic             (lo lee la Moore de la bola)
 *
 * El reloj arranca con el primer salto de cada nivel, para que la bola no le
 * caiga encima a Q*bert antes de que el jugador empiece.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import * as api from "../api/cliente";
import type { EstadoPartida, Paso, PasoTic, Piramide, Tecla } from "../api/cliente";

/** Cada cuánto baja la bola mientras está en la pirámide, en milisegundos. */
export const MS_POR_TIC = 800;
/** Cuánto tarda en volver a aparecer cuando está fuera: un valor al azar en este rango. */
export const MS_REAPARECER = { min: 1500, max: 4000 };

export type Evento =
  | { tipo: "salto"; paso: Paso }
  | { tipo: "tic"; paso: PasoTic };

const azarEntre = ({ min, max }: { min: number; max: number }) =>
  min + Math.random() * (max - min);

export function useJuego() {
  const [piramide, setPiramide] = useState<Piramide | null>(null);
  const [estado, setEstado] = useState<EstadoPartida | null>(null);
  const [ultimo, setUltimo] = useState<Evento | null>(null);
  const [relojEnMarcha, setRelojEnMarcha] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const idPartida = useRef<string | null>(null);
  // El reloj consulta el estado más reciente sin reiniciarse en cada cambio.
  const estadoActual = useRef<EstadoPartida | null>(null);
  // Los eventos se encolan para que lleguen al backend en orden,
  // aunque se aprieten varias teclas antes de que vuelva la respuesta.
  const cola = useRef<Promise<void>>(Promise.resolve());

  const encolar = useCallback((accion: () => Promise<void>) => {
    cola.current = cola.current.then(accion).catch((e: Error) => setError(e.message));
    return cola.current;
  }, []);

  const actualizar = (nuevo: EstadoPartida) => {
    estadoActual.current = nuevo;
    setEstado(nuevo);
  };

  const empezar = (nuevo: EstadoPartida) => {
    actualizar(nuevo);
    setUltimo(null);
    setRelojEnMarcha(false);
  };

  const nuevaPartida = useCallback(() => encolar(async () => {
    const anterior = idPartida.current;
    const nueva = await api.crearPartida(1);
    idPartida.current = nueva.id;
    empezar(nueva);
    setError(null);
    if (anterior) api.borrarPartida(anterior).catch(() => {});
  }), [encolar]);

  const saltar = useCallback((tecla: Tecla) => encolar(async () => {
    if (!idPartida.current) return;
    const { paso, estado } = await api.saltar(idPartida.current, tecla);
    actualizar(estado);
    if (paso) {
      setUltimo({ tipo: "salto", paso });
      setRelojEnMarcha(true);
    }
  }), [encolar]);

  const tic = useCallback(() => encolar(async () => {
    if (!idPartida.current) return;
    const { paso, estado } = await api.tic(idPartida.current);
    actualizar(estado);
    if (paso) setUltimo({ tipo: "tic", paso });
  }), [encolar]);

  const siguienteNivel = useCallback(() => encolar(async () => {
    if (!idPartida.current) return;
    try {
      empezar(await api.pasarDeNivel(idPartida.current));
    } catch (e) {
      // 409: el nivel no está completo o es el último; no es un error del usuario.
      if (!(e instanceof api.ErrorApi && e.status === 409)) throw e;
    }
  }), [encolar]);

  useEffect(() => {
    api.obtenerPiramide().then(setPiramide).catch((e: Error) => setError(e.message));
    nuevaPartida();
  }, [nuevaPartida]);

  // El reloj: programa un tic; cuando termina, programa el siguiente. La espera
  // depende de dónde quedó la bola: fija si está bajando, al azar si está fuera.
  // No se reinicia con los saltos de Q*bert: solo al empezar o terminar el juego.
  const enJuego = relojEnMarcha && estado !== null && !estado.game_over && !estado.nivel_completo;
  useEffect(() => {
    if (!enJuego) return;
    let cancelado = false;
    let temporizador: ReturnType<typeof setTimeout>;
    const programar = () => {
      const fuera = estadoActual.current?.posicion_bola === null;
      const espera = fuera ? azarEntre(MS_REAPARECER) : MS_POR_TIC;
      temporizador = setTimeout(async () => {
        await tic();
        if (!cancelado) programar();
      }, espera);
    };
    programar();
    return () => {
      cancelado = true;
      clearTimeout(temporizador);
    };
  }, [enJuego, tic]);

  return { piramide, estado, ultimo, error, saltar, siguienteNivel, nuevaPartida };
}
