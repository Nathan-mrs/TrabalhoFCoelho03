from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.veiculo import Veiculo


def agora_utc_sem_fuso() -> datetime:
    # O SQLite guarda o horário sem fuso; neste projeto, trataremos esse
    # horário como UTC.
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Estadia(Base):
    __tablename__ = "estadias"

    __table_args__ = (
        CheckConstraint(
            "status IN ('aberta', 'finalizada')",
            name="ck_estadias_status",
        ),
        CheckConstraint(
            "(status = 'aberta' AND hora_saida IS NULL AND valor_total IS NULL) "
            "OR (status = 'finalizada' AND hora_saida IS NOT NULL "
            "AND valor_total IS NOT NULL)",
            name="ck_estadias_estado_coerente",
        ),
        Index(
            "uq_estadias_veiculo_aberta",
            "veiculo_id",
            unique=True,
            sqlite_where=text("status = 'aberta'"),
        ),
        Index(
            "uq_estadias_vaga_aberta",
            "vaga",
            unique=True,
            sqlite_where=text("status = 'aberta'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    veiculo_id: Mapped[int] = mapped_column(
        ForeignKey("veiculos.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    vaga: Mapped[str] = mapped_column(String(10), nullable=False)

    hora_entrada: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=agora_utc_sem_fuso,
    )

    hora_saida: Mapped[datetime | None] = mapped_column(
        DateTime(),
        nullable=True,
    )

    valor_total: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(12),
        nullable=False,
        default="aberta",
    )

    veiculo: Mapped["Veiculo"] = relationship(
        back_populates="estadias",
    )