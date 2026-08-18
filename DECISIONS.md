# DECISIONS.md

## 1. Why this ingestion strategy?

I chose the Jobicy public jobs API as the ingestion source because the challenge explicitly allows a low-risk public job-board API/RSS source. It provides structured job data without requiring access to a live LinkedIn, Indeed, Naukri, or Wellfound account.

The obvious alternative was scraping a commercial job platform directly. I rejected that approach because those platforms actively use bot detection, rate limiting, CAPTCHAs, and other controls. Using a public API demonstrates the ingestion flow end-to-end without creating unnecessary account, IP, or Terms-of-Service risk.

## 2. One trade-off

The main trade-off was choosing a simpler public API integration instead of building a more complex multi-source scraping system within the available time. With a full week, I would add source adapters and stronger failure handling so that the pipeline could switch to another permitted public source if Jobicy became unavailable or changed its API.

## 3. AI usage

I used AI tools to help with implementation guidance, API integration, debugging, and structuring the project. I personally reviewed the implementation and verified that the Jobicy endpoint returns live job data successfully, including the HTTP 200 response and job listing fields. I also made sure the final approach stays within the challenge's low-risk public-source scope rather than relying on a live LinkedIn or other protected account.
