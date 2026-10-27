from sqlalchemy import create_engine, event
from cuidado.config import database_url

def crear_engine(url=None):
    engine=create_engine(database_url(url),pool_pre_ping=True)
    if engine.dialect.name=='sqlite':
        @event.listens_for(engine,'connect')
        def foreign_keys(connection, _):
            connection.execute('PRAGMA foreign_keys=ON')
    return engine
