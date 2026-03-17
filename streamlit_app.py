# streamlit_app.py
# =================
# Web interface for Drug Launch Intelligence Agent
# Run with: streamlit run streamlit_app.py

import streamlit as st
from agent_graph import run_launch_intelligence

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Drug Launch Intelligence",
    page_icon="🚀",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        padding: 1rem 0 0.5rem 0;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 1.5rem;
    }
    .agent-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        font-size: 0.85rem;
    }
    .readiness-high {
        background: #f0fdf4;
        border: 2px solid #86efac;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 600;
        color: #166534;
    }
    .readiness-medium {
        background: #fefce8;
        border: 2px solid #fde047;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 600;
        color: #854d0e;
    }
    .readiness-low {
        background: #fef2f2;
        border: 2px solid #fca5a5;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 600;
        color: #991b1b;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h2 style="margin:0; color:#1e293b;">🚀 Drug Launch Intelligence Agent</h2>
    <p style="margin:0.25rem 0 0; color:#64748b; font-size:0.9rem;">
        Multi-agent AI system — 4 specialist agents analyse competitive landscape, 
        clinical evidence, KOLs, and market intelligence in parallel
    </p>
</div>
""", unsafe_allow_html=True)

# ── Input section ──────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    drug_name = st.text_input(
        "Drug Name",
        placeholder="e.g. ivonescimab",
        help="Enter the generic name of the drug"
    )

with col2:
    indication = st.text_input(
        "Indication / Therapeutic Area",
        placeholder="e.g. NSCLC",
        help="Enter the disease or therapeutic area"
    )

# ── Agent status display ───────────────────────────────────────────
st.markdown("""
**4 AI agents will run automatically:**
""")

agent_col1, agent_col2, agent_col3, agent_col4 = st.columns(4)
with agent_col1:
    st.markdown("""
    <div class="agent-card">
        🔍 <strong>Competitive Agent</strong><br>
        ClinicalTrials.gov
    </div>
    """, unsafe_allow_html=True)
with agent_col2:
    st.markdown("""
    <div class="agent-card">
        📚 <strong>Evidence Agent</strong><br>
        PubMed literature
    </div>
    """, unsafe_allow_html=True)
with agent_col3:
    st.markdown("""
    <div class="agent-card">
        👥 <strong>KOL Agent</strong><br>
        NPI Registry
    </div>
    """, unsafe_allow_html=True)
with agent_col4:
    st.markdown("""
    <div class="agent-card">
        📰 <strong>News Agent</strong><br>
        Tavily web search
    </div>
    """, unsafe_allow_html=True)

# ── Generate button ────────────────────────────────────────────────
generate = st.button(
    "🚀 Generate Launch Intelligence Brief",
    type="primary",
    use_container_width=True
)

# ── Results ────────────────────────────────────────────────────────
if generate:
    if not drug_name or not indication:
        st.error("Please enter both a drug name and indication.")
        st.stop()
    
    # Progress tracking
    progress = st.progress(0)
    status = st.empty()
    
    status.text("🔍 Running Competitive Landscape Agent...")
    progress.progress(10)
    
    with st.spinner(f"Running 4 agents for {drug_name} in {indication}... This takes 30-60 seconds."):
        result = run_launch_intelligence(drug_name, indication)
    
    progress.progress(100)
    status.text("✅ All agents complete — brief ready!")
    
    st.divider()
    
    # ── Agent status ───────────────────────────────────────────────
    st.subheader("📊 Agent Pipeline Status")
    
    status_log = result.get("status_log", [])
    error_log = result.get("error_log", [])
    
    for log in status_log:
        st.caption(log)
    
    if error_log:
        for error in error_log:
            st.warning(error)
    
    st.divider()
    
    # ── Launch readiness ───────────────────────────────────────────
    brief = result.get("launch_brief", {})
    readiness = brief.get("launch_readiness", "MEDIUM")
    
    st.subheader("🎯 Launch Readiness Rating")
    
    if readiness == "HIGH":
        st.markdown("""
        <div class="readiness-high">
            🟢 HIGH — Ready to launch
        </div>
        """, unsafe_allow_html=True)
    elif readiness == "LOW":
        st.markdown("""
        <div class="readiness-low">
            🔴 LOW — Significant preparation needed
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="readiness-medium">
            🟡 MEDIUM — Launch with targeted gaps to address
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ── Summary metrics ────────────────────────────────────────────
    st.subheader("📊 Intelligence Summary")
    
    m1, m2, m3, m4 = st.columns(4)
    
    competitive_data = result.get("competitive_data", "")
    evidence_data = result.get("evidence_data", "")
    kol_data = result.get("kol_data", "")
    news_data = result.get("news_data", "")
    
    # Extract key numbers
    comp_trials = competitive_data.count("NCT") if competitive_data else 0
    evidence_score = "Moderate"
    if "Strong" in evidence_data:
        evidence_score = "Strong"
    elif "Limited" in evidence_data:
        evidence_score = "Limited"
    
    kol_count = kol_data.count("Dr.") if kol_data else 0
    news_count = news_data.count("Source:") if news_data else 0
    
    m1.metric("Competitor Trials", comp_trials)
    m2.metric("Evidence Strength", evidence_score)
    m3.metric("KOLs Identified", kol_count)
    m4.metric("News Articles", news_count)
    
    st.divider()
    
    # ── Agent outputs ──────────────────────────────────────────────
    st.subheader("🔍 Agent Intelligence Outputs")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏆 Competitive", "📚 Evidence", "👥 KOLs", "📰 Market News"
    ])
    
    with tab1:
        st.text(competitive_data if competitive_data else "No data")
    
    with tab2:
        st.text(evidence_data if evidence_data else "No data")
    
    with tab3:
        st.text(kol_data if kol_data else "No data")
    
    with tab4:
        st.text(news_data if news_data else "No data")
    
    st.divider()
    
    # ── Full launch brief ──────────────────────────────────────────
    st.subheader("📋 Full Launch Intelligence Brief")
    
    if brief.get("status") == "placeholder":
        st.warning("⚠️ Showing placeholder brief. Add ANTHROPIC_API_KEY to .env for real Claude AI analysis.")
    
    st.markdown(brief.get("brief", "No brief generated"))
    
    st.divider()
    
    # ── Download ───────────────────────────────────────────────────
    st.subheader("📥 Download Brief")
    
    full_report = f"""DRUG LAUNCH INTELLIGENCE BRIEF
Drug: {drug_name} | Indication: {indication}
{'='*60}

LAUNCH READINESS: {readiness}

{'='*60}
COMPETITIVE LANDSCAPE
{'='*60}
{competitive_data}

{'='*60}
CLINICAL EVIDENCE
{'='*60}
{evidence_data}

{'='*60}
KOL LANDSCAPE
{'='*60}
{kol_data}

{'='*60}
MARKET INTELLIGENCE
{'='*60}
{news_data}

{'='*60}
FULL LAUNCH BRIEF
{'='*60}
{brief.get('brief', '')}

Generated by Drug Launch Intelligence Agent
github.com/LifeSciForge
"""
    
    st.download_button(
        label="📥 Download Full Intelligence Brief",
        data=full_report,
        file_name=f"launch_brief_{drug_name}_{indication}.txt",
        mime="text/plain",
        use_container_width=True
    )

# ── Footer ─────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Drug Launch Intelligence Agent · "
    "Multi-agent system powered by LangGraph · "
    "Data: ClinicalTrials.gov + PubMed + NPI Registry + Tavily · "
    "AI: Claude Haiku · "
    "Built by Pranjal Das · github.com/LifeSciForge"
)