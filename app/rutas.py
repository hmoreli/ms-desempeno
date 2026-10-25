from rrhh_common.crud import router_crud

from app import esquemas as e
from app import modelos as m
from app.db import obtener_sesion

routers = [
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
        etiqueta="Sanciones",
        nombre="Tipo de sanción",
        sesion=obtener_sesion,
    ),
]
