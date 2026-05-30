import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import matplotlib.patheffects as path_effects
import joblib
import numpy as np
from optimizer.strategy_dp import optimize_strategy
from optimizer.simulate_strategy import simulate_strategy
from optimizer.track_config import TRACK_CONFIG

# Page config
st.set_page_config(
    "F1 Strategy Platform",
    layout="wide",
    page_icon="🏁",
    initial_sidebar_state="expanded"
)

# Professional F1 Design System
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
    :root {
        --f1-red: #E10600;
        --dark-bg: #0A0A0A;
        --card-bg: #111112;
        --card-hover: #151516;
        --text-primary: #FFFFFF;
        --text-secondary: #8F8F8F;
        --text-tertiary: #5A5A5A;
        --accent-gold: #FFD700;
        --border-subtle: rgba(255, 255, 255, 0.08);
        --border-hover: rgba(225, 6, 0, 0.4);
        --glow-red: rgba(225, 6, 0, 0.12);
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif !important;
        box-sizing: border-box;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    html {
        scroll-behavior: smooth;
    }
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background: var(--dark-bg) !important;
        color: var(--text-primary) !important;
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px !important;
    }
    
    /* ============================================
       HERO HEADER
    ============================================ */
    .hero-header {
        position: relative;
        padding: 6rem 2rem 5rem 2rem;
        margin: -1rem -1rem 4rem -1rem;
        text-align: center;
        background: radial-gradient(ellipse at top, var(--glow-red) 0%, transparent 50%),
                    linear-gradient(180deg, var(--card-bg) 0%, var(--dark-bg) 100%);
        border-bottom: 1px solid var(--border-subtle);
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: -60%;
        left: 50%;
        transform: translateX(-50%);
        width: 1000px;
        height: 1000px;
        background: radial-gradient(circle, var(--glow-red) 0%, transparent 65%);
        animation: float 10s ease-in-out infinite;
        pointer-events: none;
        opacity: 0.4;
    }
    
    @keyframes float {
        0%, 100% { transform: translateX(-50%) translateY(0) scale(1); }
        50% { transform: translateX(-50%) translateY(-40px) scale(1.05); }
    }
    
    .hero-header h1 {
        font-size: 4.5rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.04em !important;
        margin: 0 0 1.5rem 0 !important;
        background: linear-gradient(135deg, #FFFFFF 0%, var(--f1-red) 50%, var(--accent-gold) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        position: relative;
        z-index: 1;
        line-height: 1.05 !important;
    }
    
    .hero-header .tagline {
        font-size: 1.15rem !important;
        font-weight: 400 !important;
        color: var(--text-secondary) !important;
        margin: 0 auto 2.5rem auto !important;
        max-width: 700px;
        position: relative;
        z-index: 1;
        line-height: 1.7;
    }
    
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1.5rem;
        background: rgba(225, 6, 0, 0.08);
        border: 1px solid rgba(225, 6, 0, 0.3);
        border-radius: 100px;
        font-size: 0.9rem;
        font-weight: 500;
        color: var(--text-secondary);
        position: relative;
        z-index: 1;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background: var(--f1-red);
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }
    
    .status-text {
        color: var(--f1-red);
        font-weight: 600;
    }
    
    /* ============================================
       METRICS GRID
    ============================================ */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin-bottom: 4rem;
    }
    
    .metric-card {
        background: var(--card-bg);
        padding: 2.5rem 2rem;
        border-radius: 24px;
        border: 1px solid var(--border-subtle);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--f1-red), var(--accent-gold), transparent);
        opacity: 0;
        transition: opacity 0.4s;
    }
    
    .metric-card:hover {
        transform: translateY(-6px);
        border-color: var(--border-hover);
        background: var(--card-hover);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-tertiary);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-family: 'Space Grotesk', monospace !important;
        font-size: 3.5rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1;
        margin-bottom: 0.75rem;
    }
    
    .metric-unit {
        font-size: 0.95rem;
        font-weight: 500;
        color: var(--text-secondary);
        letter-spacing: 0.02em;
    }
    
    /* ============================================
       SECTION HEADERS
    ============================================ */
    h3 {
        font-size: 1.85rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
        margin: 4rem 0 2.5rem 0 !important;
        padding: 0 !important;
        border: none !important;
        position: relative;
    }
    
    h3::after {
        content: '';
        position: absolute;
        bottom: -0.75rem;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, var(--f1-red), transparent);
    }
    
    /* ============================================
       PIT STRATEGY CARDS
    ============================================ */
    .pit-strategy-grid {
        display: grid;
        gap: 1rem;
        margin-bottom: 3rem;
    }
    
    .pit-card {
        background: var(--card-bg);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        border: 1px solid var(--border-subtle);
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .pit-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, var(--f1-red), var(--accent-gold));
        opacity: 0;
        transition: opacity 0.4s;
    }
    
    .pit-card:hover {
        border-color: var(--border-hover);
        transform: translateX(12px);
        background: var(--card-hover);
    }
    
    .pit-card:hover::before {
        opacity: 1;
    }
    
    .pit-info {
        display: flex;
        align-items: center;
        gap: 3rem;
    }
    
    .pit-lap-number {
        font-family: 'Space Grotesk', monospace !important;
        font-size: 2.25rem;
        font-weight: 700;
        color: var(--accent-gold);
        min-width: 100px;
    }
    
    .pit-divider {
        width: 1px;
        height: 40px;
        background: var(--border-subtle);
    }
    
    .pit-label {
        font-size: 0.95rem;
        color: var(--text-secondary);
        font-weight: 400;
        letter-spacing: 0.01em;
    }
    
    .tyre-badge {
        padding: 0.85rem 2.5rem;
        border-radius: 100px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
    }
    
    .pit-card:hover .tyre-badge {
        transform: scale(1.08);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    
    .tyre-soft {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000000;
    }
    
    .tyre-medium {
        background: linear-gradient(135deg, #FF9500 0%, #FF6B00 100%);
        color: #000000;
    }
    
    .tyre-hard {
        background: linear-gradient(135deg, #707070 0%, #3D3D3D 100%);
        color: #FFFFFF;
    }
    
    /* ============================================
       TYRE INFO CARDS
    ============================================ */
    .tyre-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin-bottom: 4rem;
    }
    
    .tyre-info-card {
        background: var(--card-bg);
        padding: 2.5rem;
        border-radius: 24px;
        border: 1px solid var(--border-subtle);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
    }
    
    .tyre-info-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        border-radius: 24px 24px 0 0;
        opacity: 0;
        transition: opacity 0.4s;
    }
    
    .tyre-info-card:hover {
        transform: translateY(-6px);
        border-color: var(--border-hover);
        background: var(--card-hover);
    }
    
    .tyre-title {
        font-size: 1.35rem;
        font-weight: 700;
        margin-bottom: 1rem;
        letter-spacing: -0.01em;
    }
    
    .tyre-specs {
        font-size: 0.85rem;
        color: var(--text-secondary);
        padding: 1rem 0;
        margin: 1rem 0;
        border-top: 1px solid var(--border-subtle);
        border-bottom: 1px solid var(--border-subtle);
        line-height: 1.7;
        font-weight: 500;
    }
    
    .tyre-description {
        font-size: 0.95rem;
        color: var(--text-secondary);
        line-height: 1.8;
        font-weight: 400;
    }
    
    /* ============================================
       SIDEBAR - Complete Redesign
    ============================================ */
    [data-testid="stSidebar"] {
        background: var(--card-bg) !important;
        border-right: 1px solid var(--border-subtle);
        padding: 2rem 1.5rem !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem !important;
    }
    
    [data-testid="stSidebar"] h3 {
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        color: var(--text-tertiary) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.15em !important;
        margin: 0 0 2.5rem 0 !important;
        padding: 0 0 1rem 0 !important;
        border-bottom: 1px solid var(--border-subtle) !important;
    }
    
    [data-testid="stSidebar"] h3::after {
        display: none;
    }
    
    /* Remove all default Streamlit labels in sidebar */
    [data-testid="stSidebar"] label {
        display: none !important;
    }
    
    /* Sidebar input containers */
    [data-testid="stSidebar"] [data-testid="stSelectbox"],
    [data-testid="stSidebar"] [data-testid="stNumberInput"],
    [data-testid="stSidebar"] [data-testid="stSlider"] {
        margin-bottom: 2.5rem !important;
    }
    
    .sidebar-section {
        margin-bottom: 2.5rem;
    }
    
    .sidebar-label {
        font-size: 0.7rem;
        font-weight: 700;
        color: var(--f1-red);
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 0.75rem;
        display: block;
        font-family: 'Inter', sans-serif !important;
    }
    
    .sidebar-divider {
        height: 1px;
        background: var(--border-subtle);
        margin: 2.5rem 0;
    }
    
    /* Enhanced input styling for sidebar */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div,
    [data-testid="stSidebar"] [data-testid="stNumberInput"] > div {
        background: var(--dark-bg) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        min-height: 42px !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div:hover,
    [data-testid="stSidebar"] [data-testid="stNumberInput"] > div:hover {
        border-color: rgba(225, 6, 0, 0.4) !important;
        background: rgba(225, 6, 0, 0.03) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div:focus-within,
    [data-testid="stSidebar"] [data-testid="stNumberInput"] > div:focus-within {
        border-color: var(--f1-red) !important;
        box-shadow: 0 0 0 3px rgba(225, 6, 0, 0.1);
        background: var(--dark-bg) !important;
    }
    
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] select {
        background: transparent !important;
        color: var(--text-primary) !important;
        border: none !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Slider styling */
    [data-testid="stSidebar"] [data-testid="stSlider"] {
        padding: 0.5rem 0 1rem 0 !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="slider"] {
        margin-top: 0.5rem;
    }
    
    /* Caption text in sidebar */
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: var(--text-tertiary) !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        margin-top: 0.5rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Button in sidebar - wider and properly sized */
    [data-testid="stSidebar"] .stButton {
        margin-top: 2rem !important;
    }
    
    [data-testid="stSidebar"] .stButton button {
        background: var(--f1-red) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 1rem 1.5rem !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.1em !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 20px rgba(225, 6, 0, 0.3) !important;
        text-transform: uppercase;
        width: 100% !important;
        white-space: nowrap !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(225, 6, 0, 0.5) !important;
        background: #FF1E00 !important;
    }
    
    [data-testid="stSidebar"] .stButton button:active {
        transform: translateY(0) !important;
    }
    
    /* ============================================
       INFO BADGE
    ============================================ */
    .info-badge {
        background: var(--card-bg);
        border: 1px solid var(--border-subtle);
        border-left: 3px solid var(--f1-red);
        border-radius: 18px;
        padding: 2.5rem;
        margin: 3rem 0;
        font-size: 1rem;
        line-height: 1.9;
        color: var(--text-secondary);
    }
    
    .info-badge b {
        color: var(--text-primary);
        font-weight: 700;
    }
    
    .highlight {
        color: var(--accent-gold);
        font-weight: 700;
    }
    
    .info-section {
        margin-bottom: 1.5rem;
    }
    
    .info-section:last-child {
        margin-bottom: 0;
    }
    
    /* ============================================
       CHART CONTAINER
    ============================================ */
    .chart-container {
        background: var(--card-bg);
        border: 1px solid var(--border-subtle);
        border-radius: 24px;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .stPlotlyChart {
        border-radius: 20px;
        overflow: hidden;
    }
    
    /* ============================================
       WELCOME SCREEN
    ============================================ */
    .welcome-container {
        text-align: center;
        padding: 8rem 3rem;
        margin: 4rem auto;
        max-width: 900px;
        background: radial-gradient(ellipse at center, var(--glow-red) 0%, transparent 70%);
    }
    
    .welcome-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 2rem;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #FFFFFF 0%, var(--f1-red) 50%, var(--accent-gold) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }
    
    .welcome-text {
        font-size: 1.15rem;
        color: var(--text-secondary);
        line-height: 1.8;
        margin-bottom: 4rem;
        max-width: 650px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 3rem;
        margin-top: 4rem;
    }
    
    .feature-item {
        text-align: center;
    }
    
    .feature-number {
        font-family: 'Space Grotesk', monospace !important;
        font-size: 3rem;
        font-weight: 700;
        color: var(--f1-red);
        margin-bottom: 1rem;
        line-height: 1;
    }
    
    .feature-label {
        font-size: 0.85rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    
    .feature-desc {
        font-size: 0.9rem;
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    /* ============================================
       RESPONSIVE
    ============================================ */
    @media (max-width: 768px) {
        .hero-header h1 {
            font-size: 2.75rem !important;
        }
        
        .metrics-grid,
        .tyre-grid,
        .feature-grid {
            grid-template-columns: 1fr;
        }
        
        .pit-info {
            gap: 1.5rem;
        }
    }
    
    /* ============================================
       SCROLLBAR
    ============================================ */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--dark-bg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--f1-red);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #FF1E00;
    }
    
    /* Selection */
    ::selection {
        background: var(--f1-red);
        color: #FFFFFF;
    }
    
    /* Caption */
    [data-testid="stCaptionContainer"] {
        color: var(--text-tertiary) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
    
    /* Remove default Streamlit padding */
    .element-container {
        margin: 0 !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# Load model
track_encoder = joblib.load("models/track_encoder.pkl")

# Hero Header
st.markdown("""
    <div class="hero-header">
        <h1>F1 Strategy Intelligence</h1>
        <p class="tagline">Advanced race optimization powered by machine learning. Unlock competitive advantage through data-driven pit strategy analysis and real-time telemetry insights.</p>
        <div class="status-indicator">
            <span class="status-dot"></span>
            <span class="status-text">LIVE</span>
            <span>ML Platform Active</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### Configuration")

with st.sidebar:
    # Circuit Selection
    st.markdown('<div class="sidebar-label">Circuit</div>', unsafe_allow_html=True)
    track = st.selectbox(
        "circuit_select",
        list(TRACK_CONFIG.keys()),
        label_visibility="collapsed"
    )
    
    track_info = TRACK_CONFIG.get(track, {})
    if isinstance(track_info, dict) and "length" in track_info:
        st.caption(f"{track_info.get('length', 'N/A')} km • {track_info.get('corners', 'N/A')} corners")
    
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    
    # Race Parameters
    st.markdown('<div class="sidebar-label">Race Distance</div>', unsafe_allow_html=True)
    laps = st.slider("laps_slider", 40, 75, 58, label_visibility="collapsed")
    
    st.markdown('<div class="sidebar-label">Track Temperature</div>', unsafe_allow_html=True)
    temp = st.slider("temp_slider", 20, 55, 42, label_visibility="collapsed")
    st.caption(f"{temp}°C")
    
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    
    # Starting Compound
    st.markdown('<div class="sidebar-label">Starting Compound</div>', unsafe_allow_html=True)
    start_tyre = st.selectbox(
        "tyre_select",
        ["Soft", "Medium", "Hard"],
        index=1,
        label_visibility="collapsed"
    )
    start_map = {"Soft": 0, "Medium": 1, "Hard": 2}
    
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    
    # Race Events
    st.markdown('<div class="sidebar-label">Safety Car Events</div>', unsafe_allow_html=True)
    
    col_vsc, col_sc = st.columns(2)
    with col_vsc:
        vsc = st.number_input("VSC (Lap)", 0, laps, 0, label_visibility="collapsed")
        st.caption("VSC")
    with col_sc:
        sc = st.number_input("SC (Lap)", 0, laps, 0, label_visibility="collapsed")
        st.caption("SC")

track_id = track_encoder.transform([track])[0]

events = {}
if vsc:
    events[vsc] = "VSC"
if sc:
    events[sc] = "SC"

# Main content
if st.sidebar.button("Analyze Strategy", use_container_width=True, key="optimize"):
    with st.spinner("Analyzing race conditions..."):
        total, plan = optimize_strategy(
            laps, temp, start_map[start_tyre], track, track_id, events
        )

        pit_laps, compounds = [], [start_map[start_tyre]]

        for p in plan:
            if p[0] == "pit":
                pit_laps.append(p[1])
                compounds.append(p[2])

        # Metrics
        st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Race Distance</div>
                    <div class="metric-value">{laps}</div>
                    <div class="metric-unit">Laps</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Optimal Time</div>
                    <div class="metric-value">{round(total/60, 1)}</div>
                    <div class="metric-unit">Minutes</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Track Temperature</div>
                    <div class="metric-value">{temp}°</div>
                    <div class="metric-unit">Celsius</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

        # F1 Race Intelligence Stats
        st.markdown("### Race Intelligence")
        
        st.markdown("""
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 4rem;">
                <div style="background: var(--card-bg); padding: 1.5rem; border-radius: 16px; border: 1px solid var(--border-subtle); text-align: center;">
                    <div style="font-family: 'Space Grotesk', monospace; font-size: 2rem; font-weight: 700; color: var(--f1-red); margin-bottom: 0.5rem;">{}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em;">Pit Stops</div>
                </div>
                <div style="background: var(--card-bg); padding: 1.5rem; border-radius: 16px; border: 1px solid var(--border-subtle); text-align: center;">
                    <div style="font-family: 'Space Grotesk', monospace; font-size: 2rem; font-weight: 700; color: var(--accent-gold); margin-bottom: 0.5rem;">{}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em;">Compounds</div>
                </div>
                <div style="background: var(--card-bg); padding: 1.5rem; border-radius: 16px; border: 1px solid var(--border-subtle); text-align: center;">
                    <div style="font-family: 'Space Grotesk', monospace; font-size: 2rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">{}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em;">Avg Stint</div>
                </div>
                <div style="background: var(--card-bg); padding: 1.5rem; border-radius: 16px; border: 1px solid var(--border-subtle); text-align: center;">
                    <div style="font-family: 'Space Grotesk', monospace; font-size: 2rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">{}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em;">Events</div>
                </div>
            </div>
        """.format(
            len(pit_laps),
            len(set(compounds)),
            f"{laps // (len(pit_laps) + 1)}L" if pit_laps else f"{laps}L",
            len(events)
        ), unsafe_allow_html=True)

        # Pit Strategy
        st.markdown("### Optimal Pit Strategy")
        
        st.markdown('<div class="pit-strategy-grid">', unsafe_allow_html=True)
        for i, p in enumerate(plan):
            if p[0] == "pit":
                tyre_name = ['Soft', 'Medium', 'Hard'][p[2]]
                tyre_class = f"tyre-{tyre_name.lower()}"
                
                st.markdown(f"""
                    <div class="pit-card">
                        <div class="pit-info">
                            <div class="pit-lap-number">LAP {p[1]}</div>
                            <div class="pit-divider"></div>
                            <div class="pit-label">Switch to compound</div>
                        </div>
                        <div class="tyre-badge {tyre_class}">{tyre_name}</div>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Tyre Info
        st.markdown("### Compound Specifications")
        
        st.markdown('<div class="tyre-grid">', unsafe_allow_html=True)
        
        cols = st.columns(3)
        
        tyre_data = {
            "Soft": {
                "color": "#FFD700",
                "specs": "Maximum Grip • Rapid Degradation • Peak Performance",
                "desc": "The C5 compound delivers ultimate grip and performance for qualifying sessions and short race stints. Engineered for maximum speed with strategic timing requirements for optimal deployment."
            },
            "Medium": {
                "color": "#FF8C00",
                "specs": "Balanced Performance • Moderate Wear • Strategic Versatility",
                "desc": "The C3 compound offers optimal balance between performance and durability. A versatile choice for extended race stints with predictable degradation characteristics and consistent performance windows."
            },
            "Hard": {
                "color": "#808080",
                "specs": "Maximum Durability • Minimal Wear • Extended Stints",
                "desc": "The C1 compound prioritizes longevity over peak performance. Designed for final race stints where consistency and track position management take precedence over raw pace."
            }
        }
        
        for idx, (compound, data) in enumerate(tyre_data.items()):
            with cols[idx]:
                st.markdown(f"""
                    <div class="tyre-info-card">
                        <div class="tyre-title" style="color: {data['color']};">{compound}</div>
                        <div class="tyre-specs">{data['specs']}</div>
                        <div class="tyre-description">{data['desc']}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Chart
        st.markdown("### Performance Telemetry Analysis")
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        optimized_curve = simulate_strategy(
            laps, temp, start_map[start_tyre],
            pit_laps, compounds, track, track_id, events
        )

        # SIMPLE BASELINE: One-stop at race midpoint, always to Hard compound
        baseline_pit_lap = laps // 2
        baseline_compounds = [start_map[start_tyre], 2]  # Start -> Hard
        
        fixed_curve = simulate_strategy(
            laps, temp, start_map[start_tyre],
            [baseline_pit_lap], baseline_compounds, track, track_id, events
        )

        # Professional chart
        fig, ax = plt.subplots(figsize=(16, 7.5), facecolor='#0A0A0A')
        ax.set_facecolor('#111112')

        laps_range = np.arange(len(optimized_curve))
        
        # Optimized strategy - THICK GOLD LINE
        ax.plot(laps_range, optimized_curve, 
                color='#FFD700', linewidth=6, 
                label='Optimized Strategy', 
                zorder=3,
                marker='o', markersize=7, markevery=5,
                markerfacecolor='#FFD700',
                markeredgecolor='#000000',
                markeredgewidth=3,
                alpha=1.0,
                linestyle='-')
        
        # Baseline strategy - THICK RED LINE
        ax.plot(laps_range, fixed_curve, 
                color='#E10600', linewidth=6,
                label='Baseline Strategy', 
                zorder=2,
                alpha=1.0,
                marker='s', markersize=6, markevery=5,
                markerfacecolor='#E10600',
                markeredgecolor='#000000',
                markeredgewidth=3,
                linestyle='-')
        
        # Event markers
        event_colors = {"VSC": "#00D2FF", "SC": "#FF1E1E"}
        for lap, e in events.items():
            ax.axvline(lap, linestyle=':', alpha=0.4, color=event_colors.get(e, '#666'), linewidth=2.5)
            ax.text(lap, ax.get_ylim()[1] * 0.95, e,
                   ha='center', fontsize=11,
                   color='#FFFFFF', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.6',
                            facecolor=event_colors.get(e, '#666'),
                            edgecolor='none',
                            alpha=0.9))

        # FORCE Y-AXIS TO SHOW BOTH LINES CLEARLY
        y_min_opt = optimized_curve.min()
        y_max_opt = optimized_curve.max()
        y_min_base = fixed_curve.min()
        y_max_base = fixed_curve.max()
        
        # Get absolute bounds
        y_absolute_min = min(y_min_opt, y_min_base)
        y_absolute_max = max(y_max_opt, y_max_base)
        y_total_range = y_absolute_max - y_absolute_min
        
        # ALWAYS add generous padding - 25% or minimum 100 seconds
        padding = max(y_total_range * 0.25, 100)
        
        ax.set_ylim(y_absolute_min - padding, y_absolute_max + padding)

        ax.set_xlabel('Lap Number', fontsize=13, color='#FFFFFF', fontweight='600', labelpad=14, family='Inter')
        ax.set_ylabel('Cumulative Time (seconds)', fontsize=13, color='#FFFFFF', fontweight='600', labelpad=14, family='Inter')
        ax.set_title(f'{track} — Race Strategy Comparison',
                    fontsize=17, color='#FFFFFF', fontweight='700', pad=24, family='Inter')
        
        legend = ax.legend(loc='upper left', fontsize=12,
                          framealpha=0.95,
                          edgecolor=(1, 1, 1, 0.1),
                          facecolor='#111112',
                          labelcolor='#FFFFFF',
                          frameon=True)
        
        ax.grid(True, alpha=0.08, color='#FFFFFF', linestyle='-', linewidth=1.2)
        ax.set_axisbelow(True)
        
        ax.tick_params(colors='#8F8F8F', labelsize=11, width=0, length=0)
        
        for spine in ax.spines.values():
            spine.set_edgecolor((1, 1, 1, 0.1))
            spine.set_linewidth(1)

        st.pyplot(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Summary
        time_diff = fixed_curve[-1] - optimized_curve[-1]
        improvement = (time_diff / fixed_curve[-1]) * 100 if fixed_curve[-1] > 0 else 0

        st.markdown(f"""
            <div class="info-badge">
                <div class="info-section">
                    <b>Performance Advantage Analysis</b><br/>
                    The optimized strategy delivers a <span class="highlight">{abs(time_diff):.2f} seconds ({abs(improvement):.2f}%)</span> performance advantage over conventional baseline strategy.
                </div>
                <div class="info-section">
                    <b>Baseline Approach</b><br/>
                    Simple 1-stop strategy with pit stop at lap {baseline_pit_lap} (race midpoint), switching to Hard compound
                </div>
                <div class="info-section">
                    <b>Optimized Approach</b><br/>
                    Machine learning-driven compound selection leveraging real-time track conditions, temperature data, and degradation modeling for maximum competitive advantage
                </div>
            </div>
        """, unsafe_allow_html=True)

else:
    # Welcome screen
    st.markdown("""
        <div class="welcome-container">
            <div class="welcome-title">Strategy Intelligence Platform</div>
            <div class="welcome-text">
                Configure race parameters through the sidebar controls and initiate strategic analysis to unlock optimal performance through advanced machine learning algorithms and real-time telemetry data processing.
            </div>
            <div class="feature-grid">
                <div class="feature-item">
                    <div class="feature-number">01</div>
                    <div class="feature-label">ML-Powered</div>
                    <div class="feature-desc">Real-time optimization using advanced machine learning models</div>
                </div>
                <div class="feature-item">
                    <div class="feature-number">02</div>
                    <div class="feature-label">Data-Driven</div>
                    <div class="feature-desc">Historical telemetry and performance insights</div>
                </div>
                <div class="feature-item">
                    <div class="feature-number">03</div>
                    <div class="feature-label">Strategic Edge</div>
                    <div class="feature-desc">Competitive advantage through intelligent analysis</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)