import os
import Scripts.script_values as v

def merge_to_complete_categories(market):
    """
    Takes all the files that contain the unique items and matched categories over the years.
    Merges them and puts them back into the complete_items_categories files.
    """

    unique_items = set()  # Use a set to efficiently store unique item names
    unique_categories = set() # Use set to get all unique categories
    item_list = [] # List to hold unique items for writing to csv
    categories_list = [] # List for writing to csv

    # Load known category items into item list
    file_categories = os.path.join(v.dir_base_CSV_results, market, market+"_"+v.file_complete_items_categories)
    categoryRows = v.readCSV(file_categories)[1]

    # row[0] is item_name, row[1] is category
    for row in categoryRows:
        if row[0] not in unique_items:
            unique_items.add(row[0])
            item_list.append([row[0], row[1]])
        if row[1] not in unique_categories:
            unique_categories.add(row[1])
            categories_list.append([row[1]])

    # update unique items and item-category list with data from all the years
    dir_csv_results = os.path.join(v.dir_base_CSV_results, market)
    for filename in sorted(os.listdir(dir_csv_results)):
        if v.file_unique_items_and_categories_merged in filename:
            filepath = os.path.join(dir_csv_results, filename)

            uniqueItemsAndCategoriesMergedRows = v.readCSV(filepath)[1]
            # row[0] is item_name, row[1] is category
            for row in uniqueItemsAndCategoriesMergedRows:
                if row[0] not in unique_items:
                    unique_items.add(row[0])
                    item_list.append([row[0], row[1]])
    
    # Write data to CSV file
    if item_list: v.writeItemsToCSV(file_categories, ["item", "category"], item_list)
    
    file_unique_categories = os.path.join(v.dir_base_CSV_results, market, market+"_"+v.file_unique_categories)
    if categories_list: v.writeItemsToCSV(file_unique_categories, ["category"], categories_list)
    else: merge_to_complete_categories(market) # run again, the first time the complete categories file is not yet known.