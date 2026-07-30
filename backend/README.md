# API de Análisis Financiero

API REST desarrollada con **FastAPI** para el hackathon de NoCountry. Permite registrar usuarios y sus transacciones (ingresos y gastos), consultarlos, obtener un resumen mensual de gastos por categoría, y calcular el perfil financiero de un usuario (saludable / en observación / en riesgo) considerando su ahorro real, su meta de ahorro y su nivel de deuda, con recomendaciones personalizadas y graduales.

## Estado del proyecto

🚧 **Avance 3** — Backend con clasificación de gastos por categoría, resumen mensual, y perfil financiero completo (ahorro + deuda + categoría de mayor gasto) funcionando localmente. Aún no incluye frontend, login, base de datos en la nube (OCI) ni el modelo de Data Science del equipo.

## Tecnologías usadas

- **Python 3**
- **FastAPI** — framework para construir la API
- **SQLAlchemy** — conexión y manejo de la base de datos
- **SQLite** — base de datos local para esta primera versión (se migrará a Postgres/OCI más adelante)
- **Uvicorn** — servidor que ejecuta la API

## Cómo correrlo localmente

1. Clonar el repositorio y entrar a la carpeta `backend`:
   ```bash
   cd backend
   ```

2. Crear y activar un entorno virtual:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\Activate.ps1
   ```

3. Instalar dependencias:
   ```bash
   pip install fastapi uvicorn sqlalchemy
   ```

4. Levantar el servidor:
   ```bash
   uvicorn main:app --reload
   ```

5. Abrir la documentación interactiva en el navegador:
   ```
   http://127.0.0.1:8000/docs
   ```

## Endpoints disponibles

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Verifica que la API esté corriendo |
| `POST` | `/usuarios` | Registra un nuevo usuario (datos demográficos y financieros) |
| `PUT` | `/usuarios/{usuario_id}` | Actualiza los datos de un usuario existente |
| `DELETE` | `/usuarios/{usuario_id}` | Elimina un usuario |
| `POST` | `/transacciones` | Registra una nueva transacción (ingreso o gasto) |
| `GET` | `/transacciones/{usuario_id}` | Lista todas las transacciones de un usuario |
| `PUT` | `/transacciones/{transaccion_id}` | Actualiza una transacción existente |
| `DELETE` | `/transacciones/{transaccion_id}` | Elimina una transacción |
| `GET` | `/resumen-mensual/{usuario_id}?anio=&mes=` | Resumen del mes: ingresos, gastos totales, gastos por categoría y categoría de mayor gasto |
| `GET` | `/perfil/{usuario_id}?anio=&mes=` | Calcula el perfil financiero del usuario para ese mes y devuelve una recomendación |

### Ejemplo: crear un usuario

```json
POST /usuarios
{
  "edad": 41,
  "sexo": "O",
  "ocupacion": "Ejecutivo",
  "ciudad": "Durango",
  "ingreso_base": 86579.3,
  "ingreso_variable": 4265.64,
  "meta_ahorro": 36,
  "nivel_deuda_inicial": 45
}
```

`meta_ahorro` es el porcentaje de su ingreso que el usuario se propone ahorrar (36 = 36%).

### Categorías de gasto

`alimentacion`, `transporte`, `salud`, `vivienda`, `educacion`, `entretenimiento`, `compras`, `deudas`, `finanzas`, `otros`.

Las primeras cinco (`alimentacion`, `transporte`, `salud`, `vivienda`, `educacion`) se consideran **esenciales**; el resto se consideran **no esenciales** para efecto de las recomendaciones.

### Ejemplo: crear una transacción

```json
POST /transacciones
{
  "usuario_id": 1,
  "categoria": "alimentacion",
  "tipo": "gasto",
  "monto": 600,
  "descripcion": "Supermercado de la quincena",
  "fecha": "2026-07-08T12:00:00"
}
```

`descripcion` y `fecha` son opcionales: si no se manda `fecha`, se usa la fecha y hora actual automáticamente.

### Ejemplo: resumen mensual

```
GET /resumen-mensual/1?anio=2026&mes=7
```

Devuelve los ingresos totales, gastos totales, un desglose de gastos por categoría, y cuál fue la categoría de mayor gasto ese mes.

### Ejemplo: consultar el perfil financiero

```
GET /perfil/1?anio=2026&mes=7
```

Calcula cuánto ahorró realmente el usuario ese mes (ingresos - gastos) y lo compara contra su propia meta de ahorro, considerando también su nivel de deuda. Si el mayor gasto del mes fue en una categoría no esencial, la recomendación lo menciona explícitamente (los pagos de la categoría `deudas` se excluyen de esta comparación, ya que reducirlos no es deseable). Devuelve el ingreso total, el ahorro real, el porcentaje de ahorro real, el cumplimiento de la meta, el nivel de deuda, la categoría de mayor gasto, el perfil resultante (`saludable`, `en observación` o `en riesgo`) y una recomendación en texto.

**Regla de negocio:**
- Cumple o supera su meta de ahorro **y** deuda baja (< 30%) → **saludable**
- Cumple su meta pero deuda alta → **en observación** (sugiere destinar ahorro a la deuda, mencionando la categoría de mayor gasto si es no esencial)
- No cumple su meta y deuda alta → **en riesgo** (sugiere reducir gastos no esenciales y priorizar la deuda)
- No cumple su meta pero deuda baja → **en observación** (sugiere revisar gastos variables)

## Estructura del proyecto

```
├── backend/
│   ├── main.py        # Rutas de la API
│   ├── models.py      # Modelos de la base de datos (tablas)
│   ├── schemas.py     # Estructuras de entrada/salida de la API
│   ├── database.py    # Configuración de la conexión a la base de datos
│   └── finanzas.db    # Base de datos SQLite (se genera automáticamente)
├── .gitignore
└── README.md
```

## Próximos pasos

- Conectar con el frontend
- Evaluar agregar login por usuario con rol de administrador
- Migrar la base de datos a PostgreSQL/OCI 
- Integrar el modelo/dataset del equipo de Data Science
- Afinar la lógica de recomendaciones según feedback del equipo








# Datos de ejemplo para la demo (julio 2026)
## Usuario 1 — Saludable (ahorra mucho, deuda baja)

```json
{ "edad": 29, "sexo": "F", "ocupacion": "Ingeniera", "ciudad": "Querétaro", "ingreso_base": 30000, "ingreso_variable": 2000, "meta_ahorro": 20, "nivel_deuda_inicial": 10 }
```

Transacciones (`usuario_id: 1`):
```json
{ "usuario_id": 1, "categoria": "finanzas", "tipo": "ingreso", "monto": 32000, "descripcion": "Nómina de julio", "fecha": "2026-07-05T09:00:00" }
{ "usuario_id": 1, "categoria": "alimentacion", "tipo": "gasto", "monto": 3500, "descripcion": "Supermercado", "fecha": "2026-07-08T12:00:00" }
{ "usuario_id": 1, "categoria": "transporte", "tipo": "gasto", "monto": 1200, "descripcion": "Gasolina y mantenimiento", "fecha": "2026-07-10T08:00:00" }
{ "usuario_id": 1, "categoria": "entretenimiento", "tipo": "gasto", "monto": 1500, "descripcion": "Salidas del mes", "fecha": "2026-07-15T20:00:00" }
```

Resultado esperado: ahorra ≈ 25,800 (muy por encima de su meta), deuda baja → **saludable**

---

## Usuario 2 — En observación (ahorra bien, pero deuda alta)

```json
{ "edad": 35, "sexo": "M", "ocupacion": "Vendedor", "ciudad": "Puebla", "ingreso_base": 20000, "ingreso_variable": 3000, "meta_ahorro": 15, "nivel_deuda_inicial": 45 }
```

Transacciones (`usuario_id: 2`):
```json
{ "usuario_id": 2, "categoria": "finanzas", "tipo": "ingreso", "monto": 23000, "descripcion": "Nómina de julio", "fecha": "2026-07-05T09:00:00" }
{ "usuario_id": 2, "categoria": "vivienda", "tipo": "gasto", "monto": 5000, "descripcion": "Renta", "fecha": "2026-07-08T12:00:00" }
{ "usuario_id": 2, "categoria": "alimentacion", "tipo": "gasto", "monto": 4000, "descripcion": "Supermercado", "fecha": "2026-07-10T08:00:00" }
{ "usuario_id": 2, "categoria": "deudas", "tipo": "gasto", "monto": 3000, "descripcion": "Pago de tarjeta", "fecha": "2026-07-20T08:00:00" }
```

Resultado esperado: ahorra ≈ 11,000 (cumple su meta), pero deuda alta (45%) → **en observación**

---

## Usuario 3 — En observación (no llega a su meta, deuda manejable)

```json
{ "edad": 26, "sexo": "F", "ocupacion": "Diseñadora", "ciudad": "Mérida", "ingreso_base": 15000, "ingreso_variable": 1000, "meta_ahorro": 20, "nivel_deuda_inicial": 15 }
```

Transacciones (`usuario_id: 3`):
```json
{ "usuario_id": 3, "categoria": "finanzas", "tipo": "ingreso", "monto": 16000, "descripcion": "Nómina de julio", "fecha": "2026-07-05T09:00:00" }
{ "usuario_id": 3, "categoria": "alimentacion", "tipo": "gasto", "monto": 3500, "descripcion": "Supermercado", "fecha": "2026-07-08T12:00:00" }
{ "usuario_id": 3, "categoria": "entretenimiento", "tipo": "gasto", "monto": 3200, "descripcion": "Salidas y streaming", "fecha": "2026-07-15T20:00:00" }
{ "usuario_id": 3, "categoria": "compras", "tipo": "gasto", "monto": 2500, "descripcion": "Ropa", "fecha": "2026-07-18T08:00:00" }
```

Resultado esperado: ahorro por debajo de su meta, deuda baja → **en observación**

---

## Usuario 4 — En riesgo (no ahorra, deuda alta, mayor gasto no esencial)

```json
{ "edad": 40, "sexo": "M", "ocupacion": "Chofer", "ciudad": "Tijuana", "ingreso_base": 14000, "ingreso_variable": 1500, "meta_ahorro": 15, "nivel_deuda_inicial": 65 }
```

Transacciones (`usuario_id: 4`):
```json
{ "usuario_id": 4, "categoria": "finanzas", "tipo": "ingreso", "monto": 15500, "descripcion": "Nómina de julio", "fecha": "2026-07-05T09:00:00" }
{ "usuario_id": 4, "categoria": "vivienda", "tipo": "gasto", "monto": 4500, "descripcion": "Renta", "fecha": "2026-07-08T12:00:00" }
{ "usuario_id": 4, "categoria": "alimentacion", "tipo": "gasto", "monto": 3500, "descripcion": "Supermercado", "fecha": "2026-07-10T08:00:00" }
{ "usuario_id": 4, "categoria": "entretenimiento", "tipo": "gasto", "monto": 5000, "descripcion": "Salidas, apuestas y streaming", "fecha": "2026-07-15T20:00:00" }
{ "usuario_id": 4, "categoria": "deudas", "tipo": "gasto", "monto": 2500, "descripcion": "Pago mínimo de tarjetas", "fecha": "2026-07-22T08:00:00" }
```

Resultado esperado: gasta más de lo que gana, deuda muy alta (65%), mayor gasto en `entretenimiento` → **en riesgo**, con recomendación mencionando la categoría explícitamente