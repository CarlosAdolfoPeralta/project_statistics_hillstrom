"""Carga y preparación del dataset Hillstrom (MineThatData E-Mail Analytics Challenge)."""
from pathlib import Path

import pandas as pd

URL = (
    "http://www.minethatdata.com/"
    "Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv"
)
RAW_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "hillstrom.csv"

COLUMNAS = [
    "recency", "history_segment", "history", "mens", "womens", "zip_code",
    "newbie", "channel", "segment", "visit", "conversion", "spend",
]

# Nombre original de la campaña -> nombre corto del grupo
MAPA_GRUPOS = {
    "No E-Mail": "control",
    "Mens E-Mail": "men",
    "Womens E-Mail": "women",
}
GRUPOS = ["control", "men", "women"]


def load_hillstrom(path=RAW_PATH, url=URL):
    """Lee el CSV local; si no existe, lo descarga desde el blog de MineThatData."""
    path = Path(path)
    if path.exists():
        return pd.read_csv(path)
    try:
        df = pd.read_csv(url)
    except Exception as e:
        raise RuntimeError(
            f"No se pudo descargar el dataset desde {url}. "
            f"Se puede guardar el CSV manualmente en {path}."
        ) from e
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df


def prepare(df):
    """Valida el esquema y agrega la columna `grupo` (control / hombres / mujeres)."""
    faltan = [c for c in COLUMNAS if c not in df.columns]
    if faltan:
        raise ValueError(f"Faltan columnas esperadas: {faltan}")

    desconocidos = set(df["segment"].unique()) - set(MAPA_GRUPOS)
    if desconocidos:
        raise ValueError(f"Valores inesperados en 'segment': {desconocidos}")

    out = df.copy()
    out["group"] = pd.Categorical(
        out["segment"].map(MAPA_GRUPOS), categories=GRUPOS, ordered=True
    )
    return out
