import pypdf
import re
import os
import Scripts.script_values as v
import dateutil.parser as parser

FIELD_MAPS = {
    "Default": {
        "full":        {'name': 'name', 'price': 'price', 'quantity': 'qty'},
        "no_name":     {'price': 'price', 'quantity': 'qty'},
        "no_quantity": {'name': 'name', 'price': 'price'}
    },
    "Special": {
        "no_name_plus_total":  {'price': 'price', 'quantity': 'qty', 'total': 'total'},
        "pure_name":           {'name': 'name'},
        "barcode_name":        {'name': 'name', 'barcode': 'barcode'}
    }
}

POST_PROCESSING_MAPS = {
    "name_from_last_item": lambda i, items: {
        'name': items.pop()[0] if items else "",
        'price': i['price'],
        'quantity': i['quantity']
    },
    "calculate_price_from_weight": lambda i, items=None: {
        'name': i['name'],
        'price': round(parse_float(i['price']) / parse_float(i['quantity']), 2),
        'quantity': i['quantity']
    },
    "name_from_last_item_negative_total": lambda i, items: {
        'name': items.pop()[0] if items else "",
        'price': -parse_float(i['price']) if parse_float(i['total']) < 0 else parse_float(i['price']),
        'quantity': i['quantity']
    },
    "barcode_name": lambda i, items=None: {
        'name': i['barcode'] + " " + i['name']
    }
}

def extract_receipt_data(pdf_file, csv_file, year, market):
    """
    Extracts item details (name, price, quantity) and date from a receipt PDF (or PNG receipt processed via OCR into a text file)
    and saves them to a CSV file.

    Args:
        pdf_file (str): Path to the PDF receipt file, like "Your Receipts/{Market}"
        csv_file (str): Path to the output CSV file, like "Data/CSV Extracts/{Market}"
    """
    market_processors = {
        "REWE": processDataFromReweReceipts,
        "EDEKA": processDataFromEdekaReceipts,
        "DM": processDataFromDMReceipts,
        "LIDL": processDataFromLIDLReceipts,
        "Kaufland": processDataFromKauflandReceipts,
        "Müller": processDataFromMüllerReceipts,
        "OBI": processDataFromOBIReceipts,
    }
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
                processor = market_processors.get(market)
                if processor: items = processor(reader, dateFormated)
                else: print(f"{v.BLUE}No market provided or unknown market. :( Create a features request.{v.RESET}")
                 
                # Write data to CSV file
                csv_file_added_date = os.path.join(v.dir_base_CSV_extracts, market, f"{dateFormated}_{csv_file}")
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

    patterns = [r"(\d{4}-\d{2}-\d{2})", r"(\d{2}\.\d{2}\.\d{4})", r"(\d{1,2}\.\d{1,2}\.\d{2,4})"]

    # Go through all pages to identify date
    for page_num in range(num_pages):
        text = ""
        if isPNGFile:
            # Special handling for png files. Using reader as pdf_file string
            text = v.readTextFromFakePDF(reader)
        else:
            page = reader.pages[page_num]
            text = page.extract_text()

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

def parse_float(value: str) -> float:
    """
    Parses a string value to a float, replacing commas with dots.
    If the value cannot be converted, returns 0.0.
    """
    try:
        if isinstance(value, str):
            return float(value.replace(',', '.'))
        return value
    except ValueError:
        return 0.0

def should_process_line(line, state, start_marker_pattern=None , end_marker=None):
    """
    Determines whether a line should be processed based on the current state and markers.
    Args:
        line (str): The line of text to evaluate.
        state (dict): A dictionary containing the current state of processing.
        start_marker_pattern (str): A regex pattern to identify the start of the item list.
        end_marker (str): A string that indicates the end of the item list.
    Returns:
        bool: True if the line should be processed, False otherwise.
    """
    if not state["skippedIntroduction"]:
        if start_marker_pattern and re.search(start_marker_pattern, line):
            state["skippedIntroduction"] = True
        return False
    if end_marker and end_marker in line:
        state["skipRest"] = True
        return False
    return True

def try_append_item(field_map, line, pattern, items, date, post_process=None):
    match = pattern.search(line.strip())
    if match:
        # Extract fields using the field_map (dict: output_field -> regex group)
        item = {k: match.group(v).strip() for k, v in field_map.items()}
        # Optionally post-process fields e.g. to pop a name from a preivious item
        if post_process:
            item = post_process(item, items)
        
        item['name'] = item.get('name', '').strip()  # Ensure name is a string and stripped
        item['price'] = parse_float(item.get('price', '0.0'))  # Ensure price is a float
        item['quantity'] = parse_float(item.get('quantity', '1'))  # Ensure quantity is a float, default to 1
        item['date'] = date # Always add date
        
        items.append([item.get('name', ''), item.get('price', 0.0), item.get('quantity', 1), item['date']])
        return True
    return False

def processDataFromReweReceipts(reader, date):
    """
    Method for REWE to get items from PDF file into CSV file.
    1. We skip the header up to the first sign ("EUR") that the item list will begin.
    2. If we detect "SUMME" we stop further processing and write the gathered data into the list.
    3. If we buy something from the meat counter, we detect it by "Handeingabe"
    4. If we buy unpackaged food that will be weighted, we detect this by "kg x"
    5. If we buy higher quantities of the same item we detect it by "Stk"
    6. Otherwise we have a normale entry of item name and price
    """
    items = []  # List to store extracted item data (name, price, quantity, date)
    num_pages = len(reader.pages)
    state = {"skippedIntroduction": False, "skipRest": False}
    start_marker_pattern = r"EUR"
    end_marker = "SUMME"

    weighted_pattern = re.compile(r"^(?P<qty>\d+,\d+)\s*kg\s*x\s*(?P<price>\d+,\d{2})\s*EUR/kg") # e.g. "0,368 kg x 14,90 EUR/kg"
    counted_pattern = re.compile(r"^(?P<qty>\d+)\s*Stk\s*x\s*(?P<price>\d+,\d{2})") # e.g. "2 Stk x 1,29"
    item_pattern = re.compile(r"^(?P<name>.+?)\s+(?P<price>[-\d]+,\d{2})\s*[AB]?\s*\*?$") # e.g. "TomateCherrysüß 5,48 A*"

    for page_num in range(num_pages):
        page = reader.pages[page_num]
        text = page.extract_text()
        lines = text.split('\n')
        if state["skipRest"]: break

        for line in lines:
            # Matches the text before the first item and after the last item
            if not should_process_line(line, state, start_marker_pattern, end_marker):
                if state["skipRest"]: break
                continue

            if "Handeingabe" in line: continue # when you get food from the meat counter, skip this line
            
            # Weighted items (kg x)
            if try_append_item(FIELD_MAPS["Default"]["no_name"], line, weighted_pattern, items, date,
                POST_PROCESSING_MAPS["name_from_last_item"]
            ):continue

            # Counted items (Stk x)
            if try_append_item(FIELD_MAPS["Default"]["no_name"], line, counted_pattern, items, date,
                POST_PROCESSING_MAPS["name_from_last_item"]
            ):continue

            # Standard item line
            if try_append_item(FIELD_MAPS["Default"]["no_quantity"], line, item_pattern, items, date):continue
    return items

def processDataFromEdekaReceipts(reader, date):
    """
    Method for EDEKA to get items from PDF file into CSV file.
    1. We skip the header up to the first sign ("EUR") that the item list will begin.
    2. If our search result of two groups (first the item name, second the price) contains "Posten:" we stop further processing and write the gathered data into the list.
    3. If we buy higher quantities of the same item we detect it by seperating the initial item_name into "Quantity", "Item price" and "Item name"
    """
    items = []  # List to store extracted item data (name, price, quantity, date)
    num_pages = len(reader.pages)
    state = {"skippedIntroduction": False, "skipRest": False}
    start_marker_pattern = r"EUR"
    end_marker = "Posten:"
    
    quantity_pattern = re.compile(r"^(?P<qty>\d+)€\s*x\s*(?P<price>\d+,\d{2})(?P<name>.+?)\s*(\d+,\d{2})([A-Z*]{1,2})$")
    item_pattern = re.compile(r"^(?P<name>.+?)\s*(?P<price>[-\d]+,\d{2})([A-Z*]{1,2})*$")

    for page_num in range(num_pages):
        page = reader.pages[page_num]
        text = page.extract_text()
        lines = text.split('\n')
        if state["skipRest"]: break

        for line in lines:
            # Matches the text before the first item and after the last item
            if not should_process_line(line, state, start_marker_pattern, end_marker):
                if state["skipRest"]: break
                continue
            
            if try_append_item(FIELD_MAPS["Default"]["full"], line, quantity_pattern, items, date):continue

            if try_append_item(FIELD_MAPS["Default"]["no_quantity"], line, item_pattern, items, date):continue
    return items

def processDataFromDMReceipts(reader, date):
    """
    Method for DM to get items from PDF file into CSV file.
    1. We skip the header up to the first sign ("EUR") that the item list will begin.
    2. If our search result of two groups (first the item name, second the price) contains "Posten:" we stop further processing and write the gathered data into the list.
    3. If we buy higher quantities of the same item we detect it by seperating the initial item_name into "Quantity", "Item price" and "Item name"
    """
    items = []  # List to store extracted item data (name, price, quantity, date)
    num_pages = len(reader.pages)
    state = {"skippedIntroduction": False, "skipRest": False}
    start_marker_pattern = r"(\d{2}\.\d{2}\.\d{4})"
    end_marker = "SUMME EUR"

    pattern_subtotal = re.compile(r"^(?P<name>Zwischensumme)\s+(?P<price>\d+,\d{2})$")
    discount_pattern = re.compile(r"^(?P<name>.+?)\s+(?P<price>-?\d+,\d{2})$")
    quantity_pattern= re.compile(r"^(?P<qty>\d+)x\s*(?P<price>\d+,\d{2})\s+(?P<name>.+?)\s+(\d+,\d{2})\s+(\d+|§\d+)$")
    item_pattern = re.compile(r"^(?P<name>.+?)\s+(?P<price>[-\d]+,\d{2})\s+(\d+|§\d+)?$")

    for page_num in range(num_pages):
        page = reader.pages[page_num]
        text = page.extract_text()
        lines = text.split('\n')
        if state["skipRest"]: break

        for line in lines:
            # Matches the text before the first item and after the last item
            if not should_process_line(line, state, start_marker_pattern, end_marker):
                if state["skipRest"]: break
                continue

            # Try to match items            
            pattern_subtotal_match = pattern_subtotal.search(line.strip())
            if pattern_subtotal_match: # If we found the subtotal, we can skip this line
                continue

            if try_append_item(FIELD_MAPS["Default"]["no_quantity"], line, discount_pattern, items, date):continue

            if try_append_item(FIELD_MAPS["Default"]["full"], line, quantity_pattern, items, date):continue

            if try_append_item(FIELD_MAPS["Default"]["no_quantity"], line, item_pattern, items, date):continue
    return items

def processDataFromLIDLReceipts(reader, date):
    """
        Captures three scenarios, going from specif to coarse and skip the rest if match found
        1. weighted pattern matched e.g. "0,368 kg x 14,90 EUR/kg"
        2. quantity pattern matched e.g. "Avocado vorger. 1,29 x 2 2,58 A"
        3. item pattern matched e.g. "TomateCherrysüß 5,48 A"
    """
    items = []
    lines = v.readLinesFromFakePDF(reader)
    state = {"skippedIntroduction": False, "skipRest": False}
    start_marker_pattern = r"EUR"
    end_marker = "zu zahlen"


    weighted_pattern = re.compile(r"^(?P<qty>\d+,\d+)\s*kg\s*x\s*(?P<price>\d+,\d{2})\s*EUR\/kg$")
    quantity_pattern = re.compile(r"^(?P<name>.+?)\s+(?P<price>\d+,\d{2})\s*x\s*(?P<qty>\d+)\s+(?P<total>\d+,\d{2})\s+([A-Z])$")
    item_pattern = re.compile(r"^(?P<name>.+?)\s+(?P<price>\d+,\d{2})\s+([A-Z])$")
    # missing discount pattern as not yet having respective receipts to test against

    for line in lines:
        # Matches the text before the first item and after the last item
        if not should_process_line(line, state, start_marker_pattern, end_marker):
            if state["skipRest"]: break
            continue
        
        # Weighted items (kg x)
        if try_append_item(FIELD_MAPS["Default"]["no_name"], line, weighted_pattern, items, date,
            POST_PROCESSING_MAPS["name_from_last_item"]
        ):continue

        # Quantity items (unit price x qty ...)
        if try_append_item(FIELD_MAPS["Default"]["full"], line, quantity_pattern, items, date):continue

        # Standard item line
        if try_append_item(FIELD_MAPS["Default"]["no_quantity"], line, item_pattern, items, date):continue
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
    num_pages = len(reader.pages)
    state = {"skippedIntroduction": False, "skipRest": False}
    start_marker_pattern = r"Preis EUR"
    end_marker = "Summe"

    weighted_pattern = re.compile(r"^(?P<name>.+?)\s+(?P<qty>\d+,\d+)\s*kg\s+(?P<price>\d+,\d{2})\s+([A-Z])$")
    quantity_pattern = re.compile(r"^\s*(?P<qty>\d+)\s*\*\s*(?P<price>\d+,\d{2})\s+(?P<total>-?\d+,\d{2})\s+([A|B])$")    
    item_or_discount_pattern = re.compile(r"^(?P<name>.+?)\s+(?P<price>[-\d]+,\d{2})")
    purename_pattern = re.compile(r"(?P<name>.*)$")

    for page_num in range(num_pages):
        page = reader.pages[page_num]
        text = page.extract_text()
        lines = text.split('\n')

        if state["skipRest"]: break

        for line in lines:
            # Matches the text before the first item and after the last item
            if not should_process_line(line, state, start_marker_pattern, end_marker):
                if state["skipRest"]: break
                continue
            
            # Weighted items (name + weight + price + tax)
            if try_append_item(FIELD_MAPS["Default"]["full"], line, weighted_pattern, items, date,
                POST_PROCESSING_MAPS["calculate_price_from_weight"]
            ):continue

            # Quantity items (qty * unit_price ... total ...)
            if try_append_item(FIELD_MAPS["Special"]["no_name_plus_total"], line, quantity_pattern, items, date,
                POST_PROCESSING_MAPS["name_from_last_item_negative_total"]
            ):continue

            # Item or discount line (name + price)
            if try_append_item(FIELD_MAPS["Default"]["no_quantity"], line, item_or_discount_pattern, items, date):continue

            # Pure name line (fallback, no price/qty yet)
            if try_append_item(FIELD_MAPS["Special"]["pure_name"], line, purename_pattern, items, date):continue
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
    state = {"skippedIntroduction": False, "skipRest": False}
    start_marker_pattern = r"Summe"
    end_marker = "ZU BEZAHLEN"

    item_pattern = re.compile(r"^(?P<qty>\d+)\s+(?P<name>.+?)\s+(?P<price>\d+,\d{2})\s+(?P<total>\d+[.,]\d+[a-zA-Z0-9]*)$")
    subtotal_pattern = re.compile(r"(?P<name>Zwischensumme)\s+(?P<price>\d+,\d{2})")

    for line in lines:
        if not line: continue # Skip empty lines
        # Matches the text before the first item and after the last item
        if not should_process_line(line, state, start_marker_pattern, end_marker):
            if state["skipRest"]: break
            continue
        
        if subtotal_pattern.search(line.strip()):continue

        # item pattern
        if try_append_item(FIELD_MAPS["Default"]["full"], line, item_pattern, items, date):continue
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
    num_pages = len(reader.pages)
    state = {"skippedIntroduction": False, "skipRest": False}
    start_marker_pattern = r"\d{2}\.\d{2}\.\d{4}"
    end_marker = "Zwischensumme"

    barcode_name_pattern = re.compile(r"^(?P<barcode>\d{10,13})\s+(?P<name>.+)$")
    quantity_weight_pattern = re.compile(r"^(?P<qty>[\d,.]+)\s+(?P<unit>[A-Z]+)\s+a\s+(?P<price>\d+,\d{2})\s+([A-Z])\s+(?P<total>\d+,\d{2})$")
    item_pattern = re.compile(r"^(?P<qty>\d+)\s+([A-Z]+)\s+([A-Z])\s+(?P<price>\d+,\d{2})$")

    for page_num in range(num_pages):
        page = reader.pages[page_num]
        text = page.extract_text()
        lines = text.split('\n')
        if state["skipRest"]: break

        for line in lines:
            # Matches the text before the first item and after the last item
            if not should_process_line(line, state, start_marker_pattern, end_marker):
                if state["skipRest"]: break
                continue

            # E.g. 4007874881403 Verb.-Mutter M8x30 (first line of an item)
            if try_append_item(FIELD_MAPS["Special"]["barcode_name"], line, barcode_name_pattern, items, date,
                POST_PROCESSING_MAPS["barcode_name"]
            ):continue

            # E.g. 0,004 KG a 41,99 B 0,17 or 3 ST a 1,59 B 4,77 (second line of an item)
            if try_append_item(FIELD_MAPS["Default"]["no_name"], line, quantity_weight_pattern, items, date,
                POST_PROCESSING_MAPS["name_from_last_item"]
            ):continue

            # E.g. 1 ST B 3,29 (alternative second line of an item)
            if try_append_item(FIELD_MAPS["Default"]["no_name"], line, item_pattern, items, date,
                POST_PROCESSING_MAPS["name_from_last_item"]
            ):continue
    return items