import requests
from dotenv import load_dotenv
from os import getenv
from bs4 import BeautifulSoup
from time import sleep
from pymongo import MongoClient
from pymongo.results import InsertOneResult
from datetime import datetime, timezone

# Setup
load_dotenv()
MONGO_CLIENT = MongoClient(getenv('MONGO_CONNECTION'))
DATABASE = MONGO_CLIENT[getenv('MONGO_DB_NAME')]
COLLECTION = DATABASE[getenv('MONGO_COLLECTION_NAME')]

# Globals
BASE_URL = "https://hub.shutokorevivalproject.com/timing/points"
LEADERBOARDS = {
    "Combined" :r"",  # 
    "Clawies Selection Carpack" :r"Clawie%27s%20Selection%20Carpack",
    "Default" :r"Default",
    "Traffic" :r"Traffic",
    "TrafficSlow" :r"TrafficSlow"
}
TRACK_POSITIONS = 100   # Tracks the top X amount of players on the leaderboard


def main():
    # Search through all leaderboards and get top positions
    total_pages = TRACK_POSITIONS // 25
    for leaderboard_name, leaderboard_query in LEADERBOARDS.items():
        print(f"Processing: {leaderboard_name}")

        # Obtain leaderboard data
        leaderboard = []
        for page in range(total_pages):
            leaderboard += (parse_data(request_page(page, leaderboard_query)))
        
        # Format and save to DB
        sorted(leaderboard, key=lambda x: x['rank'])
        write_to_mongo(leaderboard_name, leaderboard)


# --- Helpers ---

def request_page(page: int, leaderboard: str) -> requests.Response:
    """
    Makes a request to the leaderboard.

    Parameters:
        page (int): The page of the leaderboard to reqyest
        leaderboard (str): The type of leaderboard to request
    
    Returns:
        page_data (Response): Returns a requests Response object of the 
            leaderboard data
    """
    # Making request
    sleep(0.5)
    query_parameters = f"?page={page}&leaderboard={leaderboard}"
    headers = {
        'Cache-Control': 'no-cache',
        "Pragma": "no-cache"
    }
    page_data = requests.get(BASE_URL + query_parameters, headers=headers)
    return page_data


def parse_data(html_data: requests.Response) -> list[dict]:
    """
    Takes in raw HTML leaderboard data and parses out a list of objects
    containing rank, name, and the points.

    Parameters:
        html_data (Response): Contains the leaderboard request information via HTML
            in the form of a requests Response object

    Returns:
        data (list[dict]): A list of dictionaries containg rank, name, and points
    """
    soup = BeautifulSoup(html_data.text, 'html.parser')
    data = []
    table_rows = soup.select('table tbody tr')
    for row in table_rows:
        cols = row.find_all('td')
        rank = int(cols[0].text.strip())
        name = cols[1].text.strip()
        points = int(cols[2].text.strip())
        data.append({
            'rank': rank,
            'name': name,
            'points': points
        })
    return data


def write_to_mongo(leaderboard: str, data: dict) -> InsertOneResult:
    """
    Inserts a document into a MongoDB collection containing the current UTC datetime,
    a leaderboard identifier, and associated data.

    Parameters:
        leaderboard (str): A string identifier for the leaderboard, indicating its source or type
        data (dict): A dictionary containing additional information related to the leaderboard,
            typically including player rankings and scores

    Returns:
        result (InsertOneResult): The result of the insert operation, which includes information about the
            inserted document, such as its ID.
    """
    # Create the document with datetime and leaderboard data
    document = {
        'datetime': datetime.now(timezone.utc),
        'leaderboard': leaderboard,
        'data': data
    }

    # Insert the document into the collection
    result = COLLECTION.insert_one(document)
    return result


# --- Top level call ---

if __name__ == '__main__':
    main()