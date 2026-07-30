from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models as models
import schemas as schemas

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
    nuevo = models.Usuario(**usuario.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo



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
    transacciones = db.query(models.Transaccion).filter(
        models.Transaccion.usuario_id == usuario_id,
        models.Transaccion.fecha >= datetime(anio, mes, 1),
        models.Transaccion.fecha < datetime(anio + (mes == 12), (mes % 12) + 1, 1)
    ).all()

    if not transacciones:
        raise HTTPException(status_code=404, detail="No hay transacciones para ese usuario en ese mes")

    ingresos = sum(t.monto for t in transacciones if t.tipo == "ingreso")
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
        "ingresos_totales": ingresos,
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