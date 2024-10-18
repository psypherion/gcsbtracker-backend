import asyncio
import csv
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict

import uvicorn
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from getData import DataFetcher  # Adjust import according to your project structure

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

# Setting up templates for rendering
templates = Jinja2Templates(directory='templates')

# Store queries in memory for simplicity (in production, you should store this in a database)
queries: list[dict[str, str]] = []
resolved_queries: list[dict[str, str]] = []

# Admin credentials
ADMIN_EMAIL = "admin@gcsb.makaut.in"
ADMIN_PASSWORD = "admin6969"

# Check if the JSON file exists
def json_file_exists(file_path: str) -> bool:
    return os.path.exists(file_path)

# Run the data fetching script if needed
async def run_get_data_script() -> None:
    if not json_file_exists("profiles_data.json"):
        logger.info("profiles_data.json not found, attempting to scrape data.")

        if json_file_exists("data/GCSJ_data.csv"):
            logger.info("Found CSV file. Fetching data...")
            fetcher = DataFetcher("data/GCSJ_data.csv", "profiles_data.json")
            fetcher.extract_profiles_to_json()
            logger.info("Data fetching complete, profiles_data.json created.")
        else:
            logger.error("CSV file not found. Cannot scrape data.")

    else:
        logger.info("profiles_data.json found, starting server...")

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

# Serve the homepage with buttons and query submission form
async def homepage(request):
    if request.method == 'POST':
        form = await request.form()
        user_query = form.get('query')

        # Save the query
        queries.append({"query": user_query})
        logger.info(f"New query submitted: {user_query}")

        # Simulate push notification
        logger.info("Push notification sent to admin for new query")

        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse('homepage.html', {"request": request})

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

# Login form handling
async def admin_login(request):
    if request.method == 'POST':
        form = await request.form()
        email = form.get('email')
        password = form.get('password')

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            request.session['is_admin'] = True
            return RedirectResponse('/admin/dashboard', status_code=303)
        else:
            return templates.TemplateResponse('admin_login.html', {"request": request, "error": "Invalid credentials"})

    return templates.TemplateResponse('admin_login.html', {"request": request})

# Function to save completed query to CSV
def save_completed_query(query: str, timestamp: str) -> None:
    with open('completed_queries.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([query, timestamp])

# Admin dashboard with authentication check
async def admin_dashboard(request):
    global resolved_queries
    if not request.session.get('is_admin'):
        return RedirectResponse('/admin/login')

    if request.method == 'POST':
        form = await request.form()
        selected_query = form.get('selected_query')
        if selected_query:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_completed_query(selected_query, timestamp)
            logger.info(f"Query marked as completed: {selected_query} at {timestamp}")

            # Move the selected query to resolved
            resolved_queries.append({"query": selected_query, "timestamp": timestamp})
            queries[:] = [query for query in queries if query['query'] != selected_query]

            return RedirectResponse('/admin/dashboard', status_code=303)

    return templates.TemplateResponse('admin_dashboard.html', {
        "request": request,
        "queries": queries,
        "resolved_queries": resolved_queries
    })

# Data fetching function to run every 30 minutes
async def run_data_fetcher() -> None:
    while True:
        await run_get_data_script()
        await asyncio.sleep(1800)  # Sleep for 30 minutes

# Define routes
routes = [
    Route('/', homepage, methods=["GET", "POST"]),
    Route('/profiles', profiles),
    Route('/profiles/id/{id}', get_profile),
    Route('/admin/dashboard', admin_dashboard, methods=["GET", "POST"]),
    Route('/admin/login', admin_login, methods=["GET", "POST"]),
]

# Mount the static files directory
app = Starlette(debug=True, routes=routes)
app.mount('/static', StaticFiles(directory='static'), name='static')

# Middleware for sessions
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # Run the data fetching script if needed before starting the server
    loop.run_until_complete(run_get_data_script())

    # Schedule the scraper task
    loop.create_task(run_data_fetcher())

    logger.info("Starting server...")
    uvicorn.run(app, host='0.0.0.0', port=8000)
    logger.info("Server stopped.")
