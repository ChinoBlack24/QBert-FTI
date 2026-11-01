# QBert-FTI
Proyecto para la implementación de automatas para la asignatura Fundamentos Teóricos de la Informática.

Modelado de Q*bert con máquinas secuenciales (Grupo 1): una Mealy de movimiento,
una Moore de color por cubo y una Moore de vidas.

```
contrato-api/   openapi.yaml: lo que el backend ofrece y el frontend usa
backend/        automatas/ (la lógica, solo automata-lib) + api/ (FastAPI) + consola + tests
frontend/       React + TypeScript (Vite). Solo dibuja; la lógica está en el backend
prueba.py       primera prueba de automata-lib (genera afd.png)
```

El frontend y el backend solo se conocen a través del contrato. Cualquiera de los
dos se puede cambiar o reescribir sin tocar el otro, siempre que se respete
`contrato-api/openapi.yaml`:

- `backend/tests/api/test_contrato.py` falla si la API no coincide con el contrato.
- `frontend/src/api/esquema.d.ts` se genera del contrato (`npm run tipos`), y
  `frontend/src/api/cliente.ts` es el único archivo del frontend que hace `fetch`.

## Correrlo

Son dos programas y cada uno va en su terminal. Los pasos completos están en cada carpeta:

- `backend/README.md`: crear el entorno, `uvicorn api.main:app --reload` → `http://localhost:8000/docs`
- `frontend/README.md`: `npm install`, `npm run dev` → `http://localhost:5173`

Primero el backend, después el frontend.

Sin frontend también se puede probar todo desde la consola: `python consola.py` en `backend/`.
Ver `backend/README.md`.

## Si cambia la API

1. Editar `contrato-api/openapi.yaml`.
2. Backend: adaptar `api/` hasta que pase `python -m pytest`.
3. Frontend: `npm run tipos` y corregir lo que deje de compilar (`npm run build`).
