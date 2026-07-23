# API de Análisis Financiero

API REST desarrollada con **FastAPI** para el hackathon de NoCountry. Permite registrar usuarios y sus transacciones (ingresos y gastos), consultarlos, y calcular el perfil financiero de un usuario (saludable / en observación / en riesgo) comparando su ahorro real contra su propia meta de ahorro, con una recomendación asociada.

## Estado del proyecto

**Avance 2** — CRUD completo de usuarios y transacciones funcionando localmente, más el cálculo de perfil financiero. Aún no incluye frontend, base de datos en la nube (OCI) ni el modelo de Data Science del equipo.

## Tecnologías usadas

- **Python 3**
- **FastAPI** — framework para construir la API
- **SQLAlchemy** — conexión y manejo de la base de datos
- **SQLite** — base de datos local para esta primera versión (se migrará a Postgres/OCI más adelante)
- **Uvicorn** — servidor que ejecuta la API

## Cómo correrlo localmente

1. Clonar el repositorio y entrar a la carpeta del proyecto.

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
| `GET` | `/perfil/{usuario_id}` | Calcula el perfil financiero del usuario y devuelve una recomendación |

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

### Ejemplo: crear una transacción

```json
POST /transacciones
{
  "usuario_id": 1,
  "categoria": "alimentacion",
  "tipo": "gasto",
  "monto": 600
}
```

### Ejemplo: consultar el perfil financiero

```
GET /perfil/1
```

Calcula cuánto ahorró realmente el usuario (ingresos - gastos de sus transacciones) y lo compara contra su propia meta de ahorro. Devuelve el ingreso total, el ahorro real, el porcentaje de ahorro real, el porcentaje de cumplimiento de su meta, el perfil resultante (`saludable`, `en observación` o `en riesgo`) y una recomendación en texto.

**Regla de negocio:**
- `cumplimiento_meta >= 1` → el usuario cumplió o superó su meta → **saludable**
- `cumplimiento_meta >= 0.5` → ahorra, pero por debajo de su meta → **en observación**
- `cumplimiento_meta < 0.5` → muy por debajo de su meta → **en riesgo**

## Estructura del proyecto

```
├── main.py        # Rutas de la API
├── models.py       # Modelos de la base de datos (tablas)
├── schemas.py      # Estructuras de entrada/salida de la API
├── database.py     # Configuración de la conexión a la base de datos
└── finanzas.db      # Base de datos SQLite (se genera automáticamente)
```

## Próximos pasos

- Conectar con el frontend
- Migrar la base de datos a PostgreSQL/OCI 
- Integrar el modelo/dataset del equipo de Data Science
- Afinar la lógica de recomendaciones según feedback del equipo