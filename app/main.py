from fastapi import FastAPI

from app.routers import estadias, veiculos

app = FastAPI(title="API de Estacionamento")

app.include_router(veiculos.router)
app.include_router(estadias.router)


@app.get("/")
def raiz():
    return {"mensagem": "API de Estacionamento no ar"}