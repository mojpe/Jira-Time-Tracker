import yaml
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests
import datetime
from requests.auth import HTTPBasicAuth
from collections import defaultdict

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Load configuration from config.yaml
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

JIRA_URL = config["JIRA_URL"]
API_TOKEN = config["API_TOKEN"]
USER_EMAIL = config["USER_EMAIL"]
TARGET_USER = config["TARGET_USER"]

def get_date_range(range_type, start_date=None, end_date=None):
    today = datetime.date.today()

    if range_type == "yesterday":
        return today - datetime.timedelta(days=1), today - datetime.timedelta(days=1)
    elif range_type == "this_week":
        start = today - datetime.timedelta(days=today.weekday())  # Monday
        return start, today
    elif range_type == "last_week":
        start = today - datetime.timedelta(days=today.weekday() + 7)
        end = start + datetime.timedelta(days=6)
        return start, end
    elif range_type == "this_month":
        return today.replace(day=1), today
    elif range_type == "last_month":
        first_day_last_month = (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
        last_day_last_month = first_day_last_month.replace(day=28) + datetime.timedelta(days=4)
        last_day_last_month = last_day_last_month - datetime.timedelta(days=last_day_last_month.day - 1)
        return first_day_last_month, last_day_last_month
    elif range_type == "custom":
        return datetime.datetime.strptime(start_date, "%Y-%m-%d").date(), datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    else:  # Default: today
        return today, today

def format_time(minutes: float) -> str:
    minutes = round(minutes)

    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours}:{remaining_minutes:02d}"


# Function to fetch time logs from Jira
def get_time_logged(start_date, end_date):
    JQL_QUERY = f'worklogAuthor="{TARGET_USER}" AND worklogDate >= "{start_date}" AND worklogDate <= "{end_date}"'
    headers = {"Accept": "application/json"}
    auth = HTTPBasicAuth(USER_EMAIL, API_TOKEN)

    url = f"{JIRA_URL}/rest/api/3/search?jql={JQL_QUERY}&fields=worklog"    
    response = requests.get(url, headers=headers, auth=auth)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=response.json().get("errorMessages", "Failed to fetch data"))

    issues = response.json().get("issues", [])
    total_seconds = 0
    grouped_issues = defaultdict(lambda: {"time": 0, "logs": []})

    for issue in issues:
        issue_key = issue["key"]
        worklogs = issue["fields"].get("worklog", {}).get("worklogs", [])

        for worklog in worklogs:
            if worklog["author"]["emailAddress"] == TARGET_USER:
                started = worklog["started"][:10]  # Extract YYYY-MM-DD
                log_date = datetime.datetime.strptime(started, "%Y-%m-%d").date()
                
                if start_date <= log_date <= end_date:
                    time_spent = worklog["timeSpentSeconds"]
                    formatted_time = f"{time_spent // 3600}:{time_spent % 3600 // 60:02}"
                    total_seconds += time_spent

                    # Add to the issue's total time
                    grouped_issues[issue_key]["time"] += time_spent

                    # Append individual worklog entry
                    grouped_issues[issue_key]["logs"].append({
                        "issue_log": issue_key,
                        "time_log": formatted_time
                    })

    final_result = {
        "total_time": format_time(sum(issue["time"] for issue in grouped_issues.values()) / 60),
        "worklogs": []
    }

    for issue_key, data in grouped_issues.items():
        total_time_str = format_time(data["time"] / 60)
        final_result["worklogs"].append({
            "issue": issue_key,
            "time": total_time_str,
            "logs": data["logs"]
        })

    return final_result

@app.get("/get_time", response_class=HTMLResponse)
@app.post("/get_time", response_class=HTMLResponse)
async def get_time(
    request: Request,
    date_range: str = Form("today"),  # Default to "today" if missing
    start_date: str = Form(None),
    end_date: str = Form(None)
):
    try:
        start_date, end_date = get_date_range(date_range, start_date, end_date)
        result = get_time_logged(start_date, end_date)
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "error": str(e)})
    
    return templates.TemplateResponse("index.html", {"request": request, "result": result})