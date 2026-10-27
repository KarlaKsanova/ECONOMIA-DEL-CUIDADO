from datetime import time
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import pytest
from cuidado.database.conexion import crear_engine
from cuidado.database.modelos import Base,Centro,Servicio,Solicitud,Vinculacion
from cuidado.services.vinculacion import confirmar
from cuidado.config import database_url

def test_urls():
    assert database_url('postgres://x:y@host/db').startswith('postgresql+psycopg2://')
    assert database_url('sqlite://')=='sqlite://'

def test_atomic_capacity_and_rollback(tmp_path):
    engine=crear_engine(f'sqlite:///{tmp_path / "test.db"}')
    Base.metadata.create_all(engine)
    with Session(engine) as s, s.begin():
        s.add(Centro(centro_id='c',nombre='Sintético',alcaldia='Iztapalapa',verificado=True));s.flush()
        s.add(Servicio(servicio_id='o',centro_id='c',tipo='infantil',inicio=time(8),fin=time(14),dias='lun',latitud=19.35,longitud=-99.06,cupos_disponibles=2))
        for i in ['s1','s2','s3']:
            s.add(Solicitud(solicitud_id=i,tipo='infantil',inicio=time(9),fin=time(12),dias='lun',latitud=19.35,longitud=-99.06))
    confirmar(engine,'s1','o')
    with pytest.raises(IntegrityError): confirmar(engine,'s1','o')
    with Session(engine) as s: assert s.get(Servicio,'o').cupos_disponibles==1
    confirmar(engine,'s2','o')
    with pytest.raises(ValueError,match='sin_cupo'): confirmar(engine,'s3','o')
    with Session(engine) as s:
        assert s.get(Servicio,'o').cupos_disponibles==0
        assert len(s.scalars(select(Vinculacion)).all())==2
    engine.dispose()

def test_concurrent_last_place(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    engine=crear_engine(f'sqlite:///{tmp_path / "concurrent.db"}')
    Base.metadata.create_all(engine)
    with Session(engine) as s, s.begin():
        s.add(Centro(centro_id='c',nombre='Sintético',alcaldia='Iztapalapa',verificado=True));s.flush()
        s.add(Servicio(servicio_id='o',centro_id='c',tipo='infantil',inicio=time(8),fin=time(14),dias='lun',latitud=19.35,longitud=-99.06,cupos_disponibles=1))
        for i in ['a','b']:
            s.add(Solicitud(solicitud_id=i,tipo='infantil',inicio=time(9),fin=time(12),dias='lun',latitud=19.35,longitud=-99.06))
    def attempt(identifier):
        try: return confirmar(engine,identifier,'o')
        except ValueError: return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        result=list(pool.map(attempt,['a','b']))
    assert sum(x is not None for x in result)==1
    with Session(engine) as s: assert s.get(Servicio,'o').cupos_disponibles==0
    engine.dispose()
