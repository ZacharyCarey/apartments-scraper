import xlsxwriter

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row + 1)

class OutputRow(object):
    def __init__(self, listValues, config):
        self.Values = {}
        self.listValues = listValues
        self.ApartmentName = None
        self.URL = None
        self.Floorplan = None
        self.config = config
        
    def setApartmentName(self, name):
        """ The name of the apartment complex. """
        self.ApartmentName = name

    def setApartmentURL(self, url):
        """ The URL to the Apartments.com page. """
        self.URL = url

    def setFloorplanName(self, name):
        """ The name of the floorplan. """
        self.Floorplan = name

    def getNameCell(self):
        """ Returns the data for the "name" cell  in the correct format. """
        apartment = self.ApartmentName
        floorplan = self.Floorplan
        if apartment is None:
            apartment = ""
        if floorplan is None:
            floorplan = ""
        text = apartment + " \'" + floorplan + "\'"
        if self.URL is None:
            return text
        else:
            return "=HYPERLINK(\"" + self.URL + "\", \"" + text + "\")"

    def setValue(self, key, value):
        self.Values[key] = value

    def getValueCell(self, key):
        if key not in self.Values:
            return ""
        return self.Values[key]
    
    def addListValue(self, key, value):
        if key not in self.Values:
            self.Values[key] = []
        val = self.Values[key]
        if value not in val:
            val.append(value)

    def getListCell(self, key):
        if key not in self.listValues:
            return ""
        listItems = self.listValues[key]
        if key not in self.Values:
            self.Values[key] = []
        val = self.Values[key]
        items = []
        #Add items from our list in the order they appear iun the restricted items
        for item in listItems:
            if item in val:
                items.append(item)
        #Check to make sure all items are valid items
        for item in val:
            if item not in items:
                items.append("Other")
                break
        return " / ".join(items)

    

class OutputFile(object):

    headers = {
        'name': ["Name / Link", 35.0],
        'neighborhood': ["Neighborhood", 15.0],
        'price': ["Price", 11.0],
        'size': ["Size (sqft)", 10.0],
        'value': ["Price/sqft", 10.0],
        'bed': ["Bed", 5.0],
        'bath': ["Bath", 5.0],
        'utilities': ["Included Utilities", 18.0, {'separateUtilities': False}],
        'utilities[Air Conditioning]': ["A/C Incl.", 8.0, {'separateUtilities': True}],
        'utilities[Electric]': ["Electric Incl.", 8.0, {'separateUtilities': True}],
        'utilities[Gas]': ["Gas Incl.", 8.0, {'separateUtilities': True}],
        'utilities[Heat]': ["Heat Incl.", 8.0, {'separateUtilities': True}],
        'utilities[Sewage]': ["Sewage Incl.", 8.0, {'separateUtilities': True}],
        'utilities[Trash]': ["Trash Incl.", 8.0, {'separateUtilities': True}],
        'utilities[Water]': ["Water Incl.", 8.0, {'separateUtilities': True}],
        'utilities[Other]': ["Other Util. Incl.", 8.0, {'separateUtilities': True}],
        'parking': ["Parking", 10.0],
        'pets': ["Pets", 7.0, {'separatePets': False}],
        'pets[Cats]': ["Cats", 7.0, {'separatePets': True}],
        'pets[Dogs]': ["Dogs", 7.0, {'separatePets': True}],
        'pets[Other]': ["Other Pets", 7.0, {'separatePets': True}],
        'monthly': ["Monthly Fees", 15.0],
        'fees': ["One-Time Fees", 15.0],
        'recreation': ["Recreation", 11.0],
        'features': ["Features", 10.0],
        'outdoors': ["Outdoors", 9.0],
        'lease': ["Lease Length (mo)", 17.0],
        'address': ["Address", 23.0],
        'distance': ["Distance (mi)", None],
        'duration': ["Duration (min)", None]
    }

    values = {
        'utilities': ["Air Conditioning", "Electric", "Gas", "Heat", "Sewage", "Trash", "Water"],
        'parking': ["Covered", "Garage", "Lot"],
        'pets': ["Cats", "Dogs"],
        'monthly': ["Storage Fee", "Cat Rent", "Dog Rent", "Parking"],
        'fees': ["Application Fee", "Admin Fee", "Cat Fee", "Dog Fee"],
        'recreation': ["Fitness Center", "Pool", "Tennis Court", "Trails", "Sauna", "Spa", "Racquetball Court", "Volleyball Court", "Playground"],
        'features': ["Smoke Free", "Storage Unit", "Fireplace"],
        'outdoors': ["Gated", "Grill", "Balcony", "Patio", "Sundeck", "Courtyard", "Picnic Area"]
    }

    def __init__(self, output_name, config):
        self.config = config
        self.wb = xlsxwriter.Workbook(output_name + '.xlsx')
        self.ws = self.wb.add_worksheet()
        self.columns = {}

        #Create the number format for later
        self.num_format = self.wb.add_format()
        self.num_format.set_num_format(44)

        #Create hyperlink format for later
        self.link_format = self.wb.add_format()
        self.link_format.set_underline()
        self.link_format.set_font_color('blue')

        #Create the header cell format
        cell_format = self.wb.add_format()
        cell_format.set_bold()

        #Write the header cells, set cell width, and store col numbers for later use
        col = 0
        for category, header in self.headers.items():
            if (len(header) > 2) and (header[2] is not None):
                #Check config requirements
                displayHeader = True
                for requirement, value in header[2].items():
                    if (requirement not in config) or (value != config[requirement]):
                        displayHeader = False
                        break
                if not displayHeader:
                    continue #Does not meet display requirements
            if (len(header) > 1) and (header[1] is not None):
                self.ws.set_column(col, col, header[1])
            self.columns[category] = col
            self.ws.write(0, col, header[0], cell_format)
            col += 1
        
        self.currentRow = 1

    def getNewRow(self):
        return OutputRow(self.values, self.config)

    def writeCell(self, key, value, format):
        if format is None:
            self.ws.write(self.currentRow, self.columns[key], value)
        else:
            self.ws.write(self.currentRow, self.columns[key], value, format)

    def writeRow(self, row):
        nameCell = row.getNameCell()
        nameFormat = None
        if "HYPERLINK" in nameCell:
            nameFormat = self.link_format
        self.writeCell('name', nameCell, nameFormat)
        self.writeCell('neighborhood', row.getValueCell('neighborhood'), None)
        self.writeCell('price', float(row.getValueCell('price')), self.num_format)
        self.writeCell('size', int(row.getValueCell('size')), None)
        self.writeCell('value', "=" + excel_style(self.currentRow, self.columns['price']) + "/" + excel_style(self.currentRow, self.columns['size']), self.num_format)
        self.writeCell('bed', float(row.getValueCell('bed')), None)
        self.writeCell('bath', float(row.getValueCell('bath')), None)
        self.writeSeparatedCells(row, 'utilities', 'separateUtilities', None)
        self.writeCell('parking', row.getListCell('parking'), None)
        self.writeSeparatedCells(row, 'pets', 'separatePets', None)
        self.writeCell('monthly', row.getListCell('monthly'), None)
        self.writeCell('fees', row.getListCell('fees'), None)
        self.writeCell('recreation', row.getListCell('recreation'), None)
        self.writeCell('features', row.getListCell('features'), None)
        self.writeCell('outdoors', row.getListCell('outdoors'), None)
        self.writeCell('lease', row.getListCell('lease'), None)
        self.writeCell('address', row.getValueCell('address'), None)
        self.writeCell('distance', row.getValueCell('distance'), None)
        self.writeCell('duration', row.getValueCell('duration'), None)

        self.currentRow += 1

    def writeSeparatedCells(self, row, key, configKey, format):
        if self.config[configKey]:
            if key in self.values:
                listValues = self.values[key]
                values = []
                if key in row.Values:
                    values = row.Values[key]
                for listValue in listValues:
                    value = "No"
                    if listValue in values:
                        value = "Yes"
                    self.writeCell(key + '[' + listValue + ']', value, format)
        else:
            self.writeCell(key, row.getListCell(key), format)

    def close(self):
        self.wb.close()
    