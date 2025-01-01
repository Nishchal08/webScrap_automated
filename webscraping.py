#Importing libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Initialize the WebDriver
def initialize_driver():
    options = Options()
    options.add_argument("--incognito")
    path = r"D:\webScrap_automated\chromedriver-win64\chromedriver.exe"  # Update with ChromeDriver path
    service = Service(path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Log in to LinkedIn
def linkedin_login(driver, email, password):
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)  # Wait for the login page to load

    # Enter email and password
    email_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    email_field.send_keys(email)
    password_field.send_keys(password)

    # Click on the Sign-in button
    driver.find_element(By.XPATH, "//button[contains(text(), 'Sign in')]").click()
    time.sleep(5)  # Wait for the dashboard to load

# Perform the search
def search_query(driver, query):
    # Click on the search button (this makes the search input field appear)
    search_button = driver.find_element(By.XPATH, "//span[@class='search-global-typeahead__collapsed-search-button-icon t-black--light']")
    search_button.click()
    time.sleep(2)  # Wait for the search input field to appear 
    
    # Now find the actual search input field
    search_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search']"))
    )
    
    # Type the search query into the input field
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(2)  # Wait for the search results to load
    see_all =driver.find_element(By.XPATH, "//a[text()='See all people results']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", see_all)
    time.sleep(2)
    see_all.click()
    time.sleep(2)
    

# Scrape search results
def scrape_results(driver):
    results = []
    for _ in range(10):  # Scrape the first 10 pages of results
        profiles = driver.find_elements(By.XPATH, "//li[contains(@class, 'hfrnpHqiFIFjzRKUPdWXOHmVUInUMZAcTFUI')]")
        for profile in profiles:
            try:
                name = profile.find_element(By.XPATH, ".//a[@class='uBRuLksiXRXJNxzCdmDLlNvbeHoNnTVInTsbWCI ']//span[1]/span[1]").text.strip()  
                occupation = profile.find_element(By.XPATH, ".//div[contains(@class, 'hnypMlQNtRKZTJxKVVHfxzWpjYbYocHvxY')]").text.strip()
                location = profile.find_element(By.XPATH, ".//div[contains(@class, 'qSAYgCOdGkfdNvdVYQsSIXUFlxoBhOlNBctY')]").text.strip()
                summary_element = profile.find_element(By.XPATH, ".//p[contains(@class, 'qbFktTvirHmfQcRiZRuLcvNbsqbhQFM')]")
                summary = summary_element.text.strip() if summary_element else "No summary available"
                results.append({"Name": name, "Occupation": occupation, "Location": location,"Summary": summary})
            except Exception as e:
                print(f"Error while scraping a profile: {e}")
            time.sleep(2)  
        # Navigate to the next page
        try:
            # Scroll to the bottom to ensure that elements are loaded
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for the scroll action to complete
            # Wait for the "Next" button to be clickable
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next' and contains(@class, 'artdeco-pagination__button--next')]"))
            )
            # Scroll the page to bring the "Next" button into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(2)  # Optional: give a little more time for the button to be fully visible

            # Click the "Next" button
            next_button.click()
            print("Clicked 'Next' button successfully.")

            # Wait for the next page to load
            time.sleep(2)  
        except Exception as e:
            print(f"Error clicking 'Next' button: {e}")
            break  # Stop the loop if navigation fails
    return results


# Save data to CSV
def save_to_csv(data, filename="linkedin_results.csv"):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Main function
def main():
    # Initialize the WebDriver
    driver = initialize_driver()

    try:
        # Login credentials
        email = input("Enter your LinkedIn email: ")
        password = input("Enter your LinkedIn password: ")

        # Log in to LinkedIn
        linkedin_login(driver, email, password)

        # Search for a query
        query = input("Enter your search query:")
        search_query(driver, query)
        

        # Scrape results
        results = scrape_results(driver)

        # Save results to CSV
        save_to_csv(results)

    finally:
        # Close the WebDriver
        driver.quit()

if __name__ == "__main__":
    main()
