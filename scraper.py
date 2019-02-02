# A program that takes takes an existing 'Letterboxd'
# user and scrapes their profile for film ratings,
# extracting them in the default csv format.
#
# Author: Emmanuel Macario
# Date: 26/01/18
# Last Modified: 28/01/19

import csv
import re
import os
import sys
import urllib.request
import urllib.error
from math import ceil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

BASE_URL = 'https://letterboxd.com/'
RATINGS_PATH = '/films/page/'
DRIVER_PATH = os.path.join(os.getcwd(), 'chromedriver.exe')
RATINGS_PER_PAGE = 72

# TODO: Experiment with PhantomJS or Headless Chrome instead of normal Chrome
# TODO: Write scraped output to CSV file


def main():
    # Open up a Chrome browser and navigate to user's profile web page
    username = input("Enter username: ")

    validate_user_existence(username)

    browser = initialise_browser()

    # Calculate total number of pages to be scraped
    total_pages = calc_total_pages(browser, username)
    print("Total Pages:", total_pages)

    # Scrape all pages for their ratings
    scrape_all_ratings(browser, username, total_pages)

    # Clean up, close browser once task is completed
    browser.close()


def initialise_browser():
    # Operate Chrome in headless mode
    chrome_options = Options()
    chrome_options.headless = False

    # Initialise and return driver
    return webdriver.Chrome(executable_path=DRIVER_PATH,
                            chrome_options=chrome_options)


def validate_user_existence(username):
    if not username:
        print("Please enter a non-empty username")
        sys.exit(0)
    else:
        try:
            urllib.request.urlopen(BASE_URL + username)
        except urllib.error.HTTPError as e:
            # Return code error (e.g. 404, 501, ...)
            print('HTTPError: {} {}'.format(e.code, e.reason))
            sys.exit(1)
        except urllib.error.URLError as e:
            # Not an HTTP-specific error (e.g. connection refused)
            print('URLError: {}'.format(e.reason))
            sys.exit(1)
        else:
            # 200
            print('User has been found')


def calc_total_pages(browser, username):
    """
    Calculates the number of pages needed to be scraped,
    given the user's total number of film ratings.
    :return:
    """
    browser.get(BASE_URL + username)
    ratings_section = browser.find_element_by_xpath('//section[@class="section ratings-histogram-chart"]')
    print(ratings_section)

    total_ratings = int(ratings_section.find_element_by_class_name('all-link')
                                       .text
                                       .replace(',', ''))
    print(total_ratings)

    total_pages = ceil(total_ratings / RATINGS_PER_PAGE)

    return total_pages


def scrape_all_ratings(browser, username, total_pages):
    with open(username + '-ratings.csv', 'w', newline='') as output_csv:
        writer = csv.writer(output_csv)
        writer.writerow(['Name', 'Year', 'URI', 'Rating'])

        for page in range(1, total_pages + 1):
            browser.get(BASE_URL + username + RATINGS_PATH + str(page))
            scrape_page_ratings(browser, writer)


def scrape_page_ratings(browser, writer):
    film_ratings = browser.find_elements_by_class_name('poster-container')
    print("Total elements:", len(film_ratings))

    # Regular expression for film title and year
    pattern = re.compile(r"(?P<title>.*) \((?P<year>\d{4})\)")

    # For each film, append data to csv
    for film in film_ratings:
        sys.stdout.flush()
        print("Next film...")
        row = []
        try:
            print("Trying to hover...")
            # Locate the mouse-over element
            hover = ActionChains(browser).move_to_element(film)
            hover.perform()

            print("Hover successful, waiting for dynamic element")
            # Get the dynamic element
            element = WebDriverWait(browser, 5).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "twipsy-inner"))
            )

            print("Dynamic element found, finding match")
            # Try to find a match
            match = pattern.match(element.text)
            if match is not None:
                title = match.group('title')
                year = match.group('year')
                row.append(title)
                row.append(year)
                print(title, year)

        except TimeoutException:
            print("Error, loading dynamic element took too much time!")

        uri = BASE_URL + film.find_element_by_xpath('.//div[1]')\
                             .get_attribute('data-target-link')\
                             .lstrip('/')
        print("URI:", uri)
        row.append(uri)

        rating = film.get_attribute('data-owner-rating')
        print("RATING:", rating)
        row.append(rating)

        writer.writerow(row)


if __name__ == '__main__':
    main()