"""Matching explicable por servicio y franja. No predice impacto laboral."""
from dataclasses import dataclass
from datetime import time
from math import radians, sin, cos, asin, sqrt, isfinite

DIAS = frozenset({'lun','mar','mie','jue','vie','sab','dom'})
VERSION = 'centros-v1'

@dataclass(frozen=True)
class Necesidad:
    solicitud_id: str
    tipo: str
    latitud: float
    longitud: float
    inicio: time
    fin: time
    dias: frozenset[str]

@dataclass(frozen=True)
class Oferta:
    servicio_id: str
    centro_id: str
    tipo: str
    latitud: float
    longitud: float
    inicio: time
    fin: time
    dias: frozenset[str]
    cupos: int
    verificado: bool = True


def validar(item):
    if not isfinite(item.latitud) or not isfinite(item.longitud) or not -90 <= item.latitud <= 90 or not -180 <= item.longitud <= 180:
        raise ValueError('Coordenadas inválidas')
    if item.inicio >= item.fin or not item.dias or not item.dias <= DIAS:
        raise ValueError('Horario o días inválidos')
    if not item.tipo.strip():
        raise ValueError('Tipo de cuidado requerido')
    if isinstance(item, Oferta) and (type(item.cupos) is not int or item.cupos < 0):
        raise ValueError('Los cupos deben ser enteros no negativos')


def distancia(a,b):
    lat1,lon1,lat2,lon2=map(radians,[a.latitud,a.longitud,b.latitud,b.longitud])
    h=sin((lat2-lat1)/2)**2+cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
    return 6371.0088*2*asin(sqrt(min(1,max(0,h))))


def recomendar(solicitudes, ofertas, radio_km=10.0):
    """Asignación greedy por orden de entrada. Cada oferta es una franja/cupo independiente.

    El cupo se consume una vez por solicitud para toda su ventana semanal.
    No reutiliza plazas en subhorarios ni optimiza globalmente la cobertura.
    Los cupos de ofertas diferentes no pueden representar la misma plaza física.
    """
    if not isfinite(radio_km) or radio_km <= 0:
        raise ValueError('Radio inválido')
    for items, key in [(solicitudes,'solicitud_id'),(ofertas,'servicio_id')]:
        ids=[getattr(i,key) for i in items]
        if any(not i for i in ids) or len(ids)!=len(set(ids)):
            raise ValueError('Identificadores vacíos o duplicados')
        for item in items: validar(item)
    disponibles={o.servicio_id:o.cupos for o in ofertas}
    salida=[]
    for s in solicitudes:
        candidatos=[o for o in ofertas if o.verificado and o.tipo==s.tipo]
        motivo='sin_servicio_compatible'
        if candidatos:
            candidatos=[o for o in candidatos if o.inicio<=s.inicio and o.fin>=s.fin and s.dias<=o.dias]
            motivo='sin_compatibilidad_horaria'
            if candidatos:
                candidatos=[(distancia(s,o),o) for o in candidatos if distancia(s,o)<=radio_km]
                motivo='fuera_de_radio'
                if candidatos:
                    candidatos=[(d,o) for d,o in candidatos if disponibles[o.servicio_id]>0]
                    motivo='sin_cupo'
                    if candidatos:
                        d,o=min(candidatos,key=lambda pair:(pair[0],pair[1].servicio_id))
                        disponibles[o.servicio_id]-=1
                        salida.append(dict(solicitud_id=s.solicitud_id,servicio_id=o.servicio_id,centro_id=o.centro_id,estado='recomendada',motivo='compatible',distancia_km=round(d,3),version=VERSION))
                        continue
        salida.append(dict(solicitud_id=s.solicitud_id,servicio_id=None,centro_id=None,estado='pendiente',motivo=motivo,distancia_km=None,version=VERSION))
    return salida
