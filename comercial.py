from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import csv

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.get("https://radiocomercial.pt/passou")

wait = WebDriverWait(driver, 10)

try:
    cookie_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "qc-cmp2-summary-buttons")))
    accept_button = cookie_div.find_element(By.XPATH, ".//button[span[text()='CONCORDO']]")
    accept_button.click()
except Exception as e:
    print("Erro ao aceitar o cookie banner:", e)

wait.until(EC.presence_of_element_located((By.ID, "radio")))

radio_select = Select(driver.find_element(By.ID, "radio"))
radio_select.select_by_visible_text("Rádio Comercial")

csv_filename = 'comercial_2.csv'
header = ["DAY", "TIME PLAYED", "SONG TITLE", "SONG ARTIST"]

with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header, delimiter='|', quoting=csv.QUOTE_NONE)
    writer.writeheader()

wait.until(EC.presence_of_element_located((By.ID, "day")))
day_select = Select(driver.find_element(By.ID, "day"))
day_values = [option.get_attribute("value") for option in day_select.options if option.get_attribute("value")]

for day_value in day_values:
    day_select = Select(driver.find_element(By.ID, "day"))
    day_select.select_by_value(day_value)
    
    procurar_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Procurar']]")))
    procurar_button.click()

    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "timePlayed")))
    
    times_played = driver.find_elements(By.CLASS_NAME, "timePlayed")
    song_titles = driver.find_elements(By.CLASS_NAME, "songTitle")
    song_artists = driver.find_elements(By.CLASS_NAME, "songArtist")
    
    if not times_played:
        continue
    
    with open(csv_filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header, delimiter='|', quoting=csv.QUOTE_NONE)
        for time_played, song_title, song_artist in zip(times_played, song_titles, song_artists):
            writer.writerow({
                "DAY": day_value.upper(),
                "TIME PLAYED": time_played.text.upper(),
                "SONG TITLE": song_title.text.upper(),
                "SONG ARTIST": song_artist.text.upper()
            })

driver.quit()
