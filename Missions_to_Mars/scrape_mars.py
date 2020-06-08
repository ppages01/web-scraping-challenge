from selenium import webdriver
import pandas as pd
import numpy as np
import requests
import pymongo
import tweepy
import requests
import os
import time
from splinter import Browser
from bs4 import BeautifulSoup as bs
from requests import get
from dotenv import load_dotenv
load_dotenv()

hemisphere_image_urls = []


def selget(url):
    chromedriver = "chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    soup = bs(html, 'html.parser')
    driver.close()
    return(soup)

def splintget(url):
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    browser.visit(url)
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = bs(html, 'html.parser')
    browser.quit()
    return(soup)
    

def newsheadlines():
    url = 'https://mars.nasa.gov/news/'
    soup = selget(url)
    
    _title = soup.find('div', class_='list_text').find('a')
    _title = _title.text.strip()
    _tease = soup.find('div', class_='article_teaser_body').text
    
    return(_title,_tease)


def featuredimage():
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    soup = splintget(url)
    imgElement = soup.find('article', class_='carousel_item')['style']
    imgElement = imgElement.split("'",1)[1]
    imgElement = imgElement.rsplit("'",1)
    featured_image_url = "https://www.jpl.nasa.gov" + imgElement[0]
    return(featured_image_url)

def getTweety():
    consumer_key = os.environ.get('twitter_key')
    consumer_secret = os.environ.get('twitter_secret')
    access_token = os.environ.get('twitter_token')
    access_token_secret = os.environ.get('twitter_token_secret')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True)

    tweetList = []
    response = api.user_timeline(screen_name = 'MarsWxReport', count=1)
    for result in api.search(q="MarsWxReport"):
        tweetList.append(result.text)
        
    mars_weather = tweetList[0]
    return(mars_weather)

def marsFacts():
    url = 'https://space-facts.com/mars/'
    tables = pd.read_html(url)
    df = tables[0]
    df.columns = ['', 'Value']
    df.set_index('', inplace=True)
    df_html = df.to_html()
    text_file = open("table.html", "w")
    text_file.write(df_html)
    text_file.close()

    
def hemisphere():
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    titles = []
    links = []

    def retrieve(url):
        soup = selget(url)
        content = soup.find(id="wide-image")
        imageContent = content.find('a')['href']
        title1 = soup.title.text.strip()
        title1 = title1.split('|')[0]
        titles.append(title1)
        links.append(imageContent)
    
    def getlinks(url):
        soup = selget(url)
        content = soup.find(id="product-section")
        bodyContent = content.find_all("div", class_="description")

        for image in bodyContent:
            suburl = image.find("a")['href']  
            fullurl = "https://astrogeology.usgs.gov" + suburl
            retrieve(fullurl)
    
    
    getlinks(url)

    r=0
    for r in range(len(titles)):
        p_dict ={}
        p_dict["title"] = titles[r]
        p_dict["img_url"] = links[r]
        hemisphere_image_urls.append(p_dict)

    
def scrape_info():
    news=newsheadlines()
    news_title = news[0]
    news_tease = news[1]
    featured_image_url = featuredimage()
    mars_weather = getTweety()
    mars_facts = marsFacts()
    hemisphere()

    #store data in a dictionary
    mars_data = {
        "featured_image_url" : featured_image_url,
        "news_title" : news_title,
        "news_tease" : news_tease,
        "mars_weather" : mars_weather,
        #"mars_facts" : mars_facts,
        "hemisphere_data" : hemisphere_image_urls
    }

    return mars_data
