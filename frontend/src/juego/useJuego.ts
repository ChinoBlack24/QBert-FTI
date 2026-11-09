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
 *
 * Tiempos del juego (solo presentación: los autómatas no cambian). El backend
 * responde al instante; acá se decide cuándo se ve cada cosa y cuándo se
 * aceptan teclas de nuevo:
 *   - Un salto dura MS_SALTO. Mientras tanto no se aceptan teclas, y el cubo
 *     cambia de color recién al aterrizar.
 *   - Si se cae, desaparece y vuelve a la cima después de MS_REAPARICION.
 *     Mientras tanto el reloj de la bola está en pausa: la bola entra por la
 *     cima y si no, chocaría con Q*bert antes de que se lo vea.
 *   - Si choca con la bola, la bola ya se retiró (el backend le hace leer X)
 *     y Q*bert queda quieto MS_ESPERA_CHOQUE antes de poder moverse de nuevo.
 *     El reloj también se pausa ese tiempo.
 * Para el jugador es como si no pudiera apretar teclas durante ese tiempo:
 * la palabra de entrada simplemente no tiene símbolos ahí.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import * as api from "../api/cliente";
import type { EstadoPartida, Paso, PasoTic, Piramide, Tecla } from "../api/cliente";
import { gifColision, gifGameover, reproducirEfecto } from "./efectos";

/** Cada cuánto baja la bola mientras está en la pirámide, en milisegundos. */
export const MS_POR_TIC = 800;
/** Cuánto tarda en volver a aparecer cuando está fuera: un valor al azar en este rango. */
export const MS_REAPARECER = { min: 1500, max: 4000 };
/** Cuánto dura un salto de Q*bert: el tiempo entre apretar la tecla y aterrizar. */
export const MS_SALTO = 500;
/** Cuánto tarda Q*bert en volver a la cima después de caerse. */
export const MS_REAPARICION = 2000;
/** Cuánto queda quieto Q*bert después de que lo choca un enemigo. */
export const MS_ESPERA_CHOQUE = 1000;
/** Cuánto dura la animación superpuesta de colisión. */
export const MS_EXPLOSION = 500;

/** Qué hace Q*bert en pantalla mientras el backend ya lo tiene en su nuevo estado. */
export type VistaQbert =
  | { tipo: "normal" }                                   // en estado.posicion
  | { tipo: "cayendo"; desde: number; tecla: Tecla }     // saltó fuera de la pirámide
  | { tipo: "oculto" };                                  // esperando para reaparecer

export type Evento =
  | { tipo: "salto"; paso: Paso }
  | { tipo: "tic"; paso: PasoTic };

const azarEntre = ({ min, max }: { min: number; max: number }) =>
  min + Math.random() * (max - min);

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
  const [ultimo, setUltimo] = useState<Evento | null>(null);
  // El último salto aparte: dice hacia dónde mira Q*bert aunque después haya tics.
  const [ultimoSalto, setUltimoSalto] = useState<Paso | null>(null);
  const [relojEnMarcha, setRelojEnMarcha] = useState(false);
  // Colores que se ven mientras Q*bert está en el aire (los de antes del salto).
  const [coloresCongelados, setColoresCongelados] = useState<string[] | null>(null);
  const [vistaQbert, setVistaQbert] = useState<VistaQbert>({ tipo: "normal" });
  const [explosion, setExplosion] = useState<{ id: number; src: string } | null>(null);
  const [gameoverGif, setGameoverGif] = useState<{ src: string; duracionMs: number } | null>(null);
  const [enPausa, setEnPausa] = useState(false);
  const [puntaje, setPuntaje] = useState(0);
  const [mejorPuntaje, setMejorPuntaje] = useState(puntajeGuardado.puntaje);
  const [errorPuntaje, setErrorPuntaje] = useState<string | null>(puntajeGuardado.error);
  const [error, setError] = useState<string | null>(null);

  const idPartida = useRef<string | null>(null);
  // El reloj consulta el estado más reciente sin reiniciarse en cada cambio.
  const estadoActual = useRef<EstadoPartida | null>(null);
  const puntajeActual = useRef(0);
  const mejorPuntajeActual = useRef(puntajeGuardado.puntaje);
  // Los eventos se encolan para que lleguen al backend en orden,
  // aunque se aprieten varias teclas antes de que vuelva la respuesta.
  const cola = useRef<Promise<void>>(Promise.resolve());
  // Hasta cuándo se ignoran las teclas (mientras salta o reaparece).
  const bloqueadoHasta = useRef(0);
  // Temporizadores de animación pendientes, para cancelarlos al reiniciar.
  const temporizadores = useRef<ReturnType<typeof setTimeout>[]>([]);
  const secuenciaExplosion = useRef(0);

  // Hasta cuándo está pausado el reloj de la bola (puede alargarse si se juntan dos pausas).
  const pausaHasta = useRef(0);

  const despues = (ms: number, accion: () => void) => {
    temporizadores.current.push(setTimeout(accion, ms));
  };

  const mostrarExplosion = () => {
    const id = ++secuenciaExplosion.current;
    setExplosion({ id, src: gifColision() });
    despues(MS_EXPLOSION, () => {
      setExplosion((actual) => actual?.id === id ? null : actual);
    });
  };

  /** No acepta teclas durante `ms` (si ya estaba bloqueado por más tiempo, queda así). */
  const bloquear = (ms: number) => {
    bloqueadoHasta.current = Math.max(bloqueadoHasta.current, performance.now() + ms);
  };

  /** Pausa el reloj de la bola durante `ms`. */
  const pausar = (ms: number) => {
    pausaHasta.current = Math.max(pausaHasta.current, performance.now() + ms);
    setEnPausa(true);
    despues(ms, () => {
      if (performance.now() >= pausaHasta.current - 1) setEnPausa(false);
    });
  };

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
    return cola.current;
  }, []);

  const actualizar = (nuevo: EstadoPartida) => {
    const gameoverNuevo = !estadoActual.current?.game_over && nuevo.game_over;
    estadoActual.current = nuevo;
    setEstado(nuevo);
    if (gameoverNuevo) {
      const gif = gifGameover();
      setGameoverGif(gif);
      despues(gif.duracionMs, () => {
        setGameoverGif((actual) => actual?.src === gif.src ? null : actual);
      });
      reproducirEfecto("gameover");
    }
  };

  const empezar = (nuevo: EstadoPartida) => {
    temporizadores.current.forEach(clearTimeout);
    temporizadores.current = [];
    bloqueadoHasta.current = 0;
    pausaHasta.current = 0;
    actualizar(nuevo);
    setUltimo(null);
    setUltimoSalto(null);
    setRelojEnMarcha(false);
    setColoresCongelados(null);
    setVistaQbert({ tipo: "normal" });
    setExplosion(null);
    setGameoverGif(null);
    setEnPausa(false);
  };

  const nuevaPartida = useCallback(() => encolar(async () => {
    const anterior = idPartida.current;
    const nueva = await api.crearPartida(1);
    idPartida.current = nueva.id;
    empezar(nueva);
    puntajeActual.current = 0;
    setPuntaje(0);
    setError(null);
    if (anterior) api.borrarPartida(anterior).catch(() => {});
  }), [encolar]);

  const saltar = useCallback((tecla: Tecla) => {
    // Mientras salta o reaparece, las teclas se ignoran (no se encolan).
    const ahora = performance.now();
    if (ahora < bloqueadoHasta.current) return;
    bloqueadoHasta.current = ahora + MS_SALTO;

    return encolar(async () => {
      if (!idPartida.current || !estadoActual.current) return;
      const antes = estadoActual.current;
      setColoresCongelados(antes.colores);      // el cubo cambia recién al aterrizar

      const { paso, estado } = await api.saltar(idPartida.current, tecla);
      actualizar(estado);
      if (!paso) {                              // la partida ya había terminado
        setColoresCongelados(null);
        bloqueadoHasta.current = 0;
        return;
      }
      setUltimo({ tipo: "salto", paso });
      setUltimoSalto(paso);
      setRelojEnMarcha(true);
      if (paso.choque) {
        mostrarExplosion();
        reproducirEfecto("colision");
      } else if (paso.movimiento.s === "X") {
        reproducirEfecto("caida");
      } else {
        reproducirEfecto(tecla === "s" || tecla === "d" ? "abajo" : "arriba");
      }

      // Puntaje: 30 por cada cambio real de color de un cubo, 100 al completar el nivel.
      if (paso.cubo && antes.colores[paso.cubo.cubo] !== estado.colores[paso.cubo.cubo]) {
        sumarPuntos(30);
      }
      if (!antes.nivel_completo && estado.nivel_completo) {
        sumarPuntos(100);
      }

      if (paso.movimiento.s === "X") {
        // Se cayó: salta fuera, desaparece y vuelve a la cima a los MS_REAPARICION.
        bloquear(MS_SALTO + MS_REAPARICION);
        pausar(MS_SALTO + MS_REAPARICION);
        setVistaQbert({ tipo: "cayendo", desde: antes.posicion, tecla });
        despues(MS_SALTO, () => {
          setColoresCongelados(null);
          setVistaQbert({ tipo: "oculto" });
        });
        despues(MS_SALTO + MS_REAPARICION, () => setVistaQbert({ tipo: "normal" }));
      } else {
        despues(MS_SALTO, () => setColoresCongelados(null));
        if (paso.choque) {
          // Saltó sobre la bola: aterriza y queda quieto MS_ESPERA_CHOQUE.
          bloquear(MS_SALTO + MS_ESPERA_CHOQUE);
          pausar(MS_SALTO + MS_ESPERA_CHOQUE);
        }
      }
    });
  }, [encolar, sumarPuntos]);

  const tic = useCallback(() => encolar(async () => {
    if (!idPartida.current) return;
    const { paso, estado } = await api.tic(idPartida.current);
    actualizar(estado);
    if (paso) setUltimo({ tipo: "tic", paso });
    if (paso?.choque && !estado.game_over) {
      mostrarExplosion();
      reproducirEfecto("colision");
      // La bola le cayó encima: queda quieto MS_ESPERA_CHOQUE.
      bloquear(MS_ESPERA_CHOQUE);
      pausar(MS_ESPERA_CHOQUE);
    }
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
  const enJuego = relojEnMarcha && !enPausa && estado !== null && !estado.game_over &&
    !estado.nivel_completo;
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

  return {
    piramide, estado, ultimo, ultimoSalto, coloresCongelados, vistaQbert, explosion, gameoverGif, error,
    puntaje, mejorPuntaje, errorPuntaje, saltar, siguienteNivel, nuevaPartida,
  };
}
