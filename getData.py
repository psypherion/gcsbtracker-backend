import csv
import json
import os  # Import os to check file existence
from typing import List, Dict
from scraper import Scraper
from studyJam import CSVProcessor  


class DataFetcher:
    def __init__(self, csv_file: str, json_file: str, badges_file: str):
        self.csv_file = csv_file
        self.json_file = json_file
        self.badges_file = badges_file

        # Initialize the CSVProcessor to read the filtered badges (GenAI badges)
        self.csv_processor = CSVProcessor(self.csv_file, self.badges_file)

    def read_csv(self) -> List[Dict[str, str]]:
        """Reads the CSV file and returns a list of dictionaries with student names and profile URLs."""
        data: List[Dict[str, str]] = []
        with open(self.csv_file, mode='r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                data.append(row)
        return data

    def check_and_generate_badges_file(self) -> None:
        """
        Checks if the badges JSON file exists. If not, generates it using CSVProcessor.
        
        Args:
            csv_file_path (str): The path to the CSV file used for generating badges.
            badges_file (str): The path to the JSON file to check or generate.
        """
        # Check if the badges JSON file exists
        if not os.path.exists(self.badges_file):
            print(f"{self.badges_file} not found. Generating the file using CSVProcessor...")
            self.csv_processor.process()
        else:
            print(f"{self.badges_file} found. Proceeding with profile extraction.")


    @staticmethod
    def extract_id_from_url(profile_url: str) -> str:
        """Extracts the profile ID from the Google Cloud Skills Boost profile URL."""
        return profile_url.split('/')[-1]

    def load_genai_badges(self) -> List[str]:
        """Loads the GenAI badges from the JSON file."""
        with open(self.badges_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return [badge['title'] for badge in data['genai_badges']]

    def extract_profiles_to_json(self) -> None:
        """Extracts profile information from the CSV and saves it to a JSON file."""
        students = self.read_csv()
        genai_badges = self.load_genai_badges()
        all_profiles: Dict[str, Dict] = {}

        for student in students:
            student_name = student['Student Name']
            profile_url = student['Google Cloud Skills Boost Profile URL']
            profile_id = self.extract_id_from_url(profile_url)

            print(f"Processing profile for: {student_name} - {profile_url}")
            scraper = Scraper(profile_url)
            scraper.fetch_page()
            profile_info = scraper.compile_profile_info()

            # Add the ID to the general section of the profile_info
            profile_info['general']['profile_id'] = profile_id

            # Rename "number_of_badges_earned" to "Number of badges"
            profile_info['general']['Number of badges'] = profile_info['general'].pop('number_of_badges_earned')

            # Count the number of GenAI badges earned
            user_badges = profile_info.get('badges', {})
            genai_badges_earned = {badge: details for badge, details in user_badges.items() if badge in genai_badges}
            
            # Check for "Level 3: Google Cloud Adventures (Game)" badge specifically
            level_3_game_badge_title = "Level 3: Google Cloud Adventures (Game)"
            games_done = genai_badges_earned.get(level_3_game_badge_title, None) is not None
            
            # Adjust the count of GenAI badges if the game badge is earned
            if games_done:
                profile_info['genai_badges_Earned'] = {badge: details for badge, details in genai_badges_earned.items() if badge != level_3_game_badge_title}
            else:
                profile_info['genai_badges_Earned'] = genai_badges_earned

            profile_info['general']['number_of_genai_skill_badges'] = len(profile_info['genai_badges_Earned'])

            # Count the number of "Level 3: Google Cloud Adventures (Game)" badges
            profile_info['general']['games_done'] = int(games_done)  # Will be 1 if true, otherwise 0

            all_profiles[student_name] = profile_info

        with open(self.json_file, 'w', encoding='utf-8') as json_file:
            json.dump(all_profiles, json_file, ensure_ascii=False, indent=4)

        print(f"Profile data extracted and saved to {self.json_file}")



if __name__ == "__main__":
    csv_file_path = "data/genai.csv"
    json_file_path = "profiles_data.json"
    badge_names = "data/badges.json"

    # Now run the DataFetcher process
    data_fetcher = DataFetcher(csv_file_path, json_file_path, badge_names)
    data_fetcher.extract_profiles_to_json()
