"""Composición de pantallas; sin ETL ni escrituras a la base operativa."""
import pandas as pd
import streamlit as st
from cuidado.services.evidencia import cargar_evidencia
from cuidado.services.simulacion import ejecutar_demo
from cuidado.services.integraciones import INTEGRACIONES
from cuidado.ui.estilos import aplicar_estilos
from cuidado.ui.territorial import mostrar_visor_territorial, mostrar_comparativo_cuidado, _metricas_principales

@st.cache_data(show_spinner='Cargando datos preparados...')
def evidencia():
    return cargar_evidencia()

def main():
    st.set_page_config(page_title='Observatorio del Cuidado CDMX',layout='wide')
    aplicar_estilos()
    st.title('Observatorio de la Economía del Cuidado CDMX')
    st.caption('Segundo avance · observatorio territorial y demostración de vinculación comunitaria')
    pagina=st.sidebar.radio('Sección',['Observatorio','Comparativos','Vinculación demostrativa','Integraciones pendientes','Fuentes y límites'])
    if pagina in ['Observatorio','Comparativos']:
        try:
            data=evidencia()
        except (FileNotFoundError,ValueError) as error:
            st.error(str(error)); return
        st.info('Los indicadores combinan años y poblaciones de referencia distintos. La estimación territorial de cuidado sin trabajo de mercado no mide abandono laboral ni causalidad.')
        _metricas_principales(data)
        if pagina=='Observatorio': mostrar_visor_territorial(data)
        else: mostrar_comparativo_cuidado(data)
    elif pagina=='Vinculación demostrativa':
        st.header('Vinculación con centros comunitarios')
        st.warning('Datos completamente sintéticos. No son familias, centros, cupos ni resultados reales del piloto. No se guardan en la base operativa.')
        radio=st.slider('Radio geográfico máximo (km)',1,20,10)
        if st.button('Ejecutar demostración'):
            result=pd.DataFrame(ejecutar_demo(radio))
            st.session_state['resultado_demo']=result
            st.session_state['radio_demo']=radio
        if 'resultado_demo' in st.session_state:
            result=st.session_state['resultado_demo']
            st.caption(f"Resultado calculado con radio de {st.session_state['radio_demo']} km")
            cols=st.columns(3)
            cols[0].metric('Solicitudes sintéticas',len(result))
            cols[1].metric('Recomendaciones',int(result.estado.eq('recomendada').sum()))
            cols[2].metric('Pendientes',int(result.estado.eq('pendiente').sum()))
            st.dataframe(result,hide_index=True,use_container_width=True)
            st.caption('Una recomendación requiere confirmación institucional. La distancia es geográfica, no tiempo de viaje. El orden de solicitudes influye en la asignación.')
    elif pagina=='Integraciones pendientes':
        st.header('Entregas del equipo')
        st.dataframe(pd.DataFrame(INTEGRACIONES),hide_index=True,use_container_width=True)
        st.info('Los módulos se incorporarán tras validar sus contratos de entrada y salida. No se muestran ahorros ni recaudaciones inventadas.')
    else:
        st.header('Fuentes y límites')
        st.markdown('''El observatorio conserva las fuentes tabulares y cartográficas del repositorio. ENUT describe CDMX; la distribución proporcional por alcaldía es exploratoria.

El dato de horas de mujeres cuidadoras procede del resumen ENUT, separado de los indicadores macroeconómicos. El conteo de infraestructura no demuestra cupos disponibles.

El matching demostrativo exige tipo de servicio, días, horario, radio y cupo. No es un modelo entrenado para predecir inserción laboral y no sustituye verificación institucional.

La aplicación pública no recoge datos personales. Antes de habilitar operación real faltan autenticación, autorización por rol, protocolo de privacidad, verificación de centros, migración de registros y seguimiento del piloto.''')
