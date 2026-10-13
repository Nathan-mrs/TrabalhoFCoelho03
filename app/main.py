from fastapi import FastAPI

from app.routers import veiculos

app = FastAPI(title="API de Estacionamento")

app.include_router(veiculos.router)


@app.get("/")
def raiz():
    return {"mensagem": "API de Estacionamento no ar"}