# Meeting 01: Project Kickoff & Architecture Alignment
**Date:** March 14, 2026
**Project:** SPM (NVIDIA Stock Price Prediction Pipeline)

## Team Roles & Responsibilities

* **Dibbo (Architect / Tech Lead):**
  * **Work Completed:** Cleaned up the legacy file structure, initialized the Django project foundation, integrated psycopg (version 3) for the database backend, implemented the DbExtra utility class for standardized batch insertions, and created the pipeline skeleton (yfinance_api.py and yfinance_prices.py). Configured Git flow to protect local database credentials.
  * **Ongoing:** Overseeing repository architecture, reviewing PRs, and unblocking the team.

* **Paul (Data Engineering / API):**
  * **Current Task:** Implementing the yfinance data extraction, transformation, and PostgreSQL batch insertion logic based on the provided Django command skeletons.
  * **Ongoing:** Managing data imports, handling API rate limits, and ensuring clean data flows into the database.

* **Mustafa (Machine Learning Engineer):**
  * **Future Task:** Will lead the ML modeling and predictive analytics phase.
  * **Ongoing:** Will utilize the currently empty notebooks/ directory to build Jupyter notebooks for data exploration, model training, and stock prediction once the database is populated.

## Next Steps
1. Paul to complete the Jira task for the NVDA data import pipeline and push for review.
2. Team to verify local PostgreSQL setups using settings_local.py.
3. Mustafa to begin researching baseline ML approaches for time-series stock prediction.