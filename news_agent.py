# news_agent.py
# ==============
# Agent 4 — News & Market Intelligence Agent
# Searches for latest news about the drug and market
# Uses Tavily API for web search
# Requires TAVILY_API_KEY in .env file

import os
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

def get_market_intelligence(drug_name: str, indication: str) -> Dict:
    """
    Search for latest news and market intelligence.
    
    Args:
        drug_name: The drug being launched
        indication: The target indication
    
    Returns:
        Dictionary with news and market data
    """
    
    print(f"[News Agent] Searching market intelligence for {drug_name}...")
    
    if not TAVILY_API_KEY:
        print("[News Agent] No Tavily API key — returning placeholder")
        return get_placeholder_news(drug_name, indication)
    
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)
        
        # Search 1 — Drug specific news
        drug_news = search_news(
            client,
            f"{drug_name} {indication} clinical trial results FDA approval 2025 2026",
            max_results=4
        )
        
        # Search 2 — Market landscape
        market_news = search_news(
            client,
            f"{drug_name} {indication} payer formulary market access reimbursement 2025",
            max_results=3
        )
        
        # Search 3 — Competitive news
        competitive_news = search_news(
            client,
            f"{drug_name} {indication} competitor drugs pipeline threat 2025 2026",
            max_results=3
        )
        
        print(f"[News Agent] Found {len(drug_news)} drug news, "
              f"{len(market_news)} market news, "
              f"{len(competitive_news)} competitive news")
        
        return {
            "status": "success",
            "drug_name": drug_name,
            "indication": indication,
            "drug_news": drug_news,
            "market_news": market_news,
            "competitive_news": competitive_news,
            "total_articles": len(drug_news) + len(market_news) + len(competitive_news)
        }
        
    except Exception as e:
        print(f"[News Agent] Error: {e}")
        return get_placeholder_news(drug_name, indication)


def search_news(client, query: str, max_results: int = 3) -> List[Dict]:
    """
    Search for news articles using Tavily.
    """
    
    try:
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_answer=False
        )
        
        articles = []
        for result in response.get("results", []):
            articles.append({
                "title": result.get("title", "Unknown"),
                "url": result.get("url", ""),
                "content": result.get("content", "")[:250],
                "score": result.get("score", 0)
            })
        
        return articles
        
    except Exception as e:
        print(f"[News Agent] Search error: {e}")
        return []


def get_placeholder_news(drug_name: str, indication: str) -> Dict:
    """
    Placeholder when Tavily API key is not configured.
    """
    
    return {
        "status": "placeholder",
        "drug_name": drug_name,
        "indication": indication,
        "drug_news": [
            {
                "title": f"{drug_name} shows promising results in {indication}",
                "url": "https://example.com",
                "content": "Placeholder — add Tavily API key for real news",
                "score": 0
            }
        ],
        "market_news": [],
        "competitive_news": [],
        "total_articles": 1
    }


def format_news_output(data: Dict) -> str:
    """
    Format news data as text for synthesis agent.
    """
    
    lines = []
    lines.append(f"MARKET INTELLIGENCE: {data['drug_name']} in {data['indication']}")
    lines.append(f"Total articles found: {data.get('total_articles', 0)}")
    
    if data.get("drug_news"):
        lines.append("\nDRUG-SPECIFIC NEWS:")
        for article in data["drug_news"][:3]:
            lines.append(f"  {article['title']}")
            lines.append(f"  {article['content'][:150]}...")
            lines.append(f"  Source: {article['url']}")
    
    if data.get("market_news"):
        lines.append("\nMARKET LANDSCAPE NEWS:")
        for article in data["market_news"][:2]:
            lines.append(f"  {article['title']}")
            lines.append(f"  {article['content'][:150]}...")
    
    if data.get("competitive_news"):
        lines.append("\nCOMPETITIVE INTELLIGENCE:")
        for article in data["competitive_news"][:2]:
            lines.append(f"  {article['title']}")
            lines.append(f"  {article['content'][:150]}...")
    
    return "\n".join(lines)


# Quick test
if __name__ == "__main__":
    result = get_market_intelligence("ivonescimab", "NSCLC")
    print(format_news_output(result))