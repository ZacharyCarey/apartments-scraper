# Apartments.com Scraper

You can use this to create an Excel sheet of apartment data.

In particular, this parses an [apartments.com](apartments.com) search result based on some criteria that are present in the page. This is current as of February 18, 2021.

It's a web scraper for the result listing and produces a .xlsx that has all the entries nicely parsed. 

## How to use:

### Installation
Please note that this assumes you have Python installed. It works with Python 2.7 and Python 3.5+.
You can install Python from [here](https://www.python.org/downloads/). 

Install dependencies automatically using pip: `pip install -r packages.txt`

### Running
In order to generate the .xlsx file:

1. Rename or copy config_example.ini to config.ini.
1. Search for apartments on apartments.com. Use your own criteria using the app. Copy the URL.
    - Replace the parenthesis after "apartmentsURL:" in config.ini with the copied URL.
1. By default, two results pages are parsed per search url given. This number can be changed after the `maxPageScrape:` field.
1. When using multiple search URLs, it is possible sometimes to get the same apartment complex in both results causing a duplicate entry to be saved. By default the program will skip an entry if it has already parsed a page with the same url. This can be disabled by setting `ignoreDuplicates` to `false`.
1. If you want your output file to be named something other than output.xlsx, change the name of the file (output) after the `fname:` field.
1. Run `python scrape_apartments.py` to generate the .xlsx file that you can then open.

