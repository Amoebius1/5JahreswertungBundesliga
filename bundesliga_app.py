import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Bundesliga Fünfjahreswertung", layout="wide")

st.title("🏆 Bundesliga Fünfjahreswertung")

# Input: Jahr wählen
selected_year = st.selectbox("Wähle ein Jahr (Stichtag):", list(range(2025, 2019, -1)))

# Gewichtungen für die letzten 5 Jahre
weights = [1.0, 0.8, 0.6, 0.4, 0.2]
years = [selected_year - i for i in range(5)]

# Beispielteams
teams = [
    "Bayern München", "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen",
    "Eintracht Frankfurt", "VfL Wolfsburg", "SC Freiburg", "1. FC Union Berlin",
    "TSG Hoffenheim", "1. FC Köln", "Mainz 05", "Borussia Mönchengladbach",
    "Werder Bremen", "VfB Stuttgart", "FC Augsburg", "Hertha BSC",
    "Schalke 04", "1. FC Heidenheim"
]

# Simulierte Saison-Daten erzeugen
@st.cache_data
def simulate_data():
    data = []
    np.random.seed(42)
    for year in years:
        for team in teams:
            wins = np.random.randint(5, 23)
            draws = np.random.randint(3, 10)
            points = wins * 3 + draws
            data.append({
                "Team": team,
                "Season": year,
                "Wins": wins,
                "Draws": draws,
                "Points": points
            })
    return pd.DataFrame(data)

season_df = simulate_data()

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
st.subheader(f"🏅 Fünfjahreswertung {selected_year}")
st.dataframe(ranking_df, use_container_width=True)

# Optional: Details je Saison anzeigen
if st.checkbox("📅 Saison-Daten anzeigen"):
    st.dataframe(season_df.sort_values(by=["Season", "Team"]), use_container_width=True)

# Erweiterungsidee: Dateneingabe-Formular
if st.checkbox("➕ Neue Saison hinzufügen (Demo)"):
    with st.form("add_season_form"):
        team = st.selectbox("Team", teams)
        year = st.selectbox("Saisonjahr", years)
        wins = st.number_input("Siege", 0, 34, 10)
        draws = st.number_input("Unentschieden", 0, 34, 5)
        submitted = st.form_submit_button("Hinzufügen")
        if submitted:
            points = wins * 3 + draws
            st.success(f"{team} - Saison {year} mit {points} Punkten hinzugefügt (nicht persistent)")
