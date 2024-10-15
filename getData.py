import csv
import json
from typing import List, Dict
from scraper import Scraper

def read_csv(file_path: str) -> List[Dict[str, str]]:
    """Reads the CSV file and returns a list of dictionaries with student names and profile URLs."""
    data: List[Dict[str, str]] = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return data

def extract_id_from_url(profile_url: str) -> str:
    """Extracts the profile ID from the Google Cloud Skills Boost profile URL."""
    return profile_url.split('/')[-1]

def extract_profiles_to_json(csv_file: str, json_file: str) -> None:
    """Extracts profile information from the CSV and saves it to a JSON file."""
    students = read_csv(csv_file)
    all_profiles: Dict[str, Dict] = {}

    for student in students:
        student_name = student['Student Name']
        profile_url = student['Google Cloud Skills Boost Profile URL']
        profile_id = extract_id_from_url(profile_url)

        print(f"Processing profile for: {student_name} - {profile_url}")
        scraper = Scraper(profile_url)
        scraper.fetch_page()
        profile_info = scraper.compile_profile_info()

        # Add the ID to the general section of the profile_info
        profile_info['general']['profile_id'] = profile_id

        all_profiles[student_name] = profile_info

    with open(json_file, 'w', encoding='utf-8') as json_file:
        json.dump(all_profiles, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    csv_file_path = "GCSJ_data.csv"
    json_file_path = "profiles_data.json" 

    extract_profiles_to_json(csv_file_path, json_file_path)

    print(f"Profile data extracted and saved to {json_file_path}")
