# indeed_scraper
Automated Indeed job scraper built with nodriver that bypasses Cloudflare challenges and performs targeted job searches. It extracts job titles, company names, and full descriptions, saving them to CSV files and organized text documents. The scraper navigates through all result pages automatically until completion.

Indeed Job Scraper (NoDriver + Cloudflare Bypass)

This project is an automated job-scraping tool built using NoDriver, designed to navigate Indeed.com, bypass Cloudflare’s Turnstile challenges, perform job searches, and extract job details including:

Job title

Company name

Full job description

All newly discovered jobs are saved to:

job_list.csv

/job_descriptions/ (each job description stored as a separate text file)

🚀 Features 
✔️ Bypasses Cloudflare Turnstile Checkbox

Automatically detects Cloudflare verification and simulates a real user click.

✔️ Automated Job Search

Performs an “easy search”

Applies additional filters (keyword + location)

✔️ Avoids Duplicate Results

Before saving any job, it checks job_list.csv.

✔️ Saves Job Descriptions

Stores each job’s full description in /job_descriptions/.

✔️ Cookie Persistence

Automatically loads & saves Cloudflare cookies to a .session.dat file.

🛠 Requirements Python Version

Python 3.9+ recommended.

Install Dependencies pip install nodriver asyncio

Also make sure you have:

csv (built-in)

json

datetime

re

These are included in Python by default.

📁 Project Structure |-- main.py |-- job_list.csv |-- job_descriptions/ |-- .session.dat |-- README.md

▶️ How to Run

Clone the repository:

git clone https://github.com/yourusername/indeed-scraper.git cd indeed-scraper

Run the script:

python main.py

The script will:

Start NoDriver browser

Attempt to load Cloudflare cookies

Bypass Cloudflare if required

Perform job search

Extract job listings

Save results locally

📌 CSV Output Example

job_list.csv:

jobTitle,companyName AI Engineer,TechCorp ML Engineer,DataLab

📌 Job Description Output Example

Files saved in /job_descriptions/:

TechCorp_AI Engineer_02:14PM on December 02, 2025

Each file contains the full scraped job description.

⚠️ Disclaimer

This tool is for educational purposes only. Scraping Indeed or bypassing Cloudflare may violate their Terms of Service. Use responsibly.
