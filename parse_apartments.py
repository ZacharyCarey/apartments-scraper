import re

def addListToRow(key, arr, row):
    for item in arr:
        row.addListValue(key, item)

def parseApartmentPage(soup, out, url, config):
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

    discoveredFloorplans = []
    floorplans = scrapeFloorplanSoups(soup)
    for floorplan in floorplans:
        floorplanName = scrapeFloorplanName(floorplan) #Separate for easier debugging
        if floorplanName in discoveredFloorplans:
            continue
        else:
            discoveredFloorplans.append(floorplanName)

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

        row.setFloorplanName(floorplanName)
        row.setValue('price', scrapePrice(floorplan, config))
        row.setValue('size', scrapeSize(floorplan))
        row.setValue('bed', scrapeBed(floorplan))
        row.setValue('bath', scrapeBath(floorplan))

        out.writeRow(row) #Actually save the data to the file


def simplify(text):
    """Given text scraped from a website, simplify the text by removing unnecessary whitespace and bullets."""
    # format it nicely: encode it, removing special symbols
    data = text.encode('ascii', 'ignore').decode("utf-8")
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

    obj = soup.find('div', class_='propertyAddressContainer')
    if obj is not None:
        obj = obj.find('h2')
        if obj is not None:
            objIgnore = obj.find('span', class_='neighborhoodAddress')
            obj = obj.find_all('span')
            if obj is not None:
                for addr in obj:
                    if addr != objIgnore:
                        address.append(simplify(addr.getText()))

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
                for span in obj:
                    if span is None:
                        continue
                    text = simplify(span.getText())
                    if "Included" not in text:
                        for util in text.split(", "):
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

def filterV2FeesWrapper(soup, desiredHeader):
    feedObj = soup.find('div', id='profileV2FeesWrapper')
    if feedObj is not None:
        for card in feedObj.find_all('div', class_='feesPoliciesCard'):
            obj = card.find('h4', class_='header-column')
            if obj is not None:
                header = simplify(obj.getText())
                if header == desiredHeader:
                    return card.find('div', class_='component-body')


def scrapeParking(soup):
    parking = []
    obj = filterV2FeesWrapper(soup, 'Parking')
    if obj is not None:
        obj = obj.find_all('li')
        for parkingType in obj:
            colObjs = parkingType.find_all('div', class_='component-row')
            for colObj in colObjs:
                header = colObj.find('div', class_='column')
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
    obj = soup.find('div', class_='tab-section active')
    if obj is not None:
        floorplans = obj.find_all('div', class_='pricingGridItem')
        if floorplans is not None:
            return floorplans
    return []

def scrapeFloorplanName(floorplan):
    if floorplan is not None:
        obj = floorplan.find('span', class_='modelName')
        if obj is not None:
            return simplify(obj.getText())
    return ''

def scrapePrice(floorplan, config):
    if floorplan is not None:
        obj = floorplan.find('span', class_='rentLabel')
        if obj is not None:
            text = simplify(obj.getText().replace("\u2013", "-"))
            text = text.replace('$', "")
            text = text.replace(",", "")
            rent = 0
            split = text.find('-')
            if split > -1:
                rent1 = int(text[:split].strip())
                rent2 = int(text[split + 1:].strip())
                if config['priceSelector'] == 'lowest':
                    rent = min(rent1, rent2)
                elif config['priceSelector'] == 'highest':
                    rent = max(rent1, rent2)
                elif config['priceSelector'] == 'average':
                    rent = (rent1 + rent2) // 2
                else:
                    raise Exception("ERROR: Invalid priceSelector value.")
            else:
                try:
                    rent = int(text.strip())
                except ValueError:
                    rent = 0
            return str(rent)
    return '0'

def findSizeInList(soup, names):
    for obj in soup.find_all('span'):
        text = obj.getText()
        if text is None:
            continue
        text = simplify(text.replace("\u0189", ".5").replace("\u2013", "-")) #Replace the 1/2 fraction character and fancy hyphen with a normal one
        for name in names:
            if name and text.endswith(name):
                return text

def scrapeSize(floorplan):
    if floorplan is not None:
        obj = floorplan.find('span', class_='detailsTextWrapper')
        if obj is not None:
            text = findSizeInList(obj, ["sq ft"])
            if not text:
                return '0'
            text = text.strip("sq ft").strip().replace(",", "")
            split = text.find('-')
            size = 0
            try:
                if split > -1:
                    size1 = int(text[:split].strip())
                    size2 = int(text[split + 1:].strip())
                    size = (size1 + size2) // 2
                else:
                    size = int(text.strip())
            except ValueError:
                size = 0
            return str(size)
    return '0'

def scrapeBed(floorplan):
    if floorplan is not None:
        obj = floorplan.find('span', class_='detailsTextWrapper')
        if obj is not None:
            text = findSizeInList(obj, ["bed", "beds", "studio"])
            if not text:
                return '0'
            text = text.lower()
            data = text.split()
            beds = text
            if len(data) >= 1:
                beds = data[0]
            if 'studio' in beds.lower():
                beds = '1'
            try:
                float(beds)
                return beds
            except ValueError:
                return '0'
    return '0'

def scrapeBath(floorplan):
    if floorplan is not None:
        obj = floorplan.find('span', class_='detailsTextWrapper')
        if obj is not None:
            text = findSizeInList(obj, ["bath", "baths", "studio"])
            if not text:
                return '0'
            text = text.lower()
            data = text.split()
            baths = text
            if len(data) >= 1:
                baths = data[0]
            if 'studio' in baths.lower():
                baths = '1'
            try:
                float(baths)
                return baths
            except ValueError:
                return '0'
    return '0'