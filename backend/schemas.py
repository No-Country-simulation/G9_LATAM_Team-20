from pydantic import BaseModel
from datetime import datetime

class TransaccionCrear(BaseModel):
    usuario_id: int
    categoria: str
    tipo: str
    monto: float
    descripcion: str | None = None 
    fecha: datetime | None = None

class TransaccionRespuesta(TransaccionCrear):
    id: int
    fecha: datetime

    class Config:
        from_attributes = True

class UsuarioCrear(BaseModel):
    nombre: str # se agrega linea para frontend
    edad: int
    sexo: str
    ocupacion: str
    ciudad: str
    ingreso_base: float
    ingreso_variable: float
    meta_ahorro: float
    nivel_deuda_inicial: float

class UsuarioRespuesta(UsuarioCrear):
    id: int

    class Config:
        from_attributes = True
