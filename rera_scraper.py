import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Start Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # run in background
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Load the RERA Odisha project list page
url = "https://rera.odisha.gov.in/projects/project-list"
driver.get(url)
time.sleep(5)

# Get project rows (first 6)
projects = driver.find_elements(By.CSS_SELECTOR, ".table-responsive table tbody tr")[:6]

project_data = []

# Iterate over first 6 projects
for i, row in enumerate(projects):
    print(f"Scraping project {i+1}...")
    try:
        view_button = row.find_element(By.LINK_TEXT, "View Details")
        driver.execute_script("arguments[0].click();", view_button)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract fields
        reg_no = soup.find("td", text="RERA Registration No.").find_next("td").text.strip()
        project_name = soup.find("td", text="Project Name").find_next("td").text.strip()
        
        # Go to promoter details tab
        promoter_tab = driver.find_element(By.XPATH, "//a[contains(text(), 'Promoter Details')]")
        driver.execute_script("arguments[0].click();", promoter_tab)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        promoter_name = soup.find("td", text="Company Name").find_next("td").text.strip()
        address = soup.find("td", text="Registered Office Address").find_next("td").text.strip()
        gst = soup.find("td", text="GST Number").find_next("td").text.strip()

        # Append to list
        project_data.append({
            "RERA Regd. No": reg_no,
            "Project Name": project_name,
            "Promoter Name": promoter_name,
            "Address of Promoter": address,
            "GST No": gst
        })

        driver.back()
        time.sleep(3)

    except Exception as e:
        print(f"Error scraping project {i+1}: {e}")
        driver.get(url)
        time.sleep(3)
        projects = driver.find_elements(By.CSS_SELECTOR, ".table-responsive table tbody tr")

driver.quit()

# Save as DataFrame
df = pd.DataFrame(project_data)
print(df)
df.to_csv("rera_odisha_projects.csv", index=False)
