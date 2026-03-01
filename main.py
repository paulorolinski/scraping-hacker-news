import time
from scraper import scrape_hacker_news
from analysis import analyze_data, export_reports
from charts import generate_all

if __name__ == "__main__":
    scrape_hacker_news()
    time.sleep(1)
    analyze_data()
    export_reports()
    generate_all()