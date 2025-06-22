import streamlit as st
import requests
import time
import pandas as pd

# --- Dune API Setup ---
DUNE_API_KEY = "Dmb8mqxsxiJ6g3v23dRg1aTVdVUk4JEy"
QUERY_ID = 4628058
HEADERS = {"x-dune-api-key": DUNE_API_KEY}


# --- Fetch and cache data ---
@st.cache_data(ttl=3600)
def run_dune_query(query_id):
    # 1. Trigger execution
    res = requests.post(f"https://api.dune.com/api/v1/query/{query_id}/execute", headers=HEADERS)
    execution_id = res.json().get("execution_id")

    # 2. Poll until complete
    while True:
        status = requests.get(
            f"https://api.dune.com/api/v1/execution/{execution_id}/status", headers=HEADERS
        ).json()
        if status["state"] == "QUERY_STATE_COMPLETED":
            break
        elif status["state"] == "QUERY_STATE_FAILED":
            raise Exception("Query failed")
        time.sleep(2)

    # 3. Fetch results
    result = requests.get(
        f"https://api.dune.com/api/v1/execution/{execution_id}/results", headers=HEADERS
    ).json()
    df = pd.DataFrame(result["result"]["rows"])
    df.columns = [c.strip() for c in df.columns]
    return df


# --- Streamlit App Layout ---
st.set_page_config(page_title="Arbitrum DAO Proposals", layout="wide")
st.title("🗳️ Arbitrum DAO Governance Overview")
st.caption("Powered by live Dune data | Query ID: 4628058")

# Get and preview data
df = run_dune_query(QUERY_ID)
st.write("Columns:", df.columns.tolist())

# Rename columns for convenience (you can adjust these to match actual)
df = df.rename(columns={
    "Proposal": "proposal",
    "Proposal Type": "type",
    "Outcome": "outcome",
    "Category": "category",
    "Theme": "theme",
    "Voters": "voters",
    "Quorum": "quorum",
    "Total Votes": "total_votes",
    "Quorum Progress": "quorum_progress",
    "Support Rate": "support_rate"
})

# Filters
with st.sidebar:
    selected_outcome = st.selectbox("Filter by Outcome", ["All"] + sorted(df["outcome"].dropna().unique().tolist()))
    selected_theme = st.selectbox("Filter by Theme", ["All"] + sorted(df["theme"].dropna().unique().tolist()))

# Apply filters
if selected_outcome != "All":
    df = df[df["outcome"] == selected_outcome]
if selected_theme != "All":
    df = df[df["theme"] == selected_theme]

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("📄 Proposals", len(df))
col2.metric("👥 Avg. Voters", f"{df['voters'].mean():,.0f}")
try:
    avg_support = df['support_rate'].astype(str).str.replace('%','').astype(float).mean()
    col3.metric("💙 Avg. Support Rate", f"{avg_support:.2f}%")
except:
    col3.metric("💙 Avg. Support Rate", "N/A")

st.divider()

# Support Rate Bars
st.subheader("🔎 Support Per Proposal")
for _, row in df.iterrows():
    st.markdown(f"**{row['proposal']}**")
    try:
        support = float(str(row["support_rate"]).replace('%',''))
        st.progress(support / 100, text=f"{row['support_rate']} support")
    except:
        st.write("❌ No support rate available")
    st.caption(f"{row['voters']} voters | {row['outcome']} | {row['theme']}")

st.divider()

# Chart: Top by Total Votes
st.subheader("📊 Top 10 Proposals by Total Votes")
try:
    df["total_votes_clean"] = df["total_votes"].astype(str).str.replace("m", "").astype(float)
    top = df.sort_values(by="total_votes_clean", ascending=False).head(10)
    st.bar_chart(top.set_index("proposal")["total_votes_clean"])
except:
    st.write("Could not parse total votes.")
