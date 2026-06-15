"""Shared data loading for the EPL stats Streamlit app."""

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).with_name("final_dataset.csv")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, index_col=0)
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%y", errors="coerce")
    df["Season"] = df["Date"].dt.year.where(
        df["Date"].dt.month >= 8, df["Date"].dt.year - 1
    )
    df["TotalGoals"] = df["FTHG"] + df["FTAG"]
    # FTR: H = home win, NH = not-home (draw or away win). Derive a readable label.
    df["Result"] = df["FTR"].map({"H": "Home win", "NH": "Draw / Away win"})
    return df
