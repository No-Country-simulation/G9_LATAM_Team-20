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
    password: str # se agrega para login de usuarios
    edad: int
    sexo: str
    ocupacion: str
    ciudad: str
    ingreso_base: float
    ingreso_variable: float
    meta_ahorro: float
    nivel_deuda_inicial: float

class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    edad: int
    sexo: str
    ocupacion: str
    ciudad: str
    ingreso_base: float
    ingreso_variable: float
    meta_ahorro: float
    nivel_deuda_inicial: float

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    id: int
    password: str


class ClasificacionRequest(BaseModel):
    descripcion: str

class AlternativaCategoria(BaseModel):
    categoria: str
    probabilidad: float

class ClasificacionResponse(BaseModel):
    categoria: str
    confianza: float
    requiere_revision: bool
    alternativas: list[AlternativaCategoria]
    modelo_version: str


# correccion de formulario bug no edita datos del usuario por formato no compatible 

class UsuarioActualizar(BaseModel):
    nombre: str
    edad: int
    sexo: str
    ocupacion: str
    ciudad: str
    ingreso_base: float
    ingreso_variable: float
    meta_ahorro: float
    nivel_deuda_inicial: float