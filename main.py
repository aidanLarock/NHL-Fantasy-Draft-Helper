import requests
from bs4 import BeautifulSoup
import pandas as pd
from values import FORWARD_VALUES, DEFENSE_VALUES, GOALIE_VALUES
import re

# URL of the webpage for a specific player
url = "https://www.hockey-reference.com/players/m/mcdavco01.html#all_stats_basic_plus_nhl"

try:
    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the webpage using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the table with the specified ID
        table = soup.find("table", {"id": "stats_basic_plus_nhl"})

        # Extract table headers (column names)
        existing_headers = set()
        headers = []

        for th in table.find_all("th", scope="col"):
            header_text = th.get_text()
            if header_text in existing_headers:
                header_text += '_2'
            existing_headers.add(header_text)
            headers.append(header_text)

        # Extract data rows from the table
        data_rows = []
        for row in table.find("tbody").find_all("tr"):
            data_row = [td.get_text() for td in row.find_all("td")]
            # Ensure data rows have the same number of columns as headers
            if len(data_row) != len(headers):
                # You can choose to pad or trim the row to match the number of columns
                # For example, padding with empty strings:
                data_row += [''] * (len(headers) - len(data_row))
                # Alternatively, you can choose to skip rows that don't match
                # continue
            data_rows.append(data_row)

        # Create a pandas DataFrame from the extracted data
        df = pd.DataFrame(data_rows, columns=headers)

        # Shift the columns to account for the shift
        df = df.shift(axis=1)

        # Remove the "Age," "Season," and "Team" columns
        df.drop(["Age", "Season", "Tm", "Lg", "EV", "EV_2", "GW", "S%", "TSA", "TOI", "ATOI", "FOL", "FO%", "Awards"], axis=1, inplace=True)

        # Combine and add 'PP' and 'PP_2'
        df['PP'] = df['PP'].astype(float) + df['PP_2'].astype(float)

        # Combine and add 'SH' and 'SH_2'
        df['SH'] = df['SH'].astype(float) + df['SH_2'].astype(float)

        # Drop the '_2' columns as they are no longer needed
        df.drop(['PP_2', 'SH_2'], axis=1, inplace=True)

        # Function to clean and convert a value to float
        def clean_and_convert(value):
            # Check if the value is already a float or int
            if isinstance(value, (float, int)):
                return float(value)

            # Remove commas and any non-numeric characters (except for periods, which can be in floats)
            cleaned_value = re.sub(r'[^\d.]+', '', str(value))
            if cleaned_value:
                return float(cleaned_value)
            return 0.0

        # Calculate points for each season based on player type (forward, defense, or goalie)
        def calculate_points(row, player_type):
            values = None
            if player_type == "Forward":
                values = FORWARD_VALUES
            elif player_type == "Defense":
                values = DEFENSE_VALUES
            elif player_type == "Goalie":
                values = GOALIE_VALUES

            total_points = 0
            if values is not None:
                for column, value in values.items():
                    cell_value = row[column]

                    # Clean and convert the cell value to a float
                    cleaned_value = clean_and_convert(cell_value)

                    # Calculate the points for the specific statistic and add it to the total
                    statistic_points = cleaned_value * value
                    total_points += statistic_points
            else:
                return 0.0
            return total_points

        # Create a new column 'Points' in the DataFrame
        df['Points Made'] = df.apply(lambda row: calculate_points(row, "Forward"), axis=1)
            # Convert 'Points Made' and 'GP' columns to float
        df['Points Made'] = df['Points Made'].astype(float)
        df['GP'] = df['GP'].astype(float)

        # Calculate Points Per Game (PPG)
        df['PPG'] = df['Points'] / df['GP']

        # Display the updated DataFrame with the 'PPG' column
        print(df)

        # Display the updated DataFrame with the 'Points' column
        #print(df)

    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)

except requests.exceptions.RequestException as e:
    print("Error during the request:", e)

except Exception as ex:
    print("An error occurred:", ex)
