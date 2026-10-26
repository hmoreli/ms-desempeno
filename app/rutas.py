from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from rrhh_common import Paginacion, Usuario, requiere_roles
from rrhh_common.crud import ROLES_ESCRITURA, ROLES_LECTURA, router_crud
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import esquemas as e
from app import modelos as m
from app.db import obtener_sesion

# ms-desempeno es la fuente del cargo actual de cada funcionario: el registro del
# historial sin fecha_egreso. Asignar un cargo nuevo cierra el anterior.
historial = APIRouter(tags=["Historial de Cargos"])


@historial.post(
    "/historicos-cargo",
    response_model=e.HistoricoCargoSalida,
    status_code=201,
    summary="Registrar un cargo en el historial",
    description="Si el registro no tiene fecha_egreso pasa a ser el cargo actual y el cargo "
    "actual anterior se cierra el día antes de fecha_ingreso.",
)
def asignar_cargo(
    datos: e.HistoricoCargo,
    db: Session = Depends(obtener_sesion),
    _: Usuario = Depends(requiere_roles(*ROLES_ESCRITURA)),
):
    if datos.fecha_egreso is None:
        actual = db.scalar(
            select(m.HistoricoCargo).where(
                m.HistoricoCargo.funcionario_id == datos.funcionario_id,
                m.HistoricoCargo.fecha_egreso.is_(None),
            )
        )
        if actual is not None:
            if datos.fecha_ingreso <= actual.fecha_ingreso:
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    detail=f"El cargo actual empezó el {actual.fecha_ingreso}; "
                    "el nuevo tiene que empezar después",
                )
            actual.fecha_egreso = datos.fecha_ingreso - timedelta(days=1)
            db.flush()
    registro = m.HistoricoCargo(**datos.model_dump())
    db.add(registro)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="El funcionario ya tiene un cargo actual"
        ) from None
    db.refresh(registro)
    return registro


@historial.get(
    "/cargos-actuales",
    response_model=list[e.HistoricoCargoSalida],
    summary="Cargo actual de cada funcionario",
    description="Registros del historial sin fecha_egreso. Filtrar por funcionario_id para "
    "uno solo, o por cargo_id para ver quiénes ocupan un cargo.",
)
def cargos_actuales(
    p: Paginacion = Depends(),
    funcionario_id: int | None = None,
    cargo_id: int | None = None,
    db: Session = Depends(obtener_sesion),
    _: Usuario = Depends(requiere_roles(*ROLES_LECTURA)),
):
    consulta = select(m.HistoricoCargo).where(m.HistoricoCargo.fecha_egreso.is_(None))
    if funcionario_id is not None:
        consulta = consulta.where(m.HistoricoCargo.funcionario_id == funcionario_id)
    if cargo_id is not None:
        consulta = consulta.where(m.HistoricoCargo.cargo_id == cargo_id)
    consulta = consulta.order_by(m.HistoricoCargo.funcionario_id)
    return db.scalars(consulta.offset(p.offset).limit(p.limit)).all()


routers = [
    historial,
    router_crud(
        modelo=m.HistoricoCargo,
        crear=e.HistoricoCargo,
        parche=e.HistoricoCargoPatch,
        salida=e.HistoricoCargoSalida,
        prefijo="/historicos-cargo",
        etiqueta="Historial de Cargos",
        nombre="Registro de historial de cargo",
        sesion=obtener_sesion,
        filtros={"funcionario_id": int, "cargo_id": int},
        # El alta va por asignar_cargo (cierra el cargo actual anterior).
        metodos={"listar", "obtener", "actualizar", "eliminar"},
    ),
    router_crud(
        modelo=m.Sancion,
        crear=e.Sancion,
        parche=e.SancionPatch,
        salida=e.SancionSalida,
        prefijo="/sanciones",
        etiqueta="Sanciones",
        nombre="Sanción",
        sesion=obtener_sesion,
        filtros={"funcionario_id": int, "tipo_sancion_id": int},
    ),
    router_crud(
        modelo=m.TipoSancion,
        crear=e.TipoSancion,
        parche=e.TipoSancionPatch,
        salida=e.TipoSancionSalida,
        prefijo="/tipos-sancion",
        busqueda=("descripcion",),
        etiqueta="Sanciones",
        nombre="Tipo de sanción",
        sesion=obtener_sesion,
    ),
]
