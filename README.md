# SRP Tracker Backend
<a  href="https://github.com/jonathanlo411/srp-tracker-backend/releases"><img  src="https://img.shields.io/github/v/release/jonathanlo411/srp-tracker-backend"></a><a  href="https://github.com/jonathanlo411/srp-tracker-backend/blob/main/LICENSE"><img  src="https://img.shields.io/github/license/jonathanlo411/srp-tracker-backend"></a>

## Overview
This is the backend of SRP Tracker. It consists of two parts: Cron scripts and a Flask server. The Cron scripts are triggered via Vercel and scrapes [https://hub.shutokorevivalproject.com/timing/points](https://hub.shutokorevivalproject.com/timing/points) for data. The Flask server serves as a proxy to access the data stored in the database.

## Local Usage
1. Clone the repository.
2. Install packages via virtual environment.
```bash
python -m venv .venv
source .venv/bin/activate  # or ./venv/Scripts/activate on windows
pip install -r requirements.txt
```
3. Fill out your environment details into a `.env` mimicking the `sample.env` .
4. Run the following commands
```
# For Flask server
flask --app api/app run --debug

# For Cron script
python cron/leaderboardPointsCrawler.py
```

## License
This project is licensed under the GNU General Public License. See `LICENSE` for more information.