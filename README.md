# ms-desempeno

Microservicio de Historial y Desempeño. Histórico de cargos y sanciones del personal.

Implementa el contrato [`contrato/openapi.yaml`](contrato/openapi.yaml) con FastAPI, SQLAlchemy 2 y Alembic sobre PostgreSQL (schema `desempeno`).

## Respecto al contrato

- Filtros: `/historicos-cargo?funcionario_id=&cargo_id=`, `/sanciones?funcionario_id=&tipo_sancion_id=`.
- Cada funcionario tiene a lo sumo un cargo abierto (`fecha_egreso` vacía). `POST /historicos-cargo` cierra el cargo abierto el día anterior al nuevo `fecha_ingreso`; si el nuevo no es posterior responde 409.
- `GET /cargos-actuales?funcionario_id=` devuelve el cargo abierto de cada funcionario.
- Búsqueda por texto con `?q=` en tipos de sanción.
- Un tipo de sanción en uso no se puede borrar (409).
- Los ids de otros servicios (funcionario y cargo) se verifican con el servicio dueño antes de guardar: 422 si no existe, 503 si no responde. Usa el client `ms-desempeno` de Keycloak (`SERVICIO_CLIENT_ID`/`SERVICIO_CLIENT_SECRET`); sin esas variables, como en las pruebas, no se verifica.

## Desarrollo

Este repo usa `rrhh-common`, que tiene que estar clonado al lado:

```
rrhh/
├── rrhh-common/
├── rrhh-plataforma/
└── ms-desempeno/
```

```bash
python -m venv .venv && . .venv/bin/activate
pip install "../rrhh-common[db]" -e ".[dev]"
pytest              # usa SQLite en memoria, no necesita la plataforma
ruff check app tests && ruff format --check app tests
```

## Levantar con la plataforma

```bash
cd ../rrhh-plataforma && docker compose up -d
cd ../ms-desempeno && docker compose up -d --build
```

Al arrancar, el contenedor aplica las migraciones (`alembic upgrade head`) en el schema `desempeno`. Queda accesible solo por Kong en `http://localhost:8000/api/desempeno/...` con un token de Keycloak. La documentación interactiva está en `/api/desempeno/docs` (también detrás del gateway).

## Migraciones

```bash
export DATABASE_URL=postgresql+psycopg://ms_desempeno:servicio-dev@localhost:5432/rrhh
alembic revision --autogenerate -m "descripcion del cambio"
alembic upgrade head
```

## Roles

Lectura: `rrhh-operador`, `nomina-liquidador`, `consulta`. Escritura: `rrhh-operador`. `rrhh-admin` puede todo.

## CI

GitHub Actions corre ruff y pytest. Como `rrhh-common` es privado, el repo necesita el secreto **`RRHH_COMMON_TOKEN`**: un token *fine-grained* con permiso `Contents: read` sobre `hmoreli/rrhh-common`.
