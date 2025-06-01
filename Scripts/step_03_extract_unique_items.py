import os
import Scripts.script_values as v

def extract_unique_items(year, market):
    """
    Extracts unique items (based on item name) from the merged receipts file 
    and writes them to a new CSV file that only contains the unique items.

    New items are always added at the end of the list.
    """

    unique_items = set()  # Use a set to efficiently store unique item names
    item_list = [] # List to hold unique items for writing to csv

    file_merged_receipts = os.path.join(v.dir_base_CSV_results, market, year + "_" + v.file_merged_receipts)
    rows = v.readCSV(file_merged_receipts)[1]

    # row[0] is item_name
    for row in rows:
        if row[0] not in unique_items:
            unique_items.add(row[0])
            item_list.append([row[0]]) # Add the entire row to the list

    # Write data to CSV file
    file_unique_items = os.path.join(v.dir_base_CSV_results, market, year + "_" + v.file_unique_items)
    if item_list: v.writeItemsToCSV(file_unique_items, ["item"], item_list)
