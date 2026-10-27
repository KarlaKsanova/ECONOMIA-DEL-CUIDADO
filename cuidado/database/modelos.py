"""Esquema v2 separado del demo anterior; create_all no transforma tablas previas."""
import uuid
from datetime import datetime, time
from sqlalchemy import String, Integer, Float, Time, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

def uid(): return str(uuid.uuid4())
class Base(DeclarativeBase): pass

class Centro(Base):
    __tablename__='centros_v2'
    centro_id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    nombre: Mapped[str]=mapped_column(String(200))
    alcaldia: Mapped[str]=mapped_column(String(100))
    verificado: Mapped[bool]=mapped_column(default=False)

class Servicio(Base):
    __tablename__='servicios_v2'
    __table_args__=(CheckConstraint('cupos_disponibles >= 0'),CheckConstraint('fin > inicio'),CheckConstraint('latitud >= -90 AND latitud <= 90'),CheckConstraint('longitud >= -180 AND longitud <= 180'))
    servicio_id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    centro_id: Mapped[str]=mapped_column(ForeignKey('centros_v2.centro_id'))
    tipo: Mapped[str]=mapped_column(String(50))
    inicio: Mapped[time]=mapped_column(Time)
    fin: Mapped[time]=mapped_column(Time)
    dias: Mapped[str]=mapped_column(String(50))
    latitud: Mapped[float]=mapped_column(Float)
    longitud: Mapped[float]=mapped_column(Float)
    cupos_disponibles: Mapped[int]=mapped_column(Integer)

class Solicitud(Base):
    __tablename__='solicitudes_v2'
    solicitud_id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    tipo: Mapped[str]=mapped_column(String(50))
    inicio: Mapped[time]=mapped_column(Time)
    fin: Mapped[time]=mapped_column(Time)
    dias: Mapped[str]=mapped_column(String(50))
    latitud: Mapped[float]=mapped_column(Float)
    longitud: Mapped[float]=mapped_column(Float)

class Vinculacion(Base):
    __tablename__='vinculaciones_v2'
    vinculacion_id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    solicitud_id: Mapped[str]=mapped_column(ForeignKey('solicitudes_v2.solicitud_id'),unique=True)
    servicio_id: Mapped[str]=mapped_column(ForeignKey('servicios_v2.servicio_id'))
    estado: Mapped[str]=mapped_column(String(30),default='confirmada')
    version_modelo: Mapped[str]=mapped_column(String(50))
    creado_en: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
