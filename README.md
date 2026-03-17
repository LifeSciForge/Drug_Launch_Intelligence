# 🚀 Drug Launch Intelligence Agent

AI-powered multi-agent system for pharmaceutical launch strategy.
Enter any drug and indication — 4 specialist AI agents run in parallel
to generate a comprehensive launch intelligence brief in 60 seconds.

---

## 🎯 What It Does

A pharma launch team manually assembling competitive intelligence,
clinical evidence, KOL mapping, and market access analysis spends
3-5 days across multiple data sources. This tool does it in 60 seconds.

**Enter drug + indication → 4 agents run simultaneously:**
- 🔍 Competitive Landscape Agent — searches ClinicalTrials.gov
- 📚 Clinical Evidence Agent — searches PubMed literature
- 👥 KOL Identification Agent — searches NPI Registry
- 📰 Market Intelligence Agent — searches live news via Tavily

**Synthesis Agent combines everything into:**
- Executive summary with launch readiness rating
- Competitive positioning table
- Evidence strength assessment
- KOL engagement strategy
- Market access and payer outlook
- Top 3 priorities before launch
- Downloadable intelligence brief

---

## 🏗️ Architecture — LangGraph Multi-Agent System
```
User Query
    ↓
Multi-Agent Orchestrator
    ↓
┌─────────────────────────────────────┐
│ Competitive  Evidence  KOL   News   │
│   Agent    + Agent  + Agent + Agent │
│ (sequential execution)              │
└─────────────────────────────────────┘
    ↓
Synthesis Agent (Claude AI)
    ↓
Launch Intelligence Brief
```

Full LangGraph implementation available in agent_graph_langgraph.py

---

## 🛠️ Built With

| Tool | Purpose |
|---|---|
| Python | Core language |
| LangGraph | Multi-agent orchestration architecture |
| LangChain | Agent framework |
| ClinicalTrials.gov API | Competitive trial landscape |
| PubMed / Biopython | Clinical evidence assessment |
| NPI Registry API | KOL identification |
| Tavily API | Market and news intelligence |
| Claude API (Anthropic) | Launch brief synthesis |
| Streamlit | Web interface |

---

## 📁 Project Structure
```
├── competitive_agent.py        # ClinicalTrials.gov competitor search
├── evidence_agent.py           # PubMed evidence assessment
├── kol_agent.py                # NPI Registry KOL identification
├── news_agent.py               # Tavily market intelligence
├── synthesis_agent.py          # Claude AI brief generation
├── agent_graph.py              # Multi-agent orchestrator
├── agent_graph_langgraph.py    # Full LangGraph implementation
├── streamlit_app.py            # Web interface
├── requirements.txt            # Python dependencies
└── .env.example                # API key template
```

---

## 🚀 Quick Start

**1. Clone the repo**
```bash
git clone https://github.com/LifeSciForge/Drug_Launch_Intelligence.git
cd Drug_Launch_Intelligence
```

**2. Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your API keys**
```bash
cp .env.example .env
# Edit .env and add your keys
```

**5. Run the app**
```bash
streamlit run streamlit_app.py
```

---

## 💡 Example Searches

| Drug | Indication | What You Get |
|---|---|---|
| ivonescimab | NSCLC | Pre-launch brief, PDUFA Nov 2026 |
| retatrutide | obesity | Phase 3 launch readiness |
| zilebesiran | hypertension | RNA interference launch strategy |
| tarlatamab | small cell lung cancer | BiTE antibody brief |

---

## 🎯 Target Users

- **Commercial teams** — launch strategy and competitive positioning
- **Medical Affairs** — KOL engagement and publication strategy
- **Market Access** — payer landscape and formulary strategy
- **CI analysts** — rapid competitive intelligence

---

## 🔑 API Keys Required

| Key | Source | Cost |
|---|---|---|
| ANTHROPIC_API_KEY | console.anthropic.com | Free trial available |
| TAVILY_API_KEY | tavily.com | Free tier — 1000/month |

App runs in placeholder mode without API keys —
all trial, literature, and KOL data still loads from live sources.

---

## 👤 Author

**Pranjal Das**
AI & Automation for Life Sciences
[github.com/LifeSciForge](https://github.com/LifeSciForge)

---

*Data sources: ClinicalTrials.gov · PubMed · NPI Registry · Tavily*
*All data is 100% open and publicly available*