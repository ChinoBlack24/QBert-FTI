/**
 * Posición animada con un salto en arco, como en el Q*bert original.
 *
 * Cuando cambia el destino (x, y), la posición va del punto actual al nuevo
 * siguiendo una parábola: avanza en línea recta y además sube `altura`
 * píxeles en la mitad del recorrido.
 *
 *     y(t) = y_inicial + (y_final - y_inicial) · t  -  altura · 4t(1 - t)      t ∈ [0, 1]
 *
 * Es solo presentación: el destino ya viene decidido por el backend.
 *
 * Si el salto es más largo que `maximo` (por ejemplo, Q*bert reaparece en la
 * cima después de caerse), no hay arco: aparece directamente en el destino.
 */

import { useEffect, useRef, useState } from "react";

export interface OpcionesSalto {
  duracion: number;   // milisegundos
  altura: number;     // píxeles que sube en la mitad del salto
  maximo: number;     // distancia a partir de la cual se teletransporta
}

export function useSalto(
  x: number,
  y: number,
  { duracion, altura, maximo }: OpcionesSalto,
  inicio?: { x: number; y: number },
) {
  const inicioX = inicio?.x ?? x;
  const inicioY = inicio?.y ?? y;
  const [pos, setPos] = useState({ x: inicioX, y: inicioY });
  // Dónde está dibujado ahora: si llega un salto nuevo a mitad de otro, arranca desde acá.
  const actual = useRef({ x: inicioX, y: inicioY });

  useEffect(() => {
    const desde = actual.current;
    const distancia = Math.hypot(x - desde.x, y - desde.y);
    if (distancia === 0) return;

    if (distancia > maximo) {
      actual.current = { x, y };
      setPos(actual.current);
      return;
    }

    let cuadro = 0;
    const inicio = performance.now();
    const avanzar = (ahora: number) => {
      // El tiempo del cuadro puede ser apenas anterior a `inicio`: t nunca baja de 0.
      const t = Math.min(Math.max((ahora - inicio) / duracion, 0), 1);
      actual.current = {
        x: desde.x + (x - desde.x) * t,
        y: desde.y + (y - desde.y) * t - altura * 4 * t * (1 - t),
      };
      setPos(actual.current);
      if (t < 1) cuadro = requestAnimationFrame(avanzar);
    };
    cuadro = requestAnimationFrame(avanzar);
    return () => cancelAnimationFrame(cuadro);
  }, [x, y, duracion, altura, maximo, inicioX, inicioY]);

  return pos;
}
