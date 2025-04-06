from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import time
import pandas as pd

BASE_URL = "https://www.sofascore.com"
CLUB_PAGE = "/team/football/corinthians/1957"

options = Options()
options.binary_location = "/usr/bin/google-chrome"
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

print(f"{datetime.now()}: Started Web Scraping...")

driver.get(BASE_URL + CLUB_PAGE)
time.sleep(5)

html_data = BeautifulSoup(driver.page_source, 'html.parser')

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
        
        full_url = BASE_URL + href
        driver.get(full_url)
        time.sleep(2)
        player_data = BeautifulSoup(driver.page_source, 'html.parser')
        rating = player_data.select_one("div.Box.klGMtt.sc-eldPxv").text.strip()
        price = player_data.find("div", class_="Text imGAlA").text.strip()
        
        player_info = {}
        for i, box in enumerate(player_data.find_all("div", class_="Box gsaNZo")):
            try:
                raw_label = box.find("div", class_="Text gzlBsj").text.strip()
                value = box.find("div", class_="Text beCNLk").text.strip()

                label = raw_label.lower().replace(" ", "_")

                if i == 1:
                    player_info["birthday"] = raw_label 
                else:
                    player_info[label] = value
            except:
                continue
        if player_info:
            player_info.popitem()
        
        skill_classes = ['attacking', 'technical', 'tactical', 'defending', 'creativity']

        for skill_class in skill_classes:
            block = player_data.find("div", class_=lambda c: c and skill_class in c.split())
            
            if block:
                key_span = block.find("span", class_="textStyle_assistive.default")
                value_span = block.find("span", class_="textStyle_table.small")
                if key_span and value_span:
                    key = key_span.text.strip().lower()  # ex: 'att'
                    value = int(value_span.text.strip())  # já como número inteiro
                    player_info[key] = value
        
        players_data.append({
            "url": href,
            "number": number,
            "name": name,
            "img_url": img_url,
            "rating": rating,
            "price": price,
            **player_info,
            "ingestion_date": ingestion_date,
        })
        
        print(f"{datetime.now()}: Player data extracted successfully {name}")
    except Exception as e:
        print(f"Error while processing Player: {e}")

driver.quit()

df = pd.DataFrame(players_data)
df.to_csv("./data/bronze/players_data.csv", index=False)

print(f"{datetime.now()}: Done Extracting!")