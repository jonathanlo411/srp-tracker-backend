# Imports
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv
from datetime import datetime, timezone
from time import sleep


# Setup
load_dotenv()
MONGO_CLIENT = MongoClient(getenv('MONGO_CONNECTION'))
DATABASE = MONGO_CLIENT[getenv('MONGO_DB_NAME')]
COLLECTION = DATABASE[getenv('MONGO_COLLECTION_NAME')]


# Globals
BASE_URL = "https://hub.shutokorevivalproject.com/timing/points"
LEADERBOARDS = {
    "Combined": r"",
    "Clawies Selection Carpack": r"Clawie%27s%20Selection%20Carpack",
    "Default": r"Default",
    "Traffic": r"Traffic",
    "TrafficSlow": r"TrafficSlow"
}
TRACK_POSITIONS = 100  # Tracks the top X amount of players on the leaderboard


def leaderboard_scraper():
    """
    Scrapes the leaderboard and saves the data to MongoDB.
    This function will be called from the central Flask app.
    """
    try:
        total_pages = TRACK_POSITIONS // 25
        for leaderboard_name, leaderboard_query in LEADERBOARDS.items():
            leaderboard = []
            for page in range(total_pages):
                leaderboard += parse_data(request_page(page, leaderboard_query))
            
            sorted(leaderboard, key=lambda x: x['rank'])
            write_to_mongo(leaderboard_name, leaderboard)

        return {"status": "success", "message": "Leaderboard data scraped and saved"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- Helpers ---


def request_page(page: int, leaderboard: str) -> requests.Response:
    sleep(0.5)
    query_parameters = f"?page={page}&leaderboard={leaderboard}"
    headers = {'Cache-Control': 'no-cache', "Pragma": "no-cache"}
    page_data = requests.get(BASE_URL + query_parameters, headers=headers)
    return page_data


def parse_data(html_data: requests.Response) -> list[dict]:
    soup = BeautifulSoup(html_data.text, 'html.parser')
    data = []
    table_rows = soup.select('table tbody tr')
    for row in table_rows:
        cols = row.find_all('td')
        rank = int(cols[0].text.strip())
        name = cols[1].text.strip()
        points = int(cols[2].text.strip())
        data.append({'rank': rank, 'name': name, 'points': points})
    return data


def write_to_mongo(leaderboard: str, data: dict):
    document = {'datetime': datetime.now(timezone.utc), 'leaderboard': leaderboard, 'data': data}
    COLLECTION.insert_one(document)


# --- Top Level Call ---


if __name__ == '__main__':
    leaderboard_scraper()