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

# Wikipedia-Daten laden
@st.cache_data(show_spinner=True)
def load_season_data(year):
    try:
        url = f"https://de.wikipedia.org/wiki/Bundesliga_{year}/{year+1}"
        tables = pd.read_html(url)
        # Suche die Tabelle mit den meisten passenden Spalten
        for table in tables:
            cols = table.columns.astype(str)
            if any("Verein" in col for col in cols) and any("S" in col for col in cols) and any("U" in col for col in cols):
                df = table.copy()
                break
        else:
            raise ValueError("Keine passende Tabelle gefunden.")

        df = df.rename(columns=lambda x: str(x).strip())
        # Vereinsspalte erkennen
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

    except Exception as e:
        st.warning(f"⚠️ Daten für {year}/{year+1} konnten nicht geladen werden. ({e})")
        return pd.DataFrame(columns=["Team", "Wins", "Draws", "Points", "Season"])

# Kombiniere alle Jahre
season_df = pd.concat([load_season_data(y) for y in years], ignore_index=True)

# Gewicht anwenden
season_df["Weight"] = season_df["Season"].map(dict(zip(years, weights)))
season_df["WeightedPoints"] = season_df["Points"] * season_df["Weight"]

# Aggregierte Fünfjahreswertung
ranking_df = (
    season_df.groupby("Team")
    .agg(TotalPoints=("Points", "sum"), FiveYearScore=("WeightedPoints", "sum"))
    .sort_values("FiveYearScore", ascending=False)
    .reset_index()
)

# Anzeige
st.subheader(f"\U0001F3C5 Fünfjahreswertung {selected_year}")
st.dataframe(ranking_df, use_container_width=True)

# Optional: Details je Saison anzeigen
if st.checkbox("\U0001F4C5 Saison-Daten anzeigen"):
    st.dataframe(season_df.sort_values(by=["Season", "Team"]), use_container_width=True)

