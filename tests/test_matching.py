from dataclasses import replace
from datetime import time
import pytest
from cuidado.domain.centros import recomendar
from cuidado.services.simulacion import escenario, ejecutar_demo

def test_capacity_and_explanations():
    result=ejecutar_demo()
    assert sum(r['estado']=='recomendada' for r in result)==5
    by_id={r['solicitud_id']:r for r in result}
    assert by_id['demo-horario']['motivo']=='sin_compatibilidad_horaria'
    assert by_id['demo-tipo']['motivo']=='sin_servicio_compatible'
    assert by_id['demo-lejana']['motivo']=='fuera_de_radio'
    assert sum(r['motivo']=='sin_cupo' for r in result)==3

def test_unverified_and_no_offers():
    s,o=escenario()
    assert recomendar(s,[])[0]['estado']=='pendiente'
    assert recomendar(s,[replace(x,verificado=False) for x in o])[0]['estado']=='pendiente'
    assert recomendar([],o)==[]

@pytest.mark.parametrize('changes',[{'dias':frozenset({'bad'})},{'latitud':float('nan')},{'fin':time(7)}])
def test_invalid_input(changes):
    s,o=escenario()
    with pytest.raises(ValueError): recomendar([replace(s[0],**changes)],o)

def test_duplicate_ids():
    s,o=escenario()
    with pytest.raises(ValueError): recomendar([s[0],s[0]],o)
