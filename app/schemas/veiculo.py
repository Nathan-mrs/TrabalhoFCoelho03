from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class VeiculoCreate(BaseModel):
    placa: str = Field(min_length=7, max_length=8)
    modelo: str = Field(min_length=1, max_length=50)
    cor: str = Field(min_length=1, max_length=30)
    tipo: Literal["carro", "moto"]


class VeiculoUpdate(BaseModel):
    modelo: Optional[str] = Field(default=None, min_length=1, max_length=50)
    cor: Optional[str] = Field(default=None, min_length=1, max_length=30)
    tipo: Optional[Literal["carro", "moto"]] = None


class VeiculoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    placa: str
    modelo: str
    cor: str
    tipo: str