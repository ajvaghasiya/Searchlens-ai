import pandas as pd
import re
from typing import List, Dict, Any

def parse_nginx_logs(file_path: str) -> pd.DataFrame:
    """
    Parses a combined Nginx log file into a pandas DataFrame.
    Format: '$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"'
    """
    # Regex pattern to match standard combined Nginx/Apache logs
    log_pattern = re.compile(
        r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>.*?)\] '
        r'"(?P<method>\S+) (?P<path>\S+) \S+" '
        r'(?P<status>\d{3}) (?P<bytes>\d+|-) '
        r'"(?P<referer>.*?)" "(?P<user_agent>.*?)"'
    )
    
    parsed_data = []
    with open(file_path, 'r') as f:
        for line in f:
            match = log_pattern.match(line)
            if match:
                parsed_data.append(match.groupdict())
                
    df = pd.DataFrame(parsed_data)
    
    if df.empty:
        return df
        
    df['status'] = pd.to_numeric(df['status'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d/%b/%Y:%H:%M:%S %z', exact=False)
    
    return df

def filter_search_bots(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters the DataFrame to only include requests from known search engine bots.
    """
    bots = ['Googlebot', 'Bingbot', 'YandexBot', 'DuckDuckBot', 'Baiduspider', 'Slurp']
    pattern = '|'.join(bots)
    return df[df['user_agent'].str.contains(pattern, case=False, na=False)]

def segment_by_url_template(df: pd.DataFrame) -> pd.DataFrame:
    """
    Segments requests by URL template (e.g. product pages, category pages, etc.)
    """
    def categorize_path(path: str) -> str:
        if path.startswith('/products/'):
            return 'Product Page'
        elif path.startswith('/category/'):
            return 'Category Page'
        elif '?' in path and ('filter' in path or 'sort' in path):
            return 'Faceted/Filtered URL'
        elif path == '/':
            return 'Homepage'
        elif path.startswith('/blog/'):
            return 'Blog Post'
        else:
            return 'Other'
            
    df['url_template'] = df['path'].apply(categorize_path)
    return df

def analyze_crawl_budget(df: pd.DataFrame, gsc_index_status: Dict[str, bool]) -> Dict[str, Any]:
    """
    Cross-references crawl frequency against indexation status to flag crawl budget waste.
    """
    # Map GSC index status to the DataFrame (mocking GSC integration)
    df['is_indexed'] = df['path'].map(gsc_index_status).fillna(False)
    
    # Analyze by URL template
    template_analysis = df.groupby('url_template').agg(
        total_crawls=('path', 'count'),
        unique_urls=('path', 'nunique'),
        wasted_crawls=('is_indexed', lambda x: (~x).sum())
    ).reset_index()
    
    # Calculate % wasted crawl budget
    template_analysis['wasted_budget_pct'] = (template_analysis['wasted_crawls'] / template_analysis['total_crawls']) * 100
    
    # Response code anomalies
    anomalies = df[df['status'].isin([404, 500, 502, 503, 504])].groupby('status').size().to_dict()
    
    return {
        "template_analysis": template_analysis.to_dict(orient='records'),
        "response_code_anomalies": anomalies,
        "recommendations": _generate_recommendations(template_analysis, anomalies)
    }
    
def _generate_recommendations(template_analysis: pd.DataFrame, anomalies: Dict[int, int]) -> List[str]:
    recs = []
    
    # Check for faceted URL waste
    faceted_data = template_analysis[template_analysis['url_template'] == 'Faceted/Filtered URL']
    if not faceted_data.empty and faceted_data.iloc[0]['wasted_budget_pct'] > 20:
        recs.append("High crawl budget waste on Faceted URLs. Consider updating robots.txt to block parameterized filtering URLs.")
        
    # Check 5xx errors
    server_errors = sum(v for k, v in anomalies.items() if k >= 500)
    if server_errors > 10:
        recs.append(f"Detected {server_errors} server errors (5xx) from bot requests. Check server logs for rendering or timeout issues during crawl.")
        
    return recs
