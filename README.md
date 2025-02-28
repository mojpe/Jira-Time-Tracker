# Jira Time Tracker Instructions

## Overview
The Jira Time Tracker is a FastAPI application that allows users to track time logged on Jira issues. It fetches time logs based on specified date ranges and displays the results on a web interface.

## Prerequisites
- Docker and Docker Compose installed on your system.
- Access to a Jira account with API permissions.

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd <repository-dir>
   ```

2. **Configure the Application**
   - Open the `config.yaml` file and update the following fields with your Jira credentials:
     ```yaml
     JIRA_URL: "https://your-jira-instance.atlassian.net/"
     API_TOKEN: "your-jira-api-token"
     USER_EMAIL: "your-email@example.com"
     TARGET_USER: "target-user-email@example.com"
     ```

3. **Build and Run the Application**
   - Use Docker Compose to build and run the application:
     ```bash
     docker-compose up --build
     ```

4. **Access the Application**
   - Open your web browser and navigate to `http://localhost:7005` to access the Jira Time Tracker interface.

## Usage

- **Select Date Range**: Choose a predefined date range (e.g., today, this week, last month) or select "custom" to specify a custom date range.
- **View Time Logs**: The application will display the total time logged and detailed worklogs for the selected date range.

## Customization

- **Styling**: Modify `static/css/styles.css` to customize the application's appearance.
- **JavaScript**: Update `static/js/script.js` to add or modify client-side functionality.

## Troubleshooting

- If you encounter any errors, check the logs in the terminal where Docker Compose is running for more details.
- Ensure your Jira API credentials are correct and have the necessary permissions.
