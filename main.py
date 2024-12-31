import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException
import time

# Request headers
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"}
url = "https://appbrewery.github.io/Zillow-Clone/"

# Send request to the URL
response = requests.get(url=url, headers=header)

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Extract the links
link_elements = soup.find_all('a', {'data-test': 'property-card-link'})
links = [link.get('href') for link in link_elements]
links = list(set(links))  # Remove duplicates
print(f"Found {len(links)} links")

# Extract the prices and clean them
def clean_price(price):
    return price.replace("+", "").replace("/mo", "").replace("1 bd", "").replace("1bd", "").strip()

price_elements = soup.find_all('span', {'data-test': 'property-card-price'})
prices = [clean_price(price.text) for price in price_elements]
print(f"Found {len(prices)} prices")

# Extract addresses and clean them
address_elements = soup.find_all('address', {'data-test': 'property-card-addr'})
addresses = [" ".join(address.text.split()).strip() for address in address_elements]
print(f"Found {len(addresses)} addresses")

# Google Form URL
form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdpzgth_nhJKiHv832D9kUDYUl2FSVtqxRI16Yzx2D6DcMGNQ/viewform?usp=header"

# Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Loop through each entry and fill out the form
for i in range(len(links)):
    try:
        driver.get(form_url)
        
        # Wait for the form elements to be visible and interactable
        wait = WebDriverWait(driver, 10)
        address_entry = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@aria-labelledby="i1 i4"]')))
        price_entry = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@aria-labelledby="i6 i9"]')))
        link_entry = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@aria-labelledby="i11 i14"]')))
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@class="NPEfkd RveJvd snByac" and text()="Submit"]')))
        
        # Fill out the form
        address_entry.send_keys(addresses[i])
        price_entry.send_keys(prices[i])
        link_entry.send_keys(links[i])
        
        # Submit the form
        submit_button.click()

        # Optional: Wait for the form to confirm submission
        WebDriverWait(driver, 5).until(EC.url_contains("formResponse"))

        # Sleep between submissions to avoid triggering bot detection
        time.sleep(2)

    except ElementNotInteractableException as e:
        print(f"Error interacting with form for link {links[i]}. Skipping.")
        continue  # Skip the current iteration if there's an error

# Quit the driver once all submissions are done
driver.quit()


# drivelink="https://docs.google.com/spreadsheets/d/1QzAuyAxXxT_Luo_RvslW0gQlLDaqOpzAPvAbOBTVJlw/edit?resourcekey=&gid=318013132#gid=318013132"