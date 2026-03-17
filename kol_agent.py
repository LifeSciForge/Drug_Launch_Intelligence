# kol_agent.py
# =============
# Agent 3 — Key Opinion Leader (KOL) Identification Agent
# Finds key investigators and thought leaders
# Uses NPI Registry + ClinicalTrials.gov investigator data
# No API key needed — free government data

import requests
from typing import Dict, List

NPI_URL = "https://npiregistry.cms.hhs.gov/api/"
TRIALS_URL = "https://clinicaltrials.gov/api/v2/studies"

def identify_kols(drug_name: str, indication: str, state: str = None) -> Dict:
    """
    Identify Key Opinion Leaders for a drug and indication.
    
    Args:
        drug_name: The drug being launched
        indication: The target indication
        state: Optional US state to focus on
    
    Returns:
        Dictionary with KOL data
    """
    
    print(f"[KOL Agent] Identifying KOLs for {drug_name} in {indication}...")
    
    # Get trial investigators
    investigators = get_trial_investigators(drug_name, indication)
    
    # Get specialist physicians in indication area
    specialists = get_specialists(indication, state)
    
    # Get top institutions running trials
    institutions = get_top_institutions(drug_name, indication)
    
    print(f"[KOL Agent] Found {len(investigators)} investigators, "
          f"{len(specialists)} specialists, "
          f"{len(institutions)} key institutions")
    
    return {
        "status": "success",
        "drug_name": drug_name,
        "indication": indication,
        "investigators": investigators[:10],
        "specialists": specialists[:10],
        "institutions": institutions[:5],
        "total_kols": len(investigators) + len(specialists)
    }


def get_trial_investigators(drug_name: str, indication: str) -> List[Dict]:
    """
    Get principal investigators from clinical trials.
    """
    
    params = {
        "query.term": drug_name,
        "query.cond": indication,
        "filter.overallStatus": "RECRUITING,ACTIVE_NOT_RECRUITING",
        "pageSize": 10,
        "format": "json"
    }
    
    try:
        response = requests.get(TRIALS_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        studies = data.get("studies", [])
        
        investigators = []
        seen_names = set()
        
        for study in studies:
            protocol = study.get("protocolSection", {})
            contacts = protocol.get("contactsLocationsModule", {})
            overall_officials = contacts.get("overallOfficials", [])
            
            for official in overall_officials:
                name = official.get("name", "")
                if name and name not in seen_names:
                    seen_names.add(name)
                    investigators.append({
                        "name": name,
                        "role": official.get("role", "Principal Investigator"),
                        "affiliation": official.get("affiliation", "Unknown"),
                        "type": "Trial Investigator"
                    })
        
        return investigators
        
    except Exception as e:
        print(f"[KOL Agent] Error getting investigators: {e}")
        return []


def get_specialists(indication: str, state: str = None) -> List[Dict]:
    """
    Get specialist physicians from NPI Registry.
    """
    
    # Map indication to medical specialty
    specialty_map = {
        "nsclc": "Hematology & Oncology",
        "lung cancer": "Hematology & Oncology",
        "oncology": "Hematology & Oncology",
        "melanoma": "Hematology & Oncology",
        "diabetes": "Endocrinology, Diabetes & Metabolism",
        "obesity": "Endocrinology, Diabetes & Metabolism",
        "alzheimers": "Neurology",
        "neurology": "Neurology",
        "cardiology": "Cardiovascular Disease",
        "rheumatology": "Rheumatology"
    }
    
    indication_lower = indication.lower()
    specialty = next(
        (v for k, v in specialty_map.items() if k in indication_lower),
        "Hematology & Oncology"
    )
    
    params = {
        "version": "2.1",
        "enumeration_type": "NPI-1",
        "taxonomy_description": specialty,
        "limit": 10
    }
    
    if state:
        params["state"] = state
    
    try:
        response = requests.get(NPI_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        
        specialists = []
        for result in results:
            basic = result.get("basic", {})
            addresses = result.get("addresses", [{}])
            taxonomies = result.get("taxonomies", [{}])
            
            address = addresses[0] if addresses else {}
            taxonomy = taxonomies[0] if taxonomies else {}
            
            name = f"Dr. {basic.get('first_name', '')} {basic.get('last_name', '')}".strip()
            
            if name != "Dr. ":
                specialists.append({
                    "name": name,
                    "credential": basic.get("credential", "MD"),
                    "specialty": taxonomy.get("desc", specialty),
                    "city": address.get("city", "Unknown"),
                    "state": address.get("state", "Unknown"),
                    "type": "Specialist Physician",
                    "npi": result.get("number", "")
                })
        
        return specialists
        
    except Exception as e:
        print(f"[KOL Agent] Error getting specialists: {e}")
        return []


def get_top_institutions(drug_name: str, indication: str) -> List[Dict]:
    """
    Get top institutions running trials for this drug.
    """
    
    params = {
        "query.term": drug_name,
        "query.cond": indication,
        "pageSize": 15,
        "format": "json"
    }
    
    try:
        response = requests.get(TRIALS_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        studies = data.get("studies", [])
        
        institution_counts = {}
        
        for study in studies:
            protocol = study.get("protocolSection", {})
            contacts = protocol.get("contactsLocationsModule", {})
            locations = contacts.get("locations", [])
            
            for location in locations[:3]:
                facility = location.get("facility", "Unknown")
                if facility and facility != "Unknown":
                    institution_counts[facility] = \
                        institution_counts.get(facility, 0) + 1
        
        top_institutions = sorted(
            institution_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return [
            {"name": inst, "trial_count": count}
            for inst, count in top_institutions
        ]
        
    except Exception as e:
        print(f"[KOL Agent] Error getting institutions: {e}")
        return []


def format_kol_output(data: Dict) -> str:
    """
    Format KOL data as text for synthesis agent.
    """
    
    if data["status"] == "error":
        return f"KOL identification failed: {data.get('error', 'Unknown error')}"
    
    lines = []
    lines.append(f"KOL LANDSCAPE: {data['drug_name']} in {data['indication']}")
    lines.append(f"Total KOLs identified: {data['total_kols']}")
    
    if data["investigators"]:
        lines.append("\nKEY TRIAL INVESTIGATORS:")
        for inv in data["investigators"][:5]:
            lines.append(f"  {inv['name']} — {inv['affiliation']}")
            lines.append(f"  Role: {inv['role']}")
    
    if data["specialists"]:
        lines.append("\nKEY SPECIALIST PHYSICIANS:")
        for spec in data["specialists"][:5]:
            lines.append(f"  {spec['name']} {spec['credential']} — "
                        f"{spec['specialty']}")
            lines.append(f"  Location: {spec['city']}, {spec['state']}")
    
    if data["institutions"]:
        lines.append("\nTOP TRIAL INSTITUTIONS:")
        for inst in data["institutions"]:
            lines.append(f"  {inst['name']} — {inst['trial_count']} trial(s)")
    
    return "\n".join(lines)


# Quick test
if __name__ == "__main__":
    result = identify_kols("ivonescimab", "NSCLC")
    print(format_kol_output(result))