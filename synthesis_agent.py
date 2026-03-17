# synthesis_agent.py
# ===================
# Synthesis Agent — combines all 4 agent outputs
# Uses Claude Haiku to generate launch intelligence brief
# This is the "brain" that makes sense of everything
# Requires ANTHROPIC_API_KEY in .env file

import os
from dotenv import load_dotenv
from typing import Dict

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

def synthesise_launch_brief(
    drug_name: str,
    indication: str,
    competitive_data: str,
    evidence_data: str,
    kol_data: str,
    news_data: str
) -> Dict:
    """
    Synthesise all agent outputs into a launch intelligence brief.
    
    Args:
        drug_name: The drug being launched
        indication: The target indication
        competitive_data: Output from competitive_agent
        evidence_data: Output from evidence_agent
        kol_data: Output from kol_agent
        news_data: Output from news_agent
    
    Returns:
        Dictionary with complete launch brief
    """
    
    print(f"[Synthesis Agent] Generating launch brief for {drug_name}...")
    
    if not API_KEY:
        print("[Synthesis Agent] No API key — returning placeholder brief")
        return get_placeholder_brief(drug_name, indication)
    
    prompt = build_synthesis_prompt(
        drug_name, indication,
        competitive_data, evidence_data,
        kol_data, news_data
    )
    
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=API_KEY)
        
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        brief_text = response.content[0].text
        
        return {
            "status": "success",
            "drug_name": drug_name,
            "indication": indication,
            "brief": brief_text,
            "launch_readiness": extract_readiness(brief_text)
        }
        
    except Exception as e:
        print(f"[Synthesis Agent] Error: {e}")
        return get_placeholder_brief(drug_name, indication)


def build_synthesis_prompt(
    drug_name: str,
    indication: str,
    competitive_data: str,
    evidence_data: str,
    kol_data: str,
    news_data: str
) -> str:
    """
    Build the synthesis prompt for Claude.
    """
    
    return f"""You are a senior pharmaceutical launch strategist with 15 years 
of experience advising on drug launches for top-20 pharma companies.

You have been asked to prepare a Drug Launch Intelligence Brief for the 
commercial and medical affairs leadership team.

DRUG: {drug_name}
INDICATION: {indication}

LIFECYCLE ASSESSMENT INSTRUCTION:
Before writing anything, first determine if {drug_name} is:
- A NEW drug with no prior approvals → write as New Launch Brief
- An EXISTING approved drug → write as Lifecycle Management Brief

If {drug_name} already has FDA approvals, clearly state upfront:
"This is a LIFECYCLE MANAGEMENT analysis, not a new product launch."
Adjust the launch readiness rating and all recommendations accordingly.
For any drug approved more than 5 years ago, you MUST address:
→ Biosimilar threats and timeline
→ IRA drug pricing negotiation implications
→ Indication expansion vs defence strategy

You have received intelligence from 4 specialist analysts:

=== COMPETITIVE LANDSCAPE ANALYSIS ===
{competitive_data}

=== CLINICAL EVIDENCE ASSESSMENT ===
{evidence_data}

=== KEY OPINION LEADER MAPPING ===
{kol_data}

=== MARKET & NEWS INTELLIGENCE ===
{news_data}

Based on all this intelligence, prepare a structured 
Drug Launch Intelligence Brief with these sections:

1. EXECUTIVE SUMMARY (3 sentences maximum)
   - What is the opportunity?
   - What is the competitive situation?
   - What is the overall launch readiness?

2. COMPETITIVE LANDSCAPE
   - Key competitors and their positioning
   - Competitive threats and opportunities
   - Our differentiation strategy

3. CLINICAL EVIDENCE STRENGTH
   - Overall evidence quality assessment
   - Key data gaps to address before launch
   - Publication strategy recommendations

4. KOL ENGAGEMENT STRATEGY
   - Top 3 KOLs to engage immediately
   - Key institutions to prioritise
   - MSL deployment recommendations

5. MARKET ACCESS OUTLOOK
   - Payer landscape assessment
   - Formulary access strategy
   - Pricing and reimbursement considerations

6. LAUNCH READINESS RATING
   Rate overall launch readiness as one of:
   🟢 HIGH — Ready to launch
   🟡 MEDIUM — Launch with targeted gaps to address
   🔴 LOW — Significant preparation needed

7. TOP 3 PRIORITIES BEFORE LAUNCH
   - Priority 1: [specific actionable recommendation]
   - Priority 2: [specific actionable recommendation]  
   - Priority 3: [specific actionable recommendation]

Keep each section concise — 3 to 5 bullet points maximum.
Be specific and actionable — this brief will be presented to 
the VP of Commercial and Chief Medical Officer tomorrow morning.
"""


def extract_readiness(brief_text: str) -> str:
    """
    Extract launch readiness rating from brief.
    """
    
    if "🟢" in brief_text or "HIGH" in brief_text.upper():
        return "HIGH"
    elif "🟡" in brief_text or "MEDIUM" in brief_text.upper():
        return "MEDIUM"
    elif "🔴" in brief_text or "LOW" in brief_text.upper():
        return "LOW"
    else:
        return "MEDIUM"


def get_placeholder_brief(drug_name: str, indication: str) -> Dict:
    """
    Placeholder brief when no API key configured.
    """
    
    return {
        "status": "placeholder",
        "drug_name": drug_name,
        "indication": indication,
        "launch_readiness": "MEDIUM",
        "brief": f"""
## Drug Launch Intelligence Brief: {drug_name} in {indication}

**Note: Placeholder brief. Add ANTHROPIC_API_KEY to .env for real AI analysis.**

1. EXECUTIVE SUMMARY
   - {drug_name} represents a significant opportunity in {indication}
   - Competitive landscape shows active Phase 3 development
   - Launch readiness is MEDIUM — targeted preparation needed

2. COMPETITIVE LANDSCAPE
   - Multiple competitors active in Phase 2/3
   - Differentiation strategy needed on efficacy and safety profile
   - First-mover advantage possible in specific patient segments

3. CLINICAL EVIDENCE STRENGTH
   - Growing evidence base with Phase 3 data emerging
   - Key publications in high-impact journals identified
   - Additional real-world evidence needed for payer submissions

4. KOL ENGAGEMENT STRATEGY
   - Trial investigators identified as priority KOLs
   - Academic medical centres as primary engagement targets
   - MSL deployment recommended at top 5 institutions

5. MARKET ACCESS OUTLOOK
   - Payer landscape competitive but accessible
   - Health economic data needed for formulary submissions
   - Early payer engagement recommended

6. LAUNCH READINESS RATING
   🟡 MEDIUM — Launch with targeted gaps to address

7. TOP 3 PRIORITIES BEFORE LAUNCH
   - Priority 1: Engage top 3 KOL investigators immediately
   - Priority 2: Complete health economic analysis for payers
   - Priority 3: Finalise MSL deployment plan for key centres

*Add your Anthropic API key to .env to replace with real AI analysis.*
"""
    }


# Quick test
if __name__ == "__main__":
    # Test with sample data
    result = synthesise_launch_brief(
        drug_name="ivonescimab",
        indication="NSCLC",
        competitive_data="15 competitor trials found. Phase 3 active.",
        evidence_data="23 papers found. Evidence score: Moderate. Lancet publications.",
        kol_data="13 KOLs identified. UC San Diego, USC key institutions.",
        news_data="7 new FDA approvals in NSCLC in 2025. Active market."
    )
    
    print(f"Status: {result['status']}")
    print(f"Launch Readiness: {result['launch_readiness']}")
    print(f"\nBrief preview:")
    print(result['brief'][:500])