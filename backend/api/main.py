"""
Aplicación FastAPI. Implementa contrato-api/openapi.yaml.

    uvicorn api.main:app --reload        (desde backend/)
"""

from fastapi import FastAPI

from .rutas import router

app = FastAPI(title="Q*bert con autómatas — API")
app.include_router(router)
