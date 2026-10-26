from tests.conftest import CONSULTA, OPERADOR, validador_simulado


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


def test_cargo_nuevo_cierra_el_actual(cliente):
    crear(
        cliente,
        "/historicos-cargo",
        {"funcionario_id": 5, "cargo_id": 1, "fecha_ingreso": "2024-01-01"},
    )
    crear(
        cliente,
        "/historicos-cargo",
        {"funcionario_id": 5, "cargo_id": 2, "fecha_ingreso": "2026-10-01"},
    )
    historial = cliente.get("/historicos-cargo?funcionario_id=5", headers=CONSULTA).json()
    assert [(h["cargo_id"], h["fecha_egreso"]) for h in historial] == [
        (1, "2026-09-30"),
        (2, None),
    ]
    actual = cliente.get("/cargos-actuales?funcionario_id=5", headers=CONSULTA).json()
    assert [a["cargo_id"] for a in actual] == [2]


def test_cargo_nuevo_anterior_al_actual_da_conflicto(cliente):
    crear(
        cliente,
        "/historicos-cargo",
        {"funcionario_id": 5, "cargo_id": 1, "fecha_ingreso": "2024-01-01"},
    )
    r = cliente.post(
        "/historicos-cargo",
        json={"funcionario_id": 5, "cargo_id": 2, "fecha_ingreso": "2023-01-01"},
        headers=OPERADOR,
    )
    assert r.status_code == 409


def test_valida_funcionario_y_cargo(cliente):
    cliente.app.state.referencias = validador_simulado(
        "ms-funcionarios/funcionarios/5", "ms-organizacion/cargos/1"
    )
    crear(
        cliente,
        "/historicos-cargo",
        {"funcionario_id": 5, "cargo_id": 1, "fecha_ingreso": "2024-01-01"},
    )
    r = cliente.post(
        "/historicos-cargo",
        json={"funcionario_id": 6, "cargo_id": 9, "fecha_ingreso": "2024-01-01"},
        headers=OPERADOR,
    )
    assert r.status_code == 422
    assert {d["mensaje"] for d in r.json()["detalles"]} == {
        "No existe el funcionario 6",
        "No existe el cargo 9",
    }
