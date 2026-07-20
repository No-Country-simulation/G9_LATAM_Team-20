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
