import streamlit as st
import pandas as pd
import numpy as np
import requests

st.set_page_config(page_title="Bundesliga Fünfjahreswertung", layout="wide")

st.title("\U0001F3C6 Bundesliga Fünfjahreswertung")

# Input: Jahr wählen
selected_year = st.selectbox("Wähle ein Jahr (Stichtag):", list(range(2025, 1962, -1)))

# Gewichtungen für die letzten 5 Jahre
weights = [1.0, 0.8, 0.6, 0.4, 0.2]
years = [selected_year - i for i in range(5) if (selected_year - i) >= 1963]

# Wikipedia-Daten laden mit URL-Fallback
@st.cache_data(show_spinner=True)
def load_season_data(year):
    urls = [
        f"https://de.wikipedia.org/wiki/Bundesliga_{year}/{year+1}",
        f"https://de.wikipedia.org/wiki/Fu%C3%9Fball-Bundesliga_{year}/{str(year+1)[-2:]}"
    ]
    for url in urls:
        try:
            tables = pd.read_html(url)
            for table in tables:
                cols = table.columns.astype(str)
                if any("Verein" in col for col in cols) and any("S" in col for col in cols) and any("U" in col for col in cols):
                    df = table.copy()
                    df = df.rename(columns=lambda x: str(x).strip())
                    team_col = [c for c in df.columns if "Verein" in c][0]
                    wins_col = [c for c in df.columns if c.strip().startswith("S")][0]
                    draws_col = [c for c in df.columns if c.strip().startswith("U")][0]
                    df = df[[team_col, wins_col, draws_col]]
                    df.columns = ["Team", "Wins", "Draws"]
                    df["Wins"] = pd.to_numeric(df["Wins"], errors='coerce')
                    df["Draws"] = pd.to_numeric(df["Draws"], errors='coerce')
                    df.dropna(inplace=True)
                    df["Points"] = df["Wins"] * 3 + df["Draws"]
                    df["Season"] = year
                    return df
        except Exception:
            continue
    st.warning(f"⚠️ Daten für {year}/{year+1} konnten nicht geladen werden. (keine gültige URL)")
    return pd.DataFrame(columns=["Team", "Wins", "Draws", "Points", "Season"])

# Kombiniere alle Jahre
season_df = pd.concat([load_season_data(y) for y in years], ignore_index=True)

# Gewicht anwenden
season_df["Weight"] = season_df["Season"].map(dict(zip(years, weights)))
season_df["WeightedPoints"] = season_df["Points"] * season_df["Weight"]

# Aggregierte Fünfjahreswertung mit Aufschlüsselung
ranking_df = (
    season_df.groupby("Team")
    .agg(
        TotalPoints=("Points", "sum"),
        WeightedBreakdown=("WeightedPoints", lambda x: list(x)),
        FiveYearScore=("WeightedPoints", "sum")
    )
    .sort_values("FiveYearScore", ascending=False)
    .reset_index()
)

ranking_df.index += 1  # Rang beginnt bei 1
ranking_df.reset_index(inplace=True)
ranking_df.rename(columns={"index": "Rang"}, inplace=True)

# Anzeige
st.subheader(f"\U0001F3C5 Fünfjahreswertung {selected_year}")
st.dataframe(ranking_df, use_container_width=True)

# Optional: Details je Saison anzeigen
if st.checkbox("\U0001F4C5 Saison-Daten anzeigen"):
    st.dataframe(season_df.sort_values(by=["Season", "Team"]), use_container_width=True)

