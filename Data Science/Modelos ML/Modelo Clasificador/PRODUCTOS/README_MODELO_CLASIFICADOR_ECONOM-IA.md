# Econom-AI — Clasificador Automático de Categorías

<p align="center">
  <strong>Módulo de Machine Learning para Econom-AI</strong><br>
  Clasificación de transacciones financieras a partir de texto
</p>

---

## Descripción

Este módulo clasifica automáticamente una transacción financiera utilizando su descripción textual.

```text
Descripción de la transacción
            ↓
TF-IDF de palabras y caracteres
            ↓
Regresión Logística
            ↓
Categoría + confianza + alternativas
```

Ejemplo:

```text
"pago mensual de internet"
                ↓
"Servicios"
```

El clasificador forma parte del flujo de Econom-AI y está diseñado para integrarse posteriormente mediante el endpoint:

```text
POST /predict/category
```

---

## Objetivo

Reducir la clasificación manual de movimientos y entregar una respuesta que pueda utilizarse desde el backend y el frontend.

El modelo devuelve:

- Categoría principal
- Nivel de confianza
- Tres alternativas
- Indicador de revisión manual
- Versión del modelo


---

## Alcance

### Entrada

```json
{
  "descripcion": "pago mensual de internet"
}
```

### Salida esperada

```json
{
  "descripcion": "pago mensual de internet",
  "categoria_predicha": "Servicios",
  "confianza": 0.873,
  "requiere_revision": false,
  "alternativas": [
    {
      "categoria": "Servicios",
      "probabilidad": 0.873
    },
    {
      "categoria": "Deudas",
      "probabilidad": 0.0401
    },
    {
      "categoria": "Otros",
      "probabilidad": 0.0134
    }
  ],
  "modelo_version": "category-classifier-v1"
}
```

---

## Categorías soportadas

El MVP trabaja con once categorías:

1. Alimentación
2. Compras
3. Deudas
4. Educación
5. Entretenimiento
6. Finanzas
7. Otros
8. Salud
9. Servicios
10. Transporte
11. Vivienda

`Ingreso` no se incluye en este clasificador porque el alcance inicial está orientado a gastos y movimientos financieros de salida.

---

## Dataset

El dataset de modelado contiene las siguientes columnas principales:

| Columna | Uso |
|---|---|
| `descripcion_modelo` | Texto utilizado como entrada |
| `categoria` | Variable objetivo |
| `split` | Train, validation o test |
| `descripcion_original` | Trazabilidad |
| `subcategoria` | Auditoría |
| `grupo_descripcion` | Control de fuga de información |
| `texto_normalizado` | Detección de duplicados y colisiones |
| `es_aumentada` | Identifica variaciones sintéticas |

### Separación de datos

La primera ejecución documentada contiene:

| Conjunto | Registros |
|---|---:|
| Train | 637 |
| Validation | 55 |
| Test | 56 |
| Total | 748 |

La separación se realiza por `grupo_descripcion`, no por filas aleatorias. De esta manera, variaciones de una misma frase permanecen en el mismo conjunto.

Ejemplo de fuga que se evita:

```text
Train: "pago de internet"
Test:  "cargo pago de internet"
```

Sin agrupamiento, el modelo podría memorizar la frase en lugar de aprender a generalizar.

---

## Preparación del texto

El pipeline combina dos representaciones TF-IDF

### TF-IDF de palabras

Configuración principal:

```python
TfidfVectorizer(
    lowercase=True,
    strip_accents="unicode",
    ngram_range=(1, 2),
    min_df=1,
    sublinear_tf=True,
)
```

Aprende términos y combinaciones como:

```text
internet
pago internet
tarjeta crédito
transferencia ahorro
```

### TF-IDF de caracteres

Configuración principal:

```python
TfidfVectorizer(
    analyzer="char_wb",
    lowercase=True,
    strip_accents="unicode",
    ngram_range=(3, 5),
    min_df=1,
    sublinear_tf=True,
)
```

Ayuda con:

- Abreviaturas
- Errores ortográficos
- Diferencias de acentos
- Palabras poco frecuentes
- Descripciones bancarias cortas

---

## Modelos evaluados

| Modelo | Motivo de inclusión |
|---|---|
| Regresión Logística | Buen baseline, rápida y con `predict_proba` |
| Complement Naive Bayes | Modelo clásico para clasificación de texto |
| Linear SVM | Suele funcionar bien con vectores TF-IDF de alta dimensión |

La métrica principal de selección es `f1_macro`, porque asigna el mismo peso a todas las categorías y reduce el efecto de las clases con más ejemplos.

### Resultados de validación de la versión inicial

| Modelo | Accuracy | F1 macro |
|---|---:|---:|
| Complement Naive Bayes | 0.7273 | 0.6972 |
| Regresión Logística | 0.7455 | 0.6936 |
| Linear SVM | 0.7455 | 0.6900 |

Aunque Complement Naive Bayes obtuvo el mejor F1 por una diferencia mínima, se seleccionó Regresión Logística para el producto porque:

- La diferencia fue de solo `0.0036`
- Obtuvo mejor accuracy
- Ofrece probabilidades nativas
- Facilita confianza, Top 3 y revisión manual
- Mantiene un pipeline sencillo para FastAPI

La regla aplicada fue preferir Regresión Logística cuando su F1 se encuentra a menos de `0.03` del mejor modelo.

---

## Evaluación inicial

Resultados sobre el conjunto de test:

| Métrica | Resultado |
|---|---:|
| Accuracy | 0.7679 |
| Precision macro | 0.7013 |
| Recall macro | 0.7576 |
| F1 macro | 0.7148 |
| Top 3 accuracy | 0.8214 |
| Confianza promedio | 0.5884 |

### Categorías con mayor dificultad

El análisis por clase detectó:

| Categoría | F1 inicial |
|---|---:|
| Educación | 0.0000 |
| Servicios | 0.4444 |
| Transporte | 0.2222 |

Los errores mostraron descripciones como:

```text
"Papelería"              → Otros
"libros de estudio"      → Servicios
"Combustible"            → Alimentación
"pasaje de camión"       → Servicios
"servicio de televisión" → Transporte
```

Este resultado indicó que el principal cuello de botella era la poca cobertura y entendimiento de palabras en algunas categorías.

---

## Mejoras del dataset

En lugar de cambiar inmediatamente de algoritmo, se aplicó una segunda iteración basada en el análisis de errores

### Soluciones implementadas

- Inclusión de más descripciones para Educación, Servicios y Transporte
- Refuerzo de categorías cercanas para disminuir confusiones
- Normalización para detectar duplicados
- Identificador estable por categoría y descripción
- Nuevos splits por grupo
- Aumento de texto únicamente en entrenamiento
- Validación y test con textos originales
- Eliminación de colisiones entre conjuntos
- Reentrenamiento con los mismos algoritmos y parámetros

Ejemplos añadidos:

```text
Educación:
pago de colegiatura
inscripción universitaria
curso en Udemy
libros escolares

Servicios:
recibo CFE
mensualidad de internet
pago del celular
servicio de agua potable

Transporte:
Uber al trabajo
gasolina Pemex
boleto de autobús
taller mecánico
```

Mantener los mismos modelos permite atribuir la diferencia principalmente a la mejora de los datos.

### Resultado de la iteración mejorada

En la ejecución integrada de la revisión, Regresión Logística obtuvo:

| Métrica | Resultado |
|---|---:|
| Accuracy | 0.7778 |
| Precision macro | 0.7643 |
| Recall macro | 0.7470 |
| F1 macro | 0.7430 |
| Top 3 accuracy | 0.8889 |

Las mejoras más claras se observaron en Servicios y Transporte. Educación mejoró, aunque sigue siendo una categoría que requiere más ejemplos y validación con datos reales.

---

## Umbral de revisión

El notebook analiza la relación entre cobertura y precisión. En la ejecución inicial, con un umbral de `0.60`:

| Indicador | Resultado |
|---|---:|
| Cobertura automática | 0.5179 |
| Registros aceptados | 29 de 56 |
| Precisión entre aceptados | 0.9310 |

La regla del MVP es:

```text
confianza >= umbral
        ↓
aceptar automáticamente

confianza < umbral
        ↓
solicitar revisión
```

---

## Función de predicción

La función principal valida la entrada, calcula probabilidades y construye la respuesta del servicio

```python
predict_category("pago mensual de internet")
```

Responsabilidades:

1. Verificar que la entrada sea texto
2. Eliminar espacios externos
3. Rechazar descripciones vacías
4. Predecir la categoría
5. Calcular probabilidades
6. Ordenar las alternativas
7. Comparar la confianza con el umbral

---

## Productos

La ejecución final produce:

```text
category_classifier_v1.joblib
category_classifier_test_predictions_v1.csv
category_text_dataset_v1.csv
```

| Archivo | Propósito |
|---|---|
| `.joblib` | Pipeline completo para producción |
| `test_predictions.csv` | Auditoría de aciertos y errores |
| `dataset_v1.csv` | Dataset final del clasificador |

El archivo `.joblib` incluye TF-IDF y clasificador, por lo que FastAPI no necesitará cargar un vectorizador por separado.

---

## Uso local

### Requisitos

```bash
pip install pandas numpy matplotlib scikit-learn joblib jupyter
```

### Cargar el modelo

```python
import joblib

model = joblib.load("category_classifier_v1.joblib")
category = model.predict(["pago de internet"])[0]
probabilities = model.predict_proba(["pago de internet"])[0]
```

---

## Integración propuesta

```text
Frontend
   ↓
Spring Boot
   ↓
POST /predict/category
   ↓
FastAPI
   ↓
category_classifier_v1.joblib
   ↓
categoría + confianza + alternativas
```

Endpoints mínimos del microservicio:

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/health` | Comprueba que el servicio y el modelo estén disponibles |
| POST | `/predict/category` | Clasifica una descripción |

---

## Limitaciones

- El dataset es principalmente sintético
- Algunas categorías tienen pocos ejemplos de test
- Las probabilidades todavía no están calibradas al 100%
- La categoría Educación necesita mayor amplitud de ejmplos
- El modelo utiliza solo la descripción
- El desempeño puede cambiar con descripciones bancarias reales
- La corrección de un usuario todavía no se utiliza para reentrenamiento

---

## Tecnologías

- Python
- Pandas
- NumPy
- Scikit-Learn
- Matplotlib
- Joblib
- Jupyter Notebook / Google Colab
- FastAPI

---

## Nota de uso

Este modelo fue desarrollado con fines educativos para el Hackathon Oracle Next Education y No Country. Los datos utilizados son sintéticos y no deben interpretarse como información financiera real.
