from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route
from starlette.staticfiles import StaticFiles
import json
import asyncio
import subprocess
import logging
from typing import Dict, Any
import os
import uvicorn
from getData import DataFetcher  

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Check if the JSON file exists
def json_file_exists(file_path: str) -> bool:
    return os.path.exists(file_path)

# Load data from the JSON file
def load_data(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            logger.info(f"Loading data from {file_path}")
            return json.load(json_file)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {file_path}")
        return {}

# Serve the homepage with buttons once data is fetched
async def homepage(request) -> HTMLResponse:
    with open("templates/homepage.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(html_content)

# Display all profiles
async def profiles(request) -> JSONResponse:
    data = load_data('profiles_data.json')
    logger.info("Retrieved all profiles.")
    return JSONResponse(data)

# Display a single profile by ID
async def get_profile(request) -> JSONResponse:
    profile_id = request.path_params['id']
    data = load_data('profiles_data.json')
    
    profile = {}
    for name, info in data.items():
        if info['general']['profile_id'] == profile_id:
            profile = {name: info}
            break
    
    if profile:
        logger.info(f"Profile found for ID: {profile_id}")
        return JSONResponse(profile)
    else:
        logger.warning(f"Profile not found for ID: {profile_id}")
        return JSONResponse({"error": "Profile not found"}, status_code=404)

# Run the data fetching script if needed
async def run_get_data_script() -> None:
    """
    Checks if profiles_data.json exists. If not, runs the getData.py script
    to fetch data and creates the file.
    """
    if not json_file_exists("profiles_data.json"):
        logger.info("profiles_data.json not found, attempting to scrape data.")
        
        # Check if CSV exists
        if json_file_exists("data/GCSJ_data.csv"):
            logger.info("Found CSV file. Fetching data...")
            
            # Create a DataFetcher instance and extract profiles to JSON
            fetcher = DataFetcher("data/GCSJ_data.csv", "profiles_data.json")
            fetcher.extract_profiles_to_json()

            logger.info("Data fetching complete, profiles_data.json created.")
        else:
            logger.error("CSV file not found. Cannot scrape data.")
            return
    else:
        logger.info("profiles_data.json found, starting server...")

# Define routes
routes = [
    Route('/', homepage),  # Homepage with buttons for interaction
    Route('/profiles', profiles),
    Route('/profiles/id/{id}', get_profile)  # Fetch by profile ID
]

# Mount the static files directory
app = Starlette(debug=True, routes=routes)
app.mount('/static', StaticFiles(directory='static'), name='static')  # Serve static files like styles.css

# Start the server and the scheduler
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_get_data_script())  
    logger.info("Starting server...")
    uvicorn.run(app, host='0.0.0.0', port=8000)
    logger.info("Server stopped.")
