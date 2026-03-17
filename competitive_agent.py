# competitive_agent.py
# =====================
# Agent 1 — Competitive Landscape Agent
# Searches ClinicalTrials.gov for competitor drugs
# in the same indication as the drug being launched
# No API key needed — free government data

import requests
from typing import Dict, List

# ClinicalTrials.gov API v2
TRIALS_URL = "https://clinicaltrials.gov/api/v2/studies"

def get_competitive_landscape(drug_name: str, indication: str) -> Dict:
    """
    Search for competitor drugs in the same indication.
    
    Args:
        drug_name: The drug being launched e.g. 'ivonescimab'
        indication: The target indication e.g. 'NSCLC'
    
    Returns:
        Dictionary with competitive landscape data
    """
    
    print(f"[Competitive Agent] Searching landscape for {indication}...")
    
    # Search for ALL drugs in this indication
    # Not just our drug — we want the full competitive picture
    params = {
        "query.cond": indication,
        "filter.overallStatus": "RECRUITING,ACTIVE_NOT_RECRUITING",
        "pageSize": 20,
        "format": "json"
    }
    
    try:
        response = requests.get(TRIALS_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        studies = data.get("studies", [])
        
        # Parse competitor trials
        competitors = []
        sponsor_counts = {}
        phase_counts = {}
        
        for study in studies:
            trial = parse_trial(study)
            if trial and drug_name.lower() not in trial["title"].lower():
                competitors.append(trial)
                
                # Count by sponsor
                sponsor = trial["sponsor"]
                sponsor_counts[sponsor] = sponsor_counts.get(sponsor, 0) + 1
                
                # Count by phase
                phase = trial["phase"]
                phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        # Also get our drug's trials
        our_trials = get_our_drug_trials(drug_name, indication)
        
        print(f"[Competitive Agent] Found {len(competitors)} competitor trials")
        
        return {
            "status": "success",
            "indication": indication,
            "drug_name": drug_name,
            "competitor_trials": competitors[:10],
            "our_trials": our_trials,
            "total_competitors": len(competitors),
            "sponsor_counts": sponsor_counts,
            "phase_counts": phase_counts,
            "top_sponsors": sorted(
                sponsor_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
        
    except Exception as e:
        print(f"[Competitive Agent] Error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "competitor_trials": [],
            "our_trials": [],
            "total_competitors": 0
        }


def get_our_drug_trials(drug_name: str, indication: str) -> List[Dict]:
    """
    Get trials specifically for our drug.
    """
    
    params = {
        "query.term": drug_name,
        "query.cond": indication,
        "filter.overallStatus": "RECRUITING,ACTIVE_NOT_RECRUITING,COMPLETED",
        "pageSize": 10,
        "format": "json"
    }
    
    try:
        response = requests.get(TRIALS_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        studies = data.get("studies", [])
        
        trials = []
        for study in studies:
            trial = parse_trial(study)
            if trial:
                trials.append(trial)
        
        return trials
        
    except Exception as e:
        print(f"[Competitive Agent] Error getting our trials: {e}")
        return []


def parse_trial(study: Dict) -> Dict:
    """
    Parse a raw ClinicalTrials.gov study.
    """
    
    try:
        protocol = study.get("protocolSection", {})
        id_module = protocol.get("identificationModule", {})
        status_module = protocol.get("statusModule", {})
        design_module = protocol.get("designModule", {})
        sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
        outcomes_module = protocol.get("outcomesModule", {})
        
        phases = design_module.get("phases", ["Unknown"])
        phase = phases[0] if phases else "Unknown"
        
        primary_outcomes = outcomes_module.get("primaryOutcomes", [])
        endpoint = primary_outcomes[0].get("measure", "Not specified") if primary_outcomes else "Not specified"
        
        lead_sponsor = sponsor_module.get("leadSponsor", {})
        sponsor = lead_sponsor.get("name", "Unknown")
        
        return {
            "nct_id": id_module.get("nctId", "Unknown"),
            "title": id_module.get("briefTitle", "Unknown")[:100],
            "status": status_module.get("overallStatus", "Unknown"),
            "phase": phase,
            "sponsor": sponsor,
            "endpoint": endpoint[:80],
            "url": f"https://clinicaltrials.gov/study/{id_module.get('nctId', '')}"
        }
        
    except Exception as e:
        return None


def format_competitive_output(data: Dict) -> str:
    """
    Format competitive landscape data as text for synthesis agent.
    """
    
    if data["status"] == "error":
        return f"Competitive landscape search failed: {data.get('error', 'Unknown error')}"
    
    lines = []
    lines.append(f"COMPETITIVE LANDSCAPE: {data['indication']}")
    lines.append(f"Total competitor trials found: {data['total_competitors']}")
    
    # Phase breakdown
    if data["phase_counts"]:
        lines.append("\nTrial phases in indication:")
        for phase, count in data["phase_counts"].items():
            lines.append(f"  {phase}: {count} trial(s)")
    
    # Top sponsors
    if data["top_sponsors"]:
        lines.append("\nMost active sponsors:")
        for sponsor, count in data["top_sponsors"][:3]:
            lines.append(f"  {sponsor}: {count} trial(s)")
    
    # Our drug trials
    if data["our_trials"]:
        lines.append(f"\nOUR DRUG ({data['drug_name']}) TRIALS:")
        for trial in data["our_trials"][:3]:
            lines.append(f"  NCT: {trial['nct_id']} | {trial['phase']} | {trial['status']}")
            lines.append(f"  Endpoint: {trial['endpoint'][:60]}")
    else:
        lines.append(f"\nNo trials found for {data['drug_name']} in {data['indication']}")
    
    # Top competitor trials
    if data["competitor_trials"]:
        lines.append("\nTOP COMPETITOR TRIALS:")
        for trial in data["competitor_trials"][:5]:
            lines.append(f"  {trial['sponsor']} — {trial['phase']} — {trial['status']}")
            lines.append(f"  {trial['title'][:70]}")
    
    return "\n".join(lines)


# Quick test
if __name__ == "__main__":
    result = get_competitive_landscape("ivonescimab", "NSCLC")
    print(format_competitive_output(result))