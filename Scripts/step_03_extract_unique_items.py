import os
import csv
import Scripts.script_values as v

def extract_unique_items(year, market):
    """
    Extracts unique items (based on item name) from the merged receipts file 
    and writes them to a new CSV file that only contains the unique items.

    New items are always added at the end of the list.

    Args:
        year:   only concentrates on the data of the selected year
        market: only concentrates on the data of the selected market
    """

    unique_items = set()  # Use a set to efficiently store unique item names
    item_list = [] # List to hold unique items for writing to csv

    file_merged_receipts = os.path.join(v.dir_data, v.dir_CSV_results, market, year + "_" + v.file_merged_receipts)
    try:
        with open(f"{file_merged_receipts}", 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            header = next(reader, None)  # Skip the header row (if it exists)

            for row in reader:
                item_name = row[0]  # Assuming item name is in the first column
                if item_name not in unique_items:
                    unique_items.add(item_name)
                    item_list.append([item_name, ""]) # Add the entire row to the list

    except FileNotFoundError:
        print(f"Error: Input file '{file_merged_receipts}' not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the input file: {e}")
        return

    file_unique_items = os.path.join(v.dir_data, v.dir_CSV_results, market, year + "_" + v.file_unique_items)
    # Write unique items to the output CSV file
    try:
        with open(f"{file_unique_items}", 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["item", "category"])  # Write the header row (if it exists in input)
            writer.writerows(item_list) # Write all unique items

        # print(f"Successfully extracted unique items to '{file_unique_items}'.")

    except Exception as e:
        print(f"An error occurred while writing to the output file: {e}")
