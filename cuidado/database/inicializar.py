"""Creación explícita y aditiva: python -m cuidado.database.inicializar."""
from cuidado.database.conexion import crear_engine
from cuidado.database.modelos import Base

def inicializar():
    engine=crear_engine()
    try: Base.metadata.create_all(engine)
    finally: engine.dispose()

if __name__=='__main__': inicializar()
