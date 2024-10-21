# gcsbtracker-backend
A backend service written in python that scrapes Google Cloud Skills Boost profiles to track skill badges and arcade game completions. The project leverages the Starlette framework for the backend API, along with a scheduler to periodically update profile data. Users can retrieve profile information through a RESTful API.

![image](https://github.com/user-attachments/assets/78e833e9-fadd-4b27-8399-fdf637fd0a0f)


## Table of Contents
- [Description](#gcsbtracker-backend)
- [Features](#Features)
- [Project Structure](#ProjectStructure)
- [Requirements](#Requirements)
- [Setup](#Setup)
- [Disclaimer](#Disclaimer)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Features
- Scrapes Google Cloud Skills Boost profiles.
- Extracts detailed profile information, including:
    - Username
    - League
    - Membership duration
    - Earned points
    - Badges (with images and earned dates)
- Stores data in a JSON format for easy access.
- Provides an API to fetch all profiles or a specific profile by its ID.
- Includes a scheduler to automatically update profiles at specified intervals.
- Logging system for monitoring server activity.

## Project Structure
```plaintext
gcsbtracker-backend/
├── getData.py              # Script to read CSV, scrape profiles, and save to JSON
├── scraper.py              # Contains the Scraper class for scraping profile data
├── server.py               # The Starlette server for the API
├── requirements.txt        # List of project dependencies
├── profiles_data.json      # Output JSON file for profile data (generated)
├── completed_queries.csv    # CSV file for storing resolved queries
├── templates/              # Directory containing HTML templates for rendering
│   ├── admin_dashboard.html # Template for the admin dashboard
│   ├── admin_login.html     # Template for the admin login page
│   └── homepage.html        # Template for the homepage with query submission
└── static/                 # Directory for serving static files (e.g., CSS)
    ├── styles.css          # Stylesheet for the application
    ├── admin_login.css      # Stylesheet for the admin login
    └── admin_dashboard.css # Stylesheet for the admin dashboard

```
___
## Modifications and Featured Updates

### New Features
1. **Admin Login**: 
   - An admin login system has been implemented, requiring authentication to access the admin dashboard.

![image](https://github.com/user-attachments/assets/8cecedc5-8d67-4ad4-90b3-dc99f48cd78d)


2. **Query Submission and Management**: 
   - Users can submit queries through a form on the homepage.
   - Admins can view, resolve, and manage submitted queries via the admin dashboard.
   - Completed queries are logged and stored in a CSV file (`completed_queries.csv`) with timestamps for tracking purposes.

![image](https://github.com/user-attachments/assets/3e9bebbb-5e35-48d2-86f3-f1d53f0542a8)

3. **Scheduled Data Updates**: 
   - The backend now includes a scheduler that automatically checks for updates and scrapes new data at specified intervals (every 30 minutes).

4. **Enhanced Logging**: 
   - A logging system has been implemented for monitoring server activity and error tracking. Logs are saved in a `server.log` file for further analysis.

5. **Profile Fetching**: 
   - Users can fetch all profiles or a specific profile by its ID via RESTful API endpoints.

### Usage of New Features
- **Admin Login**: 
   - Navigate to `http://localhost:8000/admin/login` to log in as an admin.
   - Use the provided admin ID and password to access the dashboard.

- **Query Submission**: 
   - Navigate to `http://localhost:8000/` to submit queries.
   - Queries submitted by users will be logged and can be managed in the admin dashboard.

- **Profile Fetching**: 
   - To fetch all profiles, run:
     ```bash
     curl http://localhost:8000/profiles
     ```
   - To fetch a specific profile by ID, run:
     ```bash
     curl http://localhost:8000/profiles/id/{profile_id}
     ```

- **Viewing Profiles in a Browser**:
   - Navigate to `http://localhost:8000/profiles/` to view all profiles.
   - Navigate to `http://localhost:8000/profiles/id/{id}` to view a specific profile by its ID.
___
## Requirements
- Python 3.7 or higher
- Required libraries listed in requirements.txt
- A csv file(GCSJ_data.csv) containing all the profile links to run getData.py
- for a single profile scraping use scraper.py

To install the required libraries, run:

```bash
pip install -r requirements.txt
```

## Setup

1. Clone the repository.

```bash
git clone https://github.com/psypherion/gcsbtracker-backend.git
```

2. Navigate to the cloned directory.

```bash
cd gcsbtracker-backend
```

3. Install the required libraries.

```bash
pip install -r requirements.txt
```

4. Run the server.

```bash
uvicorn server:app
```
or, 

```bash
python server.py
```

___
## Disclaimer
With the new V 0.2 Update no need to manually run the getData.py to get the database ready
running the server.py will automatically check for the existence of required files and if the database (profiles_data.json)
not present it'll check for the GCSJ_data.csv if present it'll automatically create the database first and then host the server
and for user firendliness a homepage is also added.

___
## Usage

To fetch all profiles, run:

```bash
curl http://localhost:8000/profiles
```

To fetch a specific profile by ID, run:

```bash
curl http://localhost:8000/profiles/id/{profile_id}
```

### in Browser

1. Navigate to http://localhost:8000/profiles/
![image](https://github.com/user-attachments/assets/187d51b9-99fe-4498-a24e-396d055f3386)

2. Navigate to http://localhost:8000/profiles/id/{id}
![image](https://github.com/user-attachments/assets/6c691cb8-2080-43a8-889c-a239cc9bead9)



## Contributing

If you'd like to contribute to the project, please follow these steps:

1. Create a pull request on GitHub.
2. Add the necessary changes to the README.md file.
3. Submit a pull request to the repository.

## License

This project is licensed under the BSD 2-Clause License

## Support

If you have any questions or feedback, please [open an issue](https://github.com/psypherion/gcsbtracker-backend/issues/new) or [open a pull request](https://github.com/psypherion/gcsbtracker-backend)
