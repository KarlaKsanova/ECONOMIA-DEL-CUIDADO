"""Servicio interno, no expuesto a la app pública. Requiere una capa autorizada."""
from sqlalchemy import update
from sqlalchemy.orm import Session
from cuidado.database.modelos import Centro, Servicio, Solicitud, Vinculacion
from cuidado.domain.centros import Necesidad, Oferta, recomendar, VERSION

def confirmar(engine, solicitud_id, servicio_id, radio_km=10):
    with Session(engine) as session, session.begin():
        s=session.get(Solicitud,solicitud_id)
        o=session.get(Servicio,servicio_id)
        if s is None or o is None: raise ValueError('Solicitud o servicio inexistente')
        c=session.get(Centro,o.centro_id)
        necesidad=Necesidad(s.solicitud_id,s.tipo,s.latitud,s.longitud,s.inicio,s.fin,frozenset(s.dias.split(',')))
        oferta=Oferta(o.servicio_id,o.centro_id,o.tipo,o.latitud,o.longitud,o.inicio,o.fin,frozenset(o.dias.split(',')),o.cupos_disponibles,c.verificado)
        r=recomendar([necesidad],[oferta],radio_km)[0]
        if r['estado']!='recomendada': raise ValueError(r['motivo'])
        changed=session.execute(update(Servicio).where(Servicio.servicio_id==servicio_id,Servicio.cupos_disponibles>0).values(cupos_disponibles=Servicio.cupos_disponibles-1))
        if changed.rowcount!=1: raise ValueError('sin_cupo')
        v=Vinculacion(solicitud_id=solicitud_id,servicio_id=servicio_id,version_modelo=VERSION)
        session.add(v)
        session.flush() # unique solicitud_id: doble confirmación revierte también el cupo
        return v.vinculacion_id
