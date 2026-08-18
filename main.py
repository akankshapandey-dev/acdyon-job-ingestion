from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import requests
import time

app = FastAPI(title="JobPulse - Resilient Job Ingestion")

SOURCE_URL = "https://jobicy.com/api/v2/remote-jobs"

# Simple in-memory cache
cache = {}

CACHE_TTL = 300  # 5 minutes


def fetch_jobs(keyword: str = ""):
    """
    Fetch jobs from Jobicy's public API.
    Uses timeout, validation and cache fallback.
    """

    # Return cached data for this keyword if it is still fresh
    cache_key = keyword.strip().lower()

    if (
        cache_key in cache
        and cache[cache_key]["jobs"]
        and time.time() - cache[cache_key]["timestamp"] < CACHE_TTL
    ):
        return cache[cache_key]["jobs"], "cache"

    params = {
        "count": 20
    }

    if keyword:
        params["tag"] = keyword

    try:
        response = requests.get(
            SOURCE_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()
        raw_jobs = data.get("jobs", [])

        jobs = []

        for job in raw_jobs:

            # Basic validation / normalization
            if not job.get("jobTitle") or not job.get("companyName"):
                continue

            jobs.append({
                "id": job.get("id"),
                "title": job.get("jobTitle"),
                "company": job.get("companyName"),
                "location": job.get("jobGeo", "Remote"),
                "type": ", ".join(job.get("jobType", [])),
                "level": job.get("jobLevel", ""),
                "industry": ", ".join(job.get("jobIndustry", [])),
                "description": job.get("jobExcerpt", ""),
                "url": job.get("url"),
                "published": job.get("pubDate"),
                "salary_min": job.get("salaryMin"),
                "salary_max": job.get("salaryMax"),
                "salary_currency": job.get("salaryCurrency")
            })

        # Only replace cache after successful ingestion
        if jobs:
            cache[cache_key] = {
                "jobs": jobs,
                "timestamp": time.time()
            }

        return jobs, "live"

    except requests.RequestException:

        # Resilience: return last successful data
        if cache_key in cache and cache[cache_key]["jobs"]:
            return cache[cache_key]["jobs"], "fallback-cache"

        return [], "source-unavailable"


@app.get("/api/jobs")
def get_jobs(
    keyword: str = Query(
        default="",
        description="Optional keyword such as python, java or react"
    )
):
    jobs, source = fetch_jobs(keyword)

    return {
        "status": "success" if jobs else "empty",
        "source": "Jobicy Public Jobs API",
        "mode": source,
        "count": len(jobs),
        "jobs": jobs
    }


@app.get("/", response_class=HTMLResponse)
def home():

    return """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>JobPulse</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f5f7fb;
            color: #172033;
        }

        header {
            background: #111827;
            color: white;
            padding: 24px;
        }

        header h1 {
            margin: 0;
            font-size: 28px;
        }

        header p {
            margin: 8px 0 0;
            color: #cbd5e1;
        }

        .container {
            max-width: 1100px;
            margin: 30px auto;
            padding: 0 20px;
        }

        .controls {
            background: white;
            padding: 20px;
            border-radius: 14px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.06);
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
        }

        input {
            flex: 1;
            padding: 13px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 15px;
        }

        button {
            padding: 13px 20px;
            border: none;
            border-radius: 8px;
            background: #2563eb;
            color: white;
            cursor: pointer;
            font-weight: bold;
        }

        button:hover {
            background: #1d4ed8;
        }

        #status {
            margin-bottom: 18px;
            color: #64748b;
        }

        .jobs {
            display: grid;
            gap: 16px;
        }

        .job {
            background: white;
            padding: 22px;
            border-radius: 14px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            transition: transform 0.2s ease,
                        box-shadow 0.2s ease;
        }

        .job:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 22px rgba(0,0,0,0.09);
        }

        .job h2 {
            margin: 0 0 7px;
            font-size: 20px;
        }

        .company {
            font-weight: bold;
            color: #2563eb;
        }

        .meta {
            color: #64748b;
            font-size: 14px;
            margin: 10px 0;
        }

        .description {
            color: #475569;
            line-height: 1.5;
        }

        .apply {
            display: inline-block;
            margin-top: 14px;
            text-decoration: none;
            background: #111827;
            color: white;
            padding: 9px 14px;
            border-radius: 7px;
        }

        .apply:hover {
            background: #374151;
        }

        .badge {
            display: inline-block;
            background: #e0ecff;
            color: #1d4ed8;
            padding: 4px 8px;
            border-radius: 20px;
            font-size: 12px;
            margin-top: 8px;
        }

        @media (max-width: 600px) {

            .controls {
                flex-direction: column;
            }

            button {
                width: 100%;
            }

            .container {
                padding: 0 12px;
            }

        }

    </style>

</head>


<body>


<header>

    <div class="container">

        <h1>JobPulse</h1>

        <p>
            Resilient job ingestion from a public job source
        </p>

    </div>

</header>


<main class="container">


    <div class="controls">

        <input
            id="keyword"
            placeholder="Search jobs: python, java, react..."
        />

        <button onclick="loadJobs()">
            Refresh Jobs
        </button>

    </div>


    <div id="status">
        Loading jobs...
    </div>


    <div id="jobs" class="jobs"></div>


</main>


<script>


async function loadJobs() {

    const keyword =
        document.getElementById("keyword").value.trim();

    const status =
        document.getElementById("status");

    const jobsContainer =
        document.getElementById("jobs");


    status.innerText =
        "Fetching current listings...";

    jobsContainer.innerHTML = "";


    try {

        const response = await fetch(
            "/api/jobs?keyword=" +
            encodeURIComponent(keyword)
        );


        const data =
            await response.json();


        status.innerText =
            `${data.count} jobs loaded • ${data.mode}`;


        if (!data.jobs.length) {

            jobsContainer.innerHTML =
                "<p>No jobs found.</p>";

            return;
        }


        data.jobs.forEach(job => {

            const card =
                document.createElement("div");


            card.className = "job";


            card.innerHTML = `

                <h2>
                    ${escapeHtml(job.title)}
                </h2>

                <div class="company">
                    ${escapeHtml(job.company)}
                </div>

                <div class="meta">

                    📍 ${escapeHtml(job.location)}

                    &nbsp; • &nbsp;

                    ${escapeHtml(
                        job.type || "Not specified"
                    )}

                </div>


                <span class="badge">

                    ${escapeHtml(
                        job.level || "Job"
                    )}

                </span>


                <p class="description">

                    ${escapeHtml(
                        job.description ||
                        "No summary available."
                    )}

                </p>


                <a
                    class="apply"
                    href="${job.url}"
                    target="_blank"
                    rel="noopener noreferrer"
                >

                    View Listing

                </a>

            `;


            jobsContainer.appendChild(card);

        });


    } catch (error) {

        status.innerText =
            "Unable to load jobs. Please try again.";

        console.error(error);

    }

}


function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent =
        value ?? "";

    return div.innerHTML;

}


loadJobs();


</script>


</body>

</html>
"""


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )