from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import json
import asyncio
import subprocess
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the log level to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),  # Log to a file
        logging.StreamHandler()  # Also log to the console
    ]
)

logger = logging.getLogger(__name__)

def load_data(file_path: str) -> Dict[str, Any]:
    """
    Loads profile data from a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        Dict[str, Any]: A dictionary containing the profile data.
    """
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

async def profiles(request) -> JSONResponse:
    """
    Displays all the data from the JSON file.

    Args:
        request: The incoming HTTP request.

    Returns:
        JSONResponse: A JSON response containing all profiles.
    """
    data = load_data('profiles_data.json')  
    logger.info("Retrieved all profiles.")
    return JSONResponse(data)

async def get_profile(request) -> JSONResponse:
    """
    API Endpoint to retrieve profiles by profile_id.

    Args:
        request: The incoming HTTP request.

    Returns:
        JSONResponse: A JSON response with the requested profile or an error message.
    """
    profile_id: str = request.path_params['id']
    data: Dict[str, Any] = load_data('profiles_data.json')  

    # Find the profile by ID
    profile: Dict[str, Any] = {}
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

async def run_get_data_script() -> None:
    """
    Runs the getData.py script at regular intervals.
    """
    while True:
        logger.info("Running getData.py to update profiles...")
        try:
            subprocess.run(["python", "getData.py"], check=True)
            logger.info("Successfully updated profiles.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error while running getData.py: {e}")
        await asyncio.sleep(1800)  # Wait for 30 minutes (1800 seconds)

# Define the routes
routes: list[Route] = [
    Route('/profiles', profiles),
    Route('/profiles/id/{id}', get_profile),  # Route to fetch by ID
]

# Create the application
app: Starlette = Starlette(debug=True, routes=routes)

# Start the server and the scheduler
if __name__ == '__main__':
    import uvicorn

    # Start the scheduler in the background
    loop = asyncio.get_event_loop()
    loop.create_task(run_get_data_script())

    logger.info("Starting server...")
    uvicorn.run(app, host='0.0.0.0', port=8000)
    logger.info("Server stopped.")
