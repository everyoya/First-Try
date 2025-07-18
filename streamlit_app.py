import streamlit as st
import requests
import time 
import pandas as pd
from streamlit_lottie import st_lottie
import os
import re

# --- Brand Colors ---
MIDNIGHT = "#030D1C"
DIGITAL_AZURE = "#0557F5"
STONE = "#E0E3D1"
CRYSTAL = "#9ECFF2"
WHITE = "#FFFFFF"

LOGO_URL = "https://entropyadvisors.com/wp-content/uploads/2024/05/entropy-advisors-logo-white-rgb.svg"

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
        "Passed": f"linear-gradient(135deg, #2ecc71, #27ae60)",
        "Defeated": f"linear-gradient(135deg, #e74c3c, #c0392b)",
        "Executed": f"linear-gradient(135deg, {DIGITAL_AZURE}, {CRYSTAL})",
        "Active": f"linear-gradient(135deg, {DIGITAL_AZURE}, {CRYSTAL})",
        "Cancelled": f"linear-gradient(135deg, #7f8c8d, #6c7b7d)"
    }
    gradient = color_map.get(outcome, f"linear-gradient(135deg, {MIDNIGHT}, {DIGITAL_AZURE})")
    return f"""
    <span style='background: {gradient}; padding: 6px 12px; border-radius: 20px; color: white; font-size: 0.8rem; font-weight: 600; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
        {outcome}
    </span>
    """

def load_lottie(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        st.warning(f"Could not load animation from {url}. Using fallback.")
        try:
            fallback_url = "https://assets5.lottiefiles.com/packages/lf20_UJNc2t.json"
            response = requests.get(fallback_url)
            response.raise_for_status()
            return response.json()
        except:
            return None

# --- App Setup ---
st.set_page_config(page_title="Arbitrum DAO Governance", layout="wide", initial_sidebar_state="expanded")

# --- Global Brand CSS ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
body, .main, .block-container {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: linear-gradient(135deg, {MIDNIGHT} 0%, {DIGITAL_AZURE} 70%, {CRYSTAL} 100%) !important;
    color: {WHITE};
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(135deg, {MIDNIGHT} 0%, {DIGITAL_AZURE} 100%) !important;
    color: {WHITE} !important;
}}

[data-testid="stSidebar"] * {{
    color: {WHITE} !important;
}}

.metric-card {{
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.18);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(12px);
    transition: box-shadow 0.3s;
}}
.metric-card:hover {{
    box-shadow: 0 16px 48px rgba(5,87,245,0.18);
}}
.metric-icon {{
    font-size: 2.2rem;
    margin-bottom: 0.5rem;
    display: block;
}}
.metric-value {{
    font-size: 2rem;
    font-weight: 700;
    color: {CRYSTAL};
    margin-bottom: 0.25rem;
}}
.metric-label {{
    font-size: 1rem;
    color: {WHITE};
    font-weight: 500;
}}

.custom-progress {{
    background: rgba(255,255,255,0.10);
    border-radius: 15px;
    overflow: hidden;
    height: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.10);
}}
.custom-progress-fill {{
    height: 100%;
    border-radius: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.18);
}}

.stButton > button {{
    background: linear-gradient(135deg, {DIGITAL_AZURE} 0%, {CRYSTAL} 100%);
    border: none;
    border-radius: 25px;
    color: {WHITE};
    font-weight: 600;
    padding: 0.5rem 1.5rem;
    box-shadow: 0 4px 15px rgba(5,87,245,0.18);
    transition: box-shadow 0.3s, transform 0.2s;
}}
.stButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(5,87,245,0.28);
}}

.stSelectbox > div > div, .stRadio > div, .stCheckbox > div {{
    background: rgba(255,255,255,0.08);
    border-radius: 12px;
    color: {WHITE};
}}

hr {{
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, {CRYSTAL} 50%, transparent 100%);
    margin: 2rem 0;
}}

.stDataFrame, .dataframe {{
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    color: {WHITE};
}}

h1, h2, h3 {{
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    background: linear-gradient(135deg, {CRYSTAL} 0%, {DIGITAL_AZURE} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
</style>
""", unsafe_allow_html=True)

# --- Header with Logo ---
st.markdown(f'<div style="text-align:center; margin-bottom: 1.5rem;"><img src="{LOGO_URL}" alt="Entropy Advisors Logo" style="height:80px;"/></div>', unsafe_allow_html=True)

# --- Sidebar Logo ---
with st.sidebar:
    st.markdown(f'<div style="text-align:center; margin-bottom: 1.5rem;"><img src="{LOGO_URL}" alt="Entropy Advisors Logo" style="height:60px;"/></div>', unsafe_allow_html=True)

# --- Main Background Gradient ---
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(135deg, #030D1C 0%, #0557F5 70%, #9ECFF2 100%) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Modern CSS Styling ---
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global Styles */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Main Container */
.main .block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    border-right: 1px solid rgba(255,255,255,0.1);
}

[data-testid="stSidebar"] .sidebar-content {
    background: transparent;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #5a6fd8 0%, #6a4190 100%);
}

/* Headers */
h1, h2, h3 {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Cards */
.stMetric {
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.stMetric:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.15);
}

/* Expander Styling */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    margin-bottom: 8px;
    transition: all 0.3s ease;
}

.streamlit-expanderHeader:hover {
    background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.08) 100%);
    transform: translateX(4px);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 25px;
    color: white;
    font-weight: 600;
    padding: 0.5rem 1.5rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

/* Selectbox Styling */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 12px;
    backdrop-filter: blur(10px);
}

/* Radio Buttons */
.stRadio > div {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 0.5rem;
}

/* Checkbox */
.stCheckbox > div {
    background: rgba(255,255,255,0.05);
    border-radius: 8px;
    padding: 0.5rem;
}

/* Progress Bar */
.custom-progress {
    background: linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border-radius: 15px;
    overflow: hidden;
    height: 12px;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
}

.custom-progress-fill {
    height: 100%;
    border-radius: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

/* Dark Mode Overrides */
[data-testid="stSidebar"] .dark-mode {
    background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%);
}

/* Welcome Modal */
.welcome-modal {
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 2rem;
    backdrop-filter: blur(20px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}

/* Divider */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, rgba(102, 126, 234, 0.3) 50%, transparent 100%);
    margin: 2rem 0;
}

/* Data Table */
.dataframe {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    overflow: hidden;
}

/* Chart Container */
[data-testid="stChart"] {
    background: rgba(255,255,255,0.05);
    border-radius: 16px;
    padding: 1rem;
    border: 1px solid rgba(255,255,255,0.1);
}

/* Responsive Design */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem;
    }
    
    .stMetric {
        margin-bottom: 1rem;
    }
}

/* Loading Animation */
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.loading {
    animation: pulse 2s infinite;
}

/* Custom Metric Cards */
.metric-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(0,0,0,0.15);
}

.metric-icon {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    display: block;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #667eea;
    margin-bottom: 0.25rem;
}

.metric-label {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.7);
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# --- Welcome Animation ---
if "hide_modal" not in st.session_state:
    st.session_state.hide_modal = False
if not st.session_state.hide_modal:
    with st.container():
        st.markdown('<div class="welcome-modal">', unsafe_allow_html=True)
        lottie_animation = load_lottie("https://assets3.lottiefiles.com/packages/lf20_2kscqf.json")
        if lottie_animation:
            st_lottie(lottie_animation, height=200)
        else:
            st.markdown('<div style="text-align: center; font-size: 4rem;">🎉</div>', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; margin-bottom: 1rem;'>🚀 Welcome to Arbitrum Governance</h2><p style='text-align:center; color: rgba(255,255,255,0.8);'>Explore the future of decentralized governance with real-time data and insights.</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("✨ Get Started", use_container_width=True):
                st.session_state.hide_modal = True
        st.markdown('</div>', unsafe_allow_html=True)

# --- Dark Mode Toggle ---
dark_mode = st.sidebar.toggle("🌓 Dark Mode", value=True)

# Apply theme based on toggle
if dark_mode:
    st.markdown("""
    <style>
    /* Dark Mode Styles */
    .main {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%);
        color: #ffffff;
    }
    
    /* Dark mode text colors */
    .metric-value {
        color: #667eea !important;
    }
    
    .metric-label {
        color: rgba(255,255,255,0.7) !important;
    }
    
    /* Dark mode cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Dark mode progress bars */
    .custom-progress {
        background: linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    }
    
    /* Dark mode expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        color: #ffffff;
    }
    
    /* Dark mode sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        color: #ffffff;
    }
    
    /* Dark mode form elements */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        color: #ffffff;
    }
    
    .stRadio > div {
        background: rgba(255,255,255,0.05);
        color: #ffffff;
    }
    
    .stCheckbox > div {
        background: rgba(255,255,255,0.05);
        color: #ffffff;
    }
    
    /* Dark mode charts */
    [data-testid="stChart"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Dark mode data table */
    .dataframe {
        background: rgba(255,255,255,0.05);
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] * {
        color: #fff !important;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stRadio label, [data-testid="stSidebar"] .stCheckbox label {
        color: #fff !important;
    }
    [data-testid="stSidebar"] .stSelectbox, [data-testid="stSidebar"] .stRadio, [data-testid="stSidebar"] .stCheckbox {
        color: #fff !important;
    }
    [data-testid="stSidebar"] .st-bb, [data-testid="stSidebar"] .st-c3, [data-testid="stSidebar"] .st-c4 {
        color: #fff !important;
    }
    [data-testid="stSidebar"] .st-bb:disabled, [data-testid="stSidebar"] .st-c3:disabled, [data-testid="stSidebar"] .st-c4:disabled {
        color: #bbb !important;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    /* Light Mode Styles */
    .main {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        color: #333333;
    }
    
    /* Light mode text colors */
    .metric-value {
        color: #667eea !important;
    }
    
    .metric-label {
        color: rgba(0,0,0,0.7) !important;
    }
    
    /* Light mode cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.8) 100%);
        border: 1px solid rgba(0,0,0,0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    /* Light mode progress bars */
    .custom-progress {
        background: linear-gradient(90deg, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.05) 100%);
    }
    
    /* Light mode expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.8) 100%);
        border: 1px solid rgba(0,0,0,0.1);
        color: #333333;
    }
    
    /* Light mode sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
        color: #333333;
        border-right: 1px solid rgba(0,0,0,0.1);
    }
    
    /* Light mode form elements */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.9);
        border: 1px solid rgba(0,0,0,0.2);
        color: #333333;
    }
    
    .stRadio > div {
        background: rgba(255,255,255,0.8);
        color: #333333;
    }
    
    .stCheckbox > div {
        background: rgba(255,255,255,0.8);
        color: #333333;
    }
    
    /* Light mode charts */
    [data-testid="stChart"] {
        background: rgba(255,255,255,0.8);
        border: 1px solid rgba(0,0,0,0.1);
    }
    
    /* Light mode data table */
    .dataframe {
        background: rgba(255,255,255,0.8);
        color: #333333;
    }
    
    /* Light mode buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Light mode headers */
    h1, h2, h3 {
        color: #333333 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    [data-testid="stSidebar"] * {
        color: #222 !important;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stRadio label, [data-testid="stSidebar"] .stCheckbox label {
        color: #222 !important;
    }
    [data-testid="stSidebar"] .stSelectbox, [data-testid="stSidebar"] .stRadio, [data-testid="stSidebar"] .stCheckbox {
        color: #222 !important;
    }
    [data-testid="stSidebar"] .st-bb, [data-testid="stSidebar"] .st-c3, [data-testid="stSidebar"] .st-c4 {
        color: #222 !important;
    }
    [data-testid="stSidebar"] .st-bb:disabled, [data-testid="stSidebar"] .st-c3:disabled, [data-testid="stSidebar"] .st-c4:disabled {
        color: #888 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Load Data ---
st.markdown("<h1 style='text-align: center; margin-bottom: 0.5rem;'>🗳️ Arbitrum DAO Governance</h1>", unsafe_allow_html=True)
caption_color = "rgba(255,255,255,0.7)" if dark_mode else "rgba(0,0,0,0.7)"
st.markdown(f"<p style='text-align: center; color: {caption_color}; margin-bottom: 2rem;'>Live from Dune Analytics | Query 4628058</p>", unsafe_allow_html=True)

with st.spinner("🔄 Loading governance data..."):
    df = run_dune_query(QUERY_ID)

# --- Enhanced Sidebar ---
with st.sidebar:
    st.markdown("### 🔍 <span style='color:#9ECFF2'>Filter & Sort</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**🎯 Proposal Outcome**")
    outcome = st.selectbox("", options=["All"] + sorted(df["proposal_outcome_label"].dropna().unique()), label_visibility="collapsed")
    st.markdown("**🎭 Proposal Theme**")
    theme = st.selectbox("", options=["All"] + sorted(df["proposal_theme"].dropna().unique()), label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**📊 Sort Options**")
    sort_by = st.selectbox("Sort By", options=["support_rate", "voters", "vote_participation", "proposal_number"], 
                          format_func=lambda x: {"support_rate": "💙 Support Rate", "voters": "👥 Voters", 
                                                "vote_participation": "🗳 Participation", "proposal_number": "🔢 Proposal Number"}.get(x, x))
    sort_order = st.radio("Sort Order", options=["Descending", "Ascending"], horizontal=True)
    st.markdown("---")
    high_support_only = st.checkbox("✅ Show only proposals with > 50% support")

# --- Data Filtering ---
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

# --- Enhanced Metrics Cards ---
st.markdown("### 📊 Governance Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <span class="metric-icon">🧾</span>
        <div class="metric-value">{len(df):,}</div>
        <div class="metric-label">Total Proposals</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <span class="metric-icon">👥</span>
        <div class="metric-value">{df['voters'].mean():,.0f}</div>
        <div class="metric-label">Avg. Voters</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_support_raw = df["support_rate"].astype(float).mean()
    avg_support = avg_support_raw * 100 if avg_support_raw <= 1 else avg_support_raw
    st.markdown(f"""
    <div class="metric-card">
        <span class="metric-icon">💙</span>
        <div class="metric-value">{avg_support:.1f}%</div>
        <div class="metric-label">Avg. Support Rate</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    passed_count = len(df[df["proposal_outcome_label"] == "Passed"])
    st.markdown(f"""
    <div class="metric-card">
        <span class="metric-icon">✅</span>
        <div class="metric-value">{passed_count}</div>
        <div class="metric-label">Passed Proposals</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- Enhanced Proposal Display ---
st.markdown("### 📋 Proposal Details")
for _, row in df.iterrows():
    support_rate_display = float(row['support_rate']) * 100 if float(row['support_rate']) <= 1 else float(row['support_rate'])
    st.markdown('<div class="metric-card" style="margin-bottom: 2rem;">', unsafe_allow_html=True)
    with st.expander(f"📝 {row['proposal_title']} ({support_rate_display:.1f}% support)"):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**👥 Voters:** {row['voters']:,}")
            st.markdown(f"**🎭 Theme:** {row['proposal_theme']}")
            proposal_tally = str(row.get('proposal_tally', ''))
            match = re.search(r'href=[\'"]([^\'"]+)[\'"]', proposal_tally)
            if match:
                url = match.group(1)
                st.markdown(f"[Tally]({url})")
            elif proposal_tally.startswith('http'):
                st.markdown(f"[Tally]({proposal_tally})")
            elif proposal_tally:
                st.markdown(f"**Tally:** {proposal_tally}")
        with col2:
            st.markdown(render_outcome_label(row['proposal_outcome_label']), unsafe_allow_html=True)
        support_rate_decimal = float(row["support_rate"]) if float(row["support_rate"]) <= 1 else float(row["support_rate"]) / 100
        progress = support_rate_decimal
        bar_color = f"linear-gradient(90deg, {DIGITAL_AZURE}, #2ecc71)" if progress < 0.5 else f"linear-gradient(90deg, #2ecc71, {CRYSTAL})"
        st.markdown(f"""
        <div style="margin: 1rem 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="font-weight: 600; color: {CRYSTAL};">Support Rate</span>
                <span style="font-weight: 600; color: {DIGITAL_AZURE};">{support_rate_display:.1f}%</span>
            </div>
            <div class="custom-progress">
                <div class="custom-progress-fill" style="background: {bar_color}; width: {progress*100:.1f}%; transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# --- Enhanced Charts ---
st.markdown("### 📈 Analytics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**📊 Top Proposals by Voter Participation**")
    try:
        df["vote_participation"] = df["vote_participation"].astype(float)
        top_participation = df.sort_values(by="vote_participation", ascending=False).head(8)
        st.bar_chart(top_participation.set_index("proposal_title")["vote_participation"])
    except:
        st.warning("Unable to display participation chart.")

with col2:
    st.markdown("**💙 Support Rate Distribution**")
    try:
        support_rates = df["support_rate"].astype(float)
        support_rates = support_rates * 100 if support_rates.max() <= 1 else support_rates
        
        # Create bins for distribution
        bins = [0, 25, 50, 75, 100]
        labels = ['0-25%', '25-50%', '50-75%', '75-100%']
        support_rates_binned = pd.cut(support_rates, bins=bins, labels=labels, include_lowest=True)
        distribution = support_rates_binned.value_counts().sort_index()
        
        st.bar_chart(distribution)
    except:
        st.warning("Unable to display support rate distribution.")

# --- Raw Data Section ---
with st.expander("📋 Raw Data Table"):
    st.dataframe(df, use_container_width=True)

# --- Footer ---
st.markdown("---")
footer_color = "rgba(255,255,255,0.6)" if dark_mode else "rgba(0,0,0,0.6)"
st.markdown(f"""
<div style="text-align: center; padding: 2rem 0; color: {footer_color};">
    <p>Made with ❤️ by Entropy Advisors | Powered by Dune Analytics</p>
    <p style="font-size: 0.8rem;">Real-time Arbitrum DAO governance data and insights</p>
</div>
""", unsafe_allow_html=True)
