import os
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from collections import defaultdict
from functools import lru_cache

import requests
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, validator
from requests.auth import HTTPBasicAuth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Load configuration from environment variables
JIRA_URL = os.getenv("JIRA_URL")
API_TOKEN = os.getenv("JIRA_API_TOKEN") 
USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
TARGET_USER = os.getenv("JIRA_TARGET_USER")

# Validate required environment variables
required_env_vars = {
    "JIRA_URL": JIRA_URL,
    "JIRA_API_TOKEN": API_TOKEN,
    "JIRA_USER_EMAIL": USER_EMAIL,
    "JIRA_TARGET_USER": TARGET_USER
}

missing_vars = [name for name, value in required_env_vars.items() if not value]
if missing_vars:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Request timeout in seconds
REQUEST_TIMEOUT = 30

@dataclass
class WorklogEntry:
    """Individual worklog entry"""
    issue_log: str
    time_log: str

@dataclass 
class IssueWorklog:
    """Worklog data for a specific issue"""
    issue: str
    time: str
    logs: List[WorklogEntry]

class TimeRangeRequest(BaseModel):
    """Request model for time range queries"""
    date_range: str = "today"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    @validator('date_range')
    def validate_date_range(cls, v: str) -> str:
        valid_ranges = ["today", "yesterday", "this_week", "last_week", "this_month", "last_month", "custom"]
        if v not in valid_ranges:
            raise ValueError(f"Invalid date_range. Must be one of: {', '.join(valid_ranges)}")
        return v
    
    @validator('start_date', 'end_date')
    def validate_dates(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        return v

def get_date_range(range_type: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Tuple[date, date]:
    today = date.today()

    if range_type == "yesterday":
        return today - timedelta(days=1), today - timedelta(days=1)
    elif range_type == "this_week":
        start = today - timedelta(days=today.weekday())  # Monday
        return start, today
    elif range_type == "last_week":
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=6)
        return start, end
    elif range_type == "this_month":
        return today.replace(day=1), today
    elif range_type == "last_month":
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = first_day_last_month.replace(day=28) + timedelta(days=4)
        last_day_last_month = last_day_last_month - timedelta(days=last_day_last_month.day - 1)
        return first_day_last_month, last_day_last_month
    elif range_type == "custom":
        if not start_date or not end_date:
            raise ValueError("Custom date range requires both start_date and end_date")
        return datetime.strptime(start_date, "%Y-%m-%d").date(), datetime.strptime(end_date, "%Y-%m-%d").date()
    else:  # Default: today
        return today, today

def format_time(minutes: float) -> str:
    """Format minutes into HH:MM string format"""
    minutes = round(minutes)
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours}:{remaining_minutes:02d}"

def format_time_human(minutes: float) -> str:
    """Format minutes into human-readable format (e.g., '2h 30m')"""
    minutes = round(minutes)
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if hours > 0 and remaining_minutes > 0:
        return f"{hours}h {remaining_minutes}m"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{remaining_minutes}m"

def get_time_class(minutes: float) -> str:
    """Get CSS class based on time amount"""
    if minutes < 30:
        return "time-light"
    elif minutes < 120:  # 2 hours
        return "time-medium" 
    elif minutes < 300:  # 5 hours
        return "time-heavy"
    else:
        return "time-very-heavy"

def get_progress_color(percentage: float) -> str:
    """Get progress bar color based on percentage"""
    if percentage < 10:
        return "bg-info"
    elif percentage < 25:
        return "bg-success"
    elif percentage < 50:
        return "bg-warning"
    else:
        return "bg-danger"


@lru_cache(maxsize=128)
def get_time_logged(start_date: date, end_date: date) -> Dict[str, Any]:
    """Fetch time logs from JIRA for the specified date range"""
    jql_query = f'worklogAuthor="{TARGET_USER}" AND worklogDate >= "{start_date}" AND worklogDate <= "{end_date}"'
    headers = {"Accept": "application/json"}
    auth = HTTPBasicAuth(USER_EMAIL, API_TOKEN)
    
    logger.info(f"Querying JIRA for time logs from {start_date} to {end_date}")
    logger.debug(f"JQL Query: {jql_query}")
    
    url = f"{JIRA_URL}/rest/api/3/search"
    params = {
        "jql": jql_query,
        "fields": "worklog"
    }
    
    try:
        response = requests.get(
            url, 
            headers=headers, 
            auth=auth, 
            params=params,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
    except requests.exceptions.Timeout:
        logger.error(f"Request timed out after {REQUEST_TIMEOUT} seconds")
        raise HTTPException(status_code=408, detail="Request timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch data from JIRA: {str(e)}")
    
    try:
        data = response.json()
    except ValueError as e:
        logger.error(f"Failed to parse JSON response: {str(e)}")
        raise HTTPException(status_code=500, detail="Invalid response from JIRA")

    if "errorMessages" in data:
        error_msg = "; ".join(data["errorMessages"])
        logger.error(f"JIRA API error: {error_msg}")
        raise HTTPException(status_code=400, detail=f"JIRA API error: {error_msg}")

    issues = data.get("issues", [])
    grouped_issues = defaultdict(lambda: {"time": 0, "logs": []})

    for issue in issues:
        issue_key = issue["key"]
        worklogs = issue["fields"].get("worklog", {}).get("worklogs", [])

        for worklog in worklogs:
            try:
                # Verify worklog author
                if worklog.get("author", {}).get("emailAddress") != TARGET_USER:
                    continue
                    
                # Parse worklog date
                started = worklog["started"][:10]  # Extract YYYY-MM-DD
                log_date = datetime.strptime(started, "%Y-%m-%d").date()
                
                # Check if within date range
                if start_date <= log_date <= end_date:
                    time_spent = worklog.get("timeSpentSeconds", 0)
                    formatted_time = f"{time_spent // 3600}:{time_spent % 3600 // 60:02d}"
                    
                    # Add to the issue's total time
                    grouped_issues[issue_key]["time"] += time_spent
                    
                    # Parse full datetime for more details
                    full_datetime = datetime.strptime(worklog["started"], "%Y-%m-%dT%H:%M:%S.%f%z")
                    time_of_day = full_datetime.strftime("%H:%M")
                    date_logged = full_datetime.strftime("%Y-%m-%d")
                    
                    # Append individual worklog entry with enhanced data
                    worklog_entry = {
                        "issue_log": issue_key,
                        "time_log": formatted_time,
                        "time_formatted": format_time_human(time_spent / 60),
                        "date_logged": date_logged,
                        "time_of_day": time_of_day,
                        "raw_minutes": time_spent / 60
                    }
                    grouped_issues[issue_key]["logs"].append(worklog_entry)
                    
            except (KeyError, ValueError) as e:
                logger.warning(f"Skipping invalid worklog in {issue_key}: {str(e)}")
                continue

    # Build final result with enhanced data
    total_time_minutes = sum(issue["time"] for issue in grouped_issues.values()) / 60
    total_logs = sum(len(issue["logs"]) for issue in grouped_issues.values())
    average_time_per_issue = total_time_minutes / len(grouped_issues) if grouped_issues else 0
    
    worklogs = []
    
    for issue_key, data in grouped_issues.items():
        issue_minutes = data["time"] / 60
        percentage = (issue_minutes / total_time_minutes * 100) if total_time_minutes > 0 else 0
        
        issue_worklog = {
            "issue": issue_key,
            "time": format_time(issue_minutes),  # Keep original format for compatibility
            "time_formatted": format_time_human(issue_minutes),
            "time_class": get_time_class(issue_minutes),
            "percentage": round(percentage, 1),
            "progress_color": get_progress_color(percentage),
            "logs": data["logs"],
            "raw_minutes": issue_minutes
        }
        worklogs.append(issue_worklog)

    # Sort by time spent (descending)
    worklogs.sort(key=lambda x: x["raw_minutes"], reverse=True)
    
    # Get current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    result = {
        "total_time": format_time_human(total_time_minutes),
        "total_logs": total_logs,
        "average_time_per_issue": format_time_human(average_time_per_issue),
        "last_updated": current_time,
        "worklogs": worklogs
    }
    
    logger.info(f"Found {len(worklogs)} issues with {total_logs} logs totaling {result['total_time']}")
    return result

@app.get("/get_time", response_class=HTMLResponse)
@app.post("/get_time", response_class=HTMLResponse)
async def get_time(
    request: Request,
    date_range: str = Form("today"),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None)
) -> HTMLResponse:
    """Get time logged for specified date range"""
    try:
        # Validate input using Pydantic model
        time_request = TimeRangeRequest(
            date_range=date_range,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get date range
        start_dt, end_dt = get_date_range(
            time_request.date_range, 
            time_request.start_date, 
            time_request.end_date
        )
        
        # Fetch time logs
        result = get_time_logged(start_dt, end_dt)
        logger.info(f"Successfully retrieved time logs for {start_dt} to {end_dt}")
        
        return templates.TemplateResponse(
            "index.html", 
            {"request": request, "result": result}
        )
        
    except ValueError as e:
        logger.warning(f"Invalid input: {str(e)}")
        return templates.TemplateResponse(
            "index.html", 
            {"request": request, "error": f"Invalid input: {str(e)}"}
        )
    except HTTPException:
        # Re-raise HTTPExceptions to let FastAPI handle them
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return templates.TemplateResponse(
            "index.html", 
            {"request": request, "error": "An unexpected error occurred. Please try again."}
        )


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    """Redirect root to get_time endpoint"""
    return RedirectResponse(url="/get_time")