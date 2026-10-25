from tests.conftest import CONSULTA, OPERADOR


def crear(cliente, ruta, datos):
    r = cliente.post(ruta, json=datos, headers=OPERADOR)
    assert r.status_code == 201, r.text
    return r.json()


def test_historial_de_cargos_por_funcionario(cliente):
    crear(
        cliente,
        "/historicos-cargo",
        {
            "funcionario_id": 3,
            "cargo_id": 1,
            "fecha_ingreso": "2020-01-01",
            "fecha_egreso": "2022-12-31",
        },
    )
    crear(
        cliente,
        "/historicos-cargo",
        {"funcionario_id": 3, "cargo_id": 2, "fecha_ingreso": "2023-01-01"},
    )
    crear(
        cliente,
        "/historicos-cargo",
        {"funcionario_id": 4, "cargo_id": 2, "fecha_ingreso": "2023-01-01"},
    )
    lista = cliente.get("/historicos-cargo?funcionario_id=3", headers=CONSULTA).json()
    assert [h["cargo_id"] for h in lista] == [1, 2]


def test_historial_con_fechas_invertidas(cliente):
    r = cliente.post(
        "/historicos-cargo",
        json={
            "funcionario_id": 3,
            "cargo_id": 1,
            "fecha_ingreso": "2020-01-01",
            "fecha_egreso": "2019-01-01",
        },
        headers=OPERADOR,
    )
    assert r.status_code == 422


def test_sancion_y_su_tipo(cliente):
    tipo = crear(cliente, "/tipos-sancion", {"descripcion": "Amonestación escrita"})
    s = crear(
        cliente,
        "/sanciones",
        {
            "funcionario_id": 3,
            "tipo_sancion_id": tipo["id"],
            "motivo": "Llegadas tardías reiteradas",
            "periodo_desde": "2026-10-01",
            "periodo_hasta": "2026-10-03",
        },
    )
    assert (
        cliente.get(f"/sanciones/{s['id']}", headers=CONSULTA)
        .json()["motivo"]
        .startswith("Llegadas")
    )
    assert cliente.delete(f"/tipos-sancion/{tipo['id']}", headers=OPERADOR).status_code == 409


def test_sancion_sin_motivo(cliente):
    tipo = crear(cliente, "/tipos-sancion", {"descripcion": "Suspensión"})
    r = cliente.post(
        "/sanciones", json={"funcionario_id": 3, "tipo_sancion_id": tipo["id"]}, headers=OPERADOR
    )
    assert r.status_code == 422


def test_rutas_del_contrato_existen(cliente):
    rutas = set(cliente.get("/openapi.json").json()["paths"])
    for base in ("/historicos-cargo", "/sanciones", "/tipos-sancion"):
        assert {base, base + "/{id}"} <= rutas
