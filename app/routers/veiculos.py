from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.veiculo import Veiculo
from app.schemas.veiculo import VeiculoCreate, VeiculoResponse, VeiculoUpdate

router = APIRouter(prefix="/veiculos", tags=["Veículos"])


@router.post("/", response_model=VeiculoResponse, status_code=status.HTTP_201_CREATED)
def criar_veiculo(dados: VeiculoCreate, db: Session = Depends(get_db)):
    placa = dados.placa.upper()
    if db.query(Veiculo).filter(Veiculo.placa == placa).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe um veículo com essa placa")

    veiculo = Veiculo(**dados.model_dump(exclude={"placa"}), placa=placa)
    db.add(veiculo)
    db.commit()
    db.refresh(veiculo)
    return veiculo


@router.get("/", response_model=List[VeiculoResponse])
def listar_veiculos(db: Session = Depends(get_db)):
    return db.query(Veiculo).all()


@router.get("/{veiculo_id}", response_model=VeiculoResponse)
def buscar_veiculo(veiculo_id: int, db: Session = Depends(get_db)):
    veiculo = db.get(Veiculo, veiculo_id)
    if not veiculo:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Veículo não encontrado")
    return veiculo


@router.put("/{veiculo_id}", response_model=VeiculoResponse)
def atualizar_veiculo(veiculo_id: int, dados: VeiculoUpdate, db: Session = Depends(get_db)):
    veiculo = db.get(Veiculo, veiculo_id)
    if not veiculo:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Veículo não encontrado")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(veiculo, campo, valor)

    db.commit()
    db.refresh(veiculo)
    return veiculo


@router.delete("/{veiculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_veiculo(veiculo_id: int, db: Session = Depends(get_db)):
    veiculo = db.get(Veiculo, veiculo_id)
    if not veiculo:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Veículo não encontrado")

    db.delete(veiculo)
    db.commit()