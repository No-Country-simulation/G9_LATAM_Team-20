from datetime import datetime, timezone
import joblib

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models as models
import schemas as schemas
from seguridad import encriptar_password, verificar_password

modelo_clasificador = joblib.load("modelos/category_classifier_final.joblib") # se actualiza modelo calsificador 

Base.metadata.create_all(bind=engine)

app = FastAPI( title="EconomIA API",
    description="API para el análisis de salud financiera y clasificación de transacciones",
    version="1.2.1")

# permitir que fastapi haga CORS cross-origin resource sharing
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/clasificar-gasto", response_model=schemas.ClasificacionResponse)
def clasificar_gasto(datos: schemas.ClasificacionRequest):
    descripcion = datos.descripcion.strip()
    if not descripcion:
        raise HTTPException(status_code=400, detail="La descripción no puede estar vacía")

    categoria_predicha = modelo_clasificador.predict([descripcion])[0]
    probabilidades = modelo_clasificador.predict_proba([descripcion])[0]
    clases = modelo_clasificador.classes_

    # Ordenar las 3 categorías con mayor probabilidad
    pares = sorted(zip(clases, probabilidades), key=lambda x: x[1], reverse=True)
    top_3 = pares[:3]

    confianza = float(top_3[0][1])

    return {
        "categoria": normalizar_categoria(top_3[0][0]),
        "confianza": round(confianza, 4),
        "requiere_revision": confianza < UMBRAL_REVISION,
        "alternativas": [
            {"categoria": cat, "probabilidad": round(float(prob), 4)}
            for cat, prob in top_3
        ],
        "modelo_version": "category-classifier-v1"
    }



# mensaje de preuba
@app.get("/")
def inicio():
    return{"mensaje": "API de analisis financiero prueba funcionamiento"}

# crear las transacciones de usuario
@app.post("/transacciones", response_model=schemas.TransaccionRespuesta)
def crear_transaccion(transaccion: schemas.TransaccionCrear, db: Session = Depends(get_db)):
    datos = transaccion.model_dump()

    #actualizacion para poner fecha
    if datos["fecha"] is None:
        datos["fecha"] = datetime.now(timezone.utc)
    nueva = models.Transaccion(**datos)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

# obtener las transacciones de la base de datos 
@app.get("/transacciones/{usuario_id}", response_model=list[schemas.TransaccionRespuesta])
def obtener_transacciones(usuario_id: int, db: Session = Depends(get_db)):
    return db.query(models.Transaccion).filter(models.Transaccion.usuario_id == usuario_id).all()

# creacion de usuarios
@app.post("/usuarios", response_model=schemas.UsuarioRespuesta)
def crear_usuario(usuario: schemas.UsuarioCrear, db: Session = Depends(get_db)):
    datos = usuario.model_dump()
    password_texto_plano = datos.pop("password")
    datos["password_hash"] = encriptar_password(password_texto_plano)

    nuevo = models.Usuario(**datos)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# ---------------------------------------------------------
# ============================
# MOTOR DE ANÁLISIS FINANCIERO (reglas de negocio de Data Science)
# ============================

def points_spending(rate):
    if rate <= 0.60:
        return 25
    elif rate <= 1.00:
        return round(25 * (1 - ((rate - 0.60) / 0.40)), 2)
    return 0

def points_saving(compliance):
    compliance = min(compliance, 1)
    return round(compliance * 25, 2)

def points_debt(debt_ratio):
    if debt_ratio <= 0.25:
        return 20
    elif debt_ratio <= 2.00:
        return round(20 * (1 - ((debt_ratio - 0.25) / 1.75)), 2)
    return 0

def points_balance(financing_rate):
    if financing_rate <= 0:
        return 20
    elif financing_rate <= 0.20:
        return round(20 * (1 - (financing_rate / 0.20)), 2)
    return 0

def points_control(variable_expense_rate):
    if variable_expense_rate <= 0.35:
        return 10
    elif variable_expense_rate <= 0.65:
        return round(10 * (1 - ((variable_expense_rate - 0.35) / 0.30)), 2)
    return 0

def assign_profile_ia(score):
    if score >= 75:
        return "Saludable"
    if score >= 50:
        return "En observación"
    return "En riesgo"

def assign_diagnosis(indicadores):
    if indicadores["tasa_financiamiento"] > 0:
        return "Déficit y financiamiento"
    if indicadores["ratio_saldo_deuda_ingreso"] > 0.35 or indicadores["tasa_pago_deuda"] > 0.12:
        return "Endeudamiento"
    if indicadores["tasa_gasto"] > 0.90 or indicadores["tasa_gasto_variable"] > 0.60:
        return "Gasto elevado"
    if indicadores["cumplimiento_meta_ahorro"] < 0.50:
        return "Ahorro insuficiente"
    return "Equilibrado"

RECOMENDACIONES_IA = {
    "Déficit y financiamiento": "Reducir gastos variables y evitar nuevo financiamiento.",
    "Endeudamiento": "Priorizar pagos de deuda y limitar nuevas compras a crédito.",
    "Gasto elevado": "Revisar los gastos variables y la categoría principal del mes.",
    "Ahorro insuficiente": "Programar un ahorro automático para acercarse a la meta declarada.",
    "Equilibrado": "Mantener el control actual y continuar con el hábito de ahorro.",
}


#------------endpoint de funciones y calculo de analisis completo
@app.get("/perfil-ia/{usuario_id}")
def perfil_financiero_ia(usuario_id: int, anio: int, mes: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    transacciones = db.query(models.Transaccion).filter(
        models.Transaccion.usuario_id == usuario_id,
        models.Transaccion.fecha >= datetime(anio, mes, 1),
        models.Transaccion.fecha < datetime(anio + (mes == 12), (mes % 12) + 1, 1)
    ).all()

    if not transacciones:
        raise HTTPException(status_code=404, detail="No hay transacciones para ese usuario en ese mes")

    ingresos_transacciones = sum(t.monto for t in transacciones if t.tipo == "ingreso" and t.categoria != "financiamiento")
    ingresos = ingresos_transacciones if ingresos_transacciones > 0 else (usuario.ingreso_base + usuario.ingreso_variable)

    categorias_no_gasto = CATEGORIAS_ESENCIALES + ["deudas", "inversion"]
    gastos_recurrentes = sum(t.monto for t in transacciones if t.tipo == "gasto" and t.categoria in CATEGORIAS_ESENCIALES)
    gastos_variables = sum(t.monto for t in transacciones if t.tipo == "gasto" and t.categoria not in categorias_no_gasto)
    pagos_deuda = sum(t.monto for t in transacciones if t.tipo == "gasto" and t.categoria == "deudas")
    gastos = gastos_recurrentes + gastos_variables + pagos_deuda

    financiamiento = sum(t.monto for t in transacciones if t.tipo == "ingreso" and t.categoria == "financiamiento")
    inversiones = sum(t.monto for t in transacciones if t.tipo == "gasto" and t.categoria == "inversion")

    ahorro = max(ingresos - gastos, 0)
    saldo_deuda_estimado = (usuario.nivel_deuda_inicial / 100) * ingresos if ingresos > 0 else 0

    tasa_gasto = gastos / ingresos if ingresos > 0 else 0
    tasa_pago_deuda = pagos_deuda / ingresos if ingresos > 0 else 0
    tasa_financiamiento = financiamiento / ingresos if ingresos > 0 else 0
    tasa_gasto_variable = gastos_variables / ingresos if ingresos > 0 else 0
    cumplimiento_meta_ahorro = min((ahorro / ingresos) / (usuario.meta_ahorro / 100), 1) if ingresos > 0 and usuario.meta_ahorro > 0 else 0
    ratio_saldo_deuda_ingreso = saldo_deuda_estimado / ingresos if ingresos > 0 else 0

    indicadores = {
        "tasa_gasto": round(tasa_gasto, 4),
        "tasa_pago_deuda": round(tasa_pago_deuda, 4),
        "tasa_financiamiento": round(tasa_financiamiento, 4),
        "tasa_gasto_variable": round(tasa_gasto_variable, 4),
        "cumplimiento_meta_ahorro": round(cumplimiento_meta_ahorro, 4),
        "ratio_saldo_deuda_ingreso": round(ratio_saldo_deuda_ingreso, 4),
    }

    puntos_gasto = points_spending(tasa_gasto)
    puntos_ahorro = points_saving(cumplimiento_meta_ahorro)
    puntos_deuda = points_debt(ratio_saldo_deuda_ingreso)
    puntos_balance = points_balance(tasa_financiamiento)
    puntos_control = points_control(tasa_gasto_variable)

    score_base = round(puntos_gasto + puntos_ahorro + puntos_deuda + puntos_balance + puntos_control, 2)

    bonus = 0
    motivos_bonus = []
    if cumplimiento_meta_ahorro >= 1:
        bonus += 2
        motivos_bonus.append("Meta de ahorro cumplida")
    if tasa_financiamiento == 0:
        bonus += 2
        motivos_bonus.append("Sin nuevo financiamiento")
    if tasa_gasto_variable < 0.30:
        bonus += 1
        motivos_bonus.append("Buen control del gasto variable")

    score_financiero = min(score_base + bonus, 100)
    bonus_aplicado = round(score_financiero - score_base, 2)

    perfil = assign_profile_ia(score_financiero)
    diagnostico = assign_diagnosis(indicadores)
    recomendacion = RECOMENDACIONES_IA[diagnostico]
    nota_deuda = None
    if usuario.nivel_deuda_inicial == 0 and pagos_deuda > 0:
        nota_deuda = "Registraste tu deuda inicial en 0%, pero tuviste pagos de categoría 'deudas' este mes. El diagnóstico refleja tu actividad real, no solo lo declarado al registrarte."

    return {
        "usuario_id": usuario_id,
        "anio": anio,
        "mes": mes,
        "score_base": score_base,
        "bonus_buenos_habitos": bonus,
        "bonus_aplicado": bonus_aplicado,
        "score_financiero": score_financiero,
        "perfil_financiero": perfil,
        "motivos_bonus": motivos_bonus,
        "diagnostico_principal": diagnostico,
        "recomendacion": recomendacion,
        "indicadores": indicadores,
        "inversiones": round(inversiones, 2),
        "nota_deuda": nota_deuda,
        "analysis_version": "financial-analysis-v1-aproximado"
    }



#------------------------------------------------------------
CATEGORIAS_ESENCIALES = ["alimentacion", "transporte", "salud", "vivienda", "educacion", "servicios"]

# endpoint para calcular perfil (reglas de negocio)
@app.get("/perfil/{usuario_id}")
def calcular_perfil(usuario_id: int, anio: int, mes: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    transacciones = db.query(models.Transaccion).filter(
        models.Transaccion.usuario_id == usuario_id,
        models.Transaccion.fecha >= datetime(anio, mes, 1),
        models.Transaccion.fecha < datetime(anio + (mes == 12), (mes % 12) + 1, 1)
    ).all()

    if not transacciones:
        raise HTTPException(status_code=404, detail="No hay transacciones para ese usuario en ese mes")

    ingresos = sum(t.monto for t in transacciones if t.tipo == "ingreso")
    gastos = sum(t.monto for t in transacciones if t.tipo == "gasto")

    # Categoría de mayor gasto, excluyendo "deudas" (pagar deuda no debe sugerirse como algo a reducir)
    gastos_por_categoria = {}
    for t in transacciones:
        if t.tipo == "gasto" and t.categoria != "deudas":
            gastos_por_categoria[t.categoria] = gastos_por_categoria.get(t.categoria, 0) + t.monto

    categoria_mayor_gasto = max(gastos_por_categoria, key=gastos_por_categoria.get) if gastos_por_categoria else None
    categoria_es_no_esencial = (
        categoria_mayor_gasto is not None and categoria_mayor_gasto not in CATEGORIAS_ESENCIALES
    )

    # Primero resolvemos el ingreso_total (con respaldo del perfil si no hay transacciones de ingreso)
    ingreso_total = ingresos if ingresos > 0 else (usuario.ingreso_base + usuario.ingreso_variable)

    # Y con ese ingreso_total ya resuelto, calculamos el ahorro real
    ahorro_real = ingreso_total - gastos

    if ingreso_total == 0:
        porcentaje_ahorro_real = 0
    else:
        porcentaje_ahorro_real = (ahorro_real / ingreso_total) * 100

    if usuario.meta_ahorro == 0:
        cumplimiento_meta = 0
    else:
        cumplimiento_meta = porcentaje_ahorro_real / usuario.meta_ahorro

    deuda_alta = usuario.nivel_deuda_inicial >= 30

    if cumplimiento_meta >= 1 and not deuda_alta:
        perfil = "saludable"
        recomendacion = "Estás cumpliendo tu meta de ahorro y tu nivel de deuda es manejable. Si quieres ir más lejos, podrías subir tu meta de ahorro gradualmente, por ejemplo 2-3% más el próximo mes."

    elif cumplimiento_meta >= 1 and deuda_alta:
        perfil = "en observación"
        if categoria_es_no_esencial:
            recomendacion = f"Estás ahorrando bien este mes, pero tu deuda es alta y tu mayor gasto fue en '{categoria_mayor_gasto}'. Considera reducir ese gasto y destinar la diferencia a pagar tu deuda más rápido."
        else:
            recomendacion = "Estás ahorrando bien este mes, pero tu nivel de deuda es alto. Considera destinar parte de tu ahorro a pagarla más rápido."

    elif cumplimiento_meta < 1 and deuda_alta:
        perfil = "en riesgo"
        if categoria_es_no_esencial:
            recomendacion = f"Este mes tu ahorro está por debajo de tu meta y tu deuda es alta. Tu mayor gasto fue en '{categoria_mayor_gasto}', una categoría no esencial: reducirlo es la forma más rápida de mejorar tu situación."
        else:
            recomendacion = "Este mes tu ahorro está por debajo de tu meta y tu deuda es alta. Es momento de revisar tus gastos esenciales y priorizar el pago de deuda."

    else:
        perfil = "en observación"
        recomendacion = "Este mes tu ahorro está por debajo de tu meta, aunque tu deuda es manejable. Revisa tus gastos variables para acercarte a tu meta."

    return {
        "usuario_id": usuario_id,
        "anio": anio,
        "mes": mes,
        "ingreso_total": ingreso_total,
        "ahorro_real": ahorro_real,
        "porcentaje_ahorro_real": round(porcentaje_ahorro_real, 2),
        "meta_ahorro": usuario.meta_ahorro,
        "cumplimiento_meta": round(cumplimiento_meta, 2),
        "nivel_deuda": usuario.nivel_deuda_inicial,
        "categoria_mayor_gasto": categoria_mayor_gasto,
        "perfil": perfil,
        "recomendacion": recomendacion
    }

# actualizar una transaccion existente
@app.put("/transacciones/{transaccion_id}", response_model=schemas.TransaccionRespuesta)
def actualizar_transacciones(transaccion_id: int, datos: schemas.TransaccionCrear, db: Session = Depends(get_db)):
    transaccion = db.query(models.Transaccion).filter(models.Transaccion.id == transaccion_id).first()

    if not transaccion:
        raise HTTPException(status_code=404, detail="Transaccion no encontrada revise nuevamente")

    transaccion.usuario_id = datos.usuario_id
    transaccion.categoria = datos.categoria
    transaccion.tipo = datos.tipo
    transaccion.monto = datos.monto
    transaccion.descripcion = datos.descripcion
    if datos.fecha is not None:
        transaccion.fecha = datos.fecha

    db.commit()
    db.refresh(transaccion)
    return transaccion


# borrar transacciones no deseadas o errores de registro de usuraio 
@app.delete("/transacciones/{transaccion_id}")
def borrar_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    transaccion = db.query(models.Transaccion).filter(models.Transaccion.id == transaccion_id).first()

    if not transaccion:
        raise HTTPException(status_code=404, detail="Transaccion no encontrada revise nuevamente")

    db.delete(transaccion)
    db.commit()
    return {"mensaje": f"Transaccion {transaccion_id} eliminada correctamente"}  # mismo patron solo que ahora lo borra en vez de modificarlo

# sobre escribir datos de usuarios 
@app.put("/usuarios/{usuario_id}", response_model= schemas.UsuarioRespuesta)
def actualizar_usuarios(usuario_id: int, datos: schemas.UsuarioCrear, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

    if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado verifique sus datos")
    
    usuario.nombre = datos.nombre # se agraga linea para el front
    usuario.edad = datos.edad
    usuario.sexo = datos.sexo
    usuario.ocupacion = datos.ocupacion
    usuario.ciudad = datos.ciudad
    usuario.ingreso_base = datos.ingreso_base
    usuario.ingreso_variable = datos.ingreso_variable
    usuario.meta_ahorro = datos.meta_ahorro
    usuario.nivel_deuda_inicial = datos.nivel_deuda_inicial

    db.commit()
    db.refresh(usuario)
    return usuario
    

# borrar usuarios
@app.delete("/usuarios/{usuario_id}")
def borrar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

    if not usuario:
     raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(usuario)
    db.commit()
    return {"mensaje": f"Usuario {usuario_id} eliminado correctamente"}  


@app.get("/resumen-mensual/{usuario_id}")
def resumen_mensual(usuario_id: int, anio: int, mes: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    transacciones = db.query(models.Transaccion).filter(
        models.Transaccion.usuario_id == usuario_id,
        models.Transaccion.fecha >= datetime(anio, mes, 1),
        models.Transaccion.fecha < datetime(anio + (mes == 12), (mes % 12) + 1, 1)
    ).all()

    if not transacciones:
        raise HTTPException(status_code=404, detail="No hay transacciones para ese usuario en ese mes")

    ingresos_transacciones = sum(t.monto for t in transacciones if t.tipo == "ingreso")
    ingresos_totales = ingresos_transacciones if ingresos_transacciones > 0 else (usuario.ingreso_base + usuario.ingreso_variable)

    gastos_por_categoria = {}
    for t in transacciones:
        if t.tipo == "gasto":
            gastos_por_categoria[t.categoria] = gastos_por_categoria.get(t.categoria, 0) + t.monto

    gastos_totales = sum(gastos_por_categoria.values())
    categoria_mayor_gasto = max(gastos_por_categoria, key=gastos_por_categoria.get) if gastos_por_categoria else None

    return {
        "usuario_id": usuario_id,
        "anio": anio,
        "mes": mes,
        "ingresos_totales": ingresos_totales,
        "gastos_totales": gastos_totales,
        "gastos_por_categoria": gastos_por_categoria,
        "categoria_mayor_gasto": categoria_mayor_gasto
    }


# endpoin para editar perfil en el frontend 
@app.get("/usuarios/{usuario_id}", response_model=schemas.UsuarioRespuesta)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario



# Obtener todos los usuarios registrados en la base de datos
@app.get("/usuarios", response_model=list[schemas.UsuarioRespuesta])
def obtener_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()



# Cargar el modelo UNA SOLA VEZ al iniciar el servidor (no en cada petición, sería muy lento)


UMBRAL_REVISION = 0.60

MAPA_CATEGORIAS_MODELO = {
    "Alimentación": "alimentacion",
    "Transporte": "transporte",
    "Salud": "salud",
    "Vivienda": "vivienda",
    "Educación": "educacion",
    "Entretenimiento": "entretenimiento",
    "Servicios": "servicios",
    "Compras": "compras",
    "Otros": "otros",
    "Deudas": "deudas",
    "Finanzas": "finanzas",
}

def normalizar_categoria(categoria_modelo: str) -> str:
    return MAPA_CATEGORIAS_MODELO.get(categoria_modelo, "otros")


# end point de login 
@app.post("/login", response_model=schemas.UsuarioRespuesta)
def login(datos: schemas.LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == datos.id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not verificar_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    return usuario