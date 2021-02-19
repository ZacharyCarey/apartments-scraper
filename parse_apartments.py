import re

def addListToRow(key, arr, row):
    for item in arr:
        row.addListValue(key, item)

def parseApartmentPage(soup, out, url):
    """Parses the apartment page for information and stores it in the given OutputFile for formatting."""
    name = scrapeApartmentName(soup)
    address = scrapeAddress(soup)
    neighborhood = scrapeNeighborhood(soup)
    utilities = scrapeUtilities(soup)
    parking = scrapeParking(soup)
    pets = scrapePets(soup)
    monthlyFees = scrapeMonthlyFees(soup)
    fees = scrapeFees(soup)
    recreation = scrapeRecreation(soup)
    features = scrapeFeatures(soup)
    outdoors = scrapeOutdoors(soup)

    floorplans = scrapeFloorplanSoups(soup)
    for floorplan in floorplans:
        row = out.getNewRow()
        row.setApartmentName(name)
        row.setApartmentURL(url)
        row.setValue('neighborhood', neighborhood)
        row.setValue('address', address)
        addListToRow('utilities', utilities, row)
        addListToRow('parking', parking, row)
        addListToRow('pets', pets, row)
        addListToRow('monthly', monthlyFees, row)
        addListToRow('fees', fees, row)
        addListToRow('recreation', recreation, row)
        addListToRow('features', features, row)
        addListToRow('outdoors', outdoors, row)

        row.setFloorplanName(scrapeFloorplanName(floorplan))
        row.setValue('price', scrapePrice(floorplan))
        row.setValue('size', scrapeSize(floorplan))
        row.setValue('bed', scrapeBed(floorplan))
        row.setValue('bath', scrapeBath(floorplan))


def simplify(text):
    """Given text scraped from a website, simplify the text by removing unnecessary whitespace and bullets."""
    # format it nicely: encode it, removing special symbols
    data = text.encode('ascii', 'ignore')
    # format it nicely: replace multiple spaces with just one
    data = re.sub(' +', ' ', data)
    # format it nicely: replace multiple new lines with just one
    #data = re.sub('(\r?\n *)+', '\n', data)
    data = data.replace("\r", "")
    data = data.replace("\n", "")
    data = data.replace("\t", "")
    # format it nicely: replace bullet with *
    #data = re.sub(u'\u2022', '* ', data)
    # format it nicely: replace registered symbol with (R)
    #data = re.sub(u'\xae', ' (R) ', data)
    # format it nicely: remove trailing spaces
    data = data.strip()

    return data #str(data).encode('utf-8')

def scrapeApartmentName(soup):
    """Scrapes the apartment name from the soup."""
    obj = soup.find('h1', class_='propertyName')
    if obj is not None:
        text = obj.getText()
        if text is not None:
            return simplify(text)
    return ''

def scrapeAddress(soup):
    """Scrapes the full address from the soup."""
    address = []

    obj = soup.find('div', class_='propertyAddress')
    if obj is not None:
        obj = obj.find('h2')
        if obj is not None:
            obj = obj.find_all('span')
            if obj is not None:
                address.append(simplify(obj[0].getText())) # street
                address.append(simplify(obj[1].getText())) # city
                address.append(simplify(obj[2].getText()) + " " + simplify(obj[3].getText())) # state / zip

    return ", ".join(address)

def scrapeNeighborhood(soup):
    """Scrapes the neighborhood data from the soup."""
    obj = soup.find('a', class_='neighborhood')
    if obj is not None:
        return simplify(obj.getText())    

def scrapeUtilities(soup):
    utilities = []
    obj = soup.find('div', class_='freeUtilities')
    if obj is not None:
        obj = obj.find('div', class_='descriptionWrapper')
        if obj is not None:
            obj = obj.find_all('span')
            if obj is not None:
                for span in simplify(obj.getText()):
                    if "Included" not in span:
                        for util in span.split(", "):
                            if "Trash" in util:
                                utilities.append("Trash")
                            elif ("Electric" in util) or ("Electricity" in util):
                                utilities.append("Electric")
                            elif "Sewer" in util:
                                utilities.append("Sewage")
                            else:
                                utilities.append(simplify(util))
                return utilities
    return []

def scrapeParking(soup):
    parking = []
    obj = soup.find_all('div', class_='parkingDetails')
    if obj is not None:
        for parkingType in obj:
            header = parkingType.find('h4')
            if header is not None:
                text = simplify(header.getText())
                if "Covered" in text:
                    parking.append("Covered")
                elif ("Surface" in text) or ("Lot" in text):
                    parking.append("Lot")
                elif "Garage" in text:
                    parking.append("Garage")
                else:
                    parking.append(text)
        return parking
    return []

def scrapePets(soup):
    pets = []
    obj = soup.find_all('div', class_='petPolicyDetails')
    if obj is not None:
        for details in obj:
            detailObj = details.find('p')
            if detailObj is not None:
                span = detailObj.find('span')
                if span is not None:
                    text = simplify(span.getText())
                    if "Dogs" in text:
                        pets.append("Dogs")
                    if "Cats" in text:
                        pets.append("Cats")
        return pets
    return []

def scrapeMonthlyFees(soup):
    fees = []
    obj = soup.find('div', class_='monthlyFees')
    if obj is not None:
            for expense in obj.find_all('div', class_='descriptionWrapper'):
                spans = expense.find_all('span')
                for span in spans:
                    text = simplify(span.getText())
                    if '$' not in text:
                        if "Storage" in text:
                            fees.append("Storage Fee")
                        elif "Cat" in text:
                            fees.append("Cat Rent")
                        elif "Dog" in text:
                            fees.append("Dog Rent")
                        elif "Parking" in text:
                            fees.append("Parking")
                        else:
                            fees.append(text)
            return fees
    return []

def scrapeFees(soup):
    fees = []
    obj = soup.find('div', class_='oneTimeFees')
    if obj is not None:
            for expense in obj.find_all('div', class_='descriptionWrapper'):
                spans = expense.find_all('span')
                for span in spans:
                    text = simplify(span.getText())
                    if '$' not in text:
                        if "Application" in text:
                            fees.append("Application Fee")
                        elif "Admin" in text:
                            fees.append("Admin Fee")
                        elif "Cat" in text:
                            fees.append("Cat Fee")
                        elif "Dog" in text:
                            fees.append("Dog Fee")
                        else:
                            fees.append(text)
            return fees
    return []

def scrapeRecreation(soup):
    #TODO get_field_based_on_class(soup, 'gym', 'fitnessIcon', fields)
    #fields[field] = ''

    #if soup is None: return
    
    #obj = soup.find('i', class_=icon)
    #if obj is not None:
    #    data = obj.parent.findNext('ul').getText()
    #    data = prettify_text(data)

    #    fields[field] = data
    return []

def scrapeFeatures(soup):
    #TODO get_field_based_on_class(soup, 'amenities', 'featuresIcon', fields)
    #actually propertyIcon, but shares with another category so more work is needed
    return []

def scrapeOutdoors(soup):
    #TODO get_field_based_on_class(soup, 'outdoor', 'parksIcon', fields)
    #This one didnt even have a name!
    return []

def scrapeFloorplanSoups(soup):
    """Returns a list of soups, one per floorplan"""
    obj = soup.find('table', class_='availabilityTable')
    if obj is not None:
        floorplans = obj.find_all('tr', class_='rentalGridRow')
        if floorplans is not None:
            return floorplans
    return []

def scrapeFloorplanName(floorplan):
    if floorplan is not None:
        obj = floorplan.find('td', class_='name')
        if obj is not None:
            return simplify(obj.getText())
    return ''

def scrapePrice(floorplan):
    if floorplan is not None:
        obj = floorplan.find('td', class_='rent')
        if obj is not None:
            text = simplify(obj.getText())
            dollar = text.find('$')
            text = text[dollar + 1:].replace(",", "")
            rent = 0
            split = text.find('-')
            if split > -1:
                rent1 = int(text[:split].strip())
                rent2 = int(text[split + 1:].strip())
                rent = (rent1 + rent2) / 2
            else:
                rent = int(text.strip())
            return str(rent)
    return '0'

def scrapeSize(floorplan):
    if floorplan is not None:
        obj = floorplan.find('td', class_='sqft')
        if obj is not None:
            return simplify(obj.getText()).strip("Sq Ft").strip().replace(",", "")
    return '0'

def scrapeBed(floorplan):
    if floorplan is not None:
        obj = floorplan.find('td', class_='beds')
        if obj is not None:
            obj = obj.find('span')
            if obj is not None:
                text = simplify(obj.getText().replace("\u0189", ".5")) #Replace the 1/2 fraction character
                data = text.split()
                if len(data) >= 1:
                    return data[0]
    return '0'

def scrapeBath(floorplan):
    if floorplan is not None:
        obj = floorplan.find('td', class_='baths')
        if obj is not None:
            obj = obj.find('span')
            if obj is not None:
                text = simplify(obj.getText().replace("\u0189", ".5")) #Replace the 1/2 fraction character
                data = text.split()
                if len(data) >= 1:
                    return data[0]
    return '0'