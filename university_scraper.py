import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

def fetch_qs_us_rankings():
    """
    Fetch Top 100 US Universities from QS World University Rankings
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    universities = []
    
    try:
        # QS US Rankings page
        url = "https://www.topuniversities.com/university-rankings/world-university-rankings/2024"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all university entries
        university_elements = soup.find_all('div', class_='uni-link')
        
        for element in university_elements:
            try:
                name = element.find('a', class_='uni-link').text.strip()
                # Only include US universities
                if ", United States" in name:
                    uni_data = {
                        'name': name.replace(", United States", ""),
                        'rank': len(universities) + 1,  # Temporary ranking
                        'location': 'United States',
                        'url': 'https://www.topuniversities.com' + element.find('a')['href']
                    }
                    universities.append(uni_data)
                    if len(universities) >= 100:
                        break
            except Exception as e:
                print(f"Error processing university: {e}")
                continue
                
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    
    return universities[:100]

def save_universities(universities):
    """
    Save universities to JSON file
    """
    with open('top_100_us_universities.json', 'w') as f:
        json.dump(universities, f, indent=4)
    
    # Also create a pandas DataFrame for better viewing
    df = pd.DataFrame(universities)
    df.to_csv('top_100_us_universities.csv', index=False)

if __name__ == "__main__":
    universities = fetch_qs_us_rankings()
    if universities:
        save_universities(universities)
        print(f"Successfully gathered {len(universities)} universities")
    else:
        print("Failed to gather university data")
