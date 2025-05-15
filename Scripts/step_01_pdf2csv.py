import pypdf
import csv
import re
import os
import Scripts.script_values as v


def extract_receipt_data(pdf_file, csv_file, market):
    """
    Extracts item details (name, price, quantity) and date from a receipt PDF 
    and saves them to a CSV file.

    Args:
        pdf_file (str): Path to the PDF receipt file, like "Your Receipts/{Market}"
        csv_file (str): Path to the output CSV file, like "Data/CSV Extracts/{Market}"
    """

    try:
        with open(pdf_file, 'rb') as f:
            reader = pypdf.PdfReader(f)
            num_pages = len(reader.pages) # use this variable for multiple pdf pages with bought items
            items = []  # List to store extracted item data (name, price, quantity, date)
            date = None # Initialize the date variable

            page_num = 0 # Start with first pdf page
            #for page_num in range(num_pages): # TODO: uncomment for going through multiple pages
            page = reader.pages[page_num]
            text = page.extract_text()

            # Extract Date
            date_match = re.search(r"Datum:\s*(\d{2}\.\d{2}\.\d{4})", text) # TODO: may requires adaptation (learn through bug reports)
            if date is None and date_match:  # Only assign once with the first page
                date = date_match.group(1)

            ## Extra magic to create a better sortable csv file name
            splitted_date = date.split(".")
            csv_file_added_date = os.path.join(v.dir_data, v.dir_CSV_extracts, market, splitted_date[2] + "." + splitted_date[1] + "." + splitted_date[0] + "-" + csv_file)

            skippedIntroduction = False
            # Extract item lines (This part needs careful adjustment based on receipt format)
            lines = text.split('\n')
            for line in lines:
                item_match = re.search(r"([\s]+EUR)", line) # TODO: Adapt the pattern to what always appears before the first item
                if item_match:
                    skippedIntroduction = True
                
                # Example pattern to match items (adjust as needed!)
                item_match = re.search(r"([A-Za-z0-9\s\S]+)\s+([-\d,\.]+)", line)  # Matches item name and price
                if item_match and skippedIntroduction:
                    if "SUMME" in item_match.group(1):
                        break
                    item_name = item_match.group(1).strip()
                    try:
                        price = float(item_match.group(2).replace(',', '.')) # Handle comma as decimal separator
                    except ValueError:
                        continue  # Skip lines with invalid price format

                    # Attempt to determine quantity (This is tricky and might need more sophisticated logic)
                    quantity = 1  # Default quantity if not found explicitly
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

                    if "Handeingabe" in line: # when you get food from the meat counter
                        continue


                    items.append([item_name, price, quantity, date])


            # Write data to CSV file
            try:
                with open(csv_file_added_date, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Item Name', 'Price', 'Quantity', 'Date'])  # Header row
                    writer.writerows(items)

            except Exception as e:
                print(f"An error occurred while writing the output file {csv_file_added_date}: {e}")

    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_file}")
    except Exception as e:
        print(f"An error occurred: {e}")
