# EconomIA — Análisis Financiero Mensual

## Descripción

Este módulo de **EconomIA** transforma la información de usuarios y transacciones en un resumen financiero mensual capaz de generar:

- Indicadores financieros
- Financial Score
- Bonus por buenos hábitos
- Perfil financiero
- Diagnóstico principal
- Recomendación base

A diferencia del clasificador de transacciones, este componente **no utiliza Machine Learning como motor principal del MVP**. El análisis se basa en reglas financieras explícitas.

```text
Usuarios + Transacciones
          ↓
Resumen mensual
          ↓
Indicadores financieros
          ↓
Scoring explicable
          ↓
Score base + Bonus
          ↓
Perfil financiero
          ↓
Diagnóstico + Recomendación
```

---

## Objetivo

El objetivo es convertir movimientos financieros individuales en una visión mensual comprensible del estado financiero del usuario.

El sistema busca responder preguntas como:

- ¿Qué porcentaje de sus ingresos está gastando?
- ¿Está cumpliendo su meta de ahorro?
- ¿Qué tan relevante es su deuda?
- ¿Necesitó financiamiento adicional?
- ¿Controló sus gastos variables?
- ¿Su situación mensual es saludable, requiere observación o presenta riesgo?

---

## Notebook principal

```text
HACKATON (EconomIA) - Analisis_Financiero
```

El notebook realiza:

- Carga y validación de usuarios y transacciones
- Construcción de periodos mensuales
- Agregación usuario-mes
- Cálculo de indicadores
- Estimación de deuda
- Cálculo de tendencias de tres meses
- Financial Score y bonus de buenos hábitos
- Clasificación financiera
- Diagnóstico
- Recomendación
- Benchmark experimental de Machine Learning

---

## Datos de entrada

### Usuarios

El análisis utiliza variables declaradas o iniciales como:

```text
user_id
edad
ocupacion
situacion_vida
ingreso_base_estimado
ingreso_variable_estimado
ingreso_total_estimado
meta_ahorro
frecuencia_ahorro
ratio_deuda_inicial
saldo_deuda_inicial
```

### Transacciones

Las transacciones incluyen información como:

```text
transaction_id
user_id
fecha
tipo
monto
categoria
subcategoria
descripcion
recurrente
metodo_pago
canal
origen
```

Las categorías `Deudas` y `Finanzas` se mantienen separadas de los gastos de consumo porque representan decisiones financieras diferentes.

---

## Resumen mensual

El notebook genera una fila por:

```text
usuario + mes
```

Ejemplo:

```text
USR_00001 | 2025-01
USR_00001 | 2025-02
USR_00001 | 2025-03
...
```

Esto permite analizar tendencias y comparar el comportamiento financiero a lo largo del tiempo.

---

## Indicadores principales

Entre los indicadores calculados se encuentran:

```text
ingresos
gastos
gastos_recurrentes
gastos_variables
pagos_deuda
ahorro
inversiones
financiamiento
balance_operativo
saldo_caja
tasa_gasto
tasa_ahorro
tasa_pago_deuda
tasa_financiamiento
tasa_inversion
tasa_gasto_variable
cumplimiento_meta_ahorro
saldo_deuda_estimado
ratio_saldo_deuda_ingreso
variacion_ingreso_3m
promedio_balance_3m
meses_con_financiamiento_3m
```

---

# Financial Score

El score principal está compuesto por cinco dimensiones:

| Componente | Máximo |
|---|---:|
| Nivel de gasto | 25 |
| Cumplimiento de ahorro | 25 |
| Nivel de deuda | 20 |
| Necesidad de financiamiento | 20 |
| Control del gasto variable | 10 |
| **Total score base** | **100** |

Las funciones de scoring utilizan transiciones progresivas para evitar saltos excesivos entre usuarios con valores financieros muy cercanos.

---

## Score base

El score técnico se calcula como:

```text
score_base =
puntos_gasto
+ puntos_ahorro
+ puntos_deuda
+ puntos_balance
+ puntos_control
```

Su rango es:

```text
0 – 100
```

---

# Bonus de buenos hábitos

Además del score técnico, el sistema conserva un bonus de hasta cinco puntos. El objetivo es introducir un mecanismo de **refuerzo positivo** que reconozca conductas financieras saludables.

| Conducta | Bonus |
|---|---:|
| Cumplir o superar la meta de ahorro | +2 |
| No necesitar nuevo financiamiento | +2 |
| Mantener gasto variable por debajo de 30 % del ingreso | +1 |
| **Máximo** | **+5** |

El resultado final es:

```text
score_financiero =
min(score_base + bonus_buenos_habitos, 100)
```

Para mantener trazabilidad se conservan:

```text
score_base
bonus_buenos_habitos
bonus_aplicado
motivos_bonus
score_financiero
```

---

# Perfil financiero

El score final se transforma en tres perfiles:

| Score | Perfil |
|---|---|
| 75 – 100 | Saludable |
| 50 – 74.99 | En observación |
| < 50 | En riesgo |

El perfil permite mostrar al usuario una interpretación rápida de su situación mensual.

---

# Diagnóstico financiero

Además del perfil general, el análisis identifica el principal problema financiero del periodo. El diagnóstico ayuda a identificar **qué dimensión del score necesita mayor atención**.

Ejemplos:

```text
Gasto elevado
Ahorro insuficiente
Nivel de deuda alto
Dependencia de financiamiento
Gasto variable elevado
Situación financiera estable
```

---

# Recomendaciones

El notebook genera una recomendación base asociada al diagnóstico. El sistema de recomendaciones es explicable y puede ser sustituido o complementado posteriormente por una capa generativa.

Ejemplo:

```text
Diagnóstico:
Ahorro insuficiente

Recomendación:
Incrementar progresivamente el ahorro automático hasta acercarse a la meta declarada.
```

---

# Validaciones

El notebook verifica:

- Número correcto de registros usuario-mes
- Ausencia de duplicados
- Ausencia de valores nulos
- Ingresos positivos
- Consistencia entre gasto total y gasto por categorías
- Consistencia entre gasto recurrente + variable y gasto total
- Déficits cubiertos mediante financiamiento
- Score base dentro de 0–100
- Bonus dentro de 0–5
- Score final dentro de 0–100
- Coincidencia entre score y perfil
- Ausencia de variables latentes como `arquetipo_comportamiento`

---

# Dataset para Machine Learning

El módulo exporta un dataset específico para experimentación con Machine Learning.

Para evitar **data leakage**, se excluyen variables derivadas directamente del scoring:

```text
score_base
score_financiero
bonus_buenos_habitos
bonus_aplicado
motivos_bonus
puntos_gasto
puntos_ahorro
puntos_deuda
puntos_balance
puntos_control
recomendacion_base
```

También se excluye `diagnostico_principal` cuando el objetivo experimental es predecir `perfil_financiero`.

---

# Benchmark de Machine Learning

El notebook incluye un benchmark experimental para comprobar que el dataset puede utilizarse en un pipeline de clasificación. Este benchmark **no sustituye el scoring oficial**.

La etiqueta `perfil_financiero` fue creada mediante reglas. Por lo tanto, entrenar un modelo con indicadores del mismo periodo sirve principalmente para medir qué tan bien puede reproducir esas reglas.

El benchmark se utiliza como:

- Prueba técnica
- Validación de estructura del dataset
- Práctica de pipeline
- Comparación futura

Para un modelo predictivo real sería preferible utilizar un target externo, por ejemplo:

```text
mora futura
incremento de deuda
déficit persistente
incumplimiento de pagos
clasificación experta
```

---

# Archivos generados

```text
monthly_financial_summary_final.csv
monthly_model_dataset_final.csv
monthly_profile_model_dataset_final.csv
financial_profile_benchmark.joblib
```

### `monthly_financial_summary_final.csv`

Resumen mensual completo con indicadores, score, bonus, perfil, diagnóstico y recomendación.

### `monthly_model_dataset_final.csv`

Dataset general preparado para experimentación de Machine Learning.

### `monthly_profile_model_dataset_final.csv`

Versión específica para benchmark del perfil financiero.

---

# Integración esperada

Este módulo está diseñado para alimentar:

```text
POST /analysis
```

Ejemplo de respuesta:

```json
{
  "score_base": 72,
  "bonus_buenos_habitos": 3,
  "bonus_aplicado": 3,
  "score_financiero": 75,
  "perfil_financiero": "Saludable",
  "diagnostico_principal": "Ahorro insuficiente",
  "recomendacion": "Incrementar gradualmente el ahorro automático."
}
```

---

# Tecnologías

- Python
- Pandas
- NumPy
- Matplotlib
- Scikit-Learn
- Joblib
- Jupyter Notebook / Google Colab

---

# Decisión de arquitectura

EconomIA mantiene separados sus dos componentes analíticos:

```text
Clasificador de transacciones
→ Machine Learning
→ descripción → categoría


Análisis financiero
→ reglas explicables
→ indicadores → score/perfil
```

---

# Próximos pasos

- Integrar el motor mediante FastAPI
- Monitorear resultados con datos reales anonimizados
- Evaluar un target predictivo externo para futuras versiones de ML

---

## Proyecto

**EconomIA**

Módulo de análisis financiero mensual, scoring explicable y generación de perfiles.
