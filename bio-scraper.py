import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import re
import pandas as pd
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Hardcoded credentials and profile
USERNAME = "wahabalibb10@gmail.com"
PASSWORD = "wahab@334"
PROFILE_TO_SCRAPE = "ranaazeem34jb"
NUM_FOLLOWERS = 5  # Number of followers to scrape

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    return driver

def login(driver, username, password):
    driver.get('https://www.instagram.com/accounts/login/')
    time.sleep(2)

    try:
        element = driver.find_element(By.XPATH, "/html/body/div[4]/div/div/div[3]/div[2]/button")
        element.click()
    except NoSuchElementException:
        logging.info("[Info] - Instagram did not require to accept cookies this time.")

    logging.info("[Info] - Logging in...")
    username_input = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    password_input = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

    username_input.clear()
    username_input.send_keys(username)
    password_input.clear()
    password_input.send_keys(password)

    login_button = WebDriverWait(driver, 2).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    login_button.click()
    time.sleep(10)

    WebDriverWait(driver, 60).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, 'svg[aria-label="Home"]'))
    )
    logging.info("Login successful")

def get_followers(driver, profile, num_followers):
    driver.get(f"https://www.instagram.com/{profile}/followers/")
    time.sleep(random.uniform(3, 5))
    
    followers = []
    while len(followers) < num_followers:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(random.uniform(2, 4))
        elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/followers/')]/span")
        for element in elements:
            if len(followers) >= num_followers:
                break
            followers.append(element.text)
        time.sleep(random.uniform(2, 4))  # Add delay between scrolling
    
    return followers

def extract_contact_info(bio):
    email = None
    phone_number = None

    email_match = re.search(r'[\w\.-]+@[\w\.-]+', bio)
    if email_match:
        email = email_match.group(0)

    phone_match = re.search(r'\+?\d[\d -]{8,12}\d', bio)
    if phone_match:
        phone_number = phone_match.group(0)

    return email, phone_number

def get_bio(driver, username):
    profile_url = f"https://www.instagram.com/{username}/"
    driver.get(profile_url)
    time.sleep(random.uniform(3, 5))
    
    try:
        full_name = driver.find_element(By.XPATH, "//h1[contains(@class, 'rhpdm')]").text
    except Exception as e:
        logging.warning(f"Could not get full name for {username}: {e}")
        full_name = "No full name"
    
    try:
        bio = driver.find_element(By.XPATH, "//div[contains(@class, 'v9tJq')]/div/span").text
    except Exception as e:
        logging.warning(f"Could not get bio for {username}: {e}")
        bio = "No bio"
    
    email, phone_number = extract_contact_info(bio)
    
    logging.info(f"Scraped bio for {username}: Full Name: {full_name}, Bio: {bio}, Email: {email}, Phone Number: {phone_number}")

    return {
        'username': username,
        'full_name': full_name,
        'bio': bio,
        'profile_url': profile_url,
        'email': email,
        'phone_number': phone_number
    }

def scrape():
    driver = get_driver()
    login(driver, USERNAME, PASSWORD)

    followers = get_followers(driver, PROFILE_TO_SCRAPE, NUM_FOLLOWERS)
    bio_data = []
    
    for index, follower in enumerate(followers):
        data = get_bio(driver, follower)
        bio_data.append(data)
        logging.info(f"Scraped {index + 1}/{NUM_FOLLOWERS} followers")
        if (index + 1) % 100 == 0:
            driver.quit()
            time.sleep(random.uniform(10, 20))
            driver = get_driver()
            login(driver, USERNAME, PASSWORD)
        time.sleep(random.uniform(3, 6))
    
    df = pd.DataFrame(bio_data)
    df.to_csv("followers_bio_data.csv", index=False)
    logging.info("Scraping complete. Data saved to followers_bio_data.csv")
    
    driver.quit()

if __name__ == '__main__':
    scrape()
