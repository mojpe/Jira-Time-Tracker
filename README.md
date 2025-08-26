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

   **Option A: Using Python directly**
   ```bash
   uvicorn main:app --reload
   ```
   Then access: http://localhost:8000

   **Option B: Using Docker Compose (Recommended)**
   ```bash
   docker-compose up --build
   ```
   Then access: http://localhost:7005

   **Option C: Using Docker directly**
   ```bash
   # Build the image
   docker build -t timewarrior .
   
   # Run with environment file
   docker run -p 7005:7005 --env-file .env timewarrior
   
   # Or run with individual environment variables
   docker run -p 7005:7005 \
     -e JIRA_URL="https://your-domain.atlassian.net/" \
     -e JIRA_API_TOKEN="your_token_here" \
     -e JIRA_USER_EMAIL="your_email@domain.com" \
     -e JIRA_TARGET_USER="target_user@domain.com" \
     timewarrior
   ```
   Then access: http://localhost:7005

## Environment Variables

- `JIRA_URL`: Your JIRA instance URL (e.g., https://yourcompany.atlassian.net)
- `JIRA_API_TOKEN`: Your JIRA API token
- `JIRA_USER_EMAIL`: Your JIRA user email
- `JIRA_TARGET_USER`: Email of the user whose time logs to fetch

## Features

### 🎯 **Core Functionality**
- Query time logs by date range (today, yesterday, this week, last week, this month, last month, custom)
- Group worklogs by JIRA issue with intelligent expansion (only when multiple logs exist)
- Real-time search and filtering of issues
- CSV export functionality with detailed breakdowns

### 📊 **Enhanced Analytics**
- **Summary cards** showing total time, issues worked, average per issue, and total log count
- **Visual progress bars** displaying relative time distribution across issues
- **Color-coded time indicators** (light/medium/heavy/very heavy workloads)
- **Detailed time breakdowns** with timestamps and context

### 🎨 **Modern UI/UX**
- **Fully responsive design** optimized for mobile, tablet, and desktop
- **Animated interactions** with smooth hover effects and transitions
- **Quick filter buttons** for instant date range switching
- **Real-time search** with instant results
- **Loading states** and user feedback
- **Professional styling** with Bootstrap 5 and custom CSS

### ⚡ **Performance & Reliability**
- **LRU caching** for API responses (128 entries)
- **Request timeouts** (30 seconds) preventing hanging requests
- **Comprehensive error handling** with proper HTTP status codes
- **Input validation** using Pydantic models
- **Structured logging** with different levels (info, warning, error)

### 📱 **Mobile-First Features**
- **Touch-friendly interactions** optimized for mobile devices
- **Collapsible sections** for better space utilization
- **Responsive cards layout** that adapts to screen size
- **Mobile-optimized forms** with improved touch targets

### 🔒 **Security Enhancements**
- **Environment variable configuration** (no hardcoded credentials)
- **Input sanitization** and validation
- **Secure request handling** with proper timeouts
- **Safe data parsing** with graceful error handling

## API Endpoints

- `GET/POST /get_time`: Main interface for querying time logs with enhanced data
- `GET /`: Redirects to `/get_time`