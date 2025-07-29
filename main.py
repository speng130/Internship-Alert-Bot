import os
import requests
import openai
import feedparser
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

KEYWORDS = ['sales and trading', 's&t', 'm&a', 'wealth management', 'pwm', 'private equity', 'private markets', 'capital markets', 'buy-side', 'investment research', 'structured products', 'fixed income']

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=data)

def contains_keywords(text):
    return any(k in text.lower() for k in KEYWORDS)

def filter_with_gpt(job_title, job_description, url):
    if not contains_keywords(job_title + " " + job_description):
        return None

    prompt = f"""
You are an AI assistant. Evaluate the following job posting:

Title: {job_title}

Description:
{job_description}

Only respond with a brief 2-sentence summary if the posting is for:
- a summer internship (2026 or 2027)
- in investment banking, finance, private equity, or wealth management
- located in the U.S., Canada, UK, or Europe
- matches any of the following: sales and trading, s&t, m&a, wealth management, pwm, private equity, private markets, capital markets, buy-side, investment research, structured products, fixed income

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

def fetch_efinancialcareers_jobs():
    feed = feedparser.parse("https://www.efinancialcareers.com/jobs-Internships.s024")
    for entry in feed.entries:
        title = entry.title
        desc = entry.summary
        link = entry.link
        result = filter_with_gpt(title, desc, link)
        if result:
            send_telegram_message(result)

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
            result = filter_with_gpt(title, desc, href)
            if result:
                send_telegram_message(result)

def fetch_citi_jobs():
    jobs = [("Citi 2026 Summer Analyst – Capital Markets", "Internship in NY in fixed income trading", "https://jobs.citi.com")]
    for title, desc, link in jobs:
        result = filter_with_gpt(title, desc, link)
        if result:
            send_telegram_message(result)

def fetch_kkr_jobs():
    jobs = [("KKR Private Equity Intern 2026", "Internship opportunity for PE team in New York", "https://www.kkr.com/careers")]
    for title, desc, link in jobs:
        result = filter_with_gpt(title, desc, link)
        if result:
            send_telegram_message(result)

def fetch_blackstone_jobs():
    jobs = [("Blackstone Summer 2026 Intern – PWM", "Internship in Private Wealth in HK", "https://blackstone.wd1.myworkdayjobs.com")]
    for title, desc, link in jobs:
        result = filter_with_gpt(title, desc, link)
        if result:
            send_telegram_message(result)

def fetch_carlyle_jobs():
    jobs = [("Carlyle 2026 Summer Intern – M&A", "Rotational internship in DC office", "https://carlyle.taleo.net")]
    for title, desc, link in jobs:
        result = filter_with_gpt(title, desc, link)
        if result:
            send_telegram_message(result)

if __name__ == "__main__":
    send_telegram_message("✅ Internship Alert Bot is checking postings...")
    fetch_nomura_jobs()
    fetch_bankofamerica_jobs()
    fetch_efinancialcareers_jobs()
    fetch_citi_jobs()
    fetch_kkr_jobs()
    fetch_blackstone_jobs()
    fetch_carlyle_jobs()
