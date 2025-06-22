import streamlit as st
from dune_helper import run_dune_query
import pandas as pd

st.set_page_config(page_title="Arbitrum DAO Proposals", layout="wide")

@st.cache_data(ttl=3600)
def get_data():
    return run_dune_query(4628058)

df = get_data()

st.title("🗳️ Arbitrum DAO Governance Overview")
st.caption("Live data from Dune | Query ID: 4628058")

# Sidebar filters
with st.sidebar:
    status = st.selectbox("Filter by Outcome", ["All"] + df["Outcome"].unique().tolist())
    theme = st.selectbox("Filter by Theme", ["All"] + sorted(df["Theme"].dropna().unique().tolist()))

# Apply filters
if status != "All":
    df = df[df["Outcome"] == status]
if theme != "All":
    df = df[df["Theme"] == theme]

# Top metrics
col1, col2, col3 = st.columns(3)
col1.metric("🧾 Total Proposals", len(df))
col2.metric("🧍‍♂️ Total Voters (avg)", f"{df['Voters'].mean():,.0f}")
col3.metric("💙 Avg. Support Rate", f"{df['Support Rate'].astype(float).mean():.2f}%")

st.divider()

# Show support bars and visual indicators
st.subheader("🔎 Proposal Support Overview")
for _, row in df.iterrows():
    st.markdown(f"**{row['Proposal']}**")
    st.progress(float(row["Support Rate"]) / 100, text=f"{row['Support Rate']} support")
    st.caption(f"{row['Voters']} voters | {row['Outcome']} | Theme: {row['Theme']}")

st.divider()

# Chart: Most Voted Proposals
st.subheader("📊 Top Proposals by Total Votes")
df_votes = df.copy()
df_votes["Total Votes"] = df_votes["Total Votes"].astype(str).str.replace("m", "").astype(float)
top_votes = df_votes.sort_values(by="Total Votes", ascending=False).head(10)

st.bar_chart(top_votes.set_index("Proposal")["Total Votes"])
