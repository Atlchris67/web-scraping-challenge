from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import time 

def scrape_all():

    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="../chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store in dictionary.
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "hemispheres": hemispheres(browser),
        "weather": twitter_weather(),
         "facts": mars_facts(),
         "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)
    news_titles = {} 
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    #write your code here
    news_title = soup.find('div', class_='content_title').text
    news_p = soup.find('div', class_='article_teaser_body').text
    return news_title, news_p


def featured_image(browser):
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)
    browser.is_element_present_by_css("article.carousel_item", wait_time=1)
    browser.click_link_by_id('full_image')
    browser.click_link_by_partial_text('more info')

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    feat_img_url = soup.find('figure', class_='lede').a['href']
    main_url = "https://www.jpl.nasa.gov"
    img_url = main_url + feat_img_url
    return img_url


def hemispheres(browser):

    # A way to break up long strings
    url = (
        "https://astrogeology.usgs.gov/search/"
        "results?q=hemisphere+enhanced&k1=target&v1=Mars"
    )

    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html , 'html.parser')
    hemisphere_info = []
    hemis = soup.find_all('div', class_="item")
    hemi_fqdn = 'https://astrogeology.usgs.gov'

    for sphere in hemis:
        title = sphere.find('h3').text
        image_url = sphere.find('a', class_='itemLink product-item')['href']
        browser.visit(hemi_fqdn  + image_url)
        image_html = browser.html
        soup = BeautifulSoup( image_html, 'html.parser')
        image_url = hemi_fqdn + soup.find('img', class_='wide-image')['src']
        hemisphere_info.append({"title" : title.replace('Enhanced',""), "img_url" : image_url})


    return hemisphere_info


def twitter_weather():

    browser2 = Browser("chrome", executable_path="../chromedriver", headless=True)
    url = 'https://twitter.com/marswxreport?lang=en'
    browser2.visit(url)
    #write your code here
    time.sleep(5)
    html = browser2.html
    
    soup = BeautifulSoup(html, 'html.parser')
    
    weather_divs = soup.find_all('div', class_="css-901oao r-hkyrab r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0")
    mars_weather = "not found"
    for weather in weather_divs:
    #     print(tweet)
        mars_weather = weather.text
        if 'sol' and 'pressure' in mars_weather:
            break
        else:
            pass

    browser2.quit()

    return mars_weather




def mars_facts():
    url = "https://space-facts.com/mars/"
    try:
        df = pd.read_html(url)[0]
    except BaseException:
        return None

    df.columns = ["description", "value"]
    df.set_index("description", inplace=True)

    # Add some bootstrap styling to <table>
    return df.to_html(classes="table table-striped")


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())
