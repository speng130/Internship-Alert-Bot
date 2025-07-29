
# main.py
import os
import requests
import openai
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=data)

def contains_required_terms(text):
    required_terms = ["internship", "summer", "2026", "2027"]
    text_lower = text.lower()
    return any(term in text_lower for term in required_terms)

def filter_with_gpt(job_title, job_description, url):
    prompt = f"""
You are an AI assistant. Evaluate the following job posting:

Title: {job_title}

Description:
{job_description}

Only respond with a brief 2-sentence summary if the posting is for:
- a summer internship (2026 or 2027)
- in investment banking, finance, or wealth management
- located in the U.S. or Hong Kong

If it doesn't match, reply "irrelevant".
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        summary = response.choices[0].message.content.strip()
        if summary.lower() != "irrelevant":
            return f"<b>{job_title}</b>\n{summary}\n🔗 {url}"
    except Exception as e:
        print(f"GPT error: {e}")
    return None

def fetch_nomura_jobs():
    url = "https://nomuracampus.tal.net/vx/lang-en-GB/mobile-0/appcentre-ext/brand-4/candidate/jobboard/vacancy/1/adv/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = soup.find_all("article")

    for job in jobs:
        link = job.find("a")
        title = link.text.strip()
        href = "https://nomuracampus.tal.net" + link.get("href")
        desc = job.text.strip()
        if contains_required_terms(title + " " + desc):
            result = filter_with_gpt(title, desc, href)
            if result:
                send_telegram_message(result)

def fetch_bankofamerica_jobs():
    url = "https://careers.bankofamerica.com/en-us/job-search?keywords=summer%20analyst"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = soup.find_all("li", class_="search-result")

    for job in jobs:
        title_tag = job.find("a", class_="search-result__title")
        if title_tag:
            title = title_tag.text.strip()
            href = "https://careers.bankofamerica.com" + title_tag.get("href")
            desc = job.text.strip()
            if contains_required_terms(title + " " + desc):
                result = filter_with_gpt(title, desc, href)
                if result:
                    send_telegram_message(result)

if __name__ == "__main__":
    fetch_nomura_jobs()
    fetch_bankofamerica_jobs()
