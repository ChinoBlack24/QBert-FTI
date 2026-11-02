/**
 * La bola roja dibujada con sprites. Es solo presentación: dónde está la
 * bola lo decide el backend (estado.posicion_bola).
 *
 * Se monta de nuevo cada vez que la bola cae en un cubo (ver la key en
 * Piramide.tsx) y hace un rebote corto: estirada en el aire, aplastada al
 * tocar el cubo y de vuelta redonda.
 */

import { useEffect, useState } from "react";

const REBOTE = ["estirada", "redonda", "aplastada", "redonda-2", "redonda"] as const;
const MS_POR_CUADRO = 70;

const ANCHO = 36;
const ALTO = 38;
const ESCALA = 1.1;

const ruta = (cuadro: string) => `/sprites/bola/bola-${cuadro}.png`;

// Se cargan al principio para que no parpadee la primera vez.
for (const cuadro of new Set(REBOTE)) new Image().src = ruta(cuadro);

export function BolaSprite() {
  const [paso, setPaso] = useState(0);

  useEffect(() => {
    if (paso >= REBOTE.length - 1) return;   // terminó el rebote: queda redonda
    const t = setTimeout(() => setPaso(paso + 1), MS_POR_CUADRO);
    return () => clearTimeout(t);
  }, [paso]);

  const w = ANCHO * ESCALA;
  const h = ALTO * ESCALA;
  return (
    <image
      href={ruta(REBOTE[paso])}
      x={-w / 2}
      y={-h + 8}            // apoyada sobre el centro de la cara superior del cubo
      width={w}
      height={h}
      className="sprite"
    />
  );
}
