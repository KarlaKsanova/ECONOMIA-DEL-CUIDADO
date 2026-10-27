from cuidado.services.evidencia import cargar_evidencia

def test_prepared_data_and_sources():
    data=cargar_evidencia()
    assert len(data)==16
    assert data.alcaldia.is_unique
    assert data.geometry.notna().all()
    assert data.attrs['indicadores_pobreza_tiempo_cdmx']['enut_horas_cuidado_mujeres']==12.16
    assert 'abandono_laboral_cuidados' not in data
    assert data.estimacion_cuidadores_sin_trabajo_mercado.sum()>0
