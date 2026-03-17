# agent_graph.py
# ===============
# LangGraph Orchestrator — runs all 4 agents
# and coordinates the full launch intelligence pipeline
# This is the core multi-agent architecture

import operator
from typing import Dict, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END

from competitive_agent import get_competitive_landscape, format_competitive_output
from evidence_agent import assess_evidence_strength, format_evidence_output
from kol_agent import identify_kols, format_kol_output
from news_agent import get_market_intelligence, format_news_output
from synthesis_agent import synthesise_launch_brief

# ── State Definition ──────────────────────────────────────────────
# State is the shared memory all agents read from and write to
# Think of it as a shared Google Doc for the agent team

class LaunchIntelligenceState(TypedDict):
    """
    Shared state that flows through all agents.
    Each agent reads what it needs and adds its output.
    """
    # Input
    drug_name: str
    indication: str
    
    # Agent outputs — filled in as agents complete
    competitive_data: str
    evidence_data: str
    kol_data: str
    news_data: str
    
    # Final output
    launch_brief: Dict
    
    # Status tracking
    status_log: Annotated[List[str], operator.add]
    error_log: Annotated[List[str], operator.add]


# ── Agent Node Functions ──────────────────────────────────────────
# Each function is one node in the graph
# They read from state, do their work, write back to state

def run_competitive_agent(state: LaunchIntelligenceState) -> Dict:
    """Node 1 — Run competitive landscape analysis."""
    
    print("\n[Graph] Running Competitive Agent...")
    
    try:
        result = get_competitive_landscape(
            state["drug_name"],
            state["indication"]
        )
        formatted = format_competitive_output(result)
        
        return {
            "competitive_data": formatted,
            "status_log": ["✅ Competitive Agent complete"]
        }
    except Exception as e:
        return {
            "competitive_data": f"Competitive analysis unavailable: {str(e)}",
            "error_log": [f"Competitive Agent error: {str(e)}"]
        }


def run_evidence_agent(state: LaunchIntelligenceState) -> Dict:
    """Node 2 — Run clinical evidence assessment."""
    
    print("[Graph] Running Evidence Agent...")
    
    try:
        result = assess_evidence_strength(
            state["drug_name"],
            state["indication"]
        )
        formatted = format_evidence_output(result)
        
        return {
            "evidence_data": formatted,
            "status_log": ["✅ Evidence Agent complete"]
        }
    except Exception as e:
        return {
            "evidence_data": f"Evidence assessment unavailable: {str(e)}",
            "error_log": [f"Evidence Agent error: {str(e)}"]
        }


def run_kol_agent(state: LaunchIntelligenceState) -> Dict:
    """Node 3 — Run KOL identification."""
    
    print("[Graph] Running KOL Agent...")
    
    try:
        result = identify_kols(
            state["drug_name"],
            state["indication"]
        )
        formatted = format_kol_output(result)
        
        return {
            "kol_data": formatted,
            "status_log": ["✅ KOL Agent complete"]
        }
    except Exception as e:
        return {
            "kol_data": f"KOL identification unavailable: {str(e)}",
            "error_log": [f"KOL Agent error: {str(e)}"]
        }


def run_news_agent(state: LaunchIntelligenceState) -> Dict:
    """Node 4 — Run market intelligence search."""
    
    print("[Graph] Running News Agent...")
    
    try:
        result = get_market_intelligence(
            state["drug_name"],
            state["indication"]
        )
        formatted = format_news_output(result)
        
        return {
            "news_data": formatted,
            "status_log": ["✅ News Agent complete"]
        }
    except Exception as e:
        return {
            "news_data": f"Market intelligence unavailable: {str(e)}",
            "error_log": [f"News Agent error: {str(e)}"]
        }


def run_synthesis_agent(state: LaunchIntelligenceState) -> Dict:
    """Node 5 — Synthesise all outputs into launch brief."""
    
    print("[Graph] Running Synthesis Agent...")
    
    try:
        result = synthesise_launch_brief(
            drug_name=state["drug_name"],
            indication=state["indication"],
            competitive_data=state.get("competitive_data", "No data"),
            evidence_data=state.get("evidence_data", "No data"),
            kol_data=state.get("kol_data", "No data"),
            news_data=state.get("news_data", "No data")
        )
        
        return {
            "launch_brief": result,
            "status_log": ["✅ Synthesis Agent complete — brief ready"]
        }
    except Exception as e:
        return {
            "launch_brief": {
                "status": "error",
                "brief": f"Synthesis failed: {str(e)}"
            },
            "error_log": [f"Synthesis Agent error: {str(e)}"]
        }


# ── Build the Graph ───────────────────────────────────────────────

def build_launch_intelligence_graph():
    """
    Build the LangGraph multi-agent pipeline.
    
    Graph structure:
    START → competitive + evidence + kol + news → synthesis → END
    
    The 4 research agents run sequentially
    then synthesis combines everything.
    """
    
    # Create the graph with our state type
    graph = StateGraph(LaunchIntelligenceState)
    
    # Add all agent nodes
    graph.add_node("competitive_agent", run_competitive_agent)
    graph.add_node("evidence_agent", run_evidence_agent)
    graph.add_node("kol_agent", run_kol_agent)
    graph.add_node("news_agent", run_news_agent)
    graph.add_node("synthesis_agent", run_synthesis_agent)
    
    # Define the flow
    # Sequential: each agent feeds into the next
    # Then all feed into synthesis
    graph.set_entry_point("competitive_agent")
    graph.add_edge("competitive_agent", "evidence_agent")
    graph.add_edge("evidence_agent", "kol_agent")
    graph.add_edge("kol_agent", "news_agent")
    graph.add_edge("news_agent", "synthesis_agent")
    graph.add_edge("synthesis_agent", END)
    
    return graph.compile()


def run_launch_intelligence(drug_name: str, indication: str) -> Dict:
    """
    Run the complete launch intelligence pipeline.
    
    Args:
        drug_name: The drug being launched
        indication: The target indication
    
    Returns:
        Complete state with all agent outputs and final brief
    """
    
    print(f"\n{'='*60}")
    print(f"DRUG LAUNCH INTELLIGENCE SYSTEM")
    print(f"Drug: {drug_name} | Indication: {indication}")
    print(f"{'='*60}\n")
    
    # Build the graph
    app = build_launch_intelligence_graph()
    
    # Initial state
    initial_state = {
        "drug_name": drug_name,
        "indication": indication,
        "competitive_data": "",
        "evidence_data": "",
        "kol_data": "",
        "news_data": "",
        "launch_brief": {},
        "status_log": ["🚀 Pipeline started"],
        "error_log": []
    }
    
    # Run the graph
    final_state = app.invoke(initial_state)
    
    print(f"\n{'='*60}")
    print("PIPELINE COMPLETE")
    print(f"Status log: {final_state.get('status_log', [])}")
    if final_state.get('error_log'):
        print(f"Errors: {final_state.get('error_log', [])}")
    print(f"{'='*60}\n")
    
    return final_state


# Quick test
if __name__ == "__main__":
    result = run_launch_intelligence("ivonescimab", "NSCLC")
    
    brief = result.get("launch_brief", {})
    print(f"Launch Readiness: {brief.get('launch_readiness', 'Unknown')}")
    print(f"\nBrief preview:")
    print(brief.get("brief", "No brief generated")[:600])