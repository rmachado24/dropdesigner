import json
import pandas as pd
from typing import Any
import streamlit as st

from DropDesigner.src.dropdesigner.paths import DATA_DIR, CANALS_DIR, RUBICON_DIR


def load_json(filename: str) -> Any:
    path = DATA_DIR / filename

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

def load_flumegates() -> pd.DataFrame:
    path = RUBICON_DIR / "flumegates.xlsx"
    df = pd.read_excel(path)
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ","_")
        .str.replace("(","")
        .str.replace(")","")
    )
    return df

