from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]

def test_all_pages_and_demo():
    app=AppTest.from_file(str(ROOT/'app_dashboard.py'),default_timeout=90).run()
    assert not app.exception
    for name in ['Comparativos','Vinculación demostrativa','Integraciones pendientes','Fuentes y límites']:
        app.sidebar.radio[0].set_value(name).run()
        assert not app.exception
        if name=='Vinculación demostrativa':
            app.button[0].click().run()
            assert not app.exception
            assert app.metric[1].value=='5'
