from selenium import webdriver


def main():
    # Open up a Chrome browser and navigate to user's ratings web page
    username = input("Enter username: ")
    browser = webdriver.Chrome('C:\\Users\\Allan\\Desktop\\Python\\chromedriver.exe')
    browser.get('https://letterboxd.com/' + username + '/films/ratings')

    # Extract lists of 'movies' and 'ratings'
    ratings = browser.find_element_by_xpath('//ul[@class="poster-list -p150 -grid"]') # Returns a 'WebElement' object

    film_ratings = browser.find_elements_by_class_name('poster-container')
    print("Total elements:", len(film_ratings))

    for film in film_ratings:
        # Parse rating and title in scope of child elements
        title = film.find_element_by_xpath('.//img').get_property('alt')
        print(title)

        rating = film.find_element_by_xpath('.//meta[@itemprop="ratingValue"]').get_property('content')
        print(rating)

        letterboxd_uri = 'https://letterboxd.com' + \
                         film.find_element_by_xpath('.//div[1]').get_attribute('data-target-link')
        print(letterboxd_uri)

    # Clean up, close browser once task is completed
    browser.close()


    #print(type(ratings))
    #print(ratings)


def parse_ratings(elements):
    pass


if __name__ == '__main__':
    main()