import streamlit as st
import requests
import time
import pandas as pd 

# --- Dune API Setup ---
DUNE_API_KEY = "Dmb8mqxsxiJ6g3v23dRg1aTVdVUk4JEy"
QUERY_ID = 4628058
HEADERS = {"x-dune-api-key": DUNE_API_KEY}

@st.cache_data(ttl=3600)

# --- Outcome Badge Styling ---
def render_outcome_label(outcome):
    color_map = {
        "Passed": "#2ecc71",      # Green
        "Defeated": "#e74c3c",    # Red
        "Executed": "#9b59b6",    # Purple
        "Active": "#3498db",      # Blue
        "Cancelled": "#7f8c8d"    # Gray
    }
    color = color_map.get(outcome, "#bdc3c7")  # Default gray
    return f"""
    <span style='
        background-color:{color};
        padding:4px 10px;
        border-radius:4px;
        color:white;
        font-size:0.85rem;
    '>{outcome}</span>
    """

def run_dune_query(query_id):
    res = requests.post(f"https://api.dune.com/api/v1/query/{query_id}/execute", headers=HEADERS)
    execution_id = res.json().get("execution_id")

    while True:
        status = requests.get(
            f"https://api.dune.com/api/v1/execution/{execution_id}/status", headers=HEADERS
        ).json()
        if status["state"] == "QUERY_STATE_COMPLETED":
            break
        elif status["state"] == "QUERY_STATE_FAILED":
            raise Exception("Query failed")
        time.sleep(2)

    result = requests.get(
        f"https://api.dune.com/api/v1/execution/{execution_id}/results", headers=HEADERS
    ).json()
    df = pd.DataFrame(result["result"]["rows"])
    df.columns = [c.strip() for c in df.columns]
    return df


# --- App Start ---
st.set_page_config(page_title="Arbitrum DAO Governance", layout="wide)
# --- Welcome popup on first load ---
if "welcome_shown" not in st.session_state:
    st.toast("👋 Ready to dive into Arbitrum governance? Made with ❤️ by Entropy Advisors.", icon="🌐")
    st.session_state.welcome_shown = True

st.markdown("""
<style>
/* Make everything feel cleaner and more modern */
body {
    font-family: 'Segoe UI', sans-serif;
    background-color: #f8f9fa;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Headings look smoother */
h1, h2, h3 {
    font-family: 'Segoe UI', sans-serif;
    font-weight: 600;
    color: #111111;
}

/* Proposal card spacing */
hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)

st.title("🗳️ Arbitrum DAO Governance Overview")
st.caption("Live from Dune | Query 4628058")

df = run_dune_query(QUERY_ID)

# Show all column names
st.expander("🧾 Show All Columns").write(df.columns.tolist())

# Filters
# Sidebar: Filters and Sorting
with st.sidebar:
    # SECTION 1 – Filters
    st.markdown("### 🔍 Filter Proposals")
    st.caption("Narrow the proposals by outcome and theme.")

    outcome = st.selectbox(
        "🎯 Proposal Outcome",
        options=["All"] + sorted(df["proposal_outcome_label"].dropna().unique())
    )

    theme = st.selectbox(
        "🎭 Proposal Theme",
        options=["All"] + sorted(df["proposal_theme"].dropna().unique())
    )

    st.divider()

    # SECTION 2 – Sorting
    st.markdown("### 📊 Sort Proposals")
    st.caption("Choose how to order the proposals below.")

    sort_by = st.selectbox(
        "🔢 Sort By",
        options=["support_rate", "voters", "vote_participation", "proposal_title"],
        format_func=lambda x: {
            "support_rate": "💙 Support Rate",
            "voters": "👥 Voters",
            "vote_participation": "🗳 Participation",
            "proposal_title": "🔤 Title (A-Z)"
        }.get(x, x)
    )

    sort_order = st.radio("⬆️⬇️ Sort Order", options=["Descending", "Ascending"], horizontal=True)

    st.divider()

    # SECTION 3 – Optional Toggles
    high_support_only = st.checkbox("✅ Show only proposals with > 50% support")



if outcome != "All":
    df = df[df["proposal_outcome_label"] == outcome]
if theme != "All":
    df = df[df["proposal_theme"] == theme]

ascending = sort_order == "Ascending"
try:
    df[sort_by] = pd.to_numeric(df[sort_by], errors='coerce')
    df = df.sort_values(by=sort_by, ascending=ascending)
except Exception as e:
    st.warning(f"Could not sort by '{sort_by}': {e}")



# --- Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("🧾 Total Proposals", len(df))
col2.metric("👥 Avg. Voters", f"{df['voters'].mean():,.0f}")
try:
    avg_support = df["support_rate"].astype(float).mean()
    col3.metric("💙 Avg. Support Rate", f"{avg_support:.2f}%")
except:
    col3.metric("💙 Avg. Support Rate", "N/A")

st.divider()

# --- Proposal Overview ---
st.subheader("📊 Proposal Overview")

for _, row in df.iterrows():
    with st.container():
        st.markdown(f"### 📝 {row['proposal_title']}")

        # Support bar
        try:
            st.progress(float(row["support_rate"]) / 100, text=f"{float(row['support_rate']):.2f}% support")
        except:
            st.warning("No support rate")

        # Info bar row
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        col1.markdown(f"👥 **{row['voters']} voters**")
        col2.markdown(f"🗳 **{row['vote_participation']}% participation**")
        col3.markdown(f"🎭 **{row['proposal_theme']}**")
        col4.markdown(render_outcome_label(row['proposal_outcome_label']), unsafe_allow_html=True)

        st.markdown("<hr style='margin:1rem 0'>", unsafe_allow_html=True)



st.divider()

# --- Chart: Top by Participation ---
st.subheader("📈 Top Proposals by Voter Participation")
try:
    df["vote_participation"] = df["vote_participation"].astype(float)
    top_participation = df.sort_values(by="vote_participation", ascending=False).head(10)
    st.bar_chart(top_participation.set_index("proposal_title")["vote_participation"])
except:
    st.warning("Can't parse vote_participation for chart.")

st.divider()

# --- Optional Full Table View ---
with st.expander("📋 Full Raw Data Table"):
    st.dataframe(df)

# --- Summary of All Columns ---
st.subheader("🧩 Column Dictionary")
st.markdown("""
Here’s a quick explanation of all 41 columns in your dataset:

- **arb_allocation** — ARB amount allocated by the proposal  
- **contract_address** — Address of the contract that initiated the proposal  
- **creation_block** — Block in which the proposal was created  
- **creation_time** — Timestamp of creation  
- **creation_tx_hash** — TX hash of proposal creation  
- **delegated_voting_power** — Delegated voting power at the time  
- **delegates** — Count of delegates who voted  
- **eth_allocation** — ETH allocation amount  
- **opex_arb / opex_eth / opex_usd / opex_percentage** — Opex costs in different denominations  
- **proposal_category** — Category tag (e.g. Treasury, Governance)  
- **proposal_id / proposal_index / proposal_number** — ID details  
- **proposal_outcome / proposal_outcome_label** — Raw + human-readable outcome  
- **proposal_tally** — Total vote count  
- **proposal_theme** — Thematic label (e.g. Grants, Infra)  
- **proposal_title** — Title of the proposal  
- **proposal_type** — Proposal type (e.g. AIP, TempCheck)  
- **proposer / proposer_name** — Wallet + human-readable name  
- **proposer_tally** — Voting power of the proposer  
- **quorum / quorum_progress** — Quorum details  
- **support_rate** — Support percentage (0-100%)  
- **usd_allocation / votable_tokens** — Funding and voting info  
- **vote_participation / voter_participation** — Participation rates  
- **voters / votes / votes_for / votes_against / votes_abstain / votes_total** — Voting breakdown  
- **voting_power_utilisation** — How much voting power was used  
- **voting_start_block / voting_end_block** — Voting window info  
""")
