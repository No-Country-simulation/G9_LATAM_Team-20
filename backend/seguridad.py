from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def encriptar_password(password: str) -> str:
    return pwd_context.hash(password)

def verificar_password(password_texto_plano: str, password_hash: str) -> bool:
    return pwd_context.verify(password_texto_plano, password_hash)