"""Parse an apartments.com search result page and export to CSV."""

import csv
import json
import sys
import datetime
import requests
import os
import traceback
from bs4 import BeautifulSoup
import parse_apartments as parsing
from output_formatter import OutputFile
import logging

# Config parser was renamed in Python 3
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

def scrapeApartments(out, search_urls, max_pages, ignore_duplicates, config):
    """goes through each apartment search page URL and scrapes the data"""
    # parse current entire apartment list including pagination for all search urls
    apartments = [] #List of visited apartment URLs to avoid duplicate entries
    for url in search_urls:
        url = url.strip()
        if not url.endswith('/'):
            url = url + '/'
        scrapeSearchPage(out, url, 1, max_pages, ignore_duplicates, apartments, config)


def scrapeSearchPage(out, page_url, page_num, max_pages, ignore_duplicates, apartmentList, config):
    """Given the current page URL, extract the information from each apartment in the list"""
    url = page_url
    metadata = url.find('?')
    if metadata > -1:
        url = url[:metadata] + str(page_num) + "/" + url[metadata:]
    else:
        if not url.endswith("/"):
            url += "/"
        url += str(page_num) + "/"

    logging.info("Now getting apartments from page " + str(page_num) + ": %s" % url)

    # read the current page
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    page = requests.get(url, headers=headers)
 
    # soupify the current page
    soup = BeautifulSoup(page.content, 'html.parser')
    soup.prettify()

    # get the element that contains the apartment list
    soup = soup.find('div', class_='placardContainer')

    # append the current apartments to the list
    for item in soup.find_all('article', class_='placard'):
        data_url = item.get('data-url')
        if data_url is None: 
            continue

        if ignore_duplicates and (data_url in apartmentList):
            continue

        #Take note of the url so we don't accidently create a duplicate entry later
        apartmentList.append(data_url)

        # get the name for user/debug info
        name = "N/A"
        obj = item.find('span', class_='js-placardTitle')
        if obj is not None:
            name = obj.getText().strip()
        logging.info("Collecting data for: %s" % name)

        #request the page and parse the data
        apartmentPage = requests.get(data_url, headers=headers)
        apartmentSoup = BeautifulSoup(apartmentPage.content, 'html.parser')
        apartmentSoup.prettify()
        parsing.parseApartmentPage(apartmentSoup, out, data_url, config)

    # recurse until the last page
    if page_num < max_pages:
        scrapeSearchPage(out, page_url, page_num + 1, max_pages, ignore_duplicates, apartmentList, config)

def loadConfigFromValuesNoCase(conf, key, values):
    """NOTE: The values must all be lowercase (e.x. \"highest\")"""
    value = conf.get('all', key).lower()
    if value in values:
        return value
    else:
        raise Exception("ERROR: Configuration \'" + key + "\' was an invalid value, unable to run!")

def main():
    """Read from the config file"""
    trueValues = ['T', 't', '1', 'True', 'true']
    priceSelectorValues = ['lowest', 'highest', 'average']

    conf = configparser.ConfigParser()
    config_file = os.path.join(os.path.dirname(__file__), "config.ini")
    conf.read(config_file)

    # get the apartments.com search URL(s)
    apartments_url_config = conf.get('all', 'apartmentsURL')
    urls = apartments_url_config.replace(" ", "").split(",")

    #get max page numbers
    max_pages_config = conf.get('all', 'maxPageScrape')
    max_pages = 1
    try:
        max_pages = int(max_pages_config)
    except ValueError:
        max_pages = 1

    #get ignore duplicates config
    ignore_duplicates = conf.get('all', 'ignoreDuplicates') in trueValues

    #get other configs
    config = {}
    config['separateUtilities'] = (conf.get('all', 'separateUtilities') in trueValues)
    config['separatePets'] = (conf.get('all', 'separatePets') in trueValues)
    config['separateParking'] = (conf.get('all', 'separateParking') in trueValues)
    config['priceSelector'] = loadConfigFromValuesNoCase(conf, 'priceSelector', priceSelectorValues)
    config['priceAdjustment'] = (conf.get('all', 'priceAdjustment') in trueValues)
    config['adjustPrice'] = {
        "Air Conditioning": int(conf.get('all', 'adjustACPrice')),
        "Electric": int(conf.get('all', 'adjustElectricPrice')),
        "Gas": int(conf.get('all', 'adjustGasPrice')),
        "Heat": int(conf.get('all', 'adjustHeatPrice')),
        "Sewage": int(conf.get('all', 'adjustSewagePrice')),
        "Trash": int(conf.get('all', 'adjustTrashPrice')), 
        "Water": int(conf.get('all', 'adjustWaterPrice')),
        "Other": int(conf.get('all', 'adjustOtherPrice'))
    }
    #Make sure if there are utilities not listed that we add default values
    for util in OutputFile.values['utilities']:
        if util not in config['adjustPrice']:
            config['adjustPrice'][util] = 0

    # get the name of the output file
    fname = conf.get('all', 'fname')

    #Attempt to remove old output file to make sure we have write permissions
    try:
        os.remove(fname + ".xlsx")
    except PermissionError:
        logging.error("The output file is being used by another process. Try closing the file then run the program again: \'" + fname + ".xlsx\'")
        return
    except FileNotFoundError:
        #We don't actually care about this error, we can ignore it.
        pass

    #Create the output file and start the scraping
    out = OutputFile(fname, config)
    try:
        scrapeApartments(out, urls, max_pages, ignore_duplicates, config)
    except Exception:
        logging.exception("An error has occured!")
    finally:
        out.close()
    logging.info("Finished")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, handlers=[
        logging.FileHandler(filename='logging.log'),
        logging.StreamHandler(sys.stdout)
    ])
    main()
