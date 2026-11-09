/**
 * Q*bert dibujado con sprites. Es solo presentación: no decide nada.
 *
 * Recibe ya resuelto hacia dónde mira (la última tecla que leyó la Mealy de
 * movimiento) y con qué animación arranca (ver Piramide.tsx). La lógica sigue
 * entera en el backend.
 *
 * Los cuadros están en public/sprites/qbert/ (44 × 42 px, fondo transparente).
 * La hoja original solo tiene a Q*bert mirando abajo-derecha (frente) y
 * arriba-derecha (espalda); los lados izquierdos se dibujan espejando.
 */

import { useEffect, useState } from "react";
import { TAMANO_QBERT } from "./qbertDimensiones";

type Animacion = "frente-quieto" | "frente-salto" | "espalda-quieto" | "espalda-salto" | "golpe";

const CUADROS: Record<Animacion, number> = {
  "frente-quieto": 8,
  "frente-salto": 6,
  "espalda-quieto": 8,
  "espalda-salto": 6,
  "golpe": 2,
};

/** Cuadros por segundo de cada tipo de animación. */
const FPS = { quieto: 8, salto: 24, golpe: 8 };
/** El golpe repite sus 2 cuadros varias veces antes de volver a quieto. */
const REPETICIONES_GOLPE = 3;

export type Fase = "quieto" | "salto" | "golpe";

function animacionDe(fase: Fase, lado: "frente" | "espalda"): Animacion {
  return fase === "golpe" ? "golpe" : `${lado}-${fase}`;
}

/** Cuántos cuadros dura una fase (quieto y salto tienen la misma cantidad de frente y de espalda). */
function largo(fase: Fase): number {
  if (fase === "golpe") return CUADROS.golpe * REPETICIONES_GOLPE;
  return CUADROS[animacionDe(fase, "frente")];
}

const ruta = (a: Animacion, n: number) => `/sprites/qbert/qbert-${a}-${n}.png`;

// Se cargan todos al principio para que no parpadee la primera vez que aparece cada cuadro.
for (const [a, total] of Object.entries(CUADROS)) {
  for (let n = 0; n < total; n++) new Image().src = ruta(a as Animacion, n);
}

/**
 * Se monta de nuevo en cada salto y en cada vida perdida (ver la key en
 * Piramide.tsx), así que arranca directamente con la animación `inicial` y
 * no hace falta reiniciarla. Cuando termina, queda quieto.
 *
 *   tecla    w, a, s o d: la última que leyó la Mealy de Q*bert
 *   inicial  "salto" después de saltar, "golpe" si perdió una vida
 */
export function QbertSprite({ tecla, inicial }: { tecla: string; inicial: Fase }) {
  const deEspaldas = tecla === "w" || tecla === "a";   // saltó hacia arriba
  const espejado = tecla === "s" || tecla === "a";     // saltó hacia la izquierda
  const lado = deEspaldas ? "espalda" : "frente";

  // Fase y cuadro van juntos en un solo estado para cambiarlos a la vez.
  const [{ fase, cuadro }, setAnim] = useState({ fase: inicial, cuadro: 0 });

  useEffect(() => {
    const reloj = setInterval(() => {
      setAnim(({ fase, cuadro }) => {
        const siguiente = cuadro + 1;
        if (fase !== "quieto" && siguiente >= largo(fase)) return { fase: "quieto", cuadro: 0 };
        return { fase, cuadro: siguiente % largo(fase) };
      });
    }, 1000 / FPS[fase]);
    return () => clearInterval(reloj);
  }, [fase]);

  const animacion = animacionDe(fase, lado);

  const { ancho: w, alto: h } = TAMANO_QBERT;
  return (
    <image
      href={ruta(animacion, cuadro % CUADROS[animacion])}
      x={-w / 2}
      y={-h + 10}             // los pies quedan sobre el centro de la cara superior del cubo
      width={w}
      height={h}
      className="sprite"
      transform={espejado && fase !== "golpe" ? "scale(-1, 1)" : undefined}
    />
  );
}
