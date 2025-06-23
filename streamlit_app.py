import streamlit as st
import requests
import time 
import pandas as pd
from streamlit_lottie import st_lottie

# --- Dune API Setup ---
DUNE_API_KEY = "Dmb8mqxsxiJ6g3v23dRg1aTVdVUk4JEy"
QUERY_ID = 4628058
HEADERS = {"x-dune-api-key": DUNE_API_KEY}

@st.cache_data(ttl=3600)
def run_dune_query(query_id):
    res = requests.post(f"https://api.dune.com/api/v1/query/{query_id}/execute", headers=HEADERS)
    execution_id = res.json().get("execution_id")

    while True:
        status = requests.get(f"https://api.dune.com/api/v1/execution/{execution_id}/status", headers=HEADERS).json()
        if status["state"] == "QUERY_STATE_COMPLETED":
            break
        elif status["state"] == "QUERY_STATE_FAILED":
            raise Exception("Query failed")
        time.sleep(2)

    result = requests.get(f"https://api.dune.com/api/v1/execution/{execution_id}/results", headers=HEADERS).json()
    df = pd.DataFrame(result["result"]["rows"])
    df.columns = [c.strip() for c in df.columns]
    return df

def render_outcome_label(outcome):
    color_map = {
        "Passed": "#2ecc71",
        "Defeated": "#e74c3c",
        "Executed": "#9b59b6",
        "Active": "#3498db",
        "Cancelled": "#7f8c8d"
    }
    color = color_map.get(outcome, "#bdc3c7")
    return f"""
    <span style='background-color:{color}; padding:4px 10px; border-radius:4px; color:white; font-size:0.85rem;'>
        {outcome}
    </span>
    """

def load_lottie(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except (requests.RequestException, ValueError) as e:
        st.warning(f"Could not load animation from {url}. Using fallback.")
        # Fallback to a simple animation or return None
        try:
            # Try a different Lottie animation URL as fallback
            fallback_url = "https://assets5.lottiefiles.com/packages/lf20_UJNc2t.json"
            response = requests.get(fallback_url)
            response.raise_for_status()
            return response.json()
        except:
            return None

# --- App Setup ---
st.set_page_config(page_title="Arbitrum DAO Governance", layout="wide")

# --- Styling ---
st.markdown("""
<style>
[data-testid="stSidebar"]::before {
    content: "👈 Click here to open filters & sort tools";
    color: #888;
    font-size: 0.85rem;
    margin-left: 8px;
    display: block;
}
body {
    font-family: 'Segoe UI', sans-serif;
    background-color: #f8f9fa;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
h1, h2, h3 {
    font-family: 'Segoe UI', sans-serif;
    font-weight: 600;
    color: #111111;
}
hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# --- Welcome Animation ---
if "hide_modal" not in st.session_state:
    st.session_state.hide_modal = False
if not st.session_state.hide_modal:
    with st.container():
        lottie_animation = load_lottie("https://assets3.lottiefiles.com/packages/lf20_2kscqf.json")
        if lottie_animation:
            st_lottie(lottie_animation, height=200)
        else:
            st.markdown("🎉", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>\U0001F44B Ready to dive into Arbitrum governance?</h2><p style='text-align:center;'>Made with ❤️ by Entropy Advisors.</p>", unsafe_allow_html=True)
        if st.button("✖ Close"):
            st.session_state.hide_modal = True

# --- Dark Mode Toggle ---
dark_mode = st.sidebar.toggle("🌓 Dark Mode", value=False)
if dark_mode:
    st.markdown("""
    <style>
    body { background-color: #111 !important; color: #eee !important; }
    .st-emotion-cache-1avcm0n { background-color: #1c1c1c !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Load Data ---
st.title("🗳️ Arbitrum DAO Governance Overview")
st.caption("Live from Dune | Query 4628058")
df = run_dune_query(QUERY_ID)

with st.sidebar:
    st.markdown("### 🔍 Filter Proposals")
    outcome = st.selectbox("🎯 Proposal Outcome", options=["All"] + sorted(df["proposal_outcome_label"].dropna().unique()))
    theme = st.selectbox("🎭 Proposal Theme", options=["All"] + sorted(df["proposal_theme"].dropna().unique()))
    st.divider()
    st.markdown("### 📊 Sort Proposals")
    sort_by = st.selectbox("🔢 Sort By", options=["support_rate", "voters", "vote_participation", "proposal_title"], format_func=lambda x: {"support_rate": "💙 Support Rate", "voters": "👥 Voters", "vote_participation": "🗳 Participation", "proposal_title": "🔤 Title (A-Z)"}.get(x, x))
    sort_order = st.radio("⬆️⬇️ Sort Order", options=["Descending", "Ascending"], horizontal=True)
    st.divider()
    high_support_only = st.checkbox("✅ Show only proposals with > 50% support")

if outcome != "All":
    df = df[df["proposal_outcome_label"] == outcome]
if theme != "All":
    df = df[df["proposal_theme"] == theme]
if high_support_only:
    df = df[df["support_rate"].astype(float) > 50]

ascending = sort_order == "Ascending"
try:
    df[sort_by] = pd.to_numeric(df[sort_by], errors='coerce')
    df = df.sort_values(by=sort_by, ascending=ascending)
except:
    pass

col1, col2, col3 = st.columns(3)
col1.metric("🧾 Total Proposals", len(df))
col2.metric("👥 Avg. Voters", f"{df['voters'].mean():,.0f}")
avg_support_raw = df["support_rate"].astype(float).mean()
avg_support = avg_support_raw * 100 if avg_support_raw <= 1 else avg_support_raw
col3.metric("💙 Avg. Support Rate", f"{avg_support:.2f}%")

st.divider()
st.subheader("📊 Proposal Overview")

for _, row in df.iterrows():
    # Convert support_rate to proper percentage format
    support_rate_display = float(row['support_rate']) * 100 if float(row['support_rate']) <= 1 else float(row['support_rate'])
    
    with st.expander(f"📝 {row['proposal_title']} ({support_rate_display:.2f}% support)"):
        st.markdown(f"👥 Voters: **{row['voters']}**")
        st.markdown(f"📦 Participation: **{row['vote_participation']}%**")
        st.markdown(f"🎭 Theme: **{row['proposal_theme']}**")
        st.markdown(render_outcome_label(row['proposal_outcome_label']), unsafe_allow_html=True)
        
        # Convert support_rate to decimal for progress bar (0-1 range)
        support_rate_decimal = float(row["support_rate"]) if float(row["support_rate"]) <= 1 else float(row["support_rate"]) / 100
        progress = support_rate_decimal
        bar_color = "#3498db" if progress < 0.5 else "#2ecc71"
        st.markdown(f"""
        <div style="background-color: #eee; border-radius: 10px; overflow: hidden; height: 20px; margin-top: 0.5rem;">
            <div style="height: 100%; width: {progress*100:.2f}%; background: {bar_color}; transition: width 0.5s;"></div>
        </div>
        <p style="font-size: 0.9rem;">💙 {support_rate_display:.2f}% Support</p>
        """, unsafe_allow_html=True)

st.divider()
st.subheader("📈 Top Proposals by Voter Participation")
try:
    df["vote_participation"] = df["vote_participation"].astype(float)
    top_participation = df.sort_values(by="vote_participation", ascending=False).head(10)
    st.bar_chart(top_participation.set_index("proposal_title")["vote_participation"])
except:
    st.warning("Can't parse vote_participation for chart.")

with st.expander("📋 Full Raw Data Table"):
    st.dataframe(df)

st.subheader("🧩 Column Dictionary")
st.markdown("""<ul>
<li><b>arb_allocation</b>: ARB amount allocated</li>
<li><b>proposal_outcome_label</b>: Outcome label (e.g. Passed, Defeated)</li>
<li><b>vote_participation</b>: Participation rate (%)</li>
<li><b>support_rate</b>: Support percentage</li>
<li><b>proposal_theme</b>: Thematic label</li>
<li><b>proposal_title</b>: Proposal title</li>
<li><b>voters</b>: Voter count</li>
</ul>""", unsafe_allow_html=True)
