"""Parse an apartments.com search result page and export to CSV."""

import csv
import json
import sys
import datetime
import requests
import os
from bs4 import BeautifulSoup
import parse_apartments as parsing
from output_formatter import OutputFile

# Config parser was renamed in Python 3
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

def scrapeApartments(out, search_urls, max_pages, ignore_duplicates):
    """goes through each apartment search page URL and scrapes the data"""
    # parse current entire apartment list including pagination for all search urls
    apartments = [] #List of visited apartment URLs to avoid duplicate entries
    for url in search_urls:
        url = url.strip()
        if not url.endswith('/'):
            url = url + '/'
        scrapeSearchPage(out, url, 1, max_pages, ignore_duplicates, apartments)


def scrapeSearchPage(out, page_url, page_num, max_pages, ignore_duplicates, apartmentList):
    """Given the current page URL, extract the information from each apartment in the list"""

    print ("Now getting apartments from page " + str(page_num) + ": %s" % page_url)

    # read the current page
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    page = requests.get(page_url + str(page_num) + '/', headers=headers)
 
    # soupify the current page
    soup = BeautifulSoup(page.content, 'html.parser')
    soup.prettify()

    # get the element that contains the apartment list
    soup = soup.find('div', class_='placardContainer')

    # append the current apartments to the list
    for item in soup.find_all('article', class_='placard'):
        url = item.get('data-url')
        if url is None: 
            continue

        if ignore_duplicates and (url in apartmentList):
            continue

        #Take note of the url so we don't accidently create a duplicate entry later
        apartmentList.append(url)

        # get the name for user/debug info
        name = "N/A"
        obj = item.find('span', class_='js-placardTitle')
        if obj is not None:
            name = obj.getText().strip()
        print ("Collecting data for: %s" % name)

        #request the page and parse the data
        apartmentPage = requests.get(url, headers=headers)
        apartmentSoup = BeautifulSoup(apartmentPage.content, 'html.parser')
        apartmentSoup.prettify()
        parsing.parseApartmentPage(apartmentSoup, out, url)

    # recurse until the last page
    if page_num < max_pages:
        scrapeSearchPage(out, page_url, page_num + 1, max_pages, ignore_duplicates, apartmentList)


def main():
    """Read from the config file"""
    trueValues = ['T', 't', '1', 'True', 'true']

    conf = configparser.ConfigParser()
    config_file = os.path.join(os.path.dirname(__file__), "config.ini")
    conf.read(config_file)

    # get the apartments.com search URL(s)
    apartments_url_config = conf.get('all', 'apartmentsURL')
    urls = apartments_url_config.replace(" ", "").split(",")

    max_pages_config = conf.get('all', 'maxPageScrape')
    max_pages = 1
    try:
        max_pages = int(max_pages_config)
    except ValueError:
        max_pages = 1

    ignore_duplicates = conf.get('all', 'ignoreDuplicates') in trueValues

    # get the name of the output file
    fname = conf.get('all', 'fname')


    #Create the output file and start the scraping
    out = OutputFile(fname)
    #try:
    scrapeApartments(out, urls, max_pages, ignore_duplicates)
    #except:
    #    print("An error has occured!")
    #finally:
    out.close()


if __name__ == '__main__':
    main()
