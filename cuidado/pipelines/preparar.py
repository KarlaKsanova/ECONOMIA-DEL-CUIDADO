"""Ejecutar fuera del ciclo de Streamlit: python -m cuidado.pipelines.preparar."""
import json
from cuidado.config import ROOT_DIR
from cuidado.pipelines.territorial import construir_dataset_consolidado

def preparar():
    data = construir_dataset_consolidado()
    if len(data) != 16 or data.alcaldia.isna().any() or data.geometry.isna().any():
        raise ValueError("El observatorio requiere 16 alcaldías únicas con geometría")
    folder = ROOT_DIR / "data/processed"
    folder.mkdir(parents=True, exist_ok=True)
    data.to_parquet(folder / "observatorio.parquet", index=False)
    (folder / "observatorio.metadata.json").write_text(json.dumps(data.attrs, ensure_ascii=False, indent=2), encoding="utf-8")
    report = {"alcaldias":len(data), "duplicadas":int(data.alcaldia.duplicated().sum()), "nulos":data.drop(columns="geometry").isna().sum().to_dict(), "advertencias":["Distribución proporcional de cuidado sin trabajo: no es abandono laboral ni observación por alcaldía", "Revisar comparabilidad temporal y representatividad de fuentes"]}
    (folder / "calidad.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Dataset preparado: 16 alcaldías; revisar data/processed/calidad.json")

if __name__ == "__main__":
    preparar()
