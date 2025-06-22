import streamlit as st
import requests
import time
import pandas as pd

# --- Settings ---
DUNE_API_KEY = "Dmb8mqxsxiJ6g3v23dRg1aTVdVUk4JEy"
QUERY_ID = 4628058
HEADERS = {"x-dune-api-key": DUNE_API_KEY}

# --- Dune Fetch Logic ---
@st.cache_data(ttl=3600)
def run_dune_query(query_id):
    # 1. Trigger execution
    res = requests.post(f"https://api.dune.com/api/v1/query/{query_id}/execute", headers=HEADERS)
    execution_id = res.json().get("execution_id")

    # 2. Poll until ready
    while True:
        status = requests.get(f"https://api.dune.com/api/v1/execution/{execution_id}/status", headers=HEADERS).json()
        if status["state"] == "QUERY_STATE_COMPLETED":
            break
        elif status["state"] == "QUERY_STATE_FAILED":
            raise Exception("Query failed")
        time.sleep(2)

    # 3. Get results
    results = requests.get(f"https://api.dune.com/api/v1/execution/{execution_id}/results", headers=HEADERS).json()
    return pd.DataFrame(results["result"]["rows"])

# --- UI ---
st.set_page_config(page_title="Arbitrum DAO Proposals", layout="wide")
st.title("🗳️ Arbitrum DAO Governance Overview")
st.caption("Live data from Dune | Query ID: 4628058")

df = run_dune_query(QUERY_ID)

# Filters
with st.sidebar:
    status = st.selectbox("Filter by Outcome", ["All"] + df["Outcome"].unique().tolist())
    theme = st.selectbox("Filter by Theme", ["All"] + sorted(df["Theme"].dropna().unique().tolist()))

if status != "All":
    df = df[df["Outcome"] == status]
if theme != "All":
    df = df[df["Theme"] == theme]

# Top metrics
col1, col2, col3 = st.columns(3)
col1.metric("🧾 Total Proposals", len(df))
col2.metric("🧍 Avg. Voters", f"{df['Voters'].mean():,.0f}")
col3.metric("💙 Avg. Support Rate", f"{df['Support Rate'].astype(float).mean():.2f}%")

st.divider()

# Visual support bars
st.subheader("🔎 Proposal Support Overview")
for _, row in df.iterrows():
    st.markdown(f"**{row['Proposal']}**")
    try:
        rate = float(row["Support Rate"].replace('%', ''))
        st.progress(rate / 100, text=f"{row['Support Rate']} support")
    except:
        st.write("❌ Support rate missing")
    st.caption(f"{row['Voters']} voters | {row['Outcome']} | Theme: {row['Theme']}")

st.divider()

# Chart: Total Votes
st.subheader("📊 Top Proposals by Total Votes")
df["Total Votes"] = df["Total Votes"].astype(str).str.replace("m", "").astype(float)
top_votes = df.sort_values(by="Total Votes", ascending=False).head(10)
st.bar_chart(top_votes.set_index("Proposal")["Total Votes"])
