# JobPulse - Resilient Job Ingestion

JobPulse is a FastAPI-based job ingestion application that fetches remote job listings from Jobicy's public job API.

## Features

- Fetches remote job listings from Jobicy API
- Search jobs using keywords such as Python, Java and React
- Displays up to 20 job listings
- Per-keyword in-memory caching
- 5-minute cache TTL
- API timeout handling
- Response validation and normalization
- Fallback to previously cached jobs when the external API is unavailable
- Responsive web interface
- Direct "View Listing" links for jobs

## Technology Stack

- Python
- FastAPI
- Uvicorn
- Requests
- HTML
- CSS
- JavaScript

## Project Structure

```text
acdyon-job-ingestion/
│
├── main.py
├── README.md
└── .venv/