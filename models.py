from sqlalchemy import column, Column, Integer, String, Float
from database import Base

class Transaccion(Base):
    __tablename__ = "transacciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, index=True)
    categoria = Column(String)
    tipo = Column(String) # "ingreso" o "gastos"
    monto = Column(Float)

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    edad = Column(Integer)
    sexo = Column(String)
    ocupacion = Column(String)
    ciudad = Column(String)
    ingreso_base = Column(Float)
    ingreso_variable = Column(Float)
    meta_ahorro = Column(Float)
    nivel_deuda_inicial = Column(Float)