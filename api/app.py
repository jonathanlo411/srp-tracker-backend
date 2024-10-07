# Imports
from flask import Flask, request, Response, redirect, url_for, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from os import getenv
from pymongo import MongoClient


# Setup
load_dotenv()
MONGO_CLIENT = MongoClient(getenv('MONGO_CONNECTION'))
DATABASE = MONGO_CLIENT[getenv('MONGO_DB_NAME')]
COLLECTION = DATABASE[getenv('MONGO_COLLECTION_NAME')]
app = Flask(__name__)
CORS(app)


# Globals
LEADERBOARDS = [
    'Combined',
    'Clawies Selection Carpack',
    'Default',
    'Traffic',
    'TrafficSlow'
]


@app.route('/')
def root() -> Response:
    """
    Handles requests to the root endpoint.

    This endpoint redirects users to the /docs endpoint, where documentation can be found.

    Methods:
        GET: Redirects to the /docs endpoint.

    Returns:
        Response: A redirect response to the /docs URL.
    """
    return redirect(url_for('docs'))


@app.route('/docs')
def docs() -> Response:
    """
    Handles requests to the /docs endpoint.

    This endpoint serves the main documentation page.

    Methods:
        GET: Renders the index.html template for documentation.

    Returns:
        Response: The rendered HTML page containing the documentation.
    """
    return render_template('index.html')


# --- APIs ---
@app.route('/status', methods=['GET'])
def status() -> Response:
    """
    Handles requests to the /status endpoint.

    This endpoint can be used to check the health of the server. 
    It responds with a message indicating that the server is running.

    Methods:
        GET: Retrieves the current status of the server.

    Returns:
        Response: A JSON object containing a message and an HTTP status code 200
    """
    return {"msg": 'Status OK, server is running'}, 200


@app.route('/leaderboard', methods=['GET'])
def get_leaderboard() -> Response:
    """
    Retrieves the leaderboard data from the MongoDB collection.

    This endpoint fetches documents from the leaderboard collection, 
    filtered by a required leaderboard identifier provided as a query parameter.

    Methods:
        GET: Fetches the leaderboard data.

    Query Parameters:
        leaderboard (str): A required query parameter to filter the leaderboard data 
                           based on its identifier.

    Returns:
        Response: A JSON object containing the leaderboard data and an HTTP status code.
                  If no data is found, returns an empty list with a status code 404.
    """
    # Get leaderboard
    leaderboard_param = request.args.get('leaderboard')
    if not leaderboard_param:
        return {"error": "The 'leaderboard' query parameter is required."}, 400
    if leaderboard_param not in LEADERBOARDS:
        return {"error": f"Leaderboard must be on of the following: {LEADERBOARDS}"}, 400

    # Get leaderboard data from MongoDB and return
    leaderboard_data = list(COLLECTION.find({'leaderboard': leaderboard_param}, {'_id': 0}))
    if leaderboard_data:
        return leaderboard_data, 200
    else:
        return {"data": []}, 404  # No data found