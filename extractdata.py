from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from typing import Dict

LOCALE_KEY = "page_language"
HTML_KEY = "html_content"


def get_grid_html() -> Dict:
    result = dict()
    url = "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&is_targeted_country=false&media_type=all&q=microlearning&search_type=keyword_unordered"  # Замініть на потрібний URL

    # browser setup
    options = Options()
    options.add_argument("--headless")  # run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # run browser in headless mode
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    driver.get(url)
    time.sleep(5)

    # Find the <html> element and get its 'lang' attribute
    html_element = driver.find_element(By.TAG_NAME, "html")
    page_language = html_element.get_attribute("lang")
    result[LOCALE_KEY] = page_language

    # finding css_selector of grid element
    all_elements = driver.find_elements(By.XPATH, "//*")
    # Iterate through the elements and check their display property
    grid_element = None
    for element in all_elements:
        if element.value_of_css_property("display") == "grid":
            grid_element = element
            break  # Stop at the first one found
    if grid_element:
        # print("Found the first element with display: grid")
        css_selector = f"div.{grid_element.get_attribute("class").replace(' ', '.')}"
        # print("CSS Selector:", css_selector)
    else:
        raise RuntimeError("No element with display: grid was found on the page.")

    elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
    # print(f"Total elements found with selector: {len(elements)}")
    grids_count = len(elements)

    element = elements[-1]
    # count child elements
    grid_elements_count = len(element.find_elements("xpath", "./*"))
    # print(grid_elements_count)

    # scroll while new elements are loaded
    grid_elements_count_new = 0
    repeat_times = 0
    while grid_elements_count != grid_elements_count_new or repeat_times < 3:
        grid_elements_count = grid_elements_count_new
        last_child = element.find_element("xpath", "./*[last()]")
        driver.execute_script("arguments[0].scrollIntoView();", last_child)
        time.sleep(4)
        elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
        if len(elements) > grids_count:
            grids_count = len(elements)
            grid_elements_count_new = 0
        else:
            element = elements[grids_count - 1]
            grid_elements_count_new = len(element.find_elements("xpath", "./*"))
        print(f"Extract data. Elements loaded in current grid: {grid_elements_count_new}")
        if grid_elements_count == grid_elements_count_new:
            repeat_times += 1
        else:
            repeat_times = 0

        # !!!!! for testing purpose only
        # if grids_count > 1:
        #     break

    html_content = ""
    for element in elements:
        html_content += driver.execute_script("return arguments[0].innerHTML;", element)
    print("HTML success loaded")
    result[HTML_KEY] = html_content
    driver.quit()
    return result
