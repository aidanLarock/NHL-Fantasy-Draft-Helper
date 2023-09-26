import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Define the base URL
base_url = "https://www.hockey-reference.com/players/"

# Initialize an empty list to store player names
all_player_names = []

# Loop through the alphabet (from 'a' to 'z')
for letter in range(ord('a'), ord('z')+1):
    # Generate the URL for the current letter
    url = base_url + chr(letter) + "/"

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the webpage using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all strong tags
        strong_tags = soup.find_all("strong")

        # Extract and store the text from strong tags
        player_names = [strong.get_text() for strong in strong_tags]

        # Add the player names to the list
        all_player_names.extend(player_names)
    else:
        print(f"Failed to retrieve the webpage for letter '{chr(letter)}'. Status code:", response.status_code)

    # Add a delay to avoid overloading the server
    time.sleep(1)  # You can adjust the delay time (in seconds) as needed

# Create a DataFrame from the list of player names
df = pd.DataFrame(all_player_names, columns=["Player Names"])

# Save the DataFrame to a CSV file
df.to_csv("hockey_player_names.csv", index=False)

# Print a message to confirm the CSV file has been saved
print("Player names saved to 'hockey_player_names.csv'")
