"""
API HTTP (FastAPI) sobre la lógica de automatas/. Se puede reemplazar por otra
implementación sin tocar automatas/, mientras cumpla contrato-api/openapi.yaml.

    esquemas.py     modelos JSON (mismos nombres que el contrato)
    conversion.py   objetos de automatas -> esquemas
    rutas.py        endpoints
    main.py         la app: uvicorn api.main:app
"""
