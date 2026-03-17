# agent_graph.py
# ===============
# Multi-agent orchestrator for Drug Launch Intelligence
# Runs 4 specialist agents sequentially then synthesises
# 
# Note: Full LangGraph implementation available in
# agent_graph_langgraph.py — this version uses the same
# agent architecture without the LangGraph dependency
# for maximum deployment compatibility.

from competitive_agent import get_competitive_landscape, format_competitive_output
from evidence_agent import assess_evidence_strength, format_evidence_output
from kol_agent import identify_kols, format_kol_output
from news_agent import get_market_intelligence, format_news_output
from synthesis_agent import synthesise_launch_brief

def run_launch_intelligence(drug_name: str, indication: str) -> dict:
    """
    Run the complete launch intelligence pipeline.
    Coordinates 4 specialist agents and synthesis.
    
    Args:
        drug_name: The drug being analysed
        indication: The therapeutic indication
    
    Returns:
        Complete state dictionary with all agent outputs
    """
    
    print(f"\n{'='*60}")
    print(f"DRUG LAUNCH INTELLIGENCE SYSTEM")
    print(f"Drug: {drug_name} | Indication: {indication}")
    print(f"{'='*60}\n")
    
    status_log = ["🚀 Pipeline started"]
    error_log = []
    
    # Agent 1 — Competitive Landscape
    print("[Pipeline] Running Competitive Agent...")
    try:
        competitive_result = get_competitive_landscape(drug_name, indication)
        competitive_data = format_competitive_output(competitive_result)
        status_log.append("✅ Competitive Agent complete")
    except Exception as e:
        competitive_data = f"Competitive analysis unavailable: {str(e)}"
        error_log.append(f"Competitive Agent error: {str(e)}")
    
    # Agent 2 — Clinical Evidence
    print("[Pipeline] Running Evidence Agent...")
    try:
        evidence_result = assess_evidence_strength(drug_name, indication)
        evidence_data = format_evidence_output(evidence_result)
        status_log.append("✅ Evidence Agent complete")
    except Exception as e:
        evidence_data = f"Evidence assessment unavailable: {str(e)}"
        error_log.append(f"Evidence Agent error: {str(e)}")
    
    # Agent 3 — KOL Identification
    print("[Pipeline] Running KOL Agent...")
    try:
        kol_result = identify_kols(drug_name, indication)
        kol_data = format_kol_output(kol_result)
        status_log.append("✅ KOL Agent complete")
    except Exception as e:
        kol_data = f"KOL identification unavailable: {str(e)}"
        error_log.append(f"KOL Agent error: {str(e)}")
    
    # Agent 4 — Market Intelligence
    print("[Pipeline] Running News Agent...")
    try:
        news_result = get_market_intelligence(drug_name, indication)
        news_data = format_news_output(news_result)
        status_log.append("✅ News Agent complete")
    except Exception as e:
        news_data = f"Market intelligence unavailable: {str(e)}"
        error_log.append(f"News Agent error: {str(e)}")
    
    # Synthesis Agent — Claude combines everything
    print("[Pipeline] Running Synthesis Agent...")
    try:
        launch_brief = synthesise_launch_brief(
            drug_name=drug_name,
            indication=indication,
            competitive_data=competitive_data,
            evidence_data=evidence_data,
            kol_data=kol_data,
            news_data=news_data
        )
        status_log.append("✅ Synthesis Agent complete — brief ready")
    except Exception as e:
        launch_brief = {
            "status": "error",
            "brief": f"Synthesis failed: {str(e)}"
        }
        error_log.append(f"Synthesis Agent error: {str(e)}")
    
    print(f"\n{'='*60}")
    print("PIPELINE COMPLETE")
    print(f"Status: {status_log}")
    print(f"{'='*60}\n")
    
    return {
        "drug_name": drug_name,
        "indication": indication,
        "competitive_data": competitive_data,
        "evidence_data": evidence_data,
        "kol_data": kol_data,
        "news_data": news_data,
        "launch_brief": launch_brief,
        "status_log": status_log,
        "error_log": error_log
    }