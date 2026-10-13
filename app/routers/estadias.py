import math
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import VALOR_HORA
from app.core.database import get_db
from app.models.estadia import Estadia, agora_utc_sem_fuso
from app.models.veiculo import Veiculo
from app.schemas.estadia import EstadiaCreate, EstadiaResponse, EstadiaUpdate

router = APIRouter(prefix="/estadias", tags=["Estadias"])


def normalizar_horario(data_hora: datetime) -> datetime:
    """Converte horários com fuso para UTC sem fuso, como o SQLite espera."""
    if data_hora.tzinfo is not None:
        return data_hora.astimezone(timezone.utc).replace(tzinfo=None)
    return data_hora


@router.post(
    "/",
    response_model=EstadiaResponse,
    status_code=status.HTTP_201_CREATED,
)
def abrir_estadia(dados: EstadiaCreate, db: Session = Depends(get_db)):
    veiculo = db.get(Veiculo, dados.veiculo_id)
    if veiculo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado",
        )

    veiculo_com_estadia_aberta = (
        db.query(Estadia)
        .filter(
            Estadia.veiculo_id == dados.veiculo_id,
            Estadia.status == "aberta",
        )
        .first()
    )
    if veiculo_com_estadia_aberta is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este veículo já possui uma estadia aberta",
        )

    vaga_ocupada = (
        db.query(Estadia)
        .filter(
            Estadia.vaga == dados.vaga,
            Estadia.status == "aberta",
        )
        .first()
    )
    if vaga_ocupada is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta vaga já está ocupada",
        )

    estadia = Estadia(
        veiculo_id=dados.veiculo_id,
        vaga=dados.vaga.strip().upper(),
    )
    db.add(estadia)

    try:
        db.commit()
    except IntegrityError:
        # Os índices únicos também protegem contra entradas simultâneas.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O veículo já tem uma estadia aberta ou a vaga está ocupada",
        )

    db.refresh(estadia)
    return estadia


@router.get("/", response_model=list[EstadiaResponse])
def listar_estadias(db: Session = Depends(get_db)):
    return db.query(Estadia).order_by(Estadia.hora_entrada.desc()).all()


@router.get("/{estadia_id}", response_model=EstadiaResponse)
def buscar_estadia(estadia_id: int, db: Session = Depends(get_db)):
    estadia = db.get(Estadia, estadia_id)
    if estadia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estadia não encontrada",
        )
    return estadia


@router.patch("/{estadia_id}/saida", response_model=EstadiaResponse)
def registrar_saida(
    estadia_id: int,
    dados: EstadiaUpdate | None = None,
    db: Session = Depends(get_db),
):
    estadia = db.get(Estadia, estadia_id)
    if estadia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estadia não encontrada",
        )

    if estadia.status == "finalizada":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta estadia já foi finalizada",
        )

    horario_informado = dados.hora_saida if dados is not None else None
    hora_saida = (
        normalizar_horario(horario_informado)
        if horario_informado is not None
        else agora_utc_sem_fuso()
    )

    if hora_saida <= estadia.hora_entrada:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A saída precisa ocorrer depois da entrada",
        )

    if hora_saida > agora_utc_sem_fuso():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O horário de saída não pode estar no futuro",
        )

    duracao_em_segundos = (hora_saida - estadia.hora_entrada).total_seconds()
    horas_cobradas = max(1, math.ceil(duracao_em_segundos / 3600))

    estadia.hora_saida = hora_saida
    estadia.valor_total = (
        VALOR_HORA * Decimal(horas_cobradas)
    ).quantize(Decimal("0.01"))
    estadia.status = "finalizada"

    db.commit()
    db.refresh(estadia)
    return estadia