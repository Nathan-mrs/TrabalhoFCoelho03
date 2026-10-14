# TrabalhoFCoelho03 — API de Estacionamento

API para controlar veículos e suas estadias em um estacionamento. Cada entrada cria uma estadia aberta. Ao registrar a saída, a API calcula o valor e finaliza a estadia.

## Tecnologias

- Python
- FastAPI
- SQLAlchemy
- Alembic
- SQLite
- Pydantic

## Modelo de dados

- **Veiculo**: placa, modelo, cor e tipo (`carro` ou `moto`).
- **Estadia**: veículo, vaga, horário de entrada, horário de saída, valor total e status (`aberta` ou `finalizada`).

Um veículo pode ter várias estadias ao longo do tempo. Cada estadia pertence a um único veículo, por meio da chave estrangeira `estadias.veiculo_id`, que referencia `veiculos.id`.

A API impede que um veículo tenha mais de uma estadia aberta ao mesmo tempo e que uma vaga aberta seja ocupada por duas estadias.

## Regras de cobrança

A tarifa é de **R$ 10,00 por hora iniciada**, com arredondamento para cima. Uma permanência de até uma hora custa R$ 10,00; uma hora e um minuto custa R$ 20,00.

## Instalação e execução

Os comandos abaixo são para PowerShell. Execute-os na pasta raiz do projeto:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Com a API em execução, acesse:

- Swagger: http://127.0.0.1:8000/docs
- Rota inicial: http://127.0.0.1:8000/

As tabelas do banco são criadas pelas migrações do Alembic. Para aplicar as migrações disponíveis, use `alembic upgrade head`.

## Endpoints

### Veículos

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/veiculos/` | Cadastra um veículo |
| `GET` | `/veiculos/` | Lista os veículos |
| `GET` | `/veiculos/{veiculo_id}` | Busca um veículo pelo ID |
| `PUT` | `/veiculos/{veiculo_id}` | Atualiza um veículo |
| `DELETE` | `/veiculos/{veiculo_id}` | Remove um veículo sem estadias relacionadas |

### Estadias

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/estadias/` | Abre uma estadia para um veículo e uma vaga |
| `GET` | `/estadias/` | Lista as estadias |
| `GET` | `/estadias/{estadia_id}` | Busca uma estadia pelo ID |
| `PATCH` | `/estadias/{estadia_id}/saida` | Registra a saída e calcula o valor |

Para abrir uma estadia, envie o ID de um veículo existente e o identificador da vaga. Exemplo de corpo para `POST /estadias/`:

```json
{
  "veiculo_id": 1,
  "vaga": "A01"
}
```

Ao registrar a saída, a API usa o horário atual se o corpo da requisição for omitido. Também é possível informar `hora_saida` no formato ISO 8601.

## Validações e erros

- `404 Not Found`: veículo ou estadia não encontrada.
- `409 Conflict`: placa já cadastrada, veículo já possui estadia aberta, vaga ocupada, estadia já finalizada ou veículo possui estadias relacionadas.
- `422 Unprocessable Entity`: dados inválidos ou horário de saída inválido.