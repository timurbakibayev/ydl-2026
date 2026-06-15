"""Streamlit dashboard for day1/final_dataset.csv (English Premier League matches).

Run with:
    venv/bin/streamlit run day1/stats_app.py
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from data import load_data

st.set_page_config(page_title="EPL Match Stats", page_icon="⚽", layout="wide")

df = load_data()

st.title("⚽ English Premier League — Match Statistics")
st.caption(f"{len(df):,} matches loaded from `final_dataset.csv`")

# ----------------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------------
st.sidebar.header("Filters")

seasons = sorted(int(s) for s in df["Season"].dropna().unique())
season_range = st.sidebar.select_slider(
    "Season range (start year)",
    options=seasons,
    value=(seasons[0], seasons[-1]),
)

teams = sorted(set(df["HomeTeam"]) | set(df["AwayTeam"]))
team_filter = st.sidebar.selectbox("Focus on a team (optional)", ["All teams"] + teams)

mask = df["Season"].between(season_range[0], season_range[1])
if team_filter != "All teams":
    mask &= (df["HomeTeam"] == team_filter) | (df["AwayTeam"] == team_filter)

view = df[mask]

if view.empty:
    st.warning("No matches match the current filters.")
    st.stop()

# ----------------------------------------------------------------------------
# Headline metrics
# ----------------------------------------------------------------------------
home_wins = (view["FTR"] == "H").sum()
home_win_pct = home_wins / len(view) * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Matches", f"{len(view):,}")
c2.metric("Total goals", f"{int(view['TotalGoals'].sum()):,}")
c3.metric("Goals / match", f"{view['TotalGoals'].mean():.2f}")
c4.metric("Home-win rate", f"{home_win_pct:.1f}%")

st.divider()

# ----------------------------------------------------------------------------
# Result split + goals distribution
# ----------------------------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Match outcomes")
    outcome = view["Result"].value_counts().reset_index()
    outcome.columns = ["Result", "Matches"]
    fig = px.pie(outcome, names="Result", values="Matches", hole=0.45)
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Goals per match")
    fig = px.histogram(view, x="TotalGoals", nbins=int(view["TotalGoals"].max()) + 1)
    fig.update_layout(xaxis_title="Goals in a match", yaxis_title="Number of matches")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ----------------------------------------------------------------------------
# Goals per season trend
# ----------------------------------------------------------------------------
st.subheader("Average goals per match, by season")
by_season = (
    view.dropna(subset=["Season"])
    .groupby("Season")["TotalGoals"]
    .mean()
    .reset_index()
)
fig = px.line(by_season, x="Season", y="TotalGoals", markers=True)
fig.update_layout(yaxis_title="Avg goals / match", xaxis_title="Season (start year)")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ----------------------------------------------------------------------------
# Team standings table
# ----------------------------------------------------------------------------
st.subheader("Team summary")


def team_stats(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for team in sorted(set(data["HomeTeam"]) | set(data["AwayTeam"])):
        home = data[data["HomeTeam"] == team]
        away = data[data["AwayTeam"] == team]
        played = len(home) + len(away)
        if played == 0:
            continue
        wins = (home["FTHG"] > home["FTAG"]).sum() + (away["FTAG"] > away["FTHG"]).sum()
        draws = (home["FTHG"] == home["FTAG"]).sum() + (away["FTAG"] == away["FTHG"]).sum()
        losses = played - wins - draws
        gf = home["FTHG"].sum() + away["FTAG"].sum()
        ga = home["FTAG"].sum() + away["FTHG"].sum()
        rows.append(
            {
                "Team": team,
                "Played": played,
                "Wins": int(wins),
                "Draws": int(draws),
                "Losses": int(losses),
                "Win %": round(wins / played * 100, 1),
                "Goals for": int(gf),
                "Goals against": int(ga),
                "Goal diff": int(gf - ga),
            }
        )
    return pd.DataFrame(rows).sort_values("Win %", ascending=False).reset_index(drop=True)


standings = team_stats(view)
st.dataframe(standings, use_container_width=True, hide_index=True)

with st.expander("Show raw match data"):
    st.dataframe(
        view[["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "Result"]],
        use_container_width=True,
        hide_index=True,
    )

st.divider()

# ----------------------------------------------------------------------------
# Head-to-head between two teams
# ----------------------------------------------------------------------------
st.subheader("Head-to-head")

h2h_teams = sorted(set(view["HomeTeam"]) | set(view["AwayTeam"]))
if len(h2h_teams) < 2:
    st.info("Not enough teams in the current filter for a head-to-head.")
else:
    hc, ac = st.columns(2)
    team_a = hc.selectbox("Team A", h2h_teams, index=0, key="h2h_a")
    default_b = 1 if h2h_teams[0] == team_a else 0
    team_b = ac.selectbox("Team B", h2h_teams, index=default_b, key="h2h_b")

    if team_a == team_b:
        st.info("Pick two different teams.")
    else:
        h2h = view[
            ((view["HomeTeam"] == team_a) & (view["AwayTeam"] == team_b))
            | ((view["HomeTeam"] == team_b) & (view["AwayTeam"] == team_a))
        ].sort_values("Date")

        if h2h.empty:
            st.warning(f"No matches between {team_a} and {team_b} in this range.")
        else:
            # Goals/wins from each team's perspective, regardless of venue.
            a_home = h2h["HomeTeam"] == team_a
            a_goals = h2h["FTHG"].where(a_home, h2h["FTAG"])
            b_goals = h2h["FTAG"].where(a_home, h2h["FTHG"])
            a_wins = int((a_goals > b_goals).sum())
            b_wins = int((b_goals > a_goals).sum())
            draws = int((a_goals == b_goals).sum())

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Meetings", len(h2h))
            m2.metric(f"{team_a} wins", a_wins)
            m3.metric("Draws", draws)
            m4.metric(f"{team_b} wins", b_wins)

            summary = pd.DataFrame(
                {"Team": [team_a, team_b], "Wins": [a_wins, b_wins]}
            )
            fig = px.bar(
                summary,
                x="Team",
                y="Wins",
                color="Team",
                text="Wins",
                title=f"{team_a} vs {team_b} — wins (draws: {draws})",
            )
            fig.update_layout(showlegend=False, yaxis_title="Wins")
            st.plotly_chart(fig, use_container_width=True)

            h2h_table = h2h[["Date", "HomeTeam", "FTHG", "FTAG", "AwayTeam"]].copy()
            h2h_table["Score"] = (
                h2h_table["FTHG"].astype(str) + " - " + h2h_table["FTAG"].astype(str)
            )
            st.dataframe(
                h2h_table[["Date", "HomeTeam", "Score", "AwayTeam"]],
                use_container_width=True,
                hide_index=True,
            )
