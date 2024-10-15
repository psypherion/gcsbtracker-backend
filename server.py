from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import json
from typing import Dict, Any


def load_data(file_path: str) -> Dict[str, Any]:
    """
    Loads profile data from a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        Dict[str, Any]: A dictionary containing the profile data.
    """
    with open(file_path, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


async def profiles(request) -> JSONResponse:
    """
    Displays all the data from the JSON file.

    Args:
        request: The incoming HTTP request.

    Returns:
        JSONResponse: A JSON response containing all profiles.
    """
    data = load_data('profiles_data.json')  
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
        return JSONResponse(profile)
    else:
        return JSONResponse({"error": "Profile not found"}, status_code=404)


# Define the routes
routes: list[Route] = [
    Route('/profiles', profiles),
    Route('/profiles/id/{id}', get_profile),  # Route to fetch by ID
]

# Create the application
app: Starlette = Starlette(debug=True, routes=routes)

# Start the server
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
