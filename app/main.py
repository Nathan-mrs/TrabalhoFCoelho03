from fastapi import FastAPI

app = FastAPI(title="API de Estacionamento")


@app.get("/")
def raiz():
    return {"mensagem": "API de Estacionamento no ar"}