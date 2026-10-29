from datetime import date

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class HistoricoCargo(Base):
    """Fuente del cargo actual: el registro sin fecha_egreso (como mucho uno por funcionario)."""

    __tablename__ = "historico_cargo"
    __table_args__ = (
        CheckConstraint("fecha_egreso IS NULL OR fecha_egreso >= fecha_ingreso", name="egreso"),
        Index(
            "uq_historico_cargo_actual",
            "funcionario_id",
            unique=True,
            postgresql_where=text("fecha_egreso IS NULL"),
            sqlite_where=text("fecha_egreso IS NULL"),
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    funcionario_id: Mapped[int] = mapped_column(index=True)  # ms-funcionarios
    cargo_id: Mapped[int]  # ms-organizacion
    fecha_ingreso: Mapped[date]
    fecha_egreso: Mapped[date | None]


class TipoSancion(Base):
    __tablename__ = "tipo_sancion"
    id: Mapped[int] = mapped_column(primary_key=True)
    descripcion: Mapped[str] = mapped_column(String(100), unique=True)


class Sancion(Base):
    __tablename__ = "sancion"
    __table_args__ = (
        CheckConstraint(
            "periodo_hasta IS NULL OR periodo_desde IS NULL OR periodo_hasta >= periodo_desde",
            name="periodo",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    funcionario_id: Mapped[int] = mapped_column(index=True)  # ms-funcionarios
    tipo_sancion_id: Mapped[int] = mapped_column(ForeignKey("tipo_sancion.id"))
    motivo: Mapped[str] = mapped_column(Text)
    periodo_desde: Mapped[date | None]
    periodo_hasta: Mapped[date | None]
