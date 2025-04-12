from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base  # Importar la base de datos

# Modelo para 'Personaje'
class Personaje(Base):
    __tablename__ = "personajes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    
    # Relación con las misiones (un personaje puede tener varias misiones)
    misiones = relationship("Mision", back_populates="personaje", order_by="Mision.id")

# Modelo para 'Mision'
class Mision(Base):
    __tablename__ = "misiones"
    
    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String)
    xp = Column(Integer, default=0)
    completada = Column(Boolean, default=False)  # Nuevo campo: ¿está completada la misión?
    
    # Clave foránea para el personaje que tiene la misión
    personaje_id = Column(Integer, ForeignKey("personajes.id"))
    
    # Relación con el personaje (una misión está asociada a un personaje)
    personaje = relationship("Personaje", back_populates="misiones")
