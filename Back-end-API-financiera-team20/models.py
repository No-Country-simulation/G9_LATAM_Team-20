from sqlalchemy import column, Column, Integer, String, Float
from database import Base

class Transaccion(Base):
    __tablename__ = "transacciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, index=True)
    categoria = Column(String)
    tipo = Column(String) # "ingreso" o "gastos"
    monto = Column(Float)