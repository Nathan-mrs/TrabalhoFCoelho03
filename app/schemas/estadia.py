from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EstadiaCreate(BaseModel):
    veiculo_id: int = Field(gt=0)
    vaga: str = Field(min_length=1, max_length=10)


class EstadiaUpdate(BaseModel):
    # Se não for informado, a rota usará o horário atual.
    hora_saida: datetime | None = None


class EstadiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    veiculo_id: int
    vaga: str
    hora_entrada: datetime
    hora_saida: datetime | None
    valor_total: Decimal | None
    status: Literal["aberta", "finalizada"]