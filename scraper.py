import csv
from selenium import webdriver
from math import ceil

BASE_URL = 'https://letterboxd.com/'
RATINGS_PATH = '/films/ratings/page/'
DRIVER_PATH = 'C:\\Users\\Allan\\Desktop\\Python\\chromedriver.exe'
RATINGS_PER_PAGE = 18

def main():
    # Open up a Chrome browser and navigate to user's profile web page
    username = input("Enter username: ")
    browser = initialise_browser()

    # Calculate total number of pages to be scraped
    total_pages = calc_total_pages(browser, username)
    print("Total Pages:", total_pages)

    # Scrape all pages for their ratings
    scrape_all_ratings(browser, username, total_pages)

    # Clean up, close browser once task is completed
    browser.close()


def initialise_browser():
    browser = webdriver.Chrome(DRIVER_PATH)
    return browser


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
        # Parse rating and title in scope of child elements
        title = film.find_element_by_xpath('.//img').get_property('alt')
        print("TITLE:", title)

        rating = film.find_element_by_xpath('.//meta[@itemprop="ratingValue"]')\
                     .get_property('content')
        print("RATING:", rating)

        letterboxd_uri = BASE_URL + film.find_element_by_xpath('.//div[1]')\
                                        .get_attribute('data-target-link')\
                                        .lstrip('/')
        print("URI:", letterboxd_uri)
        print()


if __name__ == '__main__':
    main()