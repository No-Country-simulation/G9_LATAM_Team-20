# EconomIA

Proyecto desarrollado para el Hackathon Oracle Next Education (ONE) y No Country
Equipo: G9 LATAM Team 20

<p align="center">
  <img src="assets/team 20 logo.jpg" alt="Logo del equipo" width="200">
</p>

## 📖 Descripción

EconomIA es una plataforma web que ayuda a las personas a entender su situación financiera de forma simple y accionable. A partir de sus ingresos, gastos, meta de ahorro y nivel de deuda, la plataforma clasifica automáticamente sus movimientos por categoría usando un modelo de Machine Learning, calcula su perfil de salud financiera, y genera recomendaciones personalizadas y graduales para mejorar sus hábitos.

## 🎯 Problema

Muchas personas registran sus ingresos y gastos, pero les resulta difícil transformar esos datos en información útil para tomar mejores decisiones financieras. EconomIA convierte esos datos en un diagnóstico claro (saludable / en observación / en riesgo) y en pasos concretos para mejorar, sin necesitar conocimientos financieros previos.

## 🚀 Funcionalidades

- Registro y gestión de usuarios (CRUD completo)
- Registro y gestión de transacciones, con fecha y descripción (CRUD completo)
- Clasificación automática de gastos por categoría mediante un modelo de Machine Learning entrenado
- Sugerencia de categoría con nivel de confianza, visible para el usuario en tiempo real
- Resumen mensual: ingresos, gastos totales y desglose por categoría
- Cálculo del perfil de salud financiera, considerando ahorro real, meta personal de ahorro y nivel de deuda
- Recomendaciones personalizadas y graduales (mencionan la categoría específica de mayor gasto cuando es relevante)
- Dashboard interactivo con historial de movimientos, gráfica de distribución de gastos y estado de salud financiera

## 🛠 Tecnologías utilizadas

**Frontend**
- HTML5, CSS3, JavaScript (sin frameworks)
- Chart.js (visualización de datos)

**Backend**
- Python
- FastAPI
- SQLAlchemy
- Pydantic

**Ciencia de Datos / Machine Learning**
- Python
- Pandas, NumPy
- Scikit-Learn (TF-IDF + Regresión Logística)
- Joblib

**Base de datos**
- SQLite (desarrollo actual)
- PostgreSQL en Oracle Cloud Infrastructure (en progreso)

**Cloud y despliegue**
- Oracle Cloud Infrastructure (OCI) — en progreso

**DevOps**
- Git, GitHub

## 🏗 Arquitectura

```
                  Usuario
                     │
                     ▼
      Frontend (HTML + CSS + JavaScript)
                     │
                     ▼
           Backend (FastAPI)
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   Usuarios /   POST /clasificar-  Perfil financiero
 Transacciones      gasto          (reglas de negocio)
        │            │
        ▼            ▼
     SQLite    category_classifier_v1.joblib
  (→ PostgreSQL/OCI, en progreso)
```

## 📂 Estructura del proyecto

```
├── backend/
│   ├── main.py           # Rutas de la API
│   ├── models.py         # Modelos de la base de datos
│   ├── schemas.py        # Estructuras de entrada/salida
│   ├── database.py       # Configuración de la base de datos
│   └── modelos/
│       └── category_classifier_v1.joblib
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── .gitignore
└── README.md
```

## 📊 Flujo de funcionamiento

```
Registro / acceso del usuario
            ↓
Registro de transacciones (con descripción)
            ↓
Clasificación automática de categoría (Machine Learning)
            ↓
Cálculo del perfil financiero (reglas de negocio)
            ↓
Recomendación personalizada
            ↓
Visualización en el Dashboard
```

## 🤖 Ciencia de Datos

El modelo de clasificación de gastos fue desarrollado a partir de un dataset propio construido por el equipo:

- Generación de un dataset sintético de descripciones de transacciones
- Separación train / validation / test agrupada por frase, para evitar fuga de información
- Representación del texto mediante TF-IDF de palabras y de caracteres
- Comparación de tres modelos (Regresión Logística, Complement Naive Bayes, Linear SVM), evaluados con F1 macro
- Selección de Regresión Logística por ofrecer probabilidades nativas, buen desempeño y un pipeline simple de integrar
- Iteración basada en análisis de errores: se reforzaron las categorías con más confusión (Educación, Servicios, Transporte) con nuevos ejemplos
- Resultado final: 77.8% de accuracy y 88.9% de accuracy considerando el top 3 de categorías sugeridas
- Serialización del pipeline completo (vectorizador + modelo) con Joblib

El modelo devuelve la categoría, el nivel de confianza, y las 3 categorías más probables — si la confianza es menor al umbral definido, se marca para revisión del usuario.

Está en desarrollo un segundo modelo de análisis financiero, que calculará un score y diagnóstico a partir de indicadores mensuales más amplios (financiamiento, inversiones, gasto recurrente vs. variable, promedio de balance de 3 meses). Su integración se hará una vez definido el formato final, sin reemplazar el sistema de reglas de negocio ya funcional.

## 🔌 API

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Verifica que la API esté corriendo |
| POST | `/usuarios` | Registra un nuevo usuario |
| GET | `/usuarios` | Lista todos los usuarios |
| GET | `/usuarios/{usuario_id}` | Consulta un usuario |
| PUT | `/usuarios/{usuario_id}` | Actualiza un usuario |
| DELETE | `/usuarios/{usuario_id}` | Elimina un usuario |
| POST | `/transacciones` | Registra una transacción |
| GET | `/transacciones/{usuario_id}` | Lista las transacciones de un usuario |
| PUT | `/transacciones/{transaccion_id}` | Actualiza una transacción |
| DELETE | `/transacciones/{transaccion_id}` | Elimina una transacción |
| GET | `/resumen-mensual/{usuario_id}` | Resumen de ingresos, gastos y categorías del mes |
| GET | `/perfil/{usuario_id}` | Calcula el perfil de salud financiera y su recomendación |
| POST | `/clasificar-gasto` | Clasifica una descripción de gasto usando el modelo de Machine Learning |

## 📅 Estado del proyecto

- ✅ Diseño de la arquitectura
- ✅ Generación del dataset sintético del clasificador
- ✅ Entrenamiento y evaluación del modelo de clasificación de gastos
- ✅ Desarrollo del backend (FastAPI) con CRUD completo de usuarios y transacciones
- ✅ Cálculo del perfil financiero con reglas de negocio explicables
- ✅ Integración del modelo de clasificación de gastos en el backend
- ✅ Desarrollo del frontend con dashboard interactivo
- ⬜ Modelo de análisis financiero (en desarrollo por el equipo de Data Science)
- ⬜ Autenticación de usuarios
- ⬜ Migración de base de datos a PostgreSQL en OCI
- ⬜ Despliegue en Oracle Cloud Infrastructure (OCI)
- ⬜ Presentación final del proyecto

## 👥 Equipo

**G9 LATAM Team 20**

Equipo multidisciplinario participante del Hackathon Oracle Next Education (ONE) y No Country.

Desarrollo de Backend, Frontend, Ciencia de Datos, Machine Learning e Integración.

## 📄 Licencia

Proyecto desarrollado con fines educativos para el Hackathon Oracle Next Education (ONE), organizado por Alura Latam, Oracle y No Country. Su propósito es demostrar la integración de tecnologías de desarrollo web, ciencia de datos y machine learning para resolver un problema real relacionado con la educación financiera. Los datos utilizados son sintéticos y no deben interpretarse como información financiera real.
