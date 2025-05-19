import pypdf
import re
import os
import Scripts.script_values as v
import dateutil.parser as parser


def extract_receipt_data(pdf_file, csv_file, year, market):
    """
    Extracts item details (name, price, quantity) and date from a receipt PDF (or PNG receipt processed via OCR into a text file)
    and saves them to a CSV file.

    Args:
        pdf_file (str): Path to the PDF receipt file, like "Your Receipts/{Market}"
        csv_file (str): Path to the output CSV file, like "Data/CSV Extracts/{Market}"
    """
    try:
        with open(pdf_file, 'rb') as f:
            items = []
            isPNGFile = False
            # use pdf_file as reader instead of pypdf reader for PNGs
            if market == v.markets.get("LIDL") or market == v.markets.get("Müller"):
                isPNGFile = True
                reader = pdf_file
            else:
                reader = pypdf.PdfReader(f)
            date = extract_date(reader, year, isPNGFile) # Initialize the date variable
            dateFormated = date.strftime("%Y-%m-%d")
            
            if date and date.year == int(year):
                match market:
                    case "REWE":
                        items = processDataFromReweReceipts(reader, dateFormated)
                    case "EDEKA":
                        items = processDataFromEdekaReceipts(reader, dateFormated)
                    case "DM":
                        items = processDataFromDMReceipts(reader, dateFormated)
                    case "LIDL":
                        items = processDataFromLIDLReceipts(reader, dateFormated)
                    case "Kaufland":
                        items = processDataFromKauflandReceipts(reader, dateFormated)
                    case "Müller":
                        items = processDataFromMüllerReceipts(reader, dateFormated)
                    case "OBI":
                        items = processDataFromOBIReceipts(reader, dateFormated)
                    case _:
                        print(f"{v.BLUE}No market provided or unknown market. :( Create a features request.{v.RESET}")

                # Write data to CSV file
                csv_file_added_date = os.path.join(v.dir_data, v.dir_CSV_extracts, market, f"{dateFormated}_{csv_file}")
                if items and market: v.writeItemsToCSV(csv_file_added_date, ['Item Name', 'Price', 'Quantity', 'Date'], items)
    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_date(reader, year, isPNGFile):
    """
        Method extracts the date from the text provided by reader object.
        In case of PNG we get a block of text, extracted from an image.
        In case of PDF we get the current page as text from the pdf-reader.
        In all cases we check the text to discover three type of time patterns.
        
        Standard date patterns for Germany (check this page for every country and form: https://en.wikipedia.org/wiki/List_of_date_formats_by_country)
            1. pattern: 2025-01-31
            2. pattern: 01.01.2025
            3. pattern: 1.1.25 or 31.12.2025 or 01.01.25
        
        Return a datetime object if date was found.
    """
    page_num = 0
    if isPNGFile: num_pages = 1
    else: num_pages = len(reader.pages)

    # Go through all pages to identify date
    for page_num in range(num_pages):
        text = ""
        if isPNGFile:
            # Special handling for png files. Using reader as pdf_file string
            text = v.readTextFromFakePDF(reader)
        else:
            page = reader.pages[page_num]
            text = page.extract_text()

        patterns = [r"(\d{4}-\d{2}-\d{2})", r"(\d{2}\.\d{2}\.\d{4})", r"(\d{1,2}\.\d{1,2}\.\d{2,4})"]
        for pattern in patterns:
            date_match = re.search(pattern, text)
            if date_match != None:
                try:
                    dateGroup = date_match.group(1)
                    if pattern == patterns[0]:
                        dt = parser.parse(dateGroup, yearfirst=True) # different pattern, different parsing
                    else:
                        dt = parser.parse(dateGroup, dayfirst=True)
                    if dt.year != int(year): break # if it is not our current year, we don't care.
                    else: return dt # assume that we found a valid year, return the datetime object
                except Exception as e:
                    print(f"Thrown error: {e}")
        
    return dt.strptime("1970-01-01",'%Y-%m-%d') # no valid date found

def processDataFromReweReceipts(reader, date):
    """
    Method for REWE to get items from PDF file into CSV file.
    1. We skip the header up to the first sign ("EUR") that the item list will begin.
    2. If our search result of two groups (first the item name, second the price) contains "SUMME" we stop further processing and write the gathered data into the list.
    3. If we buy higher quantities of the same item we detect it by "Stk"
    4. If we buy unpackaged food that will be weighted, we detect this by "kg x"
    5. If we buy something from the meat counter, we detect it by "Handeingabe"
    """
    items = []  # List to store extracted item data (name, price, quantity, date)
    page_num = 0
    num_pages = len(reader.pages)
    skippedIntroduction = False
    skipRest = False

    for page_num in range(num_pages):
        page = reader.pages[page_num]
        text = page.extract_text()
        lines = text.split('\n')
        if skipRest == True: break

        for line in lines:
            # Matches the text before the first item and after the last item
            if "EUR" in line and not skippedIntroduction:
                skippedIntroduction = True
            if "SUMME" in line:
                skipRest = True
                break

            # Try to match items
            item_match = re.search(r"([A-Za-z0-9\s\S]+)\s+([-\d,\.]+)", line)  # Matches item name and price
            if item_match and skippedIntroduction:
                item_name = item_match.group(1).strip()
                price = float(item_match.group(2).replace(',', '.')) 
                quantity = 1  # Default quantity

                if "Stk x" in line:
                    try:
                        quantity_match = re.search(r"(\d+)\s*Stk", line)
                        if quantity_match:
                            quantity = int(quantity_match.group(1))
                            cache_item = items.pop()
                            item_name = cache_item[0]

                    except ValueError:
                        pass

                if "kg x" in line:
                    try:
                        quantity_match = re.search(r"(\d+,\d+)\s*kg", line)
                        if quantity_match:
                            quantity = float(quantity_match.group(1).replace(',', '.'))
                            price_match = re.search(r"(\d+,\d+)\sEUR\/kg", line)
                            if price_match:
                                price = float(price_match.group(1).replace(',', '.'))
                                cache_item = items.pop()
                                item_name = cache_item[0]
                    except ValueError:
                        pass

                if "Handeingabe" in line: # when you get food from the meat counter, skip this line
                    continue


                items.append([item_name, price, quantity, date])
    return items

def processDataFromEdekaReceipts(reader, date):
    """
    Method for EDEKA to get items from PDF file into CSV file.
    1. We skip the header up to the first sign ("EUR") that the item list will begin.
    2. If our search result of two groups (first the item name, second the price) contains "Posten:" we stop further processing and write the gathered data into the list.
    3. If we buy higher quantities of the same item we detect it by seperating the initial item_name into "Quantity", "Item price" and "Item name"
    4. We pop the last item if it contains the "Coupon" id.
    """
    items = []  # List to store extracted item data (name, price, quantity, date)
    page_num = 0
    num_pages = len(reader.pages)
    skippedIntroduction = False
    skipRest = False

    for page_num in range(num_pages):
        page = reader.pages[page_num]
        text = page.extract_text()
        lines = text.split('\n')
        if skipRest == True: break

        for line in lines:
            # Matches the text before the first item and after the last item
            if "EUR" in line and not skippedIntroduction:
                skippedIntroduction = True
            if "Posten:" in line:
                skipRest = True
                break

            # Try to match items
            item_match = re.search(r"([A-Za-z0-9\s\S]+)\s+([-\d,\.]+)", line)  # Matches item name and price
            if item_match and skippedIntroduction:
                item_name = item_match.group(1).strip()
                price = float(item_match.group(2).replace(',', '.'))
                quantity = 1  # Default quantity
                
                quantity_match = re.search(r"(\d)+€ x (\d+.\d{2})([A-Za-z0-9\s\S]+)",item_name) # pattern like "2€ x 4,99SENSOD.ZAHNCREME" gets matched
                if quantity_match: #item name contains quantity, therefore update variables
                    quantity = quantity_match.group(1)
                    price = float(quantity_match.group(2).replace(',', '.'))
                    item_name = quantity_match.group(3)

                items.append([item_name, price, quantity, date])

    # remove Coupon id entry if exists TODO Maybe also add for other markets later if actually used
    if items and "Coupon" in items[-1][0]:
        items.pop()
    return items

def processDataFromDMReceipts(reader, date):
    """
    Method for DM to get items from PDF file into CSV file.
    1. We skip the header up to the first sign ("EUR") that the item list will begin.
    2. If our search result of two groups (first the item name, second the price) contains "Posten:" we stop further processing and write the gathered data into the list.
    3. If we buy higher quantities of the same item we detect it by seperating the initial item_name into "Quantity", "Item price" and "Item name"
    4. We remove items that got cancelled
    """
    items = []  # List to store extracted item data (name, price, quantity, date)
    page_num = 0
    num_pages = len(reader.pages)
    skippedIntroduction = False
    skipRest = False

    for page_num in range(num_pages):
        page = reader.pages[page_num]
        text = page.extract_text()
        lines = text.split('\n')
        if skipRest == True: break

        for line in lines:
            # Matches the text before the first item and after the last item
            item_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", line) # Need to use regex since a date is dynamic
            if item_match and not skippedIntroduction:
                skippedIntroduction = True
            if "SUMME EUR" in line:
                    skipRest = True
                    break
            
            # Try to match items
            item_match = re.search(r"([A-Za-z0-9\s\S]+)\s+([-\d,\.]+)\s+(\d{1})", line)  # Matches item name and price and taxation group
            coupon_match = re.search(r"([A-Za-z0-9\s\S]+)\s+([-\d,\.]+)", line)
            if item_match and skippedIntroduction:                
                item_name = item_match.group(1).strip()
                price = float(item_match.group(2).replace(',', '.')) # Handle comma as decimal separator
                quantity = 1  # Default quantity

                quantity_match = re.search(r"(\d)+x (\d+.\d{2})([A-Za-z0-9\s\S]+)",item_name) # pattern like "2x 0,65 babylove 1J Apf.Ban.Ki" gets matched
                if quantity_match: #item name contains quantity, therefore update variables
                    quantity = quantity_match.group(1)
                    price = float(quantity_match.group(2).replace(',', '.'))
                    item_name = quantity_match.group(3).strip()

                # remove item that has been cancelled
                if price < 0 and items and item_name == items[-1][0]:
                    items.pop()
                    continue # and don't add the item again

                items.append([item_name, price, quantity, date])
                
            elif coupon_match and skippedIntroduction:
                coupon_name = coupon_match.group(1).strip()
                price = float(coupon_match.group(2).replace(',','.'))
                quantity = 1
                if "Zwischensumme" not in coupon_name:
                    items.append([coupon_name, price, quantity, date])
    return items

def processDataFromLIDLReceipts(reader, date):
    """
        Captures three scenarios, going from specif to coarse and skip the rest if match found
        1. differentQuantityMatch matched e.g. "Avocado vorger. 1,29 x 2 2,58 A"
        2. weightedFoodMatch matched e.g. "0,368 kg x 14,90 EUR/kg"
        3. simplestMatch matched e.g. "TomateCherrysüß 5,48 A"
    """
    items = []
    lines = v.readLinesFromFakePDF(reader)
    skippedIntroduction = False

    for line in lines:
        # Matches the text before the first item and after the last item
        if "EUR" in line and not skippedIntroduction:
            skippedIntroduction = True
            continue
        if "zu zahlen" in line:
            break
        
        quantity = "1" # default quantity
        dQMatch = re.search(r"([A-Za-z0-9\s\S]+)\s+(\d+,\d{2}) x (\d)+ ([-\d,\.]+)",line)
        if dQMatch and skippedIntroduction:
            items.append([dQMatch.group(1), dQMatch.group(2).replace(",","."), dQMatch.group(3), date])
            continue
        
        wFMatch = re.search(r"(\d+,\d+)([A-Za-z0-9\s\S]+)\s+([-\d,\.]+) (EUR\/kg)", line)        
        if wFMatch and skippedIntroduction and items:
            cachedItem = items.pop()
            items.append([cachedItem[0], wFMatch.group(3).replace(",","."), wFMatch.group(1).replace(",","."), date])
            continue

        sMatch = re.search(r"([A-Za-z0-9\s\S]+)\s+([-\d,\.]+)", line)
        if sMatch and skippedIntroduction:
            items.append([sMatch.group(1), sMatch.group(2).replace(",","."), quantity, date])

    return items

def processDataFromKauflandReceipts(reader, date):
    """
    Method for Kaufland to get items from PDF file into CSV file.
    1. the whole PDF does not contain "\\n" newlines, therefore we split it first at "Preis EUR" and second split at "Summe" to only have the items
    2. As we can't get the lines themselves, we decided to split everything by at least two whitespaces
    3. We set the initial item data and then go through the different cases for the fragments
        a. See below for details
    4. Once we get the next item_name we conclude that the last item has all data set and can be saved and reset the item values to default again
    """
    items = []  # List to store extracted item data (name, price, quantity, date)
    page_num = 0
    num_pages = len(reader.pages)
    for page_num in range(num_pages):
        page = reader.pages[page_num]
        text = page.extract_text()
        
        firstSplit = re.split(r"([A-Za-z0-9\s\S]+)Preis EUR\s*", text)
        secondSplit = re.split(r"Summe", firstSplit[2])
        textFragments = re.split(r"(?:  )+", secondSplit[0])

        item_name = ""
        price = ""
        quantity = "1"


        for fragment in textFragments:
            """
            validate following case:
                1. if it contains an '*' split it by the '*', first part is quantiy, second price per unit
                2. if it is r"-*\\d+,d{2} [A|B]" it is the price or pawn returned
                    --> use to reset values and save item
                3. if it is r"-\\d+,d{2}" it is the discount (price)
                    --> use to reset values and save item
                4. if it is r"\\d+,\\d+ kg" is the weighted (try to calculated the correct price per unit afterwards)
                5. otherwise is the item name
            """
            priceMatch = re.search(r"-*\d+,\d{2} [A|B]", fragment)
            discountMatch = re.search(r"-\d+,\d{2}", fragment)
            weightedMatch = re.search(r"\d+,\d+ kg", fragment)

            if "*" in fragment:
                quantityAndPrice = re.split(r"\*", fragment)
                quantity = quantityAndPrice[0]
                price = float(quantityAndPrice[1].replace(',', '.'))
            elif priceMatch:
                tempPrice = float(re.split(r" ",priceMatch.group(0))[0].replace(',', '.'))
                if not price: # helps to ignore the final price and keeps quantity and price per unit correct in data
                    price = tempPrice
                elif tempPrice < 0:# e.g. money of deposit returned for bottles
                    price = -price 
                    
            elif discountMatch:
                price = float(discountMatch.group(0).replace(',', '.'))
            elif weightedMatch:
                quantity = str(float(re.split(r" ",weightedMatch.group(0))[0].replace(',', '.')))
            else:
                # required for first item name, not not append empty values to list
                if not item_name:
                    item_name = fragment
                    continue
                
                # require to calculate price per unit and save this as price instead of actual price
                if "." in quantity:
                    price = round(price/float(quantity),2)
                
                # save item and setup for next entry
                items.append([item_name, price, quantity, date])
                item_name = fragment
                price = ""
                quantity = "1"            
    return items

def processDataFromMüllerReceipts(reader, date):
    """
        Easy structured, can be splitted with one regex search.
        Has always structure of "Quantity, Name, Price per Unit, and Total Price"
            No receipt yet where discount applies.
        E.g. "1 TROLLI SAURE GLUEH- 1,09 1.096"
    """
    items = []
    lines = v.readLinesFromFakePDF(reader)
    skippedIntroduction = False

    for line in lines:
        # Matches the text before the first item and after the last item
        if not line: # skip empty lines automatically
            continue
        if "Summe" in line and not skippedIntroduction:
            skippedIntroduction = True
            continue
        if "ZU BEZAHLEN" in line:
            break
        
        # easy structure, easy search
        match = re.search(r"(\d+) ([A-Za-z0-9\s\S]+)\s+(\d+,\d{2}) ", line)
        if match and skippedIntroduction:
            if "Zwischensumme" in match.group(2): # skip them
                continue
            items.append([match.group(2), match.group(3).replace(",","."), match.group(1), date])
        
    return items

def processDataFromOBIReceipts(reader, date):
    """
    Method for OBI to get items from PDF file into CSV file.
    1. For start of item list we check for a date just like in DM market case, for end we check for "Zwischensumme"
    2. Item list contains in the first line the total name of the item, in second line quantity and price
    3. Correct price we check whether quantity is other than "1" depending on the case we take a different price.
    4. At the end we append item to list and reset to default values for next item iteration.
    """
    items = []  # List to store extracted item data (name, price, quantity, date)
    page_num = 0
    num_pages = len(reader.pages)
    skippedIntroduction = False
    skipRest = False

    for page_num in range(num_pages):
        page = reader.pages[page_num]
        text = page.extract_text()
        lines = text.split('\n')
        if skipRest == True: break

        item_name = ""
        price = ""
        quantity = "1"
        for line in lines:
            # Matches the text before the first item and after the last item
            item_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", line) # Need to use regex since a date is dynamic
            if item_match and not skippedIntroduction:
                skippedIntroduction = True
                continue # required to skip this line as it will be matched with the later regex
            if "Zwischensumme" in line:
                    skipRest = True
                    break
            
            if not item_name and skippedIntroduction:
                item_name = line.strip() # found name, continue to next line!
                continue
            
            lineFragments = re.split(r"(?: )+", line)
            if lineFragments and skippedIntroduction:                      
                if lineFragments[1]:
                    if lineFragments[1] == "1":
                        price = lineFragments[-2].replace(',',".")
                    else:
                        quantity = float(lineFragments[1].replace(',',"."))
                        price = lineFragments[-4].replace(',',".")
                    
                items.append([item_name, price, quantity, date])

                item_name = ""
                price = ""
                quantity = "1"
    return items
