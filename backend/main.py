from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import engine, SessionLocal, Base
import backend.models as models
import backend.schemas as schemas

Base.metadata.create_all(bind=engine)

app = FastAPI()

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
    nueva = models.Transaccion(**transaccion.model_dump())
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



# end pont para calcular perfil (reglas de negocio)
@app.get("/perfil/{usuario_id}")
def calcular_perfil(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado") #Excepcion de usuarios no listados

    transacciones = db.query(models.Transaccion).filter(
        models.Transaccion.usuario_id == usuario_id
    ).all()

    # filtros para ingresos y gastos
    ingresos = sum(t.monto for t in transacciones if t.tipo == "ingreso")
    gastos = sum(t.monto for t in transacciones if t.tipo == "gasto")
    ahorro_real = ingresos - gastos

    ingreso_total = usuario.ingreso_base + usuario.ingreso_variable

    if ingreso_total == 0:
        porcentaje_ahorro_real = 0
    else:
        porcentaje_ahorro_real = (ahorro_real / ingreso_total) * 100

    if usuario.meta_ahorro == 0:
        cumplimiento_meta = 0
    else:
        cumplimiento_meta = porcentaje_ahorro_real / usuario.meta_ahorro

    if cumplimiento_meta >= 1:
        perfil = "saludable"
        recomendacion = "Estás cumpliendo o superando tu meta de ahorro, ¡sigue así!"
    elif cumplimiento_meta >= 0.5:
        perfil = "en observacion"
        recomendacion = "Estás ahorrando, pero por debajo de tu meta. Revisa tus gastos variables."
    else:
        perfil = "en riesgo"
        recomendacion = "Estás muy por debajo de tu meta de ahorro, es momento de ajustar tus gastos."

    return{
         "usuario_id": usuario_id,
        "ingreso_total": ingreso_total,
        "ahorro_real": ahorro_real,
        "porcentaje_ahorro_real": round(porcentaje_ahorro_real, 2),
        "meta_ahorro": usuario.meta_ahorro,
        "cumplimiento_meta": round(cumplimiento_meta, 2),
        "perfil": perfil,
        "recomendacion": recomendacion
    }


# actualizar una transaccion existente
@app.put("/transacciones/{transacciones_id}", response_model=schemas.TransaccionRespuesta)
def actualizar_transacciones(transaccion_id: int, datos: schemas.TransaccionCrear, db: Session = Depends(get_db)):
    transaccion = db.query(models.Transaccion).filter(models.Transaccion.id == transaccion_id).first()

    if not transaccion:
        raise HTTPException(status_code=404, detail="Transaccion no encontrada revise nuevamente")

    transaccion.usuario_id = datos.usuario_id
    transaccion.categoria = datos.categoria
    transaccion.tipo = datos.tipo
    transaccion.monto = datos.monto

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
