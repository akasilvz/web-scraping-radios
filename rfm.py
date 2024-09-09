from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import csv
from datetime import datetime, timedelta

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.get("https://rfm.sapo.pt/que-musica-era")

wait = WebDriverWait(driver, 20)

try:
    cookie_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "qc-cmp2-summary-buttons")))
    accept_button = cookie_div.find_element(By.XPATH, ".//button[span[text()='ACEITAR']]")
    accept_button.click()
except Exception as e:
    print("Erro ao aceitar o cookie banner:", e)

wait.until(EC.presence_of_element_located((By.ID, "dp-dia")))
day_select = Select(driver.find_element(By.ID, "dp-dia"))
day_select.select_by_visible_text("Ontem")

yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

csv_filename = 'rfm_08.csv'
seen_songs = set()

with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.writer(csvfile, delimiter='|')
    writer.writerow(["DAY", "TIME PLAYED", "SONG TITLE", "SONG ARTIST"])

    period_select = Select(driver.find_element(By.ID, "dp-periodo"))
    for period_option in period_select.options:
        period_select.select_by_visible_text(period_option.text)

        hour_select = Select(driver.find_element(By.ID, "dp-hora"))
        for hour_option in hour_select.options:
            hour_select.select_by_visible_text(hour_option.text)

            search_button = wait.until(EC.element_to_be_clickable((By.ID, "pesquisa_quemusicaera")))
            driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
            driver.execute_script("arguments[0].click();", search_button)

            try:
                wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "t-hor")))
                times_played = driver.find_elements(By.CLASS_NAME, "t-hor")
                song_titles = driver.find_elements(By.CLASS_NAME, "medium.no-margin.align-left")
                song_artists = driver.find_elements(By.CLASS_NAME, "large.no-margin.align-left")

                for time_played, song_title, song_artist in zip(times_played, song_titles, song_artists):
                    song_data = (time_played.text, song_title.text, song_artist.text)
                    if song_data not in seen_songs:
                        seen_songs.add(song_data)
                        writer.writerow([
                            yesterday_date.upper(),
                            time_played.text.upper(),
                            song_title.text.upper(),
                            song_artist.text.upper()
                        ])
                        csvfile.flush()

            except Exception as e:
                print(f"Nenhuma música encontrada para o período: {period_option.text}, hora: {hour_option.text}. Erro: {e}")

driver.quit()
