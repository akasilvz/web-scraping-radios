from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
from datetime import datetime, timedelta

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.get("https://megahits.sapo.pt/acabou-de-tocar")

wait = WebDriverWait(driver, 15)

try:
    cookie_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "qc-cmp2-summary-buttons")))
    accept_button = cookie_div.find_element(By.XPATH, ".//button[span[text()='ACEITAR']]")
    accept_button.click()
except Exception as e:
    print("Erro ao aceitar o cookie banner:", e)

wait.until(EC.presence_of_element_located((By.ID, "dias")))

day_select = Select(driver.find_element(By.ID, "dias"))
day_select.select_by_visible_text("Ontem")

yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

csv_filename = 'megahits_08.csv'

with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.writer(csvfile, delimiter='|')
    writer.writerow(["DAY", "TIME PLAYED", "SONG TITLE", "SONG ARTIST"])

seen_songs = set()

for hour in range(24):
    for minute in range(60):
        try:
            wait.until(EC.visibility_of_element_located((By.ID, "txtHoraPesq"))).clear()
            wait.until(EC.visibility_of_element_located((By.ID, "txtHoraPesq"))).send_keys(f"{hour:02}")
            
            wait.until(EC.visibility_of_element_located((By.ID, "txtMinutoPesq"))).clear()
            wait.until(EC.visibility_of_element_located((By.ID, "txtMinutoPesq"))).send_keys(f"{minute:02}")

            wait.until(EC.element_to_be_clickable((By.ID, "pesquisa"))).click()
            time.sleep(1)

            times_played = driver.find_elements(By.CLASS_NAME, "ac-horas1")
            song_titles = driver.find_elements(By.CLASS_NAME, "ac-nomem1")
            song_artists = driver.find_elements(By.CLASS_NAME, "ac-autor1")

            for time_played, song_title, song_artist in zip(times_played, song_titles, song_artists):
                if song_title.text.startswith("INTHEMIX_"):
                    continue
                
                song_data = (time_played.text, song_title.text, song_artist.text)
                if song_data not in seen_songs:
                    seen_songs.add(song_data)
                    with open(csv_filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
                        writer = csv.writer(csvfile, delimiter='|')
                        writer.writerow([
                            yesterday_date.upper(),
                            time_played.text.upper(),
                            song_title.text.upper(),
                            song_artist.text.upper()
                        ])

        except Exception as e:
            print(f"An error occurred: {e}")
            continue

driver.quit()
