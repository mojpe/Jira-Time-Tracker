# Time Warrior - JIRA Hours Calculator

A FastAPI web application for calculating and tracking hours logged in JIRA.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Copy `env.example` to `.env` and update with your JIRA credentials:
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

3. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the web interface:**
   Open http://localhost:8000 in your browser.

## Environment Variables

- `JIRA_URL`: Your JIRA instance URL (e.g., https://yourcompany.atlassian.net)
- `JIRA_API_TOKEN`: Your JIRA API token
- `JIRA_USER_EMAIL`: Your JIRA user email
- `JIRA_TARGET_USER`: Email of the user whose time logs to fetch

## Features

- Query time logs by date range (today, yesterday, this week, last week, this month, last month, custom)
- Group worklogs by JIRA issue
- Display total time and individual log entries
- Proper error handling and logging
- Input validation with Pydantic models
- Caching for improved performance

## API Endpoints

- `GET/POST /get_time`: Main interface for querying time logs
- `GET /`: Redirects to `/get_time`