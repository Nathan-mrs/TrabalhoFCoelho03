from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Veiculo(Base):
    __tablename__ = "veiculos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    placa: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    modelo: Mapped[str] = mapped_column(String(50))
    cor: Mapped[str] = mapped_column(String(30))
    tipo: Mapped[str] = mapped_column(String(20))

    estadias: Mapped[list["Estadia"]] = relationship(
        back_populates="veiculo",
        passive_deletes="all",
    )