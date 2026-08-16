from sqlalchemy import text
from database import engine

with engine.connect() as conexion:
    conexion.execute(text("TRUNCATE TABLE transacciones, usuarios RESTART IDENTITY CASCADE;"))
    conexion.commit()

print("Base de datos limpiada correctamente.")