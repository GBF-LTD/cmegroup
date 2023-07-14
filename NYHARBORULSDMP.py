#%%
import os
import pandas as pd
import base64
import requests
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import numpy as np
import holidays

os.environ['GITHUB_TOKEN'] = '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'
csv_directory = r'C:/Users/YuriPereria/.vscode/VSCODE/cmegroup/cmacsvstorage'

def get_last_business_day():
    us_holidays = holidays.US()
    last_business_day = pd.Timestamp.now()
    while True:
        last_business_day -= pd.Timedelta(days=1)
        if last_business_day.dayofweek in (5, 6) or last_business_day in us_holidays:
            continue
        else:
            return last_business_day

def main():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    url = "https://www.cmegroup.com/markets/energy/refined-products/nymex-new-york-harbor-heating-oil-calendar-swap.quotes.html"

    load_all_xpath = "/html/body/main/div/div[3]/div[3]/div/div/div/div/div/div[2]/div/div/div/div/div/div[6]/div/div/div/div[2]/div[2]/button/span"
    table_xpath = "/html/body/main/div/div[3]/div[3]/div/div/div/div/div/div[2]/div/div/div/div/div/div[6]/div"
    repo_name = 'GBF-LTD/cmegroup'

    driver.get(url)
    load_all_button = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, load_all_xpath)))
    driver.execute_script("arguments[0].click();", load_all_button)

    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, table_xpath)))
    title = 'NY HARBOR ULSD FINANCIAL FUTURES - QUOTES'
    table = driver.find_element(By.XPATH, table_xpath).get_attribute('outerHTML')
    df = pd.read_html(table)[0]

    filename = 'NYHARBORULSDMP.csv'

    with open(os.path.join(csv_directory, filename), 'w') as f:
        f.write(f'Title: {title}\n')

    df.to_csv(os.path.join(csv_directory, filename), index=False, mode='a')

    additional_date = run_second_url_task(driver)
    if additional_date:
        print(f"Appending additional date to CSV: {additional_date}")
        try:
            with open(os.path.join(csv_directory, filename), 'r') as f:
                lines = f.readlines()
            with open(os.path.join(csv_directory, filename), 'w') as f:
                f.write(lines[0])
                f.write(f'Last Settlement Trade Date: {additional_date}\n')
                for line in lines[1:]:
                    f.write(line)
            print("Additional date successfully written to the CSV file.")
        except Exception as e:
            print(f"Failed to open or write to file: {e}")

        print("Reading CSV content:")
        with open(os.path.join(csv_directory, filename), 'r') as f:
            print(f.read())
    else:
        print("No additional date found.")

    upload_file_to_github(filename, repo_name)

    driver.quit()

def run_second_url_task(driver):
    second_url = "https://www.cmegroup.com/markets/energy/refined-products/nymex-new-york-harbor-heating-oil-calendar-swap.settlements.html#tradeDate="
    last_business_day = get_last_business_day()
    formatted_date = last_business_day.strftime("%m%%2F%d%%2F%Y")
    second_url += formatted_date

    second_date_xpath = "/html/body/main/div/div[3]/div[3]/div/div/div/div/div/div[2]/div/div/div/div/div/div[6]/div/div/div/div"

    print("Navigating to the second URL...")
    driver.get(second_url)

    print("Waiting for the additional date element...")
    while True:
        try:
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, second_date_xpath)))
            print("Element found:", element)
            print("Element text:", element.text)
            if element.text != '':
                new_updated_date = element.text
                print("New Updated Date found:", new_updated_date)
                return new_updated_date
        except:
            print("Waiting a bit more for the additional date element...")
            time.sleep(30)

def upload_file_to_github(filename, repo_name):
    with open(os.path.join(csv_directory, filename), 'r') as f:
        content = f.read()

    url = f"https://api.github.com/repos/{repo_name}/contents/{filename}"

    headers = {
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github.v3+json",
    }

    data = {
        "message": f"update {filename}",
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        existing_file = response.json()
        sha = existing_file.get("sha")
        data["sha"] = sha

    response = requests.put(url, headers=headers, json=data)
    if response.status_code not in [200, 201]:
        print(f"Failed to upload {filename} to GitHub. Response: {response.json()}")
    else:
        print(f"Successfully uploaded {filename} to GitHub.")
        download_url = response.json().get("content", {}).get("download_url")
        if download_url:
            print(f"Download URL: {download_url}")
        else:
            print("Download URL not available.")

if __name__ == "__main__":
    main()
