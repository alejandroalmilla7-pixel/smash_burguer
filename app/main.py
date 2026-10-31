import os
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Configuración de Base de Datos (Toma la URL de las variables de entorno)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://usuario:password@db:5432/midatabase")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de Base de Datos
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)

# Crear tablas automáticamente al arrancar
Base.metadata.create_all(bind=engine)

# Aplicación FastAPI
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Esquema Pydantic para recibir datos
class NombreSchema(BaseModel):
    nombre: str

# Dependencia para obtener sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ruta principal: Sirve el Front-End (HTML)
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request,"index.html", {})

# Ruta API POST: Guarda el nombre en la BD
@app.post("/nombres")
def guardar_nombre(data: NombreSchema, db: Session = Depends(get_db)):
    nuevo_usuario = Usuario(nombre=data.nombre)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"message": "Guardado exitosamente", "id": nuevo_usuario.id, "nombre": nuevo_usuario.nombre}

# Ruta API GET: Consulta todos los nombres
@app.get("/nombres")
def obtener_nombres(db: Session = Depends(get_db)):
    return db.query(Usuario).all()  