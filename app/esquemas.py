"""Esquemas del contrato contrato/openapi.yaml."""

from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator


class _Salida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int


class HistoricoCargo(BaseModel):
    funcionario_id: int
    cargo_id: int
    fecha_ingreso: date
    fecha_egreso: date | None = None

    @model_validator(mode="after")
    def _fechas(self):
        if self.fecha_egreso and self.fecha_egreso < self.fecha_ingreso:
            raise ValueError("fecha_egreso no puede ser anterior a fecha_ingreso")
        return self


class HistoricoCargoPatch(BaseModel):
    funcionario_id: int | None = None
    cargo_id: int | None = None
    fecha_ingreso: date | None = None
    fecha_egreso: date | None = None


class HistoricoCargoSalida(HistoricoCargo, _Salida):
    pass


class TipoSancion(BaseModel):
    descripcion: Annotated[str, Field(min_length=1, max_length=100)]


class TipoSancionPatch(BaseModel):
    descripcion: Annotated[str, Field(min_length=1, max_length=100)] | None = None


class TipoSancionSalida(TipoSancion, _Salida):
    pass


class Sancion(BaseModel):
    funcionario_id: int
    tipo_sancion_id: int
    motivo: Annotated[str, Field(min_length=1)]
    periodo_desde: date | None = None
    periodo_hasta: date | None = None

    @model_validator(mode="after")
    def _periodo(self):
        if self.periodo_desde and self.periodo_hasta and self.periodo_hasta < self.periodo_desde:
            raise ValueError("periodo_hasta no puede ser anterior a periodo_desde")
        return self


class SancionPatch(BaseModel):
    funcionario_id: int | None = None
    tipo_sancion_id: int | None = None
    motivo: Annotated[str, Field(min_length=1)] | None = None
    periodo_desde: date | None = None
    periodo_hasta: date | None = None


class SancionSalida(Sancion, _Salida):
    pass
