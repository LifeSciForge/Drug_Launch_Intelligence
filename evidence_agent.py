# evidence_agent.py
# ==================
# Agent 2 — Clinical Evidence Strength Agent
# Searches PubMed for published evidence on our drug
# Assesses evidence quality and publication landscape
# No API key needed — free government data

from Bio import Entrez
import time
from typing import Dict, List

# Required by NCBI — just for identification
Entrez.email = "lifesciforge@example.com"

def assess_evidence_strength(drug_name: str, indication: str) -> Dict:
    """
    Search PubMed and assess clinical evidence strength.
    
    Args:
        drug_name: The drug being launched
        indication: The target indication
    
    Returns:
        Dictionary with evidence assessment data
    """
    
    print(f"[Evidence Agent] Assessing evidence for {drug_name} in {indication}...")
    
    try:
        # Search PubMed
        search_term = f"{drug_name}[Title/Abstract] AND {indication}[Title/Abstract]"
        
        handle = Entrez.esearch(
            db="pubmed",
            term=search_term,
            retmax=15,
            sort="relevance"
        )
        search_results = Entrez.read(handle)
        handle.close()
        
        id_list = search_results["IdList"]
        total_found = int(search_results["Count"])
        
        print(f"[Evidence Agent] Found {total_found} total papers, fetching top {len(id_list)}")
        
        if not id_list:
            return {
                "status": "no_data",
                "drug_name": drug_name,
                "indication": indication,
                "total_papers": 0,
                "papers": [],
                "evidence_score": "Insufficient",
                "key_journals": []
            }
        
        # Fetch paper details
        time.sleep(0.5)
        papers = fetch_papers(id_list)
        
        # Assess evidence quality
        assessment = assess_quality(papers, total_found)
        
        return {
            "status": "success",
            "drug_name": drug_name,
            "indication": indication,
            "total_papers": total_found,
            "papers": papers,
            "evidence_score": assessment["score"],
            "evidence_rationale": assessment["rationale"],
            "key_journals": assessment["key_journals"],
            "year_range": assessment["year_range"],
            "phase3_papers": assessment["phase3_papers"]
        }
        
    except Exception as e:
        print(f"[Evidence Agent] Error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "drug_name": drug_name,
            "indication": indication,
            "total_papers": 0,
            "papers": [],
            "evidence_score": "Unknown"
        }


def fetch_papers(id_list: List[str]) -> List[Dict]:
    """
    Fetch paper details from PubMed.
    """
    
    try:
        fetch_handle = Entrez.efetch(
            db="pubmed",
            id=",".join(id_list),
            rettype="abstract",
            retmode="xml"
        )
        records = Entrez.read(fetch_handle)
        fetch_handle.close()
        
        papers = []
        for record in records["PubmedArticle"]:
            paper = parse_paper(record)
            if paper:
                papers.append(paper)
        
        return papers
        
    except Exception as e:
        print(f"[Evidence Agent] Error fetching papers: {e}")
        return []


def parse_paper(record: Dict) -> Dict:
    """
    Parse a raw PubMed record.
    """
    
    try:
        article = record["MedlineCitation"]["Article"]
        
        title = str(article.get("ArticleTitle", "Unknown"))
        
        abstract_obj = article.get("Abstract", {})
        abstract_texts = abstract_obj.get("AbstractText", ["Not available"])
        if isinstance(abstract_texts, list):
            abstract = " ".join([str(t) for t in abstract_texts])
        else:
            abstract = str(abstract_texts)
        
        journal = article.get("Journal", {})
        journal_name = str(journal.get("Title", "Unknown"))
        
        pub_date = journal.get("JournalIssue", {}).get("PubDate", {})
        year = str(pub_date.get("Year", "Unknown"))
        
        pmid = str(record["MedlineCitation"]["PMID"])
        
        # Check if this is a Phase 3 paper
        is_phase3 = any(term in abstract.lower() for term in
                       ["phase 3", "phase iii", "phase3", "randomized",
                        "randomised", "overall survival", "progression-free"])
        
        return {
            "pmid": pmid,
            "title": title,
            "journal": journal_name,
            "year": year,
            "abstract_preview": abstract[:300],
            "is_phase3": is_phase3,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        }
        
    except Exception as e:
        return None


def assess_quality(papers: List[Dict], total_found: int) -> Dict:
    """
    Assess the overall quality of the evidence base.
    """
    
    if not papers:
        return {
            "score": "Insufficient",
            "rationale": "No published evidence found",
            "key_journals": [],
            "year_range": "N/A",
            "phase3_papers": 0
        }
    
    # Count Phase 3 papers
    phase3_papers = sum(1 for p in papers if p.get("is_phase3", False))
    
    # Get key journals
    journal_counts = {}
    for paper in papers:
        journal = paper.get("journal", "Unknown")
        journal_counts[journal] = journal_counts.get(journal, 0) + 1
    
    key_journals = sorted(
        journal_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]
    
    # Get year range
    years = []
    for paper in papers:
        try:
            year = int(paper.get("year", 0))
            if year > 0:
                years.append(year)
        except:
            pass
    
    year_range = f"{min(years)}–{max(years)}" if years else "Unknown"
    
    # Score evidence strength
    if total_found >= 50 and phase3_papers >= 3:
        score = "Strong"
        rationale = f"Robust evidence base with {total_found} publications including {phase3_papers} Phase 3 studies"
    elif total_found >= 20 and phase3_papers >= 1:
        score = "Moderate"
        rationale = f"Growing evidence base with {total_found} publications and {phase3_papers} Phase 3 study"
    elif total_found >= 5:
        score = "Early"
        rationale = f"Early evidence base with {total_found} publications — Phase 3 data emerging"
    else:
        score = "Limited"
        rationale = f"Limited published evidence — only {total_found} publications found"
    
    return {
        "score": score,
        "rationale": rationale,
        "key_journals": key_journals,
        "year_range": year_range,
        "phase3_papers": phase3_papers
    }


def format_evidence_output(data: Dict) -> str:
    """
    Format evidence data as text for synthesis agent.
    """
    
    if data["status"] == "error":
        return f"Evidence search failed: {data.get('error', 'Unknown error')}"
    
    if data["status"] == "no_data":
        return f"No published evidence found for {data['drug_name']} in {data['indication']}"
    
    lines = []
    lines.append(f"EVIDENCE STRENGTH ASSESSMENT: {data['drug_name']} in {data['indication']}")
    lines.append(f"Overall Evidence Score: {data['evidence_score']}")
    lines.append(f"Rationale: {data.get('evidence_rationale', 'N/A')}")
    lines.append(f"Total Publications: {data['total_papers']}")
    lines.append(f"Phase 3 Papers: {data['phase3_papers']}")
    lines.append(f"Literature Years: {data.get('year_range', 'N/A')}")
    
    if data["key_journals"]:
        lines.append("\nKey Journals:")
        for journal, count in data["key_journals"]:
            lines.append(f"  {journal}: {count} paper(s)")
    
    if data["papers"]:
        lines.append("\nTop Publications:")
        for paper in data["papers"][:4]:
            lines.append(f"  {paper['year']} — {paper['title'][:70]}")
            lines.append(f"  Journal: {paper['journal']}")
            lines.append(f"  URL: {paper['url']}")
    
    return "\n".join(lines)


# Quick test
if __name__ == "__main__":
    result = assess_evidence_strength("ivonescimab", "NSCLC")
    print(format_evidence_output(result))