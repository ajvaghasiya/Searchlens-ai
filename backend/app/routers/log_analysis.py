from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
from typing import Dict, Any
from app.services.log_analysis import parse_nginx_logs, filter_search_bots, segment_by_url_template, analyze_crawl_budget

router = APIRouter(
    prefix="/log-analysis",
    tags=["Log Analysis"]
)

@router.post("/upload")
async def analyze_logs(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload an Nginx/Apache log file for crawl budget analysis.
    """
    temp_file = f"/tmp/{file.filename}"
    try:
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        df = parse_nginx_logs(temp_file)
        if df.empty:
            raise HTTPException(status_code=400, detail="Could not parse log file. Check format.")
            
        # Pipeline
        bots_df = filter_search_bots(df)
        segmented_df = segment_by_url_template(bots_df)
        
        # Mocking GSC index status for the demonstration
        mock_gsc_status = {
            "/": True,
            "/products/item-1": True,
            "/category/shoes": True,
            # Assume faceted are generally not indexed
            "/category/shoes?filter=red": False 
        }
        
        results = analyze_crawl_budget(segmented_df, mock_gsc_status)
        return results
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
