import csv
import json
from typing import List, Dict

class CSVProcessor:
    """
    A class to process a CSV file, read headings, filter unwanted headings, and save them in a JSON format.
    """

    def __init__(self, csv_file: str, json_file: str):
        """
        Initializes the CSVProcessor with the path to the CSV file and the path where the JSON output will be saved.

        :param csv_file: Path to the CSV file.
        :param json_file: Path to the JSON file.
        """
        self.csv_file = csv_file
        self.json_file = json_file

    def read_csv_headings(self) -> List[str]:
        """
        Reads the headings from the first row of a CSV file and filters out unwanted headings.

        :return: A list of filtered headings.
        """
        try:
            with open(self.csv_file, mode='r', newline='', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                headings = next(reader)
                unwanted_headings = ["Student Name", "Google Cloud Skills Boost Profile URL"]
                return [heading for heading in headings if heading not in unwanted_headings]
        except FileNotFoundError:
            print(f"File not found: {self.csv_file}")
            return []
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return []

    def format_headings(self, headings: List[str]) -> Dict[str, List[Dict[str, str]]]:
        """
        Formats the list of headings into a JSON-compatible dictionary format.

        :param headings: List of headings to format.
        :return: A dictionary following the format:
                 {
                     "genai_badges": [
                         {
                             "id": <id>,
                             "title": <heading_title>
                         },
                         ...
                     ]
                 }
        """
        return {
            "genai_badges": [
                {"id": idx + 1, "title": heading}
                for idx, heading in enumerate(headings)
            ]
        }

    def save_to_json(self, data: Dict) -> None:
        """
        Saves a dictionary as a JSON file.

        :param data: The dictionary to save.
        """
        try:
            with open(self.json_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Headings saved to {self.json_file}")
        except Exception as e:
            print(f"Error saving to JSON file: {e}")

    def process(self) -> None:
        """
        Orchestrates the full process: reading the CSV file, formatting the headings, and saving to JSON.
        """
        headings = self.read_csv_headings()
        if headings:
            formatted_data = self.format_headings(headings)
            self.save_to_json(formatted_data)

            print("Headings found in the CSV file:")
            for heading in headings:
                print(f"heading: {heading}")
        else:
            print("No headings found or unable to read the file.")


if __name__ == "__main__":
    # Example usage
    csv_file = 'data/genai.csv'
    json_file = 'data/badges.json'

    processor = CSVProcessor(csv_file, json_file)
    processor.process()
