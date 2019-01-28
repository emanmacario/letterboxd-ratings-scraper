# A program that takes takes an existing 'Letterboxd'
# user and scrapes their profile for film ratings,
# extracting them in the default csv format.
#
# Author: Emmanuel Macario
# Date: 26/01/18
# Last Modified: 28/01/19

import csv
import re
import sys
from math import ceil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException

BASE_URL = 'https://letterboxd.com/'
RATINGS_PATH = '/films/ratings/page/'
DRIVER_PATH = r'C:\Users\Allan\Desktop\Python\chromedriver.exe'
LOG_PATH = r'D:\chromedriver.log'
RATINGS_PER_PAGE = 18

# TODO: Experiment with PhantomJS or Headless Chrome instead of normal Chrome
# TODO: Write scraped output to CSV file


def main():
    # Open up a Chrome browser and navigate to user's profile web page
    username = input("Enter username: ")

    validate_user_existence(username)

    # Calculate total number of pages to be scraped
    total_pages = calc_total_pages(browser, username)
    print("Total Pages:", total_pages)

    # Scrape all pages for their ratings
    scrape_all_ratings(browser, username, total_pages)

    # Clean up, close browser once task is completed
    browser.close()


def initialise_browser(desired_capabilities=None):
    if desired_capabilities is None:
        return webdriver.Chrome(DRIVER_PATH)
    else:
        return webdriver.Chrome(executable_path=DRIVER_PATH,
                                service_args=["--verbose", "--log-path=" + LOG_PATH],
                                desired_capabilities=desired_capabilities)


def validate_user_existence(username):
    if not username:
        print("Please enter a non-empty username")
        sys.exit(0)
    else:
        # Enable browser logging
        desired_capabilities = DesiredCapabilities.CHROME
        print(desired_capabilities)
        desired_capabilities['loggingPrefs'] = {'performance': 'ALL'}

        browser = initialise_browser(desired_capabilities)

        browser.get(BASE_URL + username)

        print(browser.title)

        print(browser.page_source)

        performance_log = browser.get_log('performance')
        print(str(performance_log).strip('[]'))

        for entry in browser.get_log('performance'):
            print(entry)

        browser.close()

        browser.get(BASE_URL + username)


def calc_total_pages(browser, username):
    """
    Calculates the number of pages needed to be scraped,
    given the user's total number of film ratings.
    :return:
    """
    ratings_section = browser.find_element_by_xpath('//section[@class="section ratings-histogram-chart"]')
    print(ratings_section)

    total_ratings = int(ratings_section.find_element_by_class_name('all-link')
                                       .text.replace(',', ''))
    print(total_ratings)

    total_pages = ceil(total_ratings / RATINGS_PER_PAGE)

    return total_pages


def scrape_all_ratings(browser, username, total_pages):
    for page in range(1, total_pages + 1):
        browser.get(BASE_URL + username + RATINGS_PATH + str(page))
        scrape_page_ratings(browser)


def scrape_page_ratings(browser):
    film_ratings = browser.find_elements_by_class_name('poster-container')
    print("Total elements:", len(film_ratings))

    for film in film_ratings:
        try:
            # Locate the mouse-over element
            hover = ActionChains(browser).move_to_element(film)
            hover.perform()

            # Get the dynamic element
            element = WebDriverWait(browser, 30).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "twipsy-inner"))
            )

            # Regular expression for film title and year
            pattern = re.compile(r"(?P<title>.*) \((?P<year>\d{4})\)")

            # Try to find a match
            match = pattern.match(element.text)
            if match:
                title = match.group('title')
                year = match.group('year')
                print(title, year)

        except TimeoutException:
            print("Error, loading dynamic element took too much time!")


        # Parse rating and title in scope of child elements
        # title = film.find_element_by_xpath('.//img').get_property('alt')
        # print("TITLE:", title)

        rating = film.find_element_by_xpath('.//meta[@itemprop="ratingValue"]')\
                     .get_property('content')
        print("RATING:", rating)

        letterboxd_uri = BASE_URL + film.find_element_by_xpath('.//div[1]')\
                                        .get_attribute('data-target-link')\
                                        .lstrip('/')
        print("URI:", letterboxd_uri)

        #year = film.find_element_by_xpath('.//span[@class="frame-title"]').text
        #print("YEAR:", year)


if __name__ == '__main__':
    main()