from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Personaje, Mision
from database import SessionLocal, engine, Base

# Crear la base de datos y las tablas al iniciar
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ruta para crear un personaje
@app.post("/personajes/", response_model=dict)
def crear_personaje(nombre: str, db: Session = Depends(get_db)):
    # Verificar si ya existe un personaje con ese nombre
    db_personaje = db.query(Personaje).filter(Personaje.nombre == nombre).first()
    if db_personaje:
        raise HTTPException(status_code=400, detail="El personaje ya existe")
    
    # Crear un nuevo personaje
    nuevo_personaje = Personaje(nombre=nombre)
    db.add(nuevo_personaje)
    db.commit()
    db.refresh(nuevo_personaje)
    return {"id": nuevo_personaje.id, "nombre": nuevo_personaje.nombre}

# Ruta para crear una misión
@app.post("/misiones/", response_model=dict)
def crear_mision(descripcion: str, xp: int, personaje_id: int, db: Session = Depends(get_db)):
    # Verificar si el personaje existe
    db_personaje = db.query(Personaje).filter(Personaje.id == personaje_id).first()
    if not db_personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    
    # Crear una nueva misión
    nueva_mision = Mision(descripcion=descripcion, xp=xp, personaje_id=personaje_id)
    db.add(nueva_mision)
    db.commit()  # Confirmar la transacción
    db.refresh(nueva_mision)
    
    return {"id": nueva_mision.id, "descripcion": nueva_mision.descripcion, "xp": nueva_mision.xp}

# Ruta para completar una misión
@app.put("/misiones/{mision_id}/completar", response_model=dict)
def completar_mision(mision_id: int, db: Session = Depends(get_db)):
    # Buscar la misión en la base de datos
    db_mision = db.query(Mision).filter(Mision.id == mision_id).first()
    
    if not db_mision:
        raise HTTPException(status_code=404, detail="Misión no encontrada")
    
    # Marcar la misión como completada
    db_mision.completada = True
    db.commit()  # Confirmar la transacción
    db.refresh(db_mision)  # Obtener los datos actualizados de la misión
    
    return {"id": db_mision.id, "descripcion": db_mision.descripcion, "xp": db_mision.xp, "completada": db_mision.completada}

# Ruta para obtener los personajes y sus misiones en orden FIFO
@app.get("/personajes/{personaje_id}/misiones", response_model=dict)
def obtener_misiones(personaje_id: int, db: Session = Depends(get_db)):
    # Buscar el personaje
    db_personaje = db.query(Personaje).filter(Personaje.id == personaje_id).first()
    if not db_personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    
    # Obtener las misiones en orden FIFO desde la base de datos
    misiones = db.query(Mision).filter(Mision.personaje_id == personaje_id).order_by(Mision.id).all()
    
    return {
        "personaje": db_personaje.nombre,
        "misiones": [{"id": m.id, "descripcion": m.descripcion, "xp": m.xp, "completada": m.completada} for m in misiones]
    }

# Ruta para obtener todos los personajes
@app.get("/personajes/", response_model=dict)
def obtener_personajes(db: Session = Depends(get_db)):
    personajes = db.query(Personaje).all()
    return {"personajes": [{"id": p.id, "nombre": p.nombre} for p in personajes]}
