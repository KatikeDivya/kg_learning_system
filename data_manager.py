import json
import os
from datetime import datetime
from pathlib import Path

DATA_STORE_PATH = os.path.join(os.path.dirname(__file__), "data", "data_store.json")


def ensure_data_store_exists():
    """Create data_store.json if it doesn't exist"""
    if not os.path.exists(DATA_STORE_PATH):
        initial_data = {
            "queries": [],
            "domains": {},
            "last_updated": None
        }
        save_data(initial_data)


def load_data():
    """Load data from data_store.json"""
    ensure_data_store_exists()
    
    try:
        with open(DATA_STORE_PATH, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        ensure_data_store_exists()
        return {
            "queries": [],
            "domains": {},
            "last_updated": None
        }

    cleaned = False

    if "api_keys" in data:
        del data["api_keys"]
        cleaned = True

    for query in data.get("queries", []):
        if "known_topics" in query:
            del query["known_topics"]
            cleaned = True
        if "api_key_hash" in query:
            del query["api_key_hash"]
            cleaned = True

    for domain_data in data.get("domains", {}).values():
        if "queries" in domain_data:
            for query in domain_data["queries"]:
                if "known_topics" in query:
                    del query["known_topics"]
                    cleaned = True
                if "api_key_hash" in query:
                    del query["api_key_hash"]
                    cleaned = True

    if cleaned:
        save_data(data)

    return data


def save_data(data):
    """Save data to data_store.json"""
    Path(DATA_STORE_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    with open(DATA_STORE_PATH, 'w') as f:
        json.dump(data, f, indent=2)


def _extract_clean_domain(domain_text):
    """Extract clean domain name from full response text"""
    if not domain_text:
        return "General"
    
    import re
    
    # If it's already short (< 50 chars and no markdown), return as is
    if len(domain_text) < 50 and '**' not in domain_text:
        return domain_text.strip()
    
    # Extract ONLY the domain name after "**Learning Domain:**"
    # Stop at the first newline to avoid including topics
    match = re.search(r'\*\*Learning Domain:\*\*\s*([^\n]+)', domain_text)
    if match:
        domain_name = match.group(1).strip()
        # Remove any markdown or extra formatting
        domain_name = domain_name.replace('**', '').strip()
        return domain_name
    
    # If format is different, try to extract first meaningful line
    lines = domain_text.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('**') and not line.startswith('-'):
            return line.replace('**', '').strip()
    
    # Final fallback
    return "General"


def add_query(user_input, domain, learning_path, recommendations, graph_data):
    """
    Store a new query and its results
    
    Args:
        user_input: The original user query
        domain: Detected domain
        learning_path: Generated learning path
        recommendations: Recommended next topics
        graph_data: The learning graph data
    """
    data = load_data()
    
    # Check for duplicate queries based on user_input
    for existing_query in data.get("queries", []):
        if existing_query.get("user_input") == user_input:
            # Update existing query with new data
            existing_query.update({
                "timestamp": datetime.now().isoformat(),
                "domain": _extract_clean_domain(domain),
                "learning_path": learning_path,
                "recommendations": recommendations,
                "graph_data": graph_data
            })
            save_data(data)
            return existing_query
    
    clean_domain = _extract_clean_domain(domain)
    
    query_record = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "domain": clean_domain,
        "learning_path": learning_path,
        "recommendations": recommendations,
        "graph_data": graph_data
    }
    
    data["queries"].append(query_record)
    
    # Update domain-specific data
    if clean_domain not in data["domains"]:
        data["domains"][clean_domain] = {
            "queries": [],
            "graph_data": graph_data,
            "last_updated": datetime.now().isoformat()
        }
    
    # Check for duplicate in domain queries
    domain_queries = data["domains"][clean_domain]["queries"]
    for existing_query in domain_queries:
        if existing_query.get("user_input") == user_input:
            existing_query.update(query_record)
            break
    else:
        domain_queries.append(query_record)
    
    data["domains"][clean_domain]["last_updated"] = datetime.now().isoformat()
    
    data["last_updated"] = datetime.now().isoformat()
    
    save_data(data)
    return query_record


def get_domain_data(domain):
    """Get all data for a specific domain"""
    data = load_data()
    return data.get("domains", {}).get(domain, None)


def get_all_queries():
    """Get all stored queries"""
    data = load_data()
    return data.get("queries", [])


def get_recent_queries(limit=10):
    """Get recent queries"""
    data = load_data()
    queries = data.get("queries", [])
    return sorted(queries, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]


def clear_data():
    """Clear all stored data (use with caution)"""
    initial_data = {
        "queries": [],
        "domains": {},
        "last_updated": datetime.now().isoformat()
    }
    save_data(initial_data)


def get_stats():
    """Get statistics about stored data"""
    data = load_data()
    
    return {
        "total_queries": len(data.get("queries", [])),
        "unique_domains": len(data.get("domains", {})),
        "domains": list(data.get("domains", {}).keys()),
        "last_updated": data.get("last_updated")
    }
