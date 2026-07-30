from sqlalchemy import  Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from database import Base

class Transaccion(Base):
    __tablename__ = "transacciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, index=True)
    categoria = Column(String)
    tipo = Column(String) # "ingreso" o "gastos"
    monto = Column(Float)
    descripcion = Column(String, nullable=True)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String) # se agrega esta linea para mejorar la interaccion con el frontend
    edad = Column(Integer)
    sexo = Column(String)
    ocupacion = Column(String)
    ciudad = Column(String)
    ingreso_base = Column(Float)
    ingreso_variable = Column(Float)
    meta_ahorro = Column(Float)
    nivel_deuda_inicial = Column(Float)