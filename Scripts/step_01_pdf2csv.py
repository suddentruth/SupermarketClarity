import pypdf
import re
import os
import Scripts.script_values as v
import dateutil.parser as parser


def extract_receipt_data(pdf_file, csv_file, year, market):
    """
    Extracts item details (name, price, quantity) and date from a receipt PDF 
    and saves them to a CSV file.

    Args:
        pdf_file (str): Path to the PDF receipt file, like "Your Receipts/{Market}"
        csv_file (str): Path to the output CSV file, like "Data/CSV Extracts/{Market}"
    """

    try:
        with open(pdf_file, 'rb') as f:
            items = []
            reader = pypdf.PdfReader(f)
            date = extract_date(reader, year) # Initialize the date variable
            dateFormated = date.strftime("%Y-%m-%d")
            if date and date.year == int(year):
                
                match market:
                    case "REWE":
                        items = processDataFromReweReceipts(reader, dateFormated)
                    case "EDEKA":
                        items = processDataFromEdekaReceipts(reader, dateFormated)
                    case "DM":
                        items = processDataFromDMReceipts(reader, dateFormated)
                    case _:
                        print(f"{v.BLUE}No market provided or unknown market. :( Create a features request.{v.RESET}")

                # Write data to CSV file
                csv_file_added_date = os.path.join(v.dir_data, v.dir_CSV_extracts, market, f"{dateFormated}_{csv_file}")
                if items and market: v.writeItemsToCSV(csv_file_added_date, ['Item Name', 'Price', 'Quantity', 'Date'], items)
    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_date(reader, year):
    page_num = 0
    num_pages = len(reader.pages)
    # Go through all pages to identify date
    for page_num in range(num_pages):
        page = reader.pages[page_num]
        text = page.extract_text()

        # date patterns for Germany (check this page for every country and form: https://en.wikipedia.org/wiki/List_of_date_formats_by_country)
        # p1: 2025-01-31
        # p2: 01.01.2025
        # p3: 1.1.25 or 31.12.2025 or 01.01.25
        patterns = [r"(\d{4}-\d{2}-\d{2})", r"(\d{2}\.\d{2}\.\d{4})", r"(\d{1,2}\.\d{1,2}\.\d{2,4})"]
        # print(text)
        for pattern in patterns:
            date_match = re.search(pattern, text)
            
            if date_match != None:
                # print(f"page: {page_num} + date match: {date_match.groups()} + pattern: {pattern}")
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
            if "EUR" in line:
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
            if "EUR" in line:
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
            item_match = re.search(r"(\d{2}.\d{2}.\d{4})", line) # Need to use regex since a date is dynamic
            if item_match:
                skippedIntroduction = True
                continue # required to skip this line as it will be matched with the later regex
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