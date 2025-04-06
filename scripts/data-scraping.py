from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import time
import pandas as pd

options = Options()
options.binary_location = "/usr/bin/google-chrome"
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


print(f"{datetime.now()}: Started Web Scraping...")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.sofascore.com/team/football/corinthians/1957")
time.sleep(5)

html_data = BeautifulSoup(driver.page_source, 'html.parser')

driver.quit()

print(f"{datetime.now()}: Done Scraping...")

print(f"{datetime.now()}: Start extracting Players data...")

players_data = []

for player_div in html_data.find_all("div", class_="Box gDjnsl"):
    try:
        a_tag = player_div.find("a", href=True)
        href = a_tag["href"]

        number = a_tag.find("div", class_="Text jmvTmM").text.strip()
        name = a_tag.find("div", class_="Text cOreSJ").text.strip()
        img_tag = a_tag.find("img", class_="Img jEIzdG")
        img_url = img_tag["src"] if img_tag else None
        ingestion_date = datetime.now()

        players_data.append({
            "url": href,
            "number": number,
            "name": name,
            "img_url": img_url,
            "ingestion_date": ingestion_date
        })
        
        print(f"{datetime.now()}: Player data extracted successfully {name}")
    except Exception as e:
        print(f"Error while processing Player: {e}")

# Cria o DataFrame
df = pd.DataFrame(players_data)
df.to_csv("./data/bronze/players_data.csv")

print(f"{datetime.now()}: Done Extracting!")