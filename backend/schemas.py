from pydantic import BaseModel

class TransaccionCrear(BaseModel):
    usuario_id: int
    categoria: str
    tipo: str
    monto: float

class TransaccionRespuesta(TransaccionCrear):
    id: int

    class Config:
        from_attributes = True

class UsuarioCrear(BaseModel):
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
