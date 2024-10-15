import requests
import re
import html
from typing import List, Dict, Optional
import json

class Scraper:
    def __init__(self, url: str) -> None:
        """
        Initializes the profile scraper with the provided URL.

        Parameters:
            url (str): The URL of the public profile to scrape.
        """
        self.url: str = url
        self.html_content: str = ""

    def fetch_page(self) -> None:
        """Fetches the profile page and stores the HTML content."""
        response: requests.Response = requests.get(self.url)
        if response.status_code == 200:
            self.html_content = response.text
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")

    def get_username(self) -> str:
        """Extracts the username from the HTML content."""
        pattern: str = r"<title>([^|]+)\s*\|\s*Google Cloud Skills Boost</title>"
        match: List[str] = re.findall(pattern, self.html_content)
        return match[0].strip() if match else "Unknown"

    def get_league(self) -> str:
        """Extracts the league from the HTML content."""
        pattern: str = r"<h2 class='ql-headline-medium'>(.*?)</h2>"
        match: List[str] = re.findall(pattern, self.html_content)
        return match[0].strip() if match else "Unknown"

    def get_member_since(self) -> str:
        """Extracts the member since date from the HTML content."""
        pattern: str = r"<p class='ql-body-large l-mbl'>\s*Member since (\d{4})\s*</p>"
        match: List[str] = re.findall(pattern, self.html_content)
        return match[0].strip() if match else "Unknown"

    def get_earned_points(self) -> str:
        """Extracts the earned points from the HTML content."""
        pattern: str = r"<strong>(\d+ points)</strong>"
        match: List[str] = re.findall(pattern, self.html_content)
        return match[0].strip() if match else "0 points"

    def get_profile_image(self) -> str:
        """Extracts the profile image URL from the HTML content."""
        pattern: str = r"<ql-avatar class='profile-avatar l-mbl' size='\d+' src='([^']+)'></ql-avatar>"
        match: List[str] = re.findall(pattern, self.html_content)
        return match[0].strip() if match else "No Image"

    def get_badges(self) -> Dict[str, Dict[str, str]]:
        """Extracts badge names, their corresponding completion dates, and images."""
        badge_pattern: str = (
            r"<div class='profile-badge'>\s*"
            r"<a class=\"badge-image\" href=\"[^\"]*\">"
            r"<img alt=\"Badge for ([^\"]*)\" src=\"([^\"]*)\"\s*[^>]*>\s*</a>"
            r"<span class='ql-title-medium\s+l-mts'>\s*(.*?)\s*</span>"
        )
        date_pattern: str = r"<span class='ql-body-medium\s+l-mbs'>\s*(Earned [^\<]*)\s*</span>"

        badge_matches: List[tuple] = re.findall(badge_pattern, self.html_content)
        date_matches: List[str] = re.findall(date_pattern, self.html_content)

        badge_dict: Dict[str, Dict[str, str]] = {}

        # Extract badges and their details
        for (badge_name, badge_image, _), date in zip(badge_matches, date_matches):
            badge_name = html.unescape(badge_name.strip())
            badge_image = html.unescape(badge_image.strip())
            badge_dict[badge_name] = {
                "badge_image": badge_image,
                "earned_date": date.strip()
            }

        # Add the number of badges earned
        number_of_badges_earned: int = len(badge_dict)
        
        return {
            "badges": badge_dict,
            "number_of_badges_earned": number_of_badges_earned
        }

    def compile_profile_info(self) -> Dict[str, Optional[dict]]:
        """Compiles all profile information into a structured dictionary."""
        badges_info = self.get_badges()  
        profile_data: Dict[str, Optional[dict]] = {
            "profile_name": self.get_username(),
            "general": {
                "league": self.get_league(),
                "member_since": self.get_member_since(),
                "earned_points": self.get_earned_points(),
                "profile_image": self.get_profile_image(),
                "number_of_badges_earned": badges_info["number_of_badges_earned"]  # Include badge count here
            },
            "badges": badges_info["badges"]  
        }
        return profile_data

    def save_to_json(self, data: Dict[str, Optional[dict]]) -> None:
        """Saves the profile data to a JSON file."""
        with open("profile_data.json", "w", encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # URL of the public profile to scrape
    url: str = "https://www.cloudskillsboost.google/public_profiles/e2bff612-4e9a-40b5-b30d-d6138f12fd00"
    
    # Create an instance of Scraper
    badge_scraper: Scraper = Scraper(url)
    
    # Fetch the page content
    badge_scraper.fetch_page()
    
    # Compile the extracted data
    extracted_data: Dict[str, Optional[dict]] = badge_scraper.compile_profile_info()
    
    # Save the extracted data to a JSON file
    badge_scraper.save_to_json(extracted_data)
    
    if extracted_data:
        print("Extracted profile data:")
        print(json.dumps(extracted_data, ensure_ascii=False, indent=4))
    else:
        print("No matching data found.")
